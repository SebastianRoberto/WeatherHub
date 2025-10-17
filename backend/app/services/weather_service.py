"""
Servicio para conversión de datos meteorológicos
"""
from app.models import WeatherHourly
from app.schemas import WeatherData, TemperatureUnit


class WeatherService:
    """Servicio para operaciones con datos meteorológicos"""
    
    @staticmethod
    def convert_temperature(temp_c: float, unit: TemperatureUnit) -> float:
        """Convertir temperatura de Celsius a la unidad especificada"""
        if unit == TemperatureUnit.CELSIUS:
            return round(temp_c, 2)
        elif unit == TemperatureUnit.FAHRENHEIT:
            return round((temp_c * 9/5) + 32, 2)
        elif unit == TemperatureUnit.KELVIN:
            return round(temp_c + 273.15, 2)
        else:
            return temp_c
    
    @staticmethod
    def convert_weather_data(weather_hourly: WeatherHourly, unit: TemperatureUnit) -> WeatherData:
        """Convertir datos meteorológicos a la unidad especificada"""
        
        # Convertir temperaturas
        temperature = WeatherService.convert_temperature(weather_hourly.temp_c, unit)
        feels_like = WeatherService.convert_temperature(weather_hourly.feels_like_c, unit)
        
        return WeatherData(
            temperature=temperature,
            feels_like=feels_like,
            humidity=weather_hourly.humidity,
            pressure=weather_hourly.pressure,
            wind_speed=weather_hourly.wind_speed,
            wind_deg=weather_hourly.wind_deg,
            clouds=weather_hourly.clouds,
            visibility=weather_hourly.visibility,
            weather_main=weather_hourly.weather_main,
            weather_description=weather_hourly.weather_description,
            unit=unit,
            ts=weather_hourly.ts  # Incluir timestamp
        )
    
    @staticmethod
    def get_unit_symbol(unit: TemperatureUnit) -> str:
        """Obtener símbolo de unidad de temperatura"""
        symbols = {
            TemperatureUnit.CELSIUS: "°C",
            TemperatureUnit.FAHRENHEIT: "°F",
            TemperatureUnit.KELVIN: "K"
        }
        return symbols.get(unit, "°C")
