#!/usr/bin/env python3
"""
Script ETL para WeatherHub - Ejecutar como cron job
"""
import sys
import os
import asyncio
import structlog
from datetime import datetime

# Añadir el directorio backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import SessionLocal
from app.services.etl_service import ETLService
from app.config import settings

# Configurar logging
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


async def main():
    """Función principal del ETL"""
    
    logger.info("Iniciando ETL job", timestamp=datetime.utcnow().isoformat())
    
    # Crear sesión de base de datos
    db = SessionLocal()
    
    try:
        # Crear servicio ETL
        etl_service = ETLService(db)
        
        # Ejecutar ETL para todas las ciudades
        result = await etl_service.run_etl_all_cities(force_update=False)
        
        logger.info("ETL job completado", 
                   processed=result["processed"],
                   errors=len(result["errors"]),
                   total_cities=result["total_cities"])
        
        # Log de errores si los hay
        if result["errors"]:
            for error in result["errors"]:
                logger.error("Error en ETL", error=error)
        
        return 0 if not result["errors"] else 1
        
    except Exception as e:
        logger.error("Error crítico en ETL job", error=str(e), exc_info=True)
        return 1
    
    finally:
        db.close()


if __name__ == "__main__":
    # Ejecutar ETL
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
