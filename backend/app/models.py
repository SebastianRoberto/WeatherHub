"""
Modelos de base de datos para WeatherHub
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, Text, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """Modelo de usuario"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")


class City(Base):
    """Modelo de ciudad"""
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    country = Column(String(255))
    lat = Column(Float)
    lon = Column(Float)
    openweather_id = Column(Integer, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Constraint único para nombre y país
    __table_args__ = (
        UniqueConstraint('name', 'country', name='unique_city_country'),
    )
    
    # Relaciones
    weather_hourly = relationship("WeatherHourly", back_populates="city", cascade="all, delete-orphan")
    weather_daily = relationship("WeatherDaily", back_populates="city", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="city", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="city", cascade="all, delete-orphan")


class Favorite(Base):
    """Modelo de ciudad favorita por usuario"""
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Constraint único para usuario y ciudad
    __table_args__ = (
        UniqueConstraint('user_id', 'city_id', name='unique_user_city_favorite'),
    )
    
    # Relaciones
    user = relationship("User", back_populates="favorites")
    city = relationship("City", back_populates="favorites")


class WeatherRaw(Base):
    """Modelo para respuesta JSON original de OpenWeatherMap"""
    __tablename__ = "weather_raw"
    
    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False)
    fetched_at = Column(DateTime(timezone=True), nullable=False)
    data = Column(Text, nullable=False)  # JSON como texto
    
    # Relaciones
    weather_hourly = relationship("WeatherHourly", back_populates="raw_data")


class WeatherHourly(Base):
    """Modelo de datos meteorológicos por hora"""
    __tablename__ = "weather_hourly"
    
    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False)
    ts = Column(DateTime(timezone=True), nullable=False)
    
    # Temperaturas (guardamos solo en Celsius, convertimos al devolver)
    temp_c = Column(Float)
    feels_like_c = Column(Float)
    
    # Otros datos meteorológicos
    humidity = Column(Integer)
    pressure = Column(Integer)
    wind_speed = Column(Float)
    wind_deg = Column(Integer)
    clouds = Column(Integer)
    visibility = Column(Integer)
    weather_main = Column(String(255))
    weather_description = Column(String(255))
    
    # Referencia a datos raw
    raw_id = Column(Integer, ForeignKey("weather_raw.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Constraint único para ciudad y timestamp
    __table_args__ = (
        UniqueConstraint('city_id', 'ts', name='unique_city_timestamp'),
        Index('idx_weather_hourly_city_ts', 'city_id', 'ts'),
    )
    
    # Relaciones
    city = relationship("City", back_populates="weather_hourly")
    raw_data = relationship("WeatherRaw", back_populates="weather_hourly")


class WeatherDaily(Base):
    """Modelo de agregados diarios"""
    __tablename__ = "weather_daily"
    
    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False)
    day = Column(Date, nullable=False)
    
    # Agregados diarios
    temp_min = Column(Float)
    temp_max = Column(Float)
    temp_avg = Column(Float)
    precip_total = Column(Float)
    humidity_avg = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Constraint único para ciudad y día
    __table_args__ = (
        UniqueConstraint('city_id', 'day', name='unique_city_day'),
    )
    
    # Relaciones
    city = relationship("City", back_populates="weather_daily")


class Alert(Base):
    """Modelo de reglas de alertas por usuario"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False)
    
    # Configuración de la alerta
    metric = Column(String(50), nullable=False)  # 'temp', 'humidity', 'wind', 'pressure'
    operator = Column(String(10), nullable=False)  # '>', '<', '=', '>=', '<='
    threshold = Column(Float, nullable=False)
    unit = Column(String(10))  # 'c', 'f', 'k' para temperatura, null para otros
    
    # Estado de la alerta
    active = Column(Boolean, default=True)
    paused = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Constraint único para evitar duplicados
    __table_args__ = (
        UniqueConstraint('user_id', 'city_id', 'metric', 'operator', 'threshold', 
                        name='unique_user_city_metric_alert'),
    )
    
    # Relaciones
    user = relationship("User", back_populates="alerts")
    city = relationship("City", back_populates="alerts")
    alert_history = relationship("AlertHistory", back_populates="alert", cascade="all, delete-orphan")


class AlertHistory(Base):
    """Modelo de historial de activaciones de alertas"""
    __tablename__ = "alert_history"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, nullable=False)  # Redundante para consultas rápidas
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False)  # Redundante para consultas rápidas
    
    ts = Column(DateTime(timezone=True), nullable=False)
    metric = Column(String(50))
    operator = Column(String(10))
    threshold = Column(Float)
    observed_value = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Índice para consultas por timestamp
    __table_args__ = (
        Index('idx_alert_history_ts', 'ts'),
    )
    
    # Relaciones
    alert = relationship("Alert", back_populates="alert_history")
    city = relationship("City")
