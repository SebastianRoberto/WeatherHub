"""
Servicio para evaluación de alertas meteorológicas
"""
import structlog
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models import Alert, AlertHistory, WeatherHourly
from app.schemas import MetricType, OperatorType

logger = structlog.get_logger()


class AlertService:
    """Servicio para evaluación de alertas"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def evaluate_alert(self, alert: Alert, weather_data: WeatherHourly):
        """Evaluar si una alerta se debe activar"""
        
        try:
            # Obtener valor observado según la métrica
            observed_value = self._get_observed_value(alert.metric, weather_data, alert.unit)
            
            if observed_value is None:
                logger.warning("No se pudo obtener valor observado", 
                             alert_id=alert.id, metric=alert.metric)
                return
            
            # Evaluar condición
            condition_met = self._evaluate_condition(
                observed_value, alert.operator, alert.threshold
            )
            
            if condition_met:
                # Crear nuevo registro de alerta activada (sin verificar duplicados)
                alert_history = AlertHistory(
                    alert_id=alert.id,
                    user_id=alert.user_id,
                    city_id=alert.city_id,
                    ts=weather_data.ts,
                    metric=alert.metric,
                    operator=alert.operator,  # Agregar operador
                    threshold=alert.threshold,
                    observed_value=observed_value
                )
                
                self.db.add(alert_history)
                self.db.commit()
                
                logger.info("Alerta activada", 
                          alert_id=alert.id, 
                          user_id=alert.user_id,
                          city_id=alert.city_id,
                          metric=alert.metric,
                          operator=alert.operator,
                          threshold=alert.threshold,
                          observed_value=observed_value)
            
        except Exception as e:
            logger.error("Error evaluando alerta", alert_id=alert.id, error=str(e))
            self.db.rollback()
    
    def _get_observed_value(self, metric: str, weather_data: WeatherHourly, unit: Optional[str]) -> Optional[float]:
        """Obtener valor observado según la métrica"""
        
        if metric == MetricType.TEMPERATURE:
            if unit == "c":
                return weather_data.temp_c
            elif unit == "f":
                return (weather_data.temp_c * 9/5) + 32
            elif unit == "k":
                return weather_data.temp_c + 273.15
            else:
                return weather_data.temp_c
        
        elif metric == MetricType.HUMIDITY:
            return float(weather_data.humidity)
        
        elif metric == MetricType.WIND:
            return weather_data.wind_speed
        
        elif metric == MetricType.PRESSURE:
            return float(weather_data.pressure)
        
        elif metric == MetricType.CLOUDS:
            return float(weather_data.clouds)
        
        elif metric == MetricType.VISIBILITY:
            return float(weather_data.visibility) if weather_data.visibility else None
        
        else:
            logger.warning("Métrica no reconocida", metric=metric)
            return None
    
    def _evaluate_condition(self, observed_value: float, operator: str, threshold: float) -> bool:
        """Evaluar condición de alerta"""
        
        try:
            if operator == OperatorType.GREATER_THAN:
                return observed_value > threshold
            elif operator == OperatorType.LESS_THAN:
                return observed_value < threshold
            elif operator == OperatorType.EQUAL:
                return abs(observed_value - threshold) < 0.1  # Tolerancia para igualdad
            elif operator == OperatorType.GREATER_EQUAL:
                return observed_value >= threshold
            elif operator == OperatorType.LESS_EQUAL:
                return observed_value <= threshold
            else:
                logger.warning("Operador no reconocido", operator=operator)
                return False
                
        except Exception as e:
            logger.error("Error evaluando condición", 
                        observed_value=observed_value, 
                        operator=operator, 
                        threshold=threshold, 
                        error=str(e))
            return False
    
    async def get_active_alerts_for_user(self, user_id: int, city_id: Optional[int] = None) -> list:
        """Obtener alertas activas para un usuario"""
        
        query = self.db.query(Alert).filter(
            Alert.user_id == user_id,
            Alert.active == True,
            Alert.paused == False
        )
        
        if city_id:
            query = query.filter(Alert.city_id == city_id)
        
        return query.all()
    
    async def get_alert_history_for_user(self, user_id: int, limit: int = 100) -> list:
        """Obtener historial de alertas para un usuario"""
        
        return self.db.query(AlertHistory).filter(
            AlertHistory.user_id == user_id
        ).order_by(AlertHistory.ts.desc()).limit(limit).all()
