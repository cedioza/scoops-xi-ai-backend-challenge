from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.feedback import Feedback, FeedbackCreate, FeedbackRead
from app.services.metrics import MetricsService
from app.services.ai import AIService
from app.core.db import get_table
from datetime import date
from typing import List, Dict, Any, Optional
import uuid
from boto3.dynamodb.conditions import Attr

router = APIRouter()
ai_service = AIService()

# Tags for grouped documentation
TAG_FEEDBACK = "Ingesta de Datos"
TAG_INSIGHTS = "AI Insights & Analytics"

def get_filtered_feedbacks(start_date: Optional[date], end_date: Optional[date]) -> List[Feedback]:
    table = get_table()
    
    # DynamoDB Scan with FilterExpression
    filter_expression = None
    if start_date:
        filter_expression = Attr('date').gte(start_date.isoformat())
    if end_date:
        if filter_expression:
            filter_expression = filter_expression & Attr('date').lte(end_date.isoformat())
        else:
            filter_expression = Attr('date').lte(end_date.isoformat())
            
    scan_kwargs = {}
    if filter_expression:
        scan_kwargs['FilterExpression'] = filter_expression
        
    response = table.scan(**scan_kwargs)
    items = response.get('Items', [])
    
    if not items:
        raise HTTPException(status_code=404, detail="No se encontró feedback para el periodo seleccionado")
        
    # Convert back to Feedback objects
    feedbacks = []
    for item in items:
        feedbacks.append(Feedback(
            id=item['id'],
            date=date.fromisoformat(item['date']),
            nps=int(item['nps']),
            csat=int(item['csat']),
            ces=int(item['ces']),
            comment=item.get('comment')
        ))
    
    # DynamoDB scan results are unordered, sort by date for consistency
    feedbacks.sort(key=lambda x: x.date)
    return feedbacks

@router.post("/feedback", tags=[TAG_FEEDBACK], summary="Registrar nuevo feedback")
async def create_feedback(feedback_in: FeedbackCreate):
    """
    Almacena un nuevo registro de feedback del cliente en AWS DynamoDB.
    """
    table = get_table()
    feedback_id = str(uuid.uuid4())
    
    item = {
        "id": feedback_id,
        "date": feedback_in.date.isoformat(),
        "nps": feedback_in.nps,
        "csat": feedback_in.csat,
        "ces": feedback_in.ces,
        "comment": feedback_in.comment
    }
    
    table.put_item(Item=item)
    
    return {
        "status": "success",
        "message": "Feedback almacenado correctamente en DynamoDB",
        "data": {
            "id": f"fb_{feedback_id}",
            "date": feedback_in.date.isoformat()
        }
    }

@router.get("/insights/overview", tags=[TAG_INSIGHTS], summary="Resumen Ejecutivo General")
async def get_overview(
    start_date: Optional[date] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"), 
    end_date: Optional[date] = Query(None, description="Fecha de fin (YYYY-MM-DD)")
):
    feedbacks = get_filtered_feedbacks(start_date, end_date)
    metrics = MetricsService.get_all_metrics(feedbacks)
    comments = [f.comment for f in feedbacks if f.comment]
    
    summary = await ai_service.get_executive_summary(metrics, comments)
    
    return {
        "period": f"{feedbacks[0].date.strftime('%Y-%m')} to {feedbacks[-1].date.strftime('%Y-%m')}",
        "metrics": {
            "nps_avg": metrics["nps"]["score"],
            "csat_avg": metrics["csat"]["percentage"], # Retorna el % de satisfacción según la fórmula
            "ces_avg": metrics["ces"]["score"]
        },
        "executive_summary": summary
    }

@router.get("/insights/nps", tags=[TAG_INSIGHTS], summary="Análisis Detallado de NPS")
async def get_nps_insight(
    start_date: Optional[date] = Query(None), 
    end_date: Optional[date] = Query(None)
):
    feedbacks = get_filtered_feedbacks(start_date, end_date)
    metrics = MetricsService.calculate_nps(feedbacks)
    comments = [f.comment for f in feedbacks if f.nps <= 6 and f.comment]
    
    insight = await ai_service.get_indicator_insight("NPS", metrics, comments)
    
    return {
        "distribution": {
            "promoters": metrics["promoters"],
            "neutrals": metrics["neutrals"],
            "detractors": metrics["detractors"]
        },
        "insight": insight
    }

@router.get("/insights/csat", tags=[TAG_INSIGHTS], summary="Análisis Detallado de CSAT")
async def get_csat_insight(
    start_date: Optional[date] = Query(None), 
    end_date: Optional[date] = Query(None)
):
    feedbacks = get_filtered_feedbacks(start_date, end_date)
    metrics = MetricsService.calculate_csat(feedbacks)
    comments = [f.comment for f in feedbacks if f.csat < 4 and f.comment]
    
    insight = await ai_service.get_indicator_insight("CSAT", metrics, comments)
    
    return {
        "distribution": {
            "satisfied": metrics["satisfied"],
            "neutral": metrics["neutral"],
            "unsatisfied": metrics["unsatisfied"]
        },
        "insight": insight
    }

@router.get("/insights/ces", tags=[TAG_INSIGHTS], summary="Análisis Detallado de CES")
async def get_ces_insight(
    start_date: Optional[date] = Query(None), 
    end_date: Optional[date] = Query(None)
):
    feedbacks = get_filtered_feedbacks(start_date, end_date)
    metrics = MetricsService.calculate_ces(feedbacks)
    comments = [f.comment for f in feedbacks if f.ces >= 4 and f.comment]
    
    insight = await ai_service.get_indicator_insight("CES", metrics, comments)
    
    return {
        "distribution": {
            "low_effort": metrics["low_effort"],
            "medium_effort": metrics["medium_effort"],
            "high_effort": metrics["high_effort"]
        },
        "insight": insight
    }

@router.get("/insights/drivers", tags=[TAG_INSIGHTS], summary="Top Drivers Positivos y Negativos")
async def get_drivers(
    start_date: Optional[date] = Query(None), 
    end_date: Optional[date] = Query(None)
):
    feedbacks = get_filtered_feedbacks(start_date, end_date)
    comments = [f.comment for f in feedbacks if f.comment]
    return await ai_service.get_drivers(comments)

@router.get("/insights/topics", tags=[TAG_INSIGHTS], summary="Análisis de Tópicos Recurrentes")
async def get_topics(
    start_date: Optional[date] = Query(None), 
    end_date: Optional[date] = Query(None)
):
    feedbacks = get_filtered_feedbacks(start_date, end_date)
    comments = [f.comment for f in feedbacks if f.comment]
    topics = await ai_service.get_topics(comments)
    return {"topics": topics}

@router.get("/insights/segments", tags=[TAG_INSIGHTS], summary="Identificación de Segmentos Críticos")
async def get_segments(
    start_date: Optional[date] = Query(None), 
    end_date: Optional[date] = Query(None)
):
    feedbacks = get_filtered_feedbacks(start_date, end_date)
    total = len(feedbacks)
    metrics = MetricsService.get_all_metrics(feedbacks)
    segments_data = metrics["segments"]
    
    descriptions = await ai_service.get_segment_descriptions(segments_data)
    
    results = []
    for desc in descriptions:
        slug = desc["key"] # Usamos el mapeo directo por llave
        if slug in segments_data:
            results.append({
                "segment": segments_data[slug]["label"],
                "percentage": round((segments_data[slug]["count"] / total) * 100),
                "description": desc["description"]
            })
            
    return {"segments": results}

@router.get("/insights/action-plans", tags=[TAG_INSIGHTS], summary="Planes de Mejora Priorizados")
async def get_action_plans(
    start_date: Optional[date] = Query(None), 
    end_date: Optional[date] = Query(None)
):
    feedbacks = get_filtered_feedbacks(start_date, end_date)
    metrics = MetricsService.get_all_metrics(feedbacks)
    comments = [f.comment for f in feedbacks if f.comment]
    
    plans = await ai_service.get_action_plans(metrics, comments)
    return {"action_plans": plans}
