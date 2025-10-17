#!/usr/bin/env python3
"""
Script de inicio unificado para WeatherHub
Este es el ÚNICO script que necesita ejecutar el usuario
"""
import os
import sys
import subprocess
from pathlib import Path

# Añadir el directorio backend al path para importar config
sys.path.append(str(Path(__file__).parent))

from app.config import settings

# Variable global para el Python correcto
correct_python_path = None

def get_correct_python():
    
    # Intentar diferentes comandos de Python
    python_commands = [
        "py",           # Windows Python Launcher
        "python3",      # Python 3
        "python",       # Python
        "py -3.11",     # Python 3.11 específico
        "py -3.10",     # Python 3.10 específico
    ]
    
    for cmd in python_commands:
        try:
            result = subprocess.run([cmd, "--version"], capture_output=True, text=True)
            if result.returncode == 0 and "Inkscape" not in result.stdout:
                print(f"Python correcto encontrado: {cmd}")
                return cmd
        except FileNotFoundError:
            continue
    
    print("ERROR: No se encontró Python correcto")
    print("Solución:")
    print("   1. Instala Python desde python.org")
    print("   2. Asegúrate de que esté en el PATH")
    print("   3. Reinicia el sistema")
    return None

def check_python():
    """Verificar que estamos usando el Python correcto"""
    python_cmd = get_correct_python()
    if not python_cmd:
        return False
    
    # Actualizar sys.executable para usar el Python correcto
    try:
        result = subprocess.run([python_cmd, "-c", "import sys; print(sys.executable)"], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            global correct_python_path
            correct_python_path = result.stdout.strip()
            print(f"Usando Python: {correct_python_path}")
            return True
    except Exception as e:
        print(f"Error verificando Python: {e}")
        return False
    
    return True

def check_dependencies():
    """Verificar e instalar dependencias"""
    print("Verificando dependencias...")
    
    # Verificar si requirements.txt existe
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("ERROR: requirements.txt no encontrado")
        return False
    
    # Usar el Python correcto
    python_cmd = get_correct_python()
    if not python_cmd:
        return False
    
    try:
        # Verificar uvicorn
        result = subprocess.run([python_cmd, "-c", "import uvicorn"], capture_output=True, text=True)
        if result.returncode == 0:
            print("uvicorn encontrado")
        else:
            print("uvicorn no encontrado, instalando dependencias completas...")
            subprocess.run([python_cmd, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("Dependencias instaladas")
    except Exception as e:
        print(f"Error verificando uvicorn: {e}")
        print("Instalando dependencias desde requirements.txt...")
        subprocess.run([python_cmd, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("Dependencias instaladas")
    
    try:
        # Verificar otras dependencias críticas
        result = subprocess.run([python_cmd, "-c", "import fastapi, sqlalchemy, psycopg2"], capture_output=True, text=True)
        if result.returncode == 0:
            print("Dependencias principales encontradas")
        else:
            print(f"Dependencia faltante: {result.stderr}")
            print("Instalando dependencias desde requirements.txt...")
            subprocess.run([python_cmd, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("Dependencias instaladas")
    except Exception as e:
        print(f"Error verificando dependencias: {e}")
        print("Instalando dependencias desde requirements.txt...")
        subprocess.run([python_cmd, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("Dependencias instaladas")

def check_postgresql():
    """Verificar PostgreSQL"""
    print("Verificando PostgreSQL...")
    
    try:
        result = subprocess.run(["psql", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"PostgreSQL encontrado: {result.stdout.strip()}")
            return True
        else:
            print("PostgreSQL no encontrado")
            return False
    except FileNotFoundError:
        print("psql no encontrado en el PATH")
        print("Instala PostgreSQL y asegúrate de que esté en el PATH")
        return False

def setup_database():
    """Configurar base de datos si es necesario"""
    print("Configurando base de datos...")
    
    # Ejecutar script de configuración de PostgreSQL
    setup_script = Path(__file__).parent / "scripts" / "setup_postgres_simple.py"
    print(f"DEBUG: Ejecutando script: {setup_script}")
    print("DEBUG: Iniciando configuración de PostgreSQL...")
    
    python_cmd = get_correct_python()
    if not python_cmd:
        return False
    result = subprocess.run([python_cmd, str(setup_script)], capture_output=True, text=True)
    
    print(f"DEBUG: Código de salida del setup: {result.returncode}")
    print(f"DEBUG: Stdout del setup: {result.stdout}")
    print(f"DEBUG: Stderr del setup: {result.stderr}")
    
    if result.returncode == 0:
        print("PostgreSQL configurado")
    else:
        print(f"Error configurando PostgreSQL: {result.stderr}")
        return False
    
    # Inicializar base de datos
    init_script = Path(__file__).parent / "scripts" / "init_db.py"
    print(f"DEBUG: Ejecutando script: {init_script}")
    print("DEBUG: Iniciando inicialización de base de datos...")
    
    result = subprocess.run([python_cmd, str(init_script)], capture_output=True, text=True)
    
    print(f"DEBUG: Código de salida del init: {result.returncode}")
    print(f"DEBUG: Stdout del init: {result.stdout}")
    print(f"DEBUG: Stderr del init: {result.stderr}")
    
    if result.returncode == 0:
        print("Base de datos inicializada")
        return True
    else:
        print(f"Error inicializando BD: {result.stderr}")
        return False

def run_etl():
    """Ejecutar ETL inicial"""
    print("Ejecutando ETL inicial...")
    
    etl_script = Path(__file__).parent / "scripts" / "etl_simple.py"
    python_cmd = get_correct_python()
    if not python_cmd:
        return False
    result = subprocess.run([python_cmd, str(etl_script)], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("ETL ejecutado exitosamente")
        return True
    else:
        print(f"ETL con errores: {result.stderr}")
        print("Continuando sin datos meteorológicos...")
        return True  # No es crítico

def start_server():
    """Iniciar servidor FastAPI"""
    print("Iniciando servidor WeatherHub...")
    print("API disponible en: http://localhost:8000")
    print("Documentación: http://localhost:8000/docs")
    print("Para detener: Ctrl+C")
    print("-" * 50)
    
    try:
        # Cambiar al directorio backend
        os.chdir(Path(__file__).parent)
        
        # Iniciar servidor
        python_cmd = get_correct_python()
        if not python_cmd:
            print("Error: No se pudo encontrar Python correcto")
            return
        subprocess.run([
            python_cmd, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\nServidor detenido")
    except Exception as e:
        print(f"Error iniciando servidor: {e}")

def main():
    """Función principal"""
    print("WeatherHub - Sistema Unificado")
    print("=" * 50)
    
    # Verificar Python
    if not check_python():
        sys.exit(1)
    
    # Verificar dependencias
    check_dependencies()
    
    # Verificar PostgreSQL
    if not check_postgresql():
        print("\nPostgreSQL no está disponible")
        print("Instala PostgreSQL y asegúrate de que esté en el PATH")
        sys.exit(1)
    
    # Verificar archivo .env
    env_path = Path(__file__).parent / ".env"
    example_env = Path(__file__).parent / "env.example"
    
    if not env_path.exists():
        if example_env.exists():
            print("\nCreando archivo .env desde env.example...")
            import shutil
            shutil.copy(example_env, env_path)
            print("Archivo .env creado")
            print("IMPORTANTE: Configura tus credenciales en .env:")
            print("  - POSTGRES_PASSWORD=tu_contraseña_postgres")
            print("  - OPENWEATHER_API_KEY=tu_api_key")
            print("Luego ejecuta: python start.py")
            sys.exit(1)
        else:
            print("\nERROR: Archivo env.example no encontrado")
            sys.exit(1)
    
    # Configurar base de datos
    if not setup_database():
        print("\nNo se pudo configurar la base de datos")
        sys.exit(1)
    
    # Ejecutar ETL inicial
    run_etl()
    
    # Iniciar servidor
    start_server()

if __name__ == "__main__":
    main()
