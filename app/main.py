from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.core.db import init_db

app = FastAPI(
    title="Scoops XI - Experience Intelligence AI Backend",
    description="""
    ## Elevando la Experiencia del Cliente mediante Inteligencia Artificial.
    
    Este servicio backend procesa feedback de clientes aplicando el principio de procesamiento determinístico:
    1. **Cálculo Determinístico**: NPS, CSAT y CES calculados mediante lógica de negocio robusta.
    2. **IA Generativa**: Transformación de datos estructurados en insights estratégicos utilizando OpenAI.
    
    ### Endpoints Principales
    * **Ingesta**: Registro de nuevos feedbacks.
    * **Analytics**: Métricas crudas y distribuciones.
    * **AI Insights**: Análisis narrativo, drivers y planes de acción.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.logging import logger

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"status": "error", "message": "Datos de entrada inválidos", "details": exc.errors()},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "Ocurrió un error interno en el servidor"},
    )

@app.on_event("startup")
def on_startup():
    logger.info("Initializing database...")
    init_db()
    logger.info("Application started successfully.")

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Welcome to Scoops XI AI Backend API"}
