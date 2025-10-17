"""
Esquemas Pydantic para validación de datos
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


# Enums
class TemperatureUnit(str, Enum):
    CELSIUS = "c"
    FAHRENHEIT = "f"
    KELVIN = "k"


class MetricType(str, Enum):
    TEMPERATURE = "temp"
    HUMIDITY = "humidity"
    WIND = "wind"
    PRESSURE = "pressure"
    CLOUDS = "clouds"
    VISIBILITY = "visibility"


class OperatorType(str, Enum):
    GREATER_THAN = ">"
    LESS_THAN = "<"
    EQUAL = "="
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="


# Schemas de autenticación
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 6:
            raise ValueError('La nueva contraseña debe tener al menos 6 caracteres')
        return v


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Schemas de ciudades
class CityCreate(BaseModel):
    name: str
    country: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    openweather_id: Optional[int] = None


class CityResponse(BaseModel):
    id: int
    name: str
    country: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    openweather_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schemas de favoritos
class FavoriteCreate(BaseModel):
    city_id: int


class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    city_id: int
    city: CityResponse
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schemas de datos meteorológicos
class WeatherData(BaseModel):
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    wind_speed: float
    wind_deg: int
    clouds: int
    visibility: int
    weather_main: str
    weather_description: str
    unit: TemperatureUnit
    ts: datetime  # Timestamp del dato meteorológico


class WeatherCurrentResponse(BaseModel):
    city: CityResponse
    data: WeatherData
    timestamp: datetime


class WeatherHistoryResponse(BaseModel):
    city: CityResponse
    data: List[WeatherData]
    from_date: datetime
    to_date: datetime
    unit: TemperatureUnit


class WeatherCompareResponse(BaseModel):
    cities: List[CityResponse]
    data: Dict[str, List[WeatherData]]  # city_name -> weather_data_list
    from_date: datetime
    to_date: datetime
    unit: TemperatureUnit


# Schemas de alertas
class AlertCreate(BaseModel):
    city_id: int
    metric: MetricType
    operator: OperatorType
    threshold: float
    unit: Optional[TemperatureUnit] = None
    
    @validator('unit')
    def validate_unit_for_metric(cls, v, values):
        metric = values.get('metric')
        if metric == MetricType.TEMPERATURE and not v:
            raise ValueError('La unidad es requerida para alertas de temperatura')
        if metric != MetricType.TEMPERATURE and v:
            raise ValueError('La unidad solo es válida para alertas de temperatura')
        return v


class AlertUpdate(BaseModel):
    active: Optional[bool] = None
    paused: Optional[bool] = None
    threshold: Optional[float] = None


class AlertResponse(BaseModel):
    id: int
    user_id: int
    city_id: int
    city: CityResponse
    metric: str
    operator: str
    threshold: float
    unit: Optional[str]
    active: bool
    paused: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertHistoryResponse(BaseModel):
    id: int
    alert_id: int
    city_id: int
    city: CityResponse
    ts: datetime
    metric: str
    operator: Optional[str] = None  # Hacer opcional para registros existentes
    threshold: float
    observed_value: float
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schemas de exportación
class ExportRequest(BaseModel):
    city_ids: Optional[List[int]] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    unit: TemperatureUnit = TemperatureUnit.CELSIUS
    format: str = "csv"
    include_alerts: bool = False


class ExportResponse(BaseModel):
    filename: str
    download_url: str
    record_count: int


# Schemas de ETL
class ETLRunRequest(BaseModel):
    city_id: Optional[int] = None
    force_update: bool = False


class ETLStatusResponse(BaseModel):
    status: str
    message: str
    processed_cities: int
    errors: List[str] = []


# Schemas de respuesta general
class MessageResponse(BaseModel):
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    detail: str
    success: bool = False
