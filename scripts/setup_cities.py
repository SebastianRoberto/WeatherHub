#!/usr/bin/env python3
"""
Script para configurar ciudades iniciales en la base de datos
"""
import sys
import os
import requests
import json

# Añadir el directorio backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import SessionLocal, engine
from app.models import Base, City
from app.config import settings

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# Lista de ciudades principales para configurar
MAJOR_CITIES = [
    {"name": "Madrid", "country": "ES", "lat": 40.4168, "lon": -3.7038},
    {"name": "Barcelona", "country": "ES", "lat": 41.3851, "lon": 2.1734},
    {"name": "London", "country": "GB", "lat": 51.5074, "lon": -0.1278},
    {"name": "Paris", "country": "FR", "lat": 48.8566, "lon": 2.3522},
    {"name": "Berlin", "country": "DE", "lat": 52.5200, "lon": 13.4050},
    {"name": "Rome", "country": "IT", "lat": 41.9028, "lon": 12.4964},
    {"name": "New York", "country": "US", "lat": 40.7128, "lon": -74.0060},
    {"name": "Los Angeles", "country": "US", "lat": 34.0522, "lon": -118.2437},
    {"name": "Tokyo", "country": "JP", "lat": 35.6762, "lon": 139.6503},
    {"name": "Sydney", "country": "AU", "lat": -33.8688, "lon": 151.2093},
    {"name": "Lima", "country": "PE", "lat": -12.0464, "lon": -77.0428},
    {"name": "Buenos Aires", "country": "AR", "lat": -34.6118, "lon": -58.3960},
    {"name": "Mexico City", "country": "MX", "lat": 19.4326, "lon": -99.1332},
    {"name": "São Paulo", "country": "BR", "lat": -23.5505, "lon": -46.6333},
    {"name": "Beijing", "country": "CN", "lat": 39.9042, "lon": 116.4074},
    {"name": "Shanghai", "country": "CN", "lat": 31.2304, "lon": 121.4737},
    {"name": "Hong Kong", "country": "HK", "lat": 22.3193, "lon": 114.1694},
    {"name": "Singapore", "country": "SG", "lat": 1.3521, "lon": 103.8198},
    {"name": "Dubai", "country": "AE", "lat": 25.2048, "lon": 55.2708},
    {"name": "Moscow", "country": "RU", "lat": 55.7558, "lon": 37.6176},
    {"name": "Istanbul", "country": "TR", "lat": 41.0082, "lon": 28.9784},
    {"name": "Mexico City", "country": "MX", "lat": 19.4326, "lon": -99.1332},
    {"name": "Buenos Aires", "country": "AR", "lat": -34.6118, "lon": -58.3960},
    {"name": "Toronto", "country": "CA", "lat": 43.6532, "lon": -79.3832},
    {"name": "San Francisco", "country": "US", "lat": 37.7749, "lon": -122.4194},
    {"name": "Chicago", "country": "US", "lat": 41.8781, "lon": -87.6298},
    {"name": "Seoul", "country": "KR", "lat": 37.5665, "lon": 126.9780},
    {"name": "Mumbai", "country": "IN", "lat": 19.0760, "lon": 72.8777},
    {"name": "Cairo", "country": "EG", "lat": 30.0444, "lon": 31.2357},
    {"name": "Bogotá", "country": "CO", "lat": 4.7110, "lon": -74.0721},
    {"name": "Santiago", "country": "CL", "lat": -33.4489, "lon": -70.6693},
    {"name": "Rio de Janeiro", "country": "BR", "lat": -22.9068, "lon": -43.1729},
    {"name": "Monterrey", "country": "MX", "lat": 25.6866, "lon": -100.3161},
    {"name": "Quito", "country": "EC", "lat": -0.1807, "lon": -78.4678},
    {"name": "Panamá", "country": "PA", "lat": 8.5380, "lon": -80.7821},
    {"name": "Montevideo", "country": "UY", "lat": -34.9011, "lon": -56.1645},
    {"name": "Caracas", "country": "VE", "lat": 10.4806, "lon": -66.9036},
    {"name": "La Paz", "country": "BO", "lat": -16.5000, "lon": -68.1500},
    {"name": "Cali", "country": "CO", "lat": 3.4516, "lon": -76.5320},
    {"name": "Santo Domingo", "country": "DO", "lat": 18.4861, "lon": -69.9312},
    
]


def get_openweather_id(city_name: str, country: str, api_key: str) -> int:
    """Obtener ID de OpenWeatherMap para una ciudad"""
    try:
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": f"{city_name},{country}",
            "appid": api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("id")
    except Exception as e:
        print(f"Error obteniendo ID para {city_name}: {e}")
    
    return None


def setup_cities():
    """Configurar ciudades en la base de datos"""
    
    db = SessionLocal()
    
    try:
        print("Configurando ciudades en la base de datos...")
        
        for city_data in MAJOR_CITIES:
            # Verificar si la ciudad ya existe (evitar duplicados en la lista o BD)
            existing_city = db.query(City).filter(
                City.name == city_data["name"],
                City.country == city_data["country"]
            ).first()
            if existing_city:
                print(f"Ciudad {city_data['name']}, {city_data['country']} ya existe")
                continue
            
            # Obtener ID de OpenWeatherMap si tenemos API key
            openweather_id = None
            if settings.openweather_api_key:
                openweather_id = get_openweather_id(
                    city_data["name"], 
                    city_data["country"], 
                    settings.openweather_api_key
                )
            
            # Crear ciudad
            city = City(
                name=city_data["name"],
                country=city_data["country"],
                lat=city_data["lat"],
                lon=city_data["lon"],
                openweather_id=openweather_id
            )
            
            db.add(city)
            print(f"Ciudad {city_data['name']}, {city_data['country']} añadida (OpenWeather ID: {openweather_id})")
        
        db.commit()
        print(f"Se configuraron {len(MAJOR_CITIES)} ciudades exitosamente")
        
    except Exception as e:
        print(f"Error configurando ciudades: {e}")
        db.rollback()
        return False
    
    finally:
        db.close()
    
    return True


if __name__ == "__main__":
    success = setup_cities()
    sys.exit(0 if success else 1)
