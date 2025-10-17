#!/usr/bin/env python3
"""
Script simplificado para configurar PostgreSQL para WeatherHub
"""
import subprocess
import sys
import os
from pathlib import Path

# Añadir el directorio backend al path para importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

def get_db_config():
    """Obtener configuración de base de datos desde settings centralizado"""
    if not settings.postgres_user or not settings.postgres_password:
        print("ERROR: POSTGRES_USER o POSTGRES_PASSWORD no configurados en .env")
        print("Configura estas variables en tu archivo .env")
        sys.exit(1)
    
    return settings.postgres_user, settings.postgres_password, settings.postgres_host, settings.postgres_port

def run_psql_command(command, database="postgres"):
    """Ejecutar comando SQL usando psql"""
    try:
        # Obtener configuración desde settings centralizado
        postgres_user, postgres_password, postgres_host, postgres_port = get_db_config()
        
        # Configurar variable de entorno para la contraseña
        env = os.environ.copy()
        env['PGPASSWORD'] = postgres_password
        
        cmd = [
            "psql", 
            "-U", postgres_user, 
            "-h", postgres_host,
            "-p", postgres_port,
            "-d", database,
            "-c", command
        ]
        print(f"Ejecutando comando: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        
        if result.returncode != 0:
            print(f"Error en comando SQL:")
            print(f"  Código de salida: {result.returncode}")
            print(f"  Error: {result.stderr}")
            print(f"  Salida: {result.stdout}")
        else:
            print(f"Comando ejecutado exitosamente")
            if result.stdout.strip():
                print(f"  Resultado: {result.stdout.strip()}")
            
        return result.returncode == 0, result.stdout, result.stderr
    except FileNotFoundError:
        print("psql no encontrado en el PATH del sistema")
        return False, "", "psql no encontrado. Asegúrate de que PostgreSQL esté instalado y en el PATH."

def create_database():
    """Crear base de datos y usuario para WeatherHub"""
    
    print("Configurando PostgreSQL para WeatherHub...")
    print("Verificando conexión a PostgreSQL...")
    
    # Verificar conexión inicial
    print("Probando conexión con usuario postgres...")
    print("DEBUG: Ejecutando comando de prueba...")
    success, stdout, stderr = run_psql_command("SELECT version();")
    print(f"DEBUG: Resultado de conexión - Success: {success}")
    print(f"DEBUG: Stdout: {stdout}")
    print(f"DEBUG: Stderr: {stderr}")
    
    if not success:
        print(f"No se puede conectar a PostgreSQL: {stderr}")
        print("Verifica que:")
        print("   1. PostgreSQL esté ejecutándose")
        print("   2. El usuario 'postgres' tenga la contraseña configurada en POSTGRES_PASSWORD")
        print("   3. psql esté en el PATH del sistema")
        return False
    
    print("Conexión a PostgreSQL exitosa")
    
    # Crear usuario
    print("Creando usuario 'weatherhub'...")
    print("DEBUG: Ejecutando comando para crear usuario...")
    success, stdout, stderr = run_psql_command("CREATE USER weatherhub WITH PASSWORD 'weatherhub123';")
    print(f"DEBUG: Resultado de crear usuario - Success: {success}")
    print(f"DEBUG: Stdout: {stdout}")
    print(f"DEBUG: Stderr: {stderr}")
    
    if not success:
        # Verificar si el error es porque el usuario ya existe
        if "already exists" in stderr.lower() or "ya existe" in stderr.lower():
            print("Usuario weatherhub ya existe, continuando...")
        else:
            print(f"Error creando usuario: {stderr}")
            return False
    else:
        print("Usuario weatherhub configurado correctamente")
    
    # Crear base de datos
    print("Creando base de datos 'weatherhub'...")
    print("DEBUG: Ejecutando comando para crear base de datos...")
    success, stdout, stderr = run_psql_command("CREATE DATABASE weatherhub OWNER weatherhub;")
    print(f"DEBUG: Resultado de crear base de datos - Success: {success}")
    print(f"DEBUG: Stdout: {stdout}")
    print(f"DEBUG: Stderr: {stderr}")
    
    if not success:
        # Verificar si el error es porque la base de datos ya existe
        if "already exists" in stderr.lower() or "ya existe" in stderr.lower():
            print("Base de datos weatherhub ya existe, continuando...")
        else:
            print(f"Error creando base de datos: {stderr}")
            return False
    else:
        print("Base de datos weatherhub configurada correctamente")
    
    # Otorgar permisos
    print("Otorgando permisos...")
    print("DEBUG: Ejecutando comando para otorgar permisos...")
    success, stdout, stderr = run_psql_command("GRANT ALL PRIVILEGES ON DATABASE weatherhub TO weatherhub;")
    print(f"DEBUG: Resultado de otorgar permisos - Success: {success}")
    print(f"DEBUG: Stdout: {stdout}")
    print(f"DEBUG: Stderr: {stderr}")
    
    if not success:
        print(f"Error otorgando permisos: {stderr}")
        return False
    else:
        print("Permisos otorgados correctamente")
    
    print("PostgreSQL configurado exitosamente!")
    print("Configuración:")
    print("   - Usuario: weatherhub")
    print("   - Contraseña: [configurada en .env]")
    print("   - Base de datos: weatherhub")
    print("   - Host: localhost")
    print("   - Puerto: 5432")
    
    return True

def test_connection():
    """Probar conexión con las nuevas credenciales"""
    try:
        print("\nProbando conexión con usuario weatherhub...")
        success, stdout, stderr = run_psql_command("SELECT current_database(), current_user, version();", "weatherhub")
        if success:
            print(f"Conexión exitosa!")
            print(f"Base de datos: weatherhub")
            print(f"Usuario: weatherhub")
            print(f"PostgreSQL funcionando correctamente")
            return True
        else:
            print(f"Error en prueba de conexión: {stderr}")
            return False
    except Exception as e:
        print(f"Error inesperado: {e}")
        return False

def main():
    """Función principal"""
    print("Configurando PostgreSQL para WeatherHub...")
    print("=" * 50)
    
    if create_database():
        if test_connection():
            print("\nConfiguración completada!")
            print("Ahora puedes ejecutar: python scripts/init_db.py")
        else:
            print("\nBase de datos creada pero hay problemas de conexión")
    else:
        print("\nNo se pudo configurar PostgreSQL")
        print("Asegúrate de que:")
        print("   1. PostgreSQL esté instalado y ejecutándose")
        print("   2. El usuario 'postgres' tenga la contraseña configurada en POSTGRES_PASSWORD")
        print("   3. psql esté en el PATH del sistema")
        sys.exit(1)

if __name__ == "__main__":
    main()
