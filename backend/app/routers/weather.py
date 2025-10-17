"""
Router de datos meteorológicos
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models import City, WeatherHourly, Favorite
from app.schemas import (
    WeatherCurrentResponse, 
    WeatherHistoryResponse, 
    WeatherCompareResponse,
    WeatherData,
    TemperatureUnit
)
from app.auth import get_current_active_user
from app.services.weather_service import WeatherService
from app.utils.city_normalizer import normalize_city_name, normalize_city_list

router = APIRouter()


@router.get("/current", response_model=WeatherCurrentResponse)
async def get_current_weather(
    city: str = Query(..., description="Nombre de la ciudad"),
    unit: TemperatureUnit = Query(TemperatureUnit.CELSIUS, description="Unidad de temperatura"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Obtener clima actual de una ciudad"""
    
    # Normalizar nombre de ciudad
    normalized_city = normalize_city_name(city)
    
    # Buscar la ciudad
    city_obj = db.query(City).filter(City.name.ilike(f"%{normalized_city}%")).first()
    if not city_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ciudad no encontrada"
        )
    
    # Obtener datos meteorológicos más recientes
    weather_data = db.query(WeatherHourly).filter(
        WeatherHourly.city_id == city_obj.id
    ).order_by(WeatherHourly.ts.desc()).first()
    
    if not weather_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay datos meteorológicos disponibles para esta ciudad"
        )
    
    # Convertir datos según la unidad solicitada
    weather_service = WeatherService()
    converted_data = weather_service.convert_weather_data(weather_data, unit)
    
    return WeatherCurrentResponse(
        city=city_obj,
        data=converted_data,
        timestamp=weather_data.ts
    )


@router.get("/history", response_model=WeatherHistoryResponse)
async def get_weather_history(
    city: str = Query(..., description="Nombre de la ciudad"),
    from_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    to_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    days: int = Query(7, ge=1, le=365, description="Número de días hacia atrás"),
    unit: TemperatureUnit = Query(TemperatureUnit.CELSIUS, description="Unidad de temperatura"),
    limit: int = Query(1000, ge=1, le=10000, description="Límite de registros"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Obtener historial meteorológico de una ciudad"""
    
    # Buscar la ciudad
    city_obj = db.query(City).filter(City.name.ilike(f"%{city}%")).first()
    if not city_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ciudad no encontrada"
        )
    
    # Determinar rango de fechas
    if not from_date:
        from_date = datetime.utcnow() - timedelta(days=days)
    if not to_date:
        to_date = datetime.utcnow()
    
    # Obtener datos históricos
    weather_data = db.query(WeatherHourly).filter(
        WeatherHourly.city_id == city_obj.id,
        WeatherHourly.ts >= from_date,
        WeatherHourly.ts <= to_date
    ).order_by(WeatherHourly.ts.asc()).limit(limit).all()
    
    if not weather_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay datos históricos disponibles para el rango especificado"
        )
    
    # Convertir datos según la unidad solicitada
    weather_service = WeatherService()
    converted_data = [weather_service.convert_weather_data(data, unit) for data in weather_data]
    
    return WeatherHistoryResponse(
        city=city_obj,
        data=converted_data,
        from_date=from_date,
        to_date=to_date,
        unit=unit
    )


@router.get("/compare", response_model=WeatherCompareResponse)
async def compare_weather(
    cities: str = Query(..., description="Nombres de ciudades separados por coma"),
    from_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    to_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    days: int = Query(7, ge=1, le=365, description="Número de días hacia atrás"),
    unit: TemperatureUnit = Query(TemperatureUnit.CELSIUS, description="Unidad de temperatura"),
    limit: int = Query(1000, ge=1, le=10000, description="Límite de registros por ciudad"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Comparar datos meteorológicos de múltiples ciudades"""
    
    # Parsear y normalizar nombres de ciudades
    city_names = [name.strip() for name in cities.split(",")]
    normalized_cities = normalize_city_list(city_names)
    if len(city_names) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe especificar al menos 2 ciudades para comparar"
        )
    
    # Buscar ciudades
    city_objects = []
    for city_name in normalized_cities:
        city_obj = db.query(City).filter(City.name.ilike(f"%{city_name}%")).first()
        if not city_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ciudad '{city_name}' no encontrada"
            )
        city_objects.append(city_obj)
    
    # Determinar rango de fechas
    if not from_date:
        from_date = datetime.utcnow() - timedelta(days=days)
    if not to_date:
        to_date = datetime.utcnow()
    
    # Obtener datos para cada ciudad
    weather_service = WeatherService()
    cities_data = {}
    
    for city_obj in city_objects:
        weather_data = db.query(WeatherHourly).filter(
            WeatherHourly.city_id == city_obj.id,
            WeatherHourly.ts >= from_date,
            WeatherHourly.ts <= to_date
        ).order_by(WeatherHourly.ts.asc()).limit(limit).all()
        
        if weather_data:
            converted_data = [weather_service.convert_weather_data(data, unit) for data in weather_data]
            cities_data[city_obj.name] = converted_data
    
    if not cities_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay datos disponibles para las ciudades especificadas en el rango de fechas"
        )
    
    return WeatherCompareResponse(
        cities=city_objects,
        data=cities_data,
        from_date=from_date,
        to_date=to_date,
        unit=unit
    )


@router.get("/favorites/current", response_model=List[WeatherCurrentResponse])
async def get_favorites_current_weather(
    unit: TemperatureUnit = Query(TemperatureUnit.CELSIUS, description="Unidad de temperatura"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Obtener clima actual de todas las ciudades favoritas"""
    
    # Obtener ciudades favoritas
    favorites = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
    
    if not favorites:
        return []
    
    weather_service = WeatherService()
    results = []
    
    for favorite in favorites:
        # Obtener datos más recientes
        weather_data = db.query(WeatherHourly).filter(
            WeatherHourly.city_id == favorite.city_id
        ).order_by(WeatherHourly.ts.desc()).first()
        
        if weather_data:
            converted_data = weather_service.convert_weather_data(weather_data, unit)
            results.append(WeatherCurrentResponse(
                city=favorite.city,
                data=converted_data,
                timestamp=weather_data.ts
            ))
    
    return results


# =============================================================================
# NUEVOS ENDPOINTS ESPECIALIZADOS POR MÉTRICA
# =============================================================================

@router.get("/history/temperature")
async def get_temperature_history(
    city: str = Query(..., description="Nombre de la ciudad"),
    from_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    to_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    days: int = Query(7, ge=1, le=365, description="Número de días hacia atrás"),
    unit: TemperatureUnit = Query(TemperatureUnit.CELSIUS, description="Unidad de temperatura"),
    limit: int = Query(1000, ge=1, le=10000, description="Límite de registros"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Obtener historial de temperatura de una ciudad"""
    
    # Normalizar nombre de ciudad
    normalized_city = normalize_city_name(city)
    
    # Buscar la ciudad
    city_obj = db.query(City).filter(City.name.ilike(f"%{normalized_city}%")).first()
    if not city_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ciudad no encontrada"
        )
    
    # Determinar rango de fechas
    if not from_date:
        from_date = datetime.utcnow() - timedelta(days=days)
    if not to_date:
        to_date = datetime.utcnow()
    
    # Obtener datos de temperatura
    weather_data = db.query(WeatherHourly).filter(
        WeatherHourly.city_id == city_obj.id,
        WeatherHourly.ts >= from_date,
        WeatherHourly.ts <= to_date
    ).order_by(WeatherHourly.ts.asc()).limit(limit).all()
    
    if not weather_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay datos de temperatura disponibles para esta ciudad en el rango de fechas"
        )
    
    # Convertir datos según la unidad solicitada
    weather_service = WeatherService()
    converted_data = [weather_service.convert_weather_data(data, unit) for data in weather_data]
    
    return {
        "city": city_obj,
        "metric": "temperature",
        "data": converted_data,
        "from_date": from_date,
        "to_date": to_date,
        "unit": unit,
        "count": len(converted_data)
    }


@router.get("/history/humidity")
async def get_humidity_history(
    city: str = Query(..., description="Nombre de la ciudad"),
    from_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    to_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    days: int = Query(7, ge=1, le=365, description="Número de días hacia atrás"),
    limit: int = Query(1000, ge=1, le=10000, description="Límite de registros"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Obtener historial de humedad de una ciudad"""
    
    # Normalizar nombre de ciudad
    normalized_city = normalize_city_name(city)
    
    # Buscar la ciudad
    city_obj = db.query(City).filter(City.name.ilike(f"%{normalized_city}%")).first()
    if not city_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ciudad no encontrada"
        )
    
    # Determinar rango de fechas
    if not from_date:
        from_date = datetime.utcnow() - timedelta(days=days)
    if not to_date:
        to_date = datetime.utcnow()
    
    # Obtener datos de humedad
    weather_data = db.query(WeatherHourly).filter(
        WeatherHourly.city_id == city_obj.id,
        WeatherHourly.ts >= from_date,
        WeatherHourly.ts <= to_date
    ).order_by(WeatherHourly.ts.asc()).limit(limit).all()
    
    if not weather_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay datos de humedad disponibles para esta ciudad en el rango de fechas"
        )
    
    # Extraer solo datos de humedad
    humidity_data = []
    for data in weather_data:
        humidity_data.append({
            "timestamp": data.ts,
            "humidity": data.humidity,
            "city_id": data.city_id,
            "city_name": city_obj.name
        })
    
    return {
        "city": city_obj,
        "metric": "humidity",
        "data": humidity_data,
        "from_date": from_date,
        "to_date": to_date,
        "unit": "%",
        "count": len(humidity_data)
    }


@router.get("/history/pressure")
async def get_pressure_history(
    city: str = Query(..., description="Nombre de la ciudad"),
    from_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    to_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    days: int = Query(7, ge=1, le=365, description="Número de días hacia atrás"),
    limit: int = Query(1000, ge=1, le=10000, description="Límite de registros"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Obtener historial de presión de una ciudad"""
    
    # Normalizar nombre de ciudad
    normalized_city = normalize_city_name(city)
    
    # Buscar la ciudad
    city_obj = db.query(City).filter(City.name.ilike(f"%{normalized_city}%")).first()
    if not city_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ciudad no encontrada"
        )
    
    # Determinar rango de fechas
    if not from_date:
        from_date = datetime.utcnow() - timedelta(days=days)
    if not to_date:
        to_date = datetime.utcnow()
    
    # Obtener datos de presión
    weather_data = db.query(WeatherHourly).filter(
        WeatherHourly.city_id == city_obj.id,
        WeatherHourly.ts >= from_date,
        WeatherHourly.ts <= to_date
    ).order_by(WeatherHourly.ts.asc()).limit(limit).all()
    
    if not weather_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay datos de presión disponibles para esta ciudad en el rango de fechas"
        )
    
    # Extraer solo datos de presión
    pressure_data = []
    for data in weather_data:
        pressure_data.append({
            "timestamp": data.ts,
            "pressure": data.pressure,
            "city_id": data.city_id,
            "city_name": city_obj.name
        })
    
    return {
        "city": city_obj,
        "metric": "pressure",
        "data": pressure_data,
        "from_date": from_date,
        "to_date": to_date,
        "unit": "hPa",
        "count": len(pressure_data)
    }


@router.get("/history/wind")
async def get_wind_history(
    city: str = Query(..., description="Nombre de la ciudad"),
    from_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    to_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    days: int = Query(7, ge=1, le=365, description="Número de días hacia atrás"),
    limit: int = Query(1000, ge=1, le=10000, description="Límite de registros"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Obtener historial de viento de una ciudad"""
    
    # Normalizar nombre de ciudad
    normalized_city = normalize_city_name(city)
    
    # Buscar la ciudad
    city_obj = db.query(City).filter(City.name.ilike(f"%{normalized_city}%")).first()
    if not city_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ciudad no encontrada"
        )
    
    # Determinar rango de fechas
    if not from_date:
        from_date = datetime.utcnow() - timedelta(days=days)
    if not to_date:
        to_date = datetime.utcnow()
    
    # Obtener datos de viento
    weather_data = db.query(WeatherHourly).filter(
        WeatherHourly.city_id == city_obj.id,
        WeatherHourly.ts >= from_date,
        WeatherHourly.ts <= to_date
    ).order_by(WeatherHourly.ts.asc()).limit(limit).all()
    
    if not weather_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay datos de viento disponibles para esta ciudad en el rango de fechas"
        )
    
    # Extraer solo datos de viento
    wind_data = []
    for data in weather_data:
        wind_data.append({
            "timestamp": data.ts,
            "wind_speed": data.wind_speed,
            "wind_deg": data.wind_deg,
            "city_id": data.city_id,
            "city_name": city_obj.name
        })
    
    return {
        "city": city_obj,
        "metric": "wind",
        "data": wind_data,
        "from_date": from_date,
        "to_date": to_date,
        "unit": "m/s",
        "count": len(wind_data)
    }


# =============================================================================
# ENDPOINTS DE COMPARACIÓN ESPECIALIZADOS POR MÉTRICA
# =============================================================================

@router.get("/compare/temperature")
async def compare_temperature(
    cities: str = Query(..., description="Nombres de ciudades separados por coma"),
    from_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    to_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    days: int = Query(7, ge=1, le=365, description="Número de días hacia atrás"),
    unit: TemperatureUnit = Query(TemperatureUnit.CELSIUS, description="Unidad de temperatura"),
    limit: int = Query(1000, ge=1, le=10000, description="Límite de registros por ciudad"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Comparar temperatura de múltiples ciudades"""
    
    # Parsear y normalizar nombres de ciudades
    city_names = [name.strip() for name in cities.split(",")]
    normalized_cities = normalize_city_list(city_names)
    if len(city_names) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe especificar al menos 2 ciudades para comparar"
        )
    
    # Buscar ciudades
    city_objects = []
    for city_name in normalized_cities:
        city_obj = db.query(City).filter(City.name.ilike(f"%{city_name}%")).first()
        if not city_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ciudad '{city_name}' no encontrada"
            )
        city_objects.append(city_obj)
    
    # Determinar rango de fechas
    if not from_date:
        from_date = datetime.utcnow() - timedelta(days=days)
    if not to_date:
        to_date = datetime.utcnow()
    
    # Obtener datos de temperatura para cada ciudad
    weather_service = WeatherService()
    cities_data = {}
    
    for city_obj in city_objects:
        weather_data = db.query(WeatherHourly).filter(
            WeatherHourly.city_id == city_obj.id,
            WeatherHourly.ts >= from_date,
            WeatherHourly.ts <= to_date
        ).order_by(WeatherHourly.ts.asc()).limit(limit).all()
        
        if weather_data:
            converted_data = [weather_service.convert_weather_data(data, unit) for data in weather_data]
            cities_data[city_obj.name] = converted_data
    
    if not cities_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay datos de temperatura disponibles para las ciudades especificadas en el rango de fechas"
        )
    
    return {
        "cities": city_objects,
        "metric": "temperature",
        "data": cities_data,
        "from_date": from_date,
        "to_date": to_date,
        "unit": unit,
        "count": sum(len(data) for data in cities_data.values())
    }


@router.get("/compare/humidity")
async def compare_humidity(
    cities: str = Query(..., description="Nombres de ciudades separados por coma"),
    from_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    to_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    days: int = Query(7, ge=1, le=365, description="Número de días hacia atrás"),
    limit: int = Query(1000, ge=1, le=10000, description="Límite de registros por ciudad"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Comparar humedad de múltiples ciudades"""
    
    # Parsear y normalizar nombres de ciudades
    city_names = [name.strip() for name in cities.split(",")]
    normalized_cities = normalize_city_list(city_names)
    if len(city_names) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe especificar al menos 2 ciudades para comparar"
        )
    
    # Buscar ciudades
    city_objects = []
    for city_name in normalized_cities:
        city_obj = db.query(City).filter(City.name.ilike(f"%{city_name}%")).first()
        if not city_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ciudad '{city_name}' no encontrada"
            )
        city_objects.append(city_obj)
    
    # Determinar rango de fechas
    if not from_date:
        from_date = datetime.utcnow() - timedelta(days=days)
    if not to_date:
        to_date = datetime.utcnow()
    
    # Obtener datos de humedad para cada ciudad
    cities_data = {}
    
    for city_obj in city_objects:
        weather_data = db.query(WeatherHourly).filter(
            WeatherHourly.city_id == city_obj.id,
            WeatherHourly.ts >= from_date,
            WeatherHourly.ts <= to_date
        ).order_by(WeatherHourly.ts.asc()).limit(limit).all()
        
        if weather_data:
            humidity_data = []
            for data in weather_data:
                humidity_data.append({
                    "timestamp": data.ts,
                    "humidity": data.humidity,
                    "city_id": data.city_id,
                    "city_name": city_obj.name
                })
            cities_data[city_obj.name] = humidity_data
    
    if not cities_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay datos de humedad disponibles para las ciudades especificadas en el rango de fechas"
        )
    
    return {
        "cities": city_objects,
        "metric": "humidity",
        "data": cities_data,
        "from_date": from_date,
        "to_date": to_date,
        "unit": "%",
        "count": sum(len(data) for data in cities_data.values())
    }


@router.get("/compare/pressure")
async def compare_pressure(
    cities: str = Query(..., description="Nombres de ciudades separados por coma"),
    from_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    to_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    days: int = Query(7, ge=1, le=365, description="Número de días hacia atrás"),
    limit: int = Query(1000, ge=1, le=10000, description="Límite de registros por ciudad"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Comparar presión de múltiples ciudades"""
    
    # Parsear y normalizar nombres de ciudades
    city_names = [name.strip() for name in cities.split(",")]
    normalized_cities = normalize_city_list(city_names)
    if len(city_names) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe especificar al menos 2 ciudades para comparar"
        )
    
    # Buscar ciudades
    city_objects = []
    for city_name in normalized_cities:
        city_obj = db.query(City).filter(City.name.ilike(f"%{city_name}%")).first()
        if not city_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ciudad '{city_name}' no encontrada"
            )
        city_objects.append(city_obj)
    
    # Determinar rango de fechas
    if not from_date:
        from_date = datetime.utcnow() - timedelta(days=days)
    if not to_date:
        to_date = datetime.utcnow()
    
    # Obtener datos de presión para cada ciudad
    cities_data = {}
    
    for city_obj in city_objects:
        weather_data = db.query(WeatherHourly).filter(
            WeatherHourly.city_id == city_obj.id,
            WeatherHourly.ts >= from_date,
            WeatherHourly.ts <= to_date
        ).order_by(WeatherHourly.ts.asc()).limit(limit).all()
        
        if weather_data:
            pressure_data = []
            for data in weather_data:
                pressure_data.append({
                    "timestamp": data.ts,
                    "pressure": data.pressure,
                    "city_id": data.city_id,
                    "city_name": city_obj.name
                })
            cities_data[city_obj.name] = pressure_data
    
    if not cities_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay datos de presión disponibles para las ciudades especificadas en el rango de fechas"
        )
    
    return {
        "cities": city_objects,
        "metric": "pressure",
        "data": cities_data,
        "from_date": from_date,
        "to_date": to_date,
        "unit": "hPa",
        "count": sum(len(data) for data in cities_data.values())
    }


@router.get("/compare/wind")
async def compare_wind(
    cities: str = Query(..., description="Nombres de ciudades separados por coma"),
    from_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    to_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    days: int = Query(7, ge=1, le=365, description="Número de días hacia atrás"),
    limit: int = Query(1000, ge=1, le=10000, description="Límite de registros por ciudad"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Comparar viento de múltiples ciudades"""
    
    # Parsear y normalizar nombres de ciudades
    city_names = [name.strip() for name in cities.split(",")]
    normalized_cities = normalize_city_list(city_names)
    if len(city_names) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe especificar al menos 2 ciudades para comparar"
        )
    
    # Buscar ciudades
    city_objects = []
    for city_name in normalized_cities:
        city_obj = db.query(City).filter(City.name.ilike(f"%{city_name}%")).first()
        if not city_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ciudad '{city_name}' no encontrada"
            )
        city_objects.append(city_obj)
    
    # Determinar rango de fechas
    if not from_date:
        from_date = datetime.utcnow() - timedelta(days=days)
    if not to_date:
        to_date = datetime.utcnow()
    
    # Obtener datos de viento para cada ciudad
    cities_data = {}
    
    for city_obj in city_objects:
        weather_data = db.query(WeatherHourly).filter(
            WeatherHourly.city_id == city_obj.id,
            WeatherHourly.ts >= from_date,
            WeatherHourly.ts <= to_date
        ).order_by(WeatherHourly.ts.asc()).limit(limit).all()
        
        if weather_data:
            wind_data = []
            for data in weather_data:
                wind_data.append({
                    "timestamp": data.ts,
                    "wind_speed": data.wind_speed,
                    "wind_deg": data.wind_deg,
                    "city_id": data.city_id,
                    "city_name": city_obj.name
                })
            cities_data[city_obj.name] = wind_data
    
    if not cities_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay datos de viento disponibles para las ciudades especificadas en el rango de fechas"
        )
    
    return {
        "cities": city_objects,
        "metric": "wind",
        "data": cities_data,
        "from_date": from_date,
        "to_date": to_date,
        "unit": "m/s",
        "count": sum(len(data) for data in cities_data.values())
    }


# =============================================================================
# ENDPOINTS MÚLTIPLE MÉTRICAS (OPTIMIZACIÓN)
# =============================================================================

@router.get("/history/multiple")
async def get_multiple_metrics_history(
    city: str = Query(..., description="Nombre de la ciudad"),
    metrics: str = Query(..., description="Métricas separadas por coma (temperature,humidity,pressure,wind)"),
    from_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    to_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    days: int = Query(7, ge=1, le=365, description="Número de días hacia atrás"),
    unit: TemperatureUnit = Query(TemperatureUnit.CELSIUS, description="Unidad de temperatura"),
    limit: int = Query(1000, ge=1, le=10000, description="Límite de registros"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Obtener múltiples métricas de historial en una sola consulta"""
    
    # Parsear métricas
    metric_list = [m.strip() for m in metrics.split(",")]
    valid_metrics = ["temperature", "humidity", "pressure", "wind"]
    
    for metric in metric_list:
        if metric not in valid_metrics:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Métrica '{metric}' no válida. Métricas válidas: {', '.join(valid_metrics)}"
            )
    
    # Normalizar nombre de ciudad
    normalized_city = normalize_city_name(city)
    
    # Buscar la ciudad
    city_obj = db.query(City).filter(City.name.ilike(f"%{normalized_city}%")).first()
    if not city_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ciudad no encontrada"
        )
    
    # Determinar rango de fechas
    if not from_date:
        from_date = datetime.utcnow() - timedelta(days=days)
    if not to_date:
        to_date = datetime.utcnow()
    
    # Obtener datos una sola vez
    weather_data = db.query(WeatherHourly).filter(
        WeatherHourly.city_id == city_obj.id,
        WeatherHourly.ts >= from_date,
        WeatherHourly.ts <= to_date
    ).order_by(WeatherHourly.ts.asc()).limit(limit).all()
    
    if not weather_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay datos disponibles para esta ciudad en el rango de fechas"
        )
    
    # Procesar datos para cada métrica
    weather_service = WeatherService()
    results = {}
    
    for metric in metric_list:
        if metric == "temperature":
            converted_data = [weather_service.convert_weather_data(data, unit) for data in weather_data]
            results[metric] = converted_data
        else:
            # Extraer datos específicos para otras métricas
            metric_data = []
            for data in weather_data:
                if metric == "humidity":
                    metric_data.append({
                        "timestamp": data.ts,
                        "humidity": data.humidity,
                        "city_id": data.city_id,
                        "city_name": city_obj.name
                    })
                elif metric == "pressure":
                    metric_data.append({
                        "timestamp": data.ts,
                        "pressure": data.pressure,
                        "city_id": data.city_id,
                        "city_name": city_obj.name
                    })
                elif metric == "wind":
                    metric_data.append({
                        "timestamp": data.ts,
                        "wind_speed": data.wind_speed,
                        "wind_deg": data.wind_deg,
                        "city_id": data.city_id,
                        "city_name": city_obj.name
                    })
            results[metric] = metric_data
    
    return {
        "city": city_obj,
        "metrics": metric_list,
        "data": results,
        "from_date": from_date,
        "to_date": to_date,
        "unit": unit,
        "count": len(weather_data)
    }


@router.get("/compare/multiple")
async def compare_multiple_metrics(
    cities: str = Query(..., description="Nombres de ciudades separados por coma"),
    metrics: str = Query(..., description="Métricas separadas por coma (temperature,humidity,pressure,wind)"),
    from_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    to_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    days: int = Query(7, ge=1, le=365, description="Número de días hacia atrás"),
    unit: TemperatureUnit = Query(TemperatureUnit.CELSIUS, description="Unidad de temperatura"),
    limit: int = Query(1000, ge=1, le=10000, description="Límite de registros por ciudad"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Comparar múltiples métricas de múltiples ciudades en una sola consulta"""
    
    # Parsear métricas
    metric_list = [m.strip() for m in metrics.split(",")]
    valid_metrics = ["temperature", "humidity", "pressure", "wind"]
    
    for metric in metric_list:
        if metric not in valid_metrics:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Métrica '{metric}' no válida. Métricas válidas: {', '.join(valid_metrics)}"
            )
    
    # Parsear y normalizar nombres de ciudades
    city_names = [name.strip() for name in cities.split(",")]
    normalized_cities = normalize_city_list(city_names)
    if len(city_names) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe especificar al menos 2 ciudades para comparar"
        )
    
    # Buscar ciudades
    city_objects = []
    for city_name in normalized_cities:
        city_obj = db.query(City).filter(City.name.ilike(f"%{city_name}%")).first()
        if not city_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ciudad '{city_name}' no encontrada"
            )
        city_objects.append(city_obj)
    
    # Determinar rango de fechas
    if not from_date:
        from_date = datetime.utcnow() - timedelta(days=days)
    if not to_date:
        to_date = datetime.utcnow()
    
    # Obtener datos para cada ciudad
    weather_service = WeatherService()
    results = {}
    
    for city_obj in city_objects:
        weather_data = db.query(WeatherHourly).filter(
            WeatherHourly.city_id == city_obj.id,
            WeatherHourly.ts >= from_date,
            WeatherHourly.ts <= to_date
        ).order_by(WeatherHourly.ts.asc()).limit(limit).all()
        
        if weather_data:
            city_results = {}
            for metric in metric_list:
                if metric == "temperature":
                    converted_data = [weather_service.convert_weather_data(data, unit) for data in weather_data]
                    city_results[metric] = converted_data
                else:
                    # Extraer datos específicos para otras métricas
                    metric_data = []
                    for data in weather_data:
                        if metric == "humidity":
                            metric_data.append({
                                "timestamp": data.ts,
                                "humidity": data.humidity,
                                "city_id": data.city_id,
                                "city_name": city_obj.name
                            })
                        elif metric == "pressure":
                            metric_data.append({
                                "timestamp": data.ts,
                                "pressure": data.pressure,
                                "city_id": data.city_id,
                                "city_name": city_obj.name
                            })
                        elif metric == "wind":
                            metric_data.append({
                                "timestamp": data.ts,
                                "wind_speed": data.wind_speed,
                                "wind_deg": data.wind_deg,
                                "city_id": data.city_id,
                                "city_name": city_obj.name
                            })
                    city_results[metric] = metric_data
            results[city_obj.name] = city_results
    
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay datos disponibles para las ciudades especificadas en el rango de fechas"
        )
    
    return {
        "cities": city_objects,
        "metrics": metric_list,
        "data": results,
        "from_date": from_date,
        "to_date": to_date,
        "unit": unit,
        "count": sum(len(data) for city_data in results.values() for metric_data in city_data.values() for data in metric_data)
    }
