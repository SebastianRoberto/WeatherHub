"""
Router de ciudades
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import City, Favorite
from app.schemas import CityCreate, CityResponse, FavoriteCreate, FavoriteResponse, MessageResponse
from app.auth import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[CityResponse])
async def get_cities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Obtener lista de ciudades con paginación y búsqueda"""
    
    query = db.query(City)
    
    if search:
        query = query.filter(
            City.name.ilike(f"%{search}%") | 
            City.country.ilike(f"%{search}%")
        )
    
    cities = query.offset(skip).limit(limit).all()
    return cities


@router.get("/{city_id}", response_model=CityResponse)
async def get_city(city_id: int, db: Session = Depends(get_db)):
    """Obtener ciudad por ID"""
    
    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ciudad no encontrada"
        )
    
    return city


@router.post("/", response_model=CityResponse, status_code=status.HTTP_201_CREATED)
async def create_city(
    city_data: CityCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Crear nueva ciudad (requiere autenticación)"""
    
    # Verificar si la ciudad ya existe
    existing_city = db.query(City).filter(
        City.name == city_data.name,
        City.country == city_data.country
    ).first()
    
    if existing_city:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La ciudad ya existe"
        )
    
    db_city = City(**city_data.dict())
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    
    return db_city


@router.get("/favorites/", response_model=List[FavoriteResponse])
async def get_user_favorites(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener ciudades favoritas del usuario"""
    
    favorites = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
    return favorites


@router.post("/favorites/", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    favorite_data: FavoriteCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Añadir ciudad a favoritos"""
    
    # Verificar que la ciudad existe
    city = db.query(City).filter(City.id == favorite_data.city_id).first()
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ciudad no encontrada"
        )
    
    # Verificar si ya es favorita
    existing_favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.city_id == favorite_data.city_id
    ).first()
    
    if existing_favorite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La ciudad ya está en favoritos"
        )
    
    db_favorite = Favorite(
        user_id=current_user.id,
        city_id=favorite_data.city_id
    )
    
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    
    return db_favorite


@router.delete("/favorites/{city_id}", response_model=MessageResponse)
async def remove_favorite(
    city_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Eliminar ciudad de favoritos"""
    
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.city_id == city_id
    ).first()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La ciudad no está en favoritos"
        )
    
    db.delete(favorite)
    db.commit()
    
    return {"message": "Ciudad eliminada de favoritos"}
