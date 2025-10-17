#!/usr/bin/env python3
"""
Script de diagnóstico para verificar datos en la base de datos
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import WeatherHourly, City
from sqlalchemy.orm import Session

def main():
    print("🔍 DIAGNÓSTICO DE BASE DE DATOS")
    print("=" * 50)
    
    try:
        db = next(get_db())
        
        print("\n📊 CIUDADES DISPONIBLES:")
        cities = db.query(City).all()
        for city in cities:
            print(f"  - ID: {city.id}, Nombre: {city.name}")
        
        print(f"\n📈 TOTAL DE CIUDADES: {len(cities)}")
        
        print("\n🌤️ DATOS METEOROLÓGICOS (Últimos 5 registros):")
        weather_data = db.query(WeatherHourly).order_by(WeatherHourly.ts.desc()).limit(5).all()
        for data in weather_data:
            print(f"  - Ciudad ID: {data.city_id}, Timestamp: {data.ts}")
            print(f"    Temp: {data.temp_c}°C, Humedad: {data.humidity}%, Presión: {data.pressure}hPa")
        
        total_records = db.query(WeatherHourly).count()
        print(f"\n📊 TOTAL DE REGISTROS: {total_records}")
        
        if total_records == 0:
            print("\n❌ PROBLEMA: No hay datos meteorológicos en la base de datos")
            print("💡 SOLUCIÓN: Ejecutar ETL para obtener datos")
        else:
            print("\n✅ Base de datos tiene datos meteorológicos")
            
            # Verificar datos por ciudad
            print("\n🏙️ DATOS POR CIUDAD:")
            for city in cities:
                count = db.query(WeatherHourly).filter(WeatherHourly.city_id == city.id).count()
                print(f"  - {city.name}: {count} registros")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
