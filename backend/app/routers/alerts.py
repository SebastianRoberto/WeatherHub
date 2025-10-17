"""
Router de alertas meteorológicas
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Alert, AlertHistory, City
from app.schemas import (
    AlertCreate, 
    AlertUpdate, 
    AlertResponse, 
    AlertHistoryResponse,
    MessageResponse
)
from app.auth import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[AlertResponse])
async def get_user_alerts(
    active_only: bool = Query(True, description="Solo alertas activas"),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener alertas del usuario"""
    
    query = db.query(Alert).filter(Alert.user_id == current_user.id)
    
    if active_only:
        query = query.filter(Alert.active == True, Alert.paused == False)
    
    alerts = query.all()
    return alerts


@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Crear nueva alerta"""
    
    # Verificar que la ciudad existe
    city = db.query(City).filter(City.id == alert_data.city_id).first()
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ciudad no encontrada"
        )
    
    # Verificar si ya existe una alerta similar
    existing_alert = db.query(Alert).filter(
        Alert.user_id == current_user.id,
        Alert.city_id == alert_data.city_id,
        Alert.metric == alert_data.metric,
        Alert.operator == alert_data.operator,
        Alert.threshold == alert_data.threshold
    ).first()
    
    if existing_alert:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una alerta con estos parámetros"
        )
    
    db_alert = Alert(
        user_id=current_user.id,
        city_id=alert_data.city_id,
        metric=alert_data.metric,
        operator=alert_data.operator,
        threshold=alert_data.threshold,
        unit=alert_data.unit
    )
    
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    return db_alert


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener alerta específica"""
    
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta no encontrada"
        )
    
    return alert


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Actualizar alerta"""
    
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta no encontrada"
        )
    
    # Actualizar campos
    if alert_update.active is not None:
        alert.active = alert_update.active
    if alert_update.paused is not None:
        alert.paused = alert_update.paused
    if alert_update.threshold is not None:
        alert.threshold = alert_update.threshold
    
    db.commit()
    db.refresh(alert)
    
    return alert


@router.delete("/{alert_id}", response_model=MessageResponse)
async def delete_alert(
    alert_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Eliminar alerta"""
    
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta no encontrada"
        )
    
    db.delete(alert)
    db.commit()
    
    return {"message": "Alerta eliminada exitosamente"}


@router.get("/history/", response_model=List[AlertHistoryResponse])
async def get_alert_history(
    from_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    to_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    city_id: Optional[int] = Query(None, description="ID de ciudad"),
    metric: Optional[str] = Query(None, description="Tipo de métrica"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de registros"),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener historial de activaciones de alertas"""
    
    from sqlalchemy.orm import selectinload
    
    query = db.query(AlertHistory).options(selectinload(AlertHistory.city)).filter(AlertHistory.user_id == current_user.id)
    
    if from_date:
        query = query.filter(AlertHistory.ts >= from_date)
    if to_date:
        query = query.filter(AlertHistory.ts <= to_date)
    if city_id:
        query = query.filter(AlertHistory.city_id == city_id)
    if metric:
        query = query.filter(AlertHistory.metric == metric)
    
    history = query.order_by(AlertHistory.ts.desc()).limit(limit).all()
    return history


@router.get("/active/", response_model=List[AlertHistoryResponse])
async def get_active_alerts(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener alertas activas recientes (últimas 24 horas)"""
    from sqlalchemy.orm import selectinload
    
    from_date = datetime.utcnow() - timedelta(hours=24)
    
    history = db.query(AlertHistory).options(selectinload(AlertHistory.city)).filter(
        AlertHistory.user_id == current_user.id,
        AlertHistory.ts >= from_date
    ).order_by(AlertHistory.ts.desc()).all()
    
    return history
