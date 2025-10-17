#!/usr/bin/env python3
"""
Script para inicializar la base de datos con datos básicos
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import City, User
from app.auth import get_password_hash
import structlog

logger = structlog.get_logger()

def create_tables():
    """Crear todas las tablas"""
    logger.info("Creando tablas de la base de datos...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas creadas exitosamente")

def create_initial_cities():
    """Crear ciudades iniciales"""
    db = SessionLocal()
    try:
        # Verificar si ya existen ciudades
        if db.query(City).count() > 0:
            logger.info("Las ciudades ya existen, saltando creación")
            return
        
        cities_data = [
            {"name": "Madrid", "country": "ES", "lat": 40.4168, "lon": -3.7038, "openweather_id": 3117735},
            {"name": "Barcelona", "country": "ES", "lat": 41.3851, "lon": 2.1734, "openweather_id": 3128760},
            {"name": "Valencia", "country": "ES", "lat": 39.4699, "lon": -0.3763, "openweather_id": 2509954},
            {"name": "Sevilla", "country": "ES", "lat": 37.3891, "lon": -5.9845, "openweather_id": 2510911},
            {"name": "Bilbao", "country": "ES", "lat": 43.2627, "lon": -2.9253, "openweather_id": 3128026},
            {"name": "London", "country": "GB", "lat": 51.5074, "lon": -0.1278, "openweather_id": 2643743},
            {"name": "Paris", "country": "FR", "lat": 48.8566, "lon": 2.3522, "openweather_id": 2988507},
            {"name": "Berlin", "country": "DE", "lat": 52.5200, "lon": 13.4050, "openweather_id": 2950159},
            {"name": "Rome", "country": "IT", "lat": 41.9028, "lon": 12.4964, "openweather_id": 3169070},
            {"name": "Amsterdam", "country": "NL", "lat": 52.3676, "lon": 4.9041, "openweather_id": 2759794},
            {"name": "New York", "country": "US", "lat": 40.7128, "lon": -74.0060, "openweather_id": 5128581},
            {"name": "Los Angeles", "country": "US", "lat": 34.0522, "lon": -118.2437, "openweather_id": 5368361},
            {"name": "Tokyo", "country": "JP", "lat": 35.6762, "lon": 139.6503, "openweather_id": 1850147},
            {"name": "Sydney", "country": "AU", "lat": -33.8688, "lon": 151.2093, "openweather_id": 2147714},
            {"name": "São Paulo", "country": "BR", "lat": -23.5505, "lon": -46.6333, "openweather_id": 3448439},
            {"name": "Beijing", "country": "CN", "lat": 39.9042, "lon": 116.4074, "openweather_id": 1816670},
            {"name": "Shanghai", "country": "CN", "lat": 31.2304, "lon": 121.4737, "openweather_id": 1796236},
            {"name": "Hong Kong", "country": "HK", "lat": 22.3193, "lon": 114.1694, "openweather_id": 1819729},
            {"name": "Singapore", "country": "SG", "lat": 1.3521, "lon": 103.8198, "openweather_id": 1880252},
            {"name": "Dubai", "country": "AE", "lat": 25.2048, "lon": 55.2708, "openweather_id": 292223},
            {"name": "Moscow", "country": "RU", "lat": 55.7558, "lon": 37.6176, "openweather_id": 524901},
            {"name": "Istanbul", "country": "TR", "lat": 41.0082, "lon": 28.9784, "openweather_id": 745044},
            {"name": "Mexico City", "country": "MX", "lat": 19.4326, "lon": -99.1332, "openweather_id": 3530597},
            {"name": "Buenos Aires", "country": "AR", "lat": -34.6118, "lon": -58.3960, "openweather_id": 3435910},
            {"name": "Toronto", "country": "CA", "lat": 43.6532, "lon": -79.3832, "openweather_id": 6167865},
            {"name": "San Francisco", "country": "US", "lat": 37.7749, "lon": -122.4194, "openweather_id": 5391959},
            {"name": "Chicago", "country": "US", "lat": 41.8781, "lon": -87.6298, "openweather_id": 4887398},
            {"name": "Seoul", "country": "KR", "lat": 37.5665, "lon": 126.9780, "openweather_id": 1835848},
            {"name": "Mumbai", "country": "IN", "lat": 19.0760, "lon": 72.8777, "openweather_id": 1275339},
            {"name": "Cairo", "country": "EG", "lat": 30.0444, "lon": 31.2357, "openweather_id": 360630},
            
            
            {"name": "Bogotá", "country": "CO", "lat": 4.7110, "lon": -74.0721, "openweather_id": 3688689},
            {"name": "Lima", "country": "PE", "lat": -12.0464, "lon": -77.0428, "openweather_id": 3936456},
            {"name": "Santiago", "country": "CL", "lat": -33.4489, "lon": -70.6693, "openweather_id": 3871336},
            {"name": "Rio de Janeiro", "country": "BR", "lat": -22.9068, "lon": -43.1729, "openweather_id": 3451190},
            {"name": "Monterrey", "country": "MX", "lat": 25.6866, "lon": -100.3161, "openweather_id": 3995465},
            {"name": "Quito", "country": "EC", "lat": -0.1807, "lon": -78.4678, "openweather_id": 3652462},
            {"name": "Panamá", "country": "PA", "lat": 8.5380, "lon": -80.7821, "openweather_id": 3703443},
            {"name": "Montevideo", "country": "UY", "lat": -34.9011, "lon": -56.1645, "openweather_id": 3441575},
            {"name": "Caracas", "country": "VE", "lat": 10.4806, "lon": -66.9036, "openweather_id": 3646738},
            {"name": "La Paz", "country": "BO", "lat": -16.5000, "lon": -68.1500, "openweather_id": 3911924},
            {"name": "Cali", "country": "CO", "lat": 3.4516, "lon": -76.5320, "openweather_id": 3687925},
            {"name": "Santo Domingo", "country": "DO", "lat": 18.4861, "lon": -69.9312, "openweather_id": 3492908},
            
            
        ]
        
        for city_data in cities_data:
            # Evitar duplicados por (name, country) si la lista contiene repetidos
            existing = db.query(City).filter(
                City.name == city_data["name"],
                City.country == city_data["country"]
            ).first()
            if existing:
                continue
            city = City(**city_data)
            db.add(city)
        
        db.commit()
        logger.info(f"Creadas {len(cities_data)} ciudades iniciales")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creando ciudades: {e}")
        raise
    finally:
        db.close()

def create_admin_user():
    """Crear usuario administrador inicial"""
    db = SessionLocal()
    try:
        # Verificar si ya existe el admin
        admin = db.query(User).filter(User.email == "admin@weatherhub.com").first()
        if admin:
            logger.info("Usuario admin ya existe, saltando creación")
            return
        
        admin_user = User(
            email="admin@weatherhub.com",
            password_hash=get_password_hash("admin123"),
            full_name="Administrador WeatherHub"
        )
        
        db.add(admin_user)
        db.commit()
        logger.info("Usuario administrador creado: admin@weatherhub.com / admin123")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creando usuario admin: {e}")
        raise
    finally:
        db.close()

def main():
    """Función principal"""
    logger.info("Inicializando base de datos WeatherHub...")
    
    try:
        # Crear tablas
        create_tables()
        
        # Crear datos iniciales
        create_initial_cities()
        create_admin_user()
        
        logger.info("Base de datos inicializada exitosamente")
        print("\n[OK] Base de datos inicializada correctamente!")
        print("[INFO] Ciudades: 15 ciudades principales")
        print("[INFO] Usuario admin: admin@weatherhub.com / admin123")
        print("\n[START] Puedes iniciar el servidor con: python -m app.main")
        
    except Exception as e:
        logger.error(f"Error inicializando base de datos: {e}")
        print(f"\n[ERROR] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
