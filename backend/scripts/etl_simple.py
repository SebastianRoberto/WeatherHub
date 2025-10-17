#!/usr/bin/env python3
"""
Script ETL simplificado para WeatherHub con SQLite
"""
import sys
import os
import requests
import json
from datetime import datetime
from sqlalchemy.orm import Session

# Añadir el directorio backend al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import City, WeatherRaw, WeatherHourly
from app.config import settings

def get_weather_data(city_id, openweather_id):
    """Obtener datos de OpenWeatherMap para una ciudad"""
    try:
        url = f"{settings.openweather_base_url}/weather"
        params = {
            'id': openweather_id,
            'appid': settings.openweather_api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        return response.json()
    
    except Exception as e:
        print(f"Error obteniendo datos para ciudad {city_id}: {e}")
        return None

def save_weather_data(db: Session, city_id: int, weather_data: dict):
    """Guardar datos meteorológicos en la base de datos"""
    try:
        # Guardar datos raw
        weather_raw = WeatherRaw(
            city_id=city_id,
            fetched_at=datetime.utcnow(),
            data=json.dumps(weather_data)
        )
        db.add(weather_raw)
        db.flush()  # Para obtener el ID
        
        # Extraer y guardar datos procesados
        main_data = weather_data.get('main', {})
        weather_info = weather_data.get('weather', [{}])[0]
        wind_data = weather_data.get('wind', {})
        
        # Usar timestamp de la API si está disponible, sino usar hora actual
        api_timestamp = weather_data.get('dt')
        if api_timestamp:
            ts = datetime.fromtimestamp(api_timestamp)
        else:
            ts = datetime.utcnow()
        
        weather_hourly = WeatherHourly(
            city_id=city_id,
            ts=ts,
            temp_c=main_data.get('temp'),
            feels_like_c=main_data.get('feels_like'),
            humidity=main_data.get('humidity'),
            pressure=main_data.get('pressure'),
            wind_speed=wind_data.get('speed'),
            wind_deg=wind_data.get('deg'),
            clouds=weather_data.get('clouds', {}).get('all'),
            visibility=weather_data.get('visibility'),
            weather_main=weather_info.get('main'),
            weather_description=weather_info.get('description'),
            raw_id=weather_raw.id
        )
        
        db.add(weather_hourly)
        db.commit()
        
        return True
    
    except Exception as e:
        print(f"Error guardando datos para ciudad {city_id}: {e}")
        db.rollback()
        return False

def main():
    """Función principal del ETL"""
    print("[START] Iniciando ETL para obtener datos meteorológicos...")
    
    db = SessionLocal()
    
    try:
        # Obtener todas las ciudades
        cities = db.query(City).all()
        print(f"[INFO] Procesando {len(cities)} ciudades...")
        
        success_count = 0
        error_count = 0
        
        for city in cities:
            print(f"[PROCESS] Procesando {city.name}, {city.country}...")
            
            # Obtener datos de OpenWeatherMap
            weather_data = get_weather_data(city.id, city.openweather_id)
            
            if weather_data:
                # Guardar en base de datos
                if save_weather_data(db, city.id, weather_data):
                    success_count += 1
                    temp = weather_data.get('main', {}).get('temp', 'N/A')
                    print(f"[OK] {city.name}: {temp}°C")
                else:
                    error_count += 1
                    print(f"[ERROR] Error guardando {city.name}")
            else:
                error_count += 1
                print(f"[ERROR] Error obteniendo datos de {city.name}")
        
        print(f"\n[COMPLETE] ETL completado!")
        print(f"[OK] Exitosos: {success_count}")
        print(f"[ERROR] Errores: {error_count}")
        
        return 0 if error_count == 0 else 1
        
    except Exception as e:
        print(f"[CRITICAL] Error crítico: {e}")
        return 1
    
    finally:
        db.close()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
