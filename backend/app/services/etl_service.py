"""
Servicio ETL para extracción de datos de OpenWeatherMap
"""
import requests
import json
import structlog
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.config import settings
from app.models import City, WeatherRaw, WeatherHourly, Alert, AlertHistory
from app.services.alert_service import AlertService

logger = structlog.get_logger()


class ETLService:
    """Servicio para operaciones ETL"""
    
    def __init__(self, db: Session):
        self.db = db
        self.alert_service = AlertService(db)
        self.base_url = settings.openweather_base_url
        self.api_key = settings.openweather_api_key
        
    async def run_etl_all_cities(self, force_update: bool = False) -> Dict[str, Any]:
        """Ejecutar ETL para todas las ciudades"""
        
        logger.info("Iniciando ETL para todas las ciudades", force_update=force_update)
        
        cities = self.db.query(City).all()
        processed = 0
        errors = []
        
        for city in cities:
            try:
                await self.run_etl_for_city(city.id, force_update)
                processed += 1
                logger.info("ETL completado para ciudad", city_id=city.id, city_name=city.name)
            except Exception as e:
                error_msg = f"Error procesando ciudad {city.name} (ID: {city.id}): {str(e)}"
                errors.append(error_msg)
                logger.error("Error en ETL de ciudad", city_id=city.id, error=str(e))
        
        logger.info("ETL completado", processed=processed, errors=len(errors))
        
        return {
            "processed": processed,
            "errors": errors,
            "total_cities": len(cities)
        }
    
    async def run_etl_for_city(self, city_id: int, force_update: bool = False) -> Dict[str, Any]:
        """Ejecutar ETL para una ciudad específica"""
        
        city = self.db.query(City).filter(City.id == city_id).first()
        if not city:
            raise ValueError(f"Ciudad con ID {city_id} no encontrada")
        
        logger.info("Iniciando ETL para ciudad", city_id=city_id, city_name=city.name)
        
        # Verificar si necesitamos actualizar (última actualización hace más de 1 hora)
        if not force_update:
            last_update = self.db.query(WeatherHourly).filter(
                WeatherHourly.city_id == city_id
            ).order_by(WeatherHourly.ts.desc()).first()
            
            if last_update and last_update.ts > datetime.now(timezone.utc) - timedelta(hours=1):
                logger.info("Datos recientes encontrados, saltando ETL", city_id=city_id)
                return {"status": "skipped", "reason": "recent_data_available"}
        
        # Extraer datos de OpenWeatherMap
        weather_data = await self._extract_weather_data(city)
        
        if not weather_data:
            raise ValueError("No se pudieron obtener datos de OpenWeatherMap")
        
        # Transformar y cargar datos
        result = await self._transform_and_load(city, weather_data)
        
        # Evaluar alertas
        await self._evaluate_alerts(city_id)
        
        logger.info("ETL completado para ciudad", city_id=city_id, result=result)
        
        return result
    
    async def _extract_weather_data(self, city: City) -> Optional[Dict[str, Any]]:
        """Extraer datos de OpenWeatherMap API"""
        
        try:
            # Construir URL para Current Weather API
            url = f"{self.base_url}/weather"
            params = {
                "q": f"{city.name},{city.country}" if city.country else city.name,
                "appid": self.api_key,
                "units": "metric"  # Obtener en Celsius
            }
            
            # Si tenemos coordenadas, usarlas para mayor precisión
            if city.lat and city.lon:
                params = {
                    "lat": city.lat,
                    "lon": city.lon,
                    "appid": self.api_key,
                    "units": "metric"
                }
            
            logger.info("Solicitando datos de OpenWeatherMap", url=url, params=params)
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info("Datos obtenidos de OpenWeatherMap", city_id=city.id, data_keys=list(data.keys()))
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error("Error en request a OpenWeatherMap", city_id=city.id, error=str(e))
            raise
        except Exception as e:
            logger.error("Error extrayendo datos meteorológicos", city_id=city.id, error=str(e))
            raise
    
    async def _transform_and_load(self, city: City, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transformar y cargar datos en la base de datos"""
        
        try:
            # Guardar datos raw
            raw_record = WeatherRaw(
                city_id=city.id,
                fetched_at=datetime.now(timezone.utc),
                data=json.dumps(raw_data)
            )
            self.db.add(raw_record)
            self.db.flush()  # Para obtener el ID
            
            # Extraer y transformar datos meteorológicos
            main_data = raw_data.get("main", {})
            wind_data = raw_data.get("wind", {})
            clouds_data = raw_data.get("clouds", {})
            weather_data = raw_data.get("weather", [{}])[0]
            
            # Crear timestamp (usar timestamp de la API si está disponible)
            api_timestamp = raw_data.get("dt")
            if api_timestamp:
                ts = datetime.fromtimestamp(api_timestamp, tz=timezone.utc)
            else:
                ts = datetime.now(timezone.utc)
            
            # Crear registro de weather_hourly
            weather_hourly = WeatherHourly(
                city_id=city.id,
                ts=ts,
                temp_c=main_data.get("temp"),
                feels_like_c=main_data.get("feels_like"),
                humidity=main_data.get("humidity"),
                pressure=main_data.get("pressure"),
                wind_speed=wind_data.get("speed"),
                wind_deg=wind_data.get("deg"),
                clouds=clouds_data.get("all"),
                visibility=raw_data.get("visibility"),
                weather_main=weather_data.get("main"),
                weather_description=weather_data.get("description"),
                raw_id=raw_record.id
            )
            
            # UPSERT: actualizar si existe, insertar si no
            existing = self.db.query(WeatherHourly).filter(
                and_(
                    WeatherHourly.city_id == city.id,
                    WeatherHourly.ts == ts
                )
            ).first()
            
            if existing:
                # Actualizar registro existente
                for key, value in weather_hourly.__dict__.items():
                    if key not in ['id', 'created_at']:
                        setattr(existing, key, value)
                existing.raw_id = raw_record.id
            else:
                # Insertar nuevo registro
                self.db.add(weather_hourly)
            
            self.db.commit()
            
            logger.info("Datos transformados y cargados", city_id=city.id, timestamp=ts)
            
            return {
                "status": "success",
                "timestamp": ts.isoformat(),
                "raw_id": raw_record.id
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error("Error transformando y cargando datos", city_id=city.id, error=str(e))
            raise
    
    async def _evaluate_alerts(self, city_id: int):
        """Evaluar alertas para una ciudad"""
        
        try:
            # Obtener alertas activas para la ciudad
            alerts = self.db.query(Alert).filter(
                and_(
                    Alert.city_id == city_id,
                    Alert.active == True,
                    Alert.paused == False
                )
            ).all()
            
            if not alerts:
                return
            
            # Obtener datos meteorológicos más recientes
            latest_weather = self.db.query(WeatherHourly).filter(
                WeatherHourly.city_id == city_id
            ).order_by(WeatherHourly.ts.desc()).first()
            
            if not latest_weather:
                return
            
            # Evaluar cada alerta
            for alert in alerts:
                await self.alert_service.evaluate_alert(alert, latest_weather)
            
            logger.info("Alertas evaluadas", city_id=city_id, alert_count=len(alerts))
            
        except Exception as e:
            logger.error("Error evaluando alertas", city_id=city_id, error=str(e))
    
    async def get_etl_status(self) -> Dict[str, Any]:
        """Obtener estado del ETL"""
        
        try:
            # Contar ciudades totales
            total_cities = self.db.query(City).count()
            
            # Contar ciudades con datos recientes (últimas 2 horas)
            recent_threshold = datetime.now(timezone.utc) - timedelta(hours=2)
            cities_with_recent_data = self.db.query(WeatherHourly.city_id).filter(
                WeatherHourly.ts >= recent_threshold
            ).distinct().count()
            
            # Obtener errores recientes (últimas 24 horas)
            recent_errors = []  # Aquí podrías implementar un sistema de logging de errores
            
            return {
                "total_cities": total_cities,
                "cities_with_recent_data": cities_with_recent_data,
                "last_update": datetime.now(timezone.utc).isoformat(),
                "recent_errors": recent_errors
            }
            
        except Exception as e:
            logger.error("Error obteniendo estado del ETL", error=str(e))
            raise
    
    async def get_etl_cities(self) -> List[Dict[str, Any]]:
        """Obtener lista de ciudades configuradas para ETL"""
        
        cities = self.db.query(City).all()
        
        result = []
        for city in cities:
            # Obtener última actualización
            last_update = self.db.query(WeatherHourly).filter(
                WeatherHourly.city_id == city.id
            ).order_by(WeatherHourly.ts.desc()).first()
            
            result.append({
                "id": city.id,
                "name": city.name,
                "country": city.country,
                "last_update": last_update.ts.isoformat() if last_update else None,
                "has_recent_data": last_update and last_update.ts > datetime.now(timezone.utc) - timedelta(hours=2)
            })
        
        return result
