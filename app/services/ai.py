from openai import AsyncOpenAI
import json
import re
from typing import Dict, List, Any
from app.core.config import settings
from app.core.logging import logger

class AIService:
    def __init__(self):
        if settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL
        else:
            self.client = None
            self.model = None

    async def _generate_json(self, prompt: str) -> Any:
        if not self.client:
            logger.warning("OpenAI client not configured.")
            return None
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un analista de datos experto. Responde ÚNICAMENTE en formato JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error generating JSON from OpenAI: {str(e)}")
            return None

    async def get_executive_summary(self, metrics: Dict, comments: List[str]) -> str:
        if not self.client: return "IA no configurada (falta OPENAI_API_KEY)."
        
        # Prepare a clear summary of metrics for the LLM
        context = f"""
        Métricas actuales:
        - NPS Score: {metrics['nps']['score']} (Promotores: {metrics['nps']['promoters']}, Neutrales: {metrics['nps']['neutrals']}, Detractores: {metrics['nps']['detractors']})
        - CSAT %: {metrics['csat']['percentage']}% de satisfacción (Satisfechos: {metrics['csat']['satisfied']}, Neutrales: {metrics['csat']['neutral']}, Insatisfechos: {metrics['csat']['unsatisfied']})
        - CES promedio: {metrics['ces']['score']} / 5 (donde 1 es fácil y 5 es muy difícil)
        """
        
        prompt = f"{context}\nBasado en estos datos y los siguientes comentarios: {comments[:15]}, genera un resumen ejecutivo profesional y crítico de la situación actual. Debe ser un único párrafo corto (máximo 3 oraciones), directo y con enfoque de negocio."
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return "Error al generar resumen ejecutivo."

    async def get_indicator_insight(self, name: str, data: Any, comments: List[str]) -> str:
        if not self.client: return "IA no configurada."
        
        desc = ""
        if name == "NPS":
            desc = f"Score: {data['score']} (Promotores: {data['promoters']}, Neutrales: {data['neutrals']}, Detractores: {data['detractors']})"
        elif name == "CSAT":
            desc = f"Porcentaje de Satisfacción: {data['percentage']}% (Satisfechos: {data['satisfied']}, Neutrales: {data['neutral']}, Insatisfechos: {data['unsatisfied']}). IMPORTANTE: No confundas el promedio ({data['score']}) con el porcentaje de satisfacción ({data['percentage']}%)."
        elif name == "CES":
            desc = f"Esfuerzo promedio: {data['score']} / 5. (Bajo esfuerzo: {data['low_effort']}, Medio: {data['medium_effort']}, Alto: {data['high_effort']})"

        prompt = f"Analiza este indicador de {name}: {desc}. Comentarios relacionados: {comments[:15]}. Genera un único insight estratégico muy conciso que explique la raíz del número."
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except: return "Error al generar insight."

    async def get_drivers(self, comments: List[str]) -> Dict:
        prompt = f"""Analiza estos comentarios: {comments[:30]}. 
        Extrae el Top 3 de positive_drivers y el Top 3 de negative_drivers. 
        Formato JSON: {{"positive_drivers": [str], "negative_drivers": [str]}}"""
        result = await self._generate_json(prompt)
        return result or {"positive_drivers": [], "negative_drivers": []}

    async def get_topics(self, comments: List[str]) -> List[Dict]:
        prompt = f"""Analiza los siguientes comentarios: {comments[:40]}. 
        Identifica temas recurrentes y cuenta menciones aproximadas. 
        Formato JSON: {{"topics": [{{"topic": str, "mentions": int}}]}}"""
        result = await self._generate_json(prompt)
        return result.get("topics", []) if result else []

    async def get_action_plans(self, metrics: Dict, comments: List[str]) -> List[Dict]:
        prompt = f"""Basado en estas métricas ({metrics}) y estos comentarios ({comments[:20]}), 
        propón planes de acción priorizados. 
        Formato JSON: {{"action_plans": [{{"priority": "Alta/Media/Baja", "issue": "descripción", "recommendation": "descripción", "expected_impact": "descripción"}}]}}"""
        result = await self._generate_json(prompt)
        return result.get("action_plans", []) if result else []

    async def get_segment_descriptions(self, segments: Dict) -> List[Dict]:
        segments_list = []
        for key, data in segments.items():
            name = key.replace("_", " ").title()
            prompt = f"""Describe el perfil de cliente del segmento '{name}' basados en este contexto de feedback: {data['comments']}. Retorna un JSON con {{"description": "texto"}}"""
            desc_json = await self._generate_json(prompt)
            desc = desc_json.get("description", "Sin descripción disponible.") if desc_json else "Error al generar descripción."
            segments_list.append({
                "key": key, # Mantenemos la llave original para mapeo seguro
                "segment": name,
                "description": desc
            })
        return segments_list
