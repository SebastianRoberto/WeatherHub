"""
Aplicación principal FastAPI para WeatherHub
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.database import SessionLocal
from app.services.etl_service import ETLService
import structlog
from app.config import settings
from app.database import engine, Base
from app.routers import auth, weather, cities, alerts, export, etl

# Configurar logging estructurado
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("Iniciando WeatherHub API")
    
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)
    logger.info("Base de datos inicializada")
    # Iniciar scheduler ETL si está habilitado
    stop_event = asyncio.Event()
    etl_task = None
    if settings.etl_enabled:
        logger.info("ETL automático habilitado", interval_minutes=settings.etl_interval_minutes)

        async def etl_loop():
            executor = ThreadPoolExecutor(max_workers=1)
            try:
                while not stop_event.is_set():
                    try:
                        logger.info("ETL programado: inicio")
                        # Ejecutar en hilo para no bloquear el event loop
                        def run_job():
                            db = SessionLocal()
                            try:
                                service = ETLService(db)
                                # Respetar política de skip por datos recientes
                                return asyncio.run(service.run_etl_all_cities(force_update=False))
                            finally:
                                db.close()
                        loop = asyncio.get_running_loop()
                        await loop.run_in_executor(executor, run_job)
                        logger.info("ETL programado: fin")
                    except Exception as e:
                        logger.error("Error en ETL programado", error=str(e), exc_info=True)
                    # esperar intervalo o hasta stop
                    try:
                        await asyncio.wait_for(stop_event.wait(), timeout=max(1, settings.etl_interval_minutes * 60))
                    except asyncio.TimeoutError:
                        pass
            finally:
                executor.shutdown(wait=False, cancel_futures=True)

        etl_task = asyncio.create_task(etl_loop())
    
    yield
    
    # Shutdown
    logger.info("Cerrando WeatherHub API")
    # Parar scheduler
    try:
        stop_event.set()
        if etl_task:
            await asyncio.wait([etl_task], timeout=5)
    except Exception:
        pass


# Crear aplicación FastAPI
app = FastAPI(
    title="WeatherHub API",
    description="API para sistema ETL de datos meteorológicos",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar CORS
# En desarrollo permite todos los orígenes, en producción solo los configurados
allow_origins = ["*"] if settings.debug else settings.cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware de logging de requests
@app.middleware("http")
async def log_requests(request, call_next):
    """Middleware para logging de requests"""
    start_time = structlog.get_logger().info("Request started", 
                                            method=request.method, 
                                            url=str(request.url))
    
    response = await call_next(request)
    
    structlog.get_logger().info("Request completed", 
                               method=request.method, 
                               url=str(request.url),
                               status_code=response.status_code)
    
    return response


# Incluir routers
app.include_router(auth.router, prefix="/auth", tags=["autenticación"])
app.include_router(cities.router, prefix="/cities", tags=["ciudades"])
app.include_router(weather.router, prefix="/weather", tags=["clima"])
app.include_router(alerts.router, prefix="/alerts", tags=["alertas"])
app.include_router(export.router, prefix="/export", tags=["exportación"])
app.include_router(etl.router, prefix="/etl", tags=["etl"])


# Endpoints básicos
@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "WeatherHub API",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "weatherhub-api",
        "version": "1.0.0"
    }


# Manejo global de excepciones
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Manejo global de excepciones HTTP"""
    logger.error("HTTP Exception", 
                status_code=exc.status_code, 
                detail=exc.detail,
                url=str(request.url))
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "success": False}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Manejo global de excepciones generales"""
    logger.error("Unhandled exception", 
                error=str(exc), 
                url=str(request.url),
                exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error interno del servidor", "success": False}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
