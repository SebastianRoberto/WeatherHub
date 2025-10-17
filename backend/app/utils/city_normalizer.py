#!/usr/bin/env python3
"""
Utilidad para normalizar nombres de ciudades
"""

# Mapeo de nombres alternativos a nombres oficiales en la BD
CITY_ALIASES = {
    # Español -> Inglés
    'madrid': 'Madrid',
    'barcelona': 'Barcelona', 
    'valencia': 'Valencia',
    'sevilla': 'Sevilla',
    'bilbao': 'Bilbao',
    
    # Londres/London
    'londres': 'London',
    'london': 'London',
    
    # París/Paris
    'paris': 'Paris',
    'parís': 'Paris',
    
    # Berlín/Berlin
    'berlin': 'Berlin',
    'berlín': 'Berlin',
    
    # Roma/Rome
    'roma': 'Rome',
    'rome': 'Rome',
    
    # Amsterdam
    'amsterdam': 'Amsterdam',
    'ámsterdam': 'Amsterdam',
    
    # Nueva York
    'nueva york': 'New York',
    'new york': 'New York',
    'nueva_york': 'New York',
    'newyork': 'New York',
    
    # Los Ángeles
    'los angeles': 'Los Angeles',
    'los ángeles': 'Los Angeles',
    'los_angeles': 'Los Angeles',
    'losangeles': 'Los Angeles',
    
    # Tokyo/Tokio
    'tokyo': 'Tokyo',
    'tokio': 'Tokyo',
    'tókio': 'Tokyo',
    
    # Sydney/Sídney
    'sydney': 'Sydney',
    'sidney': 'Sydney',
    'sídney': 'Sydney',
    
    # São Paulo
    'sao paulo': 'São Paulo',
    'são paulo': 'São Paulo',
    'san pablo': 'São Paulo',
    
    # Beijing/Pekín
    'beijing': 'Beijing',
    'pekín': 'Beijing',
    'pekin': 'Beijing',
    
    # Shanghai
    'shanghai': 'Shanghai',
    'shanghái': 'Shanghai',
    
    # Hong Kong
    'hong kong': 'Hong Kong',
    'hong_kong': 'Hong Kong',
    
    # Singapore
    'singapore': 'Singapore',
    'singapur': 'Singapore',
    
    # Dubai
    'dubai': 'Dubai',
    'dubái': 'Dubai',
    
    # Moscow/Moscú
    'moscow': 'Moscow',
    'moscú': 'Moscow',
    'moscu': 'Moscow',
    
    # Istanbul/Estambul
    'istanbul': 'Istanbul',
    'estambul': 'Istanbul',
    
    # Mexico City/Ciudad de México
    'mexico city': 'Mexico City',
    'ciudad de mexico': 'Mexico City',
    'ciudad de méxico': 'Mexico City',
    'mexico': 'Mexico City',
    
    
    # Toronto
    'toronto': 'Toronto',
    
    # San Francisco
    'san francisco': 'San Francisco',
    'san_francisco': 'San Francisco',
    
    # Chicago
    'chicago': 'Chicago',
    
    # Seoul/Seúl
    'seoul': 'Seoul',
    'seúl': 'Seoul',
    'seul': 'Seoul',
    
    # Mumbai/Bombay
    'mumbai': 'Mumbai',
    'bombay': 'Mumbai',
    
    # Cairo/El Cairo
    'cairo': 'Cairo',
    'el cairo': 'Cairo',
    'el_cairo': 'Cairo',
    
    

    'buenos aires': 'Buenos Aires',
    'buenos_aires': 'Buenos Aires',
    
    # Bogotá
    'bogota': 'Bogotá',
    'bogotá': 'Bogotá',
    'bogotá dc': 'Bogotá',
    'bogota dc': 'Bogotá',
    
    # Lima
    'lima': 'Lima',
    
    # Santiago
    'santiago': 'Santiago',
    'santiago de chile': 'Santiago',
    
    # Rio de Janeiro
    'rio de janeiro': 'Rio de Janeiro',
    'rio_de_janeiro': 'Rio de Janeiro',
    'rio': 'Rio de Janeiro',
    
    # Monterrey
    'monterrey': 'Monterrey',
    
    # Quito
    'quito': 'Quito',
    
    # Panamá
    'panama': 'Panamá',
    'panamá': 'Panamá',
    'panama city': 'Panamá',
    'ciudad de panama': 'Panamá',
    'ciudad de panamá': 'Panamá',
    
    # Montevideo
    'montevideo': 'Montevideo',
    
    # Caracas
    'caracas': 'Caracas',
    
    # La Paz
    'la paz': 'La Paz',
    'la_paz': 'La Paz',
    
    # Cali
    'cali': 'Cali',
    'santiago de cali': 'Cali',
    
    # Santo Domingo
    'santo domingo': 'Santo Domingo',
    'santo_domingo': 'Santo Domingo',
    
    # Mexico City (ya existe, pero añadiendo variaciones)
    'mexico city': 'Mexico City',
    'ciudad de mexico': 'Mexico City',
    'ciudad de méxico': 'Mexico City',
    'mexico': 'Mexico City',
    'cdmx': 'Mexico City',
}

def normalize_city_name(city_name: str) -> str:
    """
    Normaliza el nombre de una ciudad usando el mapeo de alias
    
    Args:
        city_name: Nombre de ciudad a normalizar
        
    Returns:
        Nombre normalizado de la ciudad o el original si no se encuentra
    """
    if not city_name:
        return city_name
    
    # Convertir a minúsculas para búsqueda case-insensitive
    city_lower = city_name.strip().lower()
    
    # Buscar en alias
    if city_lower in CITY_ALIASES:
        return CITY_ALIASES[city_lower]
    
    # Si no se encuentra, devolver el original con primera letra mayúscula
    return city_name.strip().title()

def normalize_city_list(cities: list) -> list:
    """
    Normaliza una lista de nombres de ciudades
    
    Args:
        cities: Lista de nombres de ciudades
        
    Returns:
        Lista de nombres normalizados
    """
    return [normalize_city_name(city) for city in cities if city and city.strip()]

def get_city_suggestions(query: str, limit: int = 5) -> list:
    """
    Obtiene sugerencias de ciudades basadas en una búsqueda parcial
    
    Args:
        query: Texto de búsqueda
        limit: Número máximo de sugerencias
        
    Returns:
        Lista de sugerencias de ciudades
    """
    if not query or len(query) < 2:
        return []
    
    query_lower = query.lower()
    suggestions = []
    
    # Buscar coincidencias en alias
    for alias, official_name in CITY_ALIASES.items():
        if query_lower in alias and official_name not in suggestions:
            suggestions.append(official_name)
            if len(suggestions) >= limit:
                break
    
    return suggestions
