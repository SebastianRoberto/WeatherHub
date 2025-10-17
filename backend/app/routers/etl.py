"""
Router de ETL (Extract, Transform, Load)
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ETLRunRequest, ETLStatusResponse, MessageResponse
from app.auth import get_current_active_user
from app.services.etl_service import ETLService
from datetime import datetime

router = APIRouter()


@router.post("/run", response_model=ETLStatusResponse)
async def run_etl_manual(
    etl_request: ETLRunRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Ejecutar ETL manualmente (requiere autenticación)"""
    
    etl_service = ETLService(db)
    
    try:
        if etl_request.city_id:
            # Ejecutar ETL para una ciudad específica
            result = await etl_service.run_etl_for_city(etl_request.city_id, etl_request.force_update)
            return ETLStatusResponse(
                status="success",
                message=f"ETL ejecutado para ciudad ID {etl_request.city_id}",
                processed_cities=1,
                errors=[]
            )
        else:
            # Ejecutar ETL para todas las ciudades
            result = await etl_service.run_etl_all_cities(etl_request.force_update)
            return ETLStatusResponse(
                status="success",
                message="ETL ejecutado para todas las ciudades",
                processed_cities=result.get("processed", 0),
                errors=result.get("errors", [])
            )
    
    except Exception as e:
        return ETLStatusResponse(
            status="error",
            message=f"Error ejecutando ETL: {str(e)}",
            processed_cities=0,
            errors=[str(e)]
        )


@router.post("/run/background", response_model=MessageResponse)
async def run_etl_background(
    etl_request: ETLRunRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Ejecutar ETL en segundo plano"""
    
    etl_service = ETLService(db)
    
    if etl_request.city_id:
        background_tasks.add_task(
            etl_service.run_etl_for_city, 
            etl_request.city_id, 
            etl_request.force_update
        )
        return {"message": f"ETL iniciado en segundo plano para ciudad ID {etl_request.city_id}"}
    else:
        background_tasks.add_task(
            etl_service.run_etl_all_cities, 
            etl_request.force_update
        )
        return {"message": "ETL iniciado en segundo plano para todas las ciudades"}


@router.get("/status", response_model=ETLStatusResponse)
async def get_etl_status(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener estado del ETL"""
    
    etl_service = ETLService(db)
    
    try:
        status_info = await etl_service.get_etl_status()
        return ETLStatusResponse(
            status="success",
            message="Estado del ETL obtenido exitosamente",
            processed_cities=status_info.get("total_cities", 0),
            errors=status_info.get("recent_errors", [])
        )
    except Exception as e:
        return ETLStatusResponse(
            status="error",
            message=f"Error obteniendo estado del ETL: {str(e)}",
            processed_cities=0,
            errors=[str(e)]
        )


@router.get("/cities", response_model=dict)
async def get_etl_cities(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de ciudades configuradas para ETL"""
    
    etl_service = ETLService(db)
    cities = await etl_service.get_etl_cities()
    
    return {
        "cities": cities,
        "total": len(cities)
    }
