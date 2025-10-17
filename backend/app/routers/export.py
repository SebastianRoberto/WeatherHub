"""
Router de exportación de datos
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import csv
import io
from app.database import get_db
from app.models import WeatherHourly, AlertHistory, City
from app.schemas import ExportRequest, ExportResponse, TemperatureUnit
from app.auth import get_current_active_user
from app.services.weather_service import WeatherService

router = APIRouter()


@router.get("/history", response_class=Response)
async def export_weather_history(
    city: Optional[str] = Query(None, description="Nombre de la ciudad (para vista Historial)"),
    city_ids: Optional[str] = Query(None, description="IDs de ciudades separados por coma (modo múltiple)"),
    metrics: Optional[str] = Query(None, description="Métricas separadas por coma (temperature,humidity,pressure,wind)"),
    mode: Optional[str] = Query("standard", description="standard|detailed"),
    from_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    to_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    days: Optional[int] = Query(7, ge=1, le=365, description="Número de días hacia atrás"),
    unit: TemperatureUnit = Query(TemperatureUnit.CELSIUS, description="Unidad de temperatura"),
    filename: Optional[str] = Query(None, description="Nombre de archivo deseado"),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Exportar historial a CSV.
    - Si se indica `city`, genera CSV tipo Historial (una ciudad) con columnas por métricas.
    - Si se indican `city_ids`, exporta en formato tabular amplio por registro.
    """
    metric_list = [m.strip() for m in (metrics.split(",") if metrics else ["temperature"]) if m.strip()]

    # Determinar rango de fechas
    if not from_date or not to_date:
        to_date = to_date or datetime.utcnow()
        from_date = from_date or (to_date - timedelta(days=days or 7))

    output = io.StringIO()
    writer = csv.writer(output)
    weather_service = WeatherService()

    if city:
        # Vista Historial (una ciudad, columnas por métricas, encabezado 'Fecha')
        city_obj = db.query(City).filter(City.name.ilike(f"%{city}%")).first()
        if not city_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ciudad no encontrada")

        # Encabezados
        headers = ["Fecha"]
        for m in metric_list:
            if m == "temperature":
                headers.append(f"Temperatura ({unit.value})")
            elif m == "humidity":
                headers.append("Humedad (%)")
            elif m == "pressure":
                headers.append("Presión (hPa)")
            elif m == "wind":
                headers.append("Viento (m/s)")
            else:
                headers.append(m)
        writer.writerow(headers)

        rows = db.query(WeatherHourly).filter(
            WeatherHourly.city_id == city_obj.id,
            WeatherHourly.ts >= from_date,
            WeatherHourly.ts <= to_date
        ).order_by(WeatherHourly.ts.asc()).all()

        for r in rows:
            values = []
            for m in metric_list:
                if m == "temperature":
                    values.append(weather_service.convert_temperature(r.temp_c, unit))
                elif m == "humidity":
                    values.append(r.humidity)
                elif m == "pressure":
                    values.append(r.pressure)
                elif m == "wind":
                    values.append(r.wind_speed)
                else:
                    values.append("")
            writer.writerow([r.ts.isoformat(), *values])

        csv_content = output.getvalue()
        output.close()

        if not filename:
            metric_slug = "-".join(metric_list)
            filename = f"history_{city_obj.name}_{from_date.strftime('%Y-%m-%d')}_{to_date.strftime('%Y-%m-%d')}.csv"

        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    else:
        # Modo múltiple por IDs de ciudades (formato amplio por registro)
        if city_ids:
            city_id_list = [int(id.strip()) for id in city_ids.split(",") if id.strip()]
        else:
            cities = db.query(City).all()
            city_id_list = [city.id for city in cities]

        rows = db.query(WeatherHourly).filter(
            WeatherHourly.city_id.in_(city_id_list),
            WeatherHourly.ts >= from_date,
            WeatherHourly.ts <= to_date
        ).order_by(WeatherHourly.city_id, WeatherHourly.ts.asc()).all()

        if not rows:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay datos disponibles para exportar")

        headers = [
            "city_id", "city_name", "country", "timestamp",
            f"temperature_{unit.value}", f"feels_like_{unit.value}",
            "humidity", "pressure", "wind_speed", "wind_deg",
            "clouds", "visibility", "weather_main", "weather_description"
        ]
        writer.writerow(headers)

        for data in rows:
            temp = weather_service.convert_temperature(data.temp_c, unit)
            feels_like = weather_service.convert_temperature(data.feels_like_c, unit)
            writer.writerow([
                data.city_id,
                data.city.name,
                data.city.country,
                data.ts.isoformat(),
                temp,
                feels_like,
                data.humidity,
                data.pressure,
                data.wind_speed,
                data.wind_deg,
                data.clouds,
                data.visibility,
                data.weather_main,
                data.weather_description,
            ])

        csv_content = output.getvalue()
        output.close()

        if not filename:
            filename = f"weather_history_{from_date.strftime('%Y%m%d')}_{to_date.strftime('%Y%m%d')}.csv"

        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )


@router.get("/compare", response_class=Response)
async def export_compare(
    cities: str = Query(..., description="Nombres de ciudades separados por coma"),
    metrics: Optional[str] = Query(None, description="Métricas separadas por coma (temperature,humidity,pressure,wind)"),
    from_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    to_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    days: Optional[int] = Query(7, ge=1, le=365, description="Número de días hacia atrás"),
    unit: TemperatureUnit = Query(TemperatureUnit.CELSIUS, description="Unidad de temperatura"),
    limit: Optional[int] = Query(10000, ge=1, le=100000, description="Límite de registros"),
    filename: Optional[str] = Query(None, description="Nombre de archivo deseado"),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Exportar comparación por métricas y ciudades a CSV (por gráfico o general)."""
    city_names = [c.strip() for c in cities.split(",") if c.strip()]
    metric_list = [m.strip() for m in (metrics.split(",") if metrics else ["temperature"]) if m.strip()]

    # Determinar rango de fechas
    if not from_date or not to_date:
        to_date = to_date or datetime.utcnow()
        from_date = from_date or (to_date - timedelta(days=days or 7))

    # Resolver IDs de ciudades por nombre (ilike)
    city_objs: List[City] = []
    for name in city_names:
        city = db.query(City).filter(City.name.ilike(f"%{name}%")).first()
        if city:
            city_objs.append(city)

    if not city_objs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ciudades no encontradas")

    weather_service = WeatherService()

    # CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output)

    # Encabezados: Ciudad, Fecha, columnas por cada métrica seleccionada
    headers = ["Ciudad", "Fecha"]
    for m in metric_list:
        if m == "temperature":
            headers.append(f"Temperatura ({unit.value})")
        elif m == "humidity":
            headers.append("Humedad (%)")
        elif m == "pressure":
            headers.append("Presión (hPa)")
        elif m == "wind":
            headers.append("Viento (m/s)")
        else:
            headers.append(m)
    writer.writerow(headers)

    # Para cada ciudad, obtener datos y escribir filas
    for city in city_objs:
        q = db.query(WeatherHourly).filter(
            WeatherHourly.city_id == city.id,
            WeatherHourly.ts >= from_date,
            WeatherHourly.ts <= to_date,
        ).order_by(WeatherHourly.ts.asc())
        if limit:
            q = q.limit(limit)
        rows = q.all()
        for row in rows:
            # Convertir temperatura si corresponde
            values = []
            for m in metric_list:
                if m == "temperature":
                    values.append(weather_service.convert_temperature(row.temp_c, unit))
                elif m == "humidity":
                    values.append(row.humidity)
                elif m == "pressure":
                    values.append(row.pressure)
                elif m == "wind":
                    values.append(row.wind_speed)
                else:
                    values.append("")
            writer.writerow([city.name, row.ts.isoformat(), *values])

    csv_content = output.getvalue()
    output.close()

    if not filename:
        city_slug = "-".join([c.name for c in city_objs])
        metric_slug = "-".join(metric_list)
        filename = f"compare_{metric_slug}_{city_slug}_{from_date.strftime('%Y-%m-%d')}_{to_date.strftime('%Y-%m-%d')}.csv"

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/compare-summary", response_class=Response)
async def export_compare_summary(
    cities: str = Query(..., description="Nombres de ciudades separados por coma"),
    metrics: str = Query("temperature", description="Métricas separadas por coma"),
    from_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    to_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    days: Optional[int] = Query(7, ge=1, le=365, description="Número de días hacia atrás"),
    unit: TemperatureUnit = Query(TemperatureUnit.CELSIUS, description="Unidad de temperatura"),
    filename: Optional[str] = Query(None, description="Nombre de archivo deseado"),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Exportar resumen por ciudad (promedios por métrica) a CSV."""
    city_names = [c.strip() for c in cities.split(",") if c.strip()]
    metric_list = [m.strip() for m in metrics.split(",") if m.strip()]

    if not from_date or not to_date:
        to_date = to_date or datetime.utcnow()
        from_date = from_date or (to_date - timedelta(days=days or 7))

    # Resolver ciudades
    city_objs: List[City] = []
    for name in city_names:
        city = db.query(City).filter(City.name.ilike(f"%{name}%")).first()
        if city:
            city_objs.append(city)
    if not city_objs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ciudades no encontradas")

    weather_service = WeatherService()

    # CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output)

    headers = ["Ciudad"]
    for m in metric_list:
        if m == "temperature":
            headers.append(f"Temperatura Promedio ({unit.value})")
        elif m == "humidity":
            headers.append("Humedad Promedio (%)")
        elif m == "pressure":
            headers.append("Presión Promedio (hPa)")
        elif m == "wind":
            headers.append("Viento Promedio (m/s)")
        else:
            headers.append(f"{m} Promedio")
    writer.writerow(headers)

    for city in city_objs:
        q = db.query(WeatherHourly).filter(
            WeatherHourly.city_id == city.id,
            WeatherHourly.ts >= from_date,
            WeatherHourly.ts <= to_date,
        ).order_by(WeatherHourly.ts.asc())
        rows = q.all()
        if not rows:
            writer.writerow([city.name] + [""] * len(metric_list))
            continue
        # Calcular promedios simples
        values = []
        for m in metric_list:
            if m == "temperature":
                temps = [weather_service.convert_temperature(r.temp_c, unit) for r in rows if r.temp_c is not None]
                avg = round(sum(temps) / len(temps), 1) if temps else ""
                values.append(avg)
            elif m == "humidity":
                vals = [r.humidity for r in rows if r.humidity is not None]
                avg = round(sum(vals) / len(vals), 1) if vals else ""
                values.append(avg)
            elif m == "pressure":
                vals = [r.pressure for r in rows if r.pressure is not None]
                avg = round(sum(vals) / len(vals), 1) if vals else ""
                values.append(avg)
            elif m == "wind":
                vals = [r.wind_speed for r in rows if r.wind_speed is not None]
                avg = round(sum(vals) / len(vals), 1) if vals else ""
                values.append(avg)
            else:
                values.append("")
        writer.writerow([city.name, *values])

    csv_content = output.getvalue()
    output.close()

    if not filename:
        city_slug = "-".join([c.name for c in city_objs])
        metric_slug = "-".join(metric_list)
        filename = f"compare_summary_{city_slug}_{metric_slug}_{from_date.strftime('%Y-%m-%d')}_{to_date.strftime('%Y-%m-%d')}.csv"

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/alerts", response_class=Response)
async def export_alert_history(
    from_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    to_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    city_id: Optional[int] = Query(None, description="ID de ciudad"),
    metric: Optional[str] = Query(None, description="Tipo de métrica"),
    format: str = Query("csv", description="Formato de exportación"),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Exportar historial de alertas a CSV"""
    
    # Determinar rango de fechas
    if not from_date:
        from_date = datetime.utcnow() - timedelta(days=30)
    if not to_date:
        to_date = datetime.utcnow()
    
    # Construir query
    query = db.query(AlertHistory).filter(
        AlertHistory.user_id == current_user.id,
        AlertHistory.ts >= from_date,
        AlertHistory.ts <= to_date
    )
    
    if city_id:
        query = query.filter(AlertHistory.city_id == city_id)
    if metric:
        query = query.filter(AlertHistory.metric == metric)
    
    alert_history = query.order_by(AlertHistory.ts.desc()).all()
    
    if not alert_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay datos de alertas disponibles para exportar"
        )
    
    # Crear CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Escribir encabezados
    headers = [
        "alert_id", "city_id", "city_name", "timestamp", 
        "metric", "threshold", "observed_value", "created_at"
    ]
    writer.writerow(headers)
    
    # Escribir datos
    for alert in alert_history:
        # Obtener nombre de la ciudad
        city = db.query(City).filter(City.id == alert.city_id).first()
        city_name = city.name if city else "Unknown"
        
        row = [
            alert.alert_id,
            alert.city_id,
            city_name,
            alert.ts.isoformat(),
            alert.metric,
            alert.threshold,
            alert.observed_value,
            alert.created_at.isoformat()
        ]
        writer.writerow(row)
    
    # Preparar respuesta
    csv_content = output.getvalue()
    output.close()
    
    # Generar nombre de archivo
    filename = f"alert_history_{from_date.strftime('%Y%m%d')}_{to_date.strftime('%Y%m%d')}.csv"
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/custom", response_class=Response)
async def export_custom_data(
    export_request: ExportRequest,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Exportar datos personalizados según filtros"""
    
    # Si no se especifican ciudades, usar todas
    if not export_request.city_ids:
        cities = db.query(City).all()
        city_ids = [city.id for city in cities]
    else:
        city_ids = export_request.city_ids
    
    # Determinar rango de fechas
    from_date = export_request.from_date or (datetime.utcnow() - timedelta(days=30))
    to_date = export_request.to_date or datetime.utcnow()
    
    # Obtener datos meteorológicos
    weather_data = db.query(WeatherHourly).filter(
        WeatherHourly.city_id.in_(city_ids),
        WeatherHourly.ts >= from_date,
        WeatherHourly.ts <= to_date
    ).order_by(WeatherHourly.city_id, WeatherHourly.ts.asc()).all()
    
    if not weather_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay datos disponibles para exportar"
        )
    
    # Crear CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Escribir encabezados
    headers = [
        "city_id", "city_name", "country", "timestamp", 
        f"temperature_{export_request.unit.value}", f"feels_like_{export_request.unit.value}",
        "humidity", "pressure", "wind_speed", "wind_deg",
        "clouds", "visibility", "weather_main", "weather_description"
    ]
    
    # Añadir columna de alertas si se solicita
    if export_request.include_alerts:
        headers.append("alert_triggered")
    
    writer.writerow(headers)
    
    # Escribir datos
    weather_service = WeatherService()
    for data in weather_data:
        # Convertir temperaturas
        temp = weather_service.convert_temperature(data.temp_c, export_request.unit)
        feels_like = weather_service.convert_temperature(data.feels_like_c, export_request.unit)
        
        row = [
            data.city_id,
            data.city.name,
            data.city.country,
            data.ts.isoformat(),
            temp,
            feels_like,
            data.humidity,
            data.pressure,
            data.wind_speed,
            data.wind_deg,
            data.clouds,
            data.visibility,
            data.weather_main,
            data.weather_description
        ]
        
        # Añadir información de alertas si se solicita
        if export_request.include_alerts:
            # Verificar si hay alertas activas para este timestamp
            alert_count = db.query(AlertHistory).filter(
                AlertHistory.user_id == current_user.id,
                AlertHistory.city_id == data.city_id,
                AlertHistory.ts == data.ts
            ).count()
            row.append("1" if alert_count > 0 else "0")
        
        writer.writerow(row)
    
    # Preparar respuesta
    csv_content = output.getvalue()
    output.close()
    
    # Generar nombre de archivo
    filename = f"custom_export_{from_date.strftime('%Y%m%d')}_{to_date.strftime('%Y%m%d')}.csv"
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
