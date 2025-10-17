# Guía para instalar y ejecutar el proyecto

WeatherHub es una plataforma para la obtención y análisis de datos meteorológicos

## Requisitos
- Python 3.11+
- Node.js 18+
- PostgreSQL 13+

## 1) Clonar el repositorio
```bash
git clone https://github.com/SebastianRoberto/WeatherHub
cd WeatherHub
```

## 2) Configurar variables de entorno (backend)
1. Ir a `backend/`
2. Busca `example.env` y cambiale el nombre a `.env`
3. Edita los siguientes camposs:
   - `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`
   - `OPENWEATHER_API_KEY` (tu API key de OpenWeatherMap)
   - `DATABASE_URL` (si quieres cambiar usuario/contraseña/base/host/puerto por los tuyos)

Archivo de ejemplo: `backend/example.env` (cópialo y cambia valores reales)

## 3) Backend: instalar dependencias y arrancar
Desde `backend/` ejecuta:
```bash
pip install -r requirements.txt
python start.py
```
Este script automatiza:
- Detección del intérprete de Python disponible
- Verificación e instalación de dependencias (`requirements.txt`) si faltan
- Verificación de PostgreSQL (psql en PATH)
- Creación de `.env` a partir de `env.example` si no existe
- Configuración de PostgreSQL (usuario/BD/tablas si faltan)
- Inicialización de la base de datos
- Ejecución del ETL inicial para los primeros datos, no bloqueante si falla(no veras graficos con datos de varios dias a medida que el ETL vaya obteniendo datos cada día)
- Arranque del servidor FastAPI en `http://localhost:8000` (docs en `http://localhost:8000/docs`)

Notas:
- Si `.env` no existe, el script lo creará y terminará; edítalo y vuelve a ejecutar `python start.py`.
- Si `psql` no está en PATH, instala PostgreSQL y reinicia la terminal.
- Si ya existen usuario/BD/tablas, los scripts de setup/initialización se saltarán o terminarán sin afectar tus datos, a si que cada vez que quieras arrancar el backend simplemente ejecuta el "start.py".

## 4) Arrancar el frontend
En una segunda terminal:
```bash
cd frontend
npm install
npm run dev
```
Accede a `http://localhost:5173`. El frontend consume el backend en `http://localhost:8000`.

## 5) Flujo típico tras clonar
1. Instala PostgreSQL y configura la contraseña de `postgres`.
2. Copia y edita `backend/example.env` → `backend/.env`.
3. `cd backend && pip install -r requirements.txt && python start.py` (instala dependencias, prepara BD y levanta API).
4. `cd frontend && npm install && npm run dev` (levanta UI).

## 6) Problemas comunes
- psql no encontrado: añade PostgreSQL al PATH.
- Error de conexión a BD: revisa `DATABASE_URL` y credenciales `POSTGRES_*` en `.env`.
- API key inválida: revisa `OPENWEATHER_API_KEY`.
