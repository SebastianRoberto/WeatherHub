import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useCitiesStore = defineStore('cities', () => {
  const list = ref([])
  const favorites = ref([])
  const loading = ref(false)
  
  // Mapeo de nombres de ciudad para normalización (sincronizado con backend)
  const cityNameMap = {
    // Español -> Inglés
    'madrid': 'Madrid',
    'barcelona': 'Barcelona',
    'valencia': 'Valencia',
    'sevilla': 'Sevilla',
    'bilbao': 'Bilbao',
    
    // Londres/London
    'londres': 'London',
    'london': 'London',
    
    // París/Paris
    'paris': 'Paris',
    'parís': 'Paris',
    
    // Berlín/Berlin
    'berlin': 'Berlin',
    'berlín': 'Berlin',
    
    // Roma/Rome
    'roma': 'Rome',
    'rome': 'Rome',
    
    // Amsterdam
    'amsterdam': 'Amsterdam',
    'ámsterdam': 'Amsterdam',
    
    // Nueva York
    'nueva york': 'New York',
    'new york': 'New York',
    'nueva_york': 'New York',
    'newyork': 'New York',
    
    // Los Ángeles
    'los angeles': 'Los Angeles',
    'los ángeles': 'Los Angeles',
    'los_angeles': 'Los Angeles',
    'losangeles': 'Los Angeles',
    
    // Tokyo/Tokio
    'tokyo': 'Tokyo',
    'tokio': 'Tokyo',
    'tókio': 'Tokyo',
    
    // Sydney/Sídney
    'sydney': 'Sydney',
    'sidney': 'Sydney',
    'sídney': 'Sydney',
    
    // São Paulo
    'sao paulo': 'São Paulo',
    'são paulo': 'São Paulo',
    'san pablo': 'São Paulo',
    
    // Beijing/Pekín
    'beijing': 'Beijing',
    'pekín': 'Beijing',
    'pekin': 'Beijing',
    
    // Shanghai
    'shanghai': 'Shanghai',
    'shanghái': 'Shanghai',
    
    // Hong Kong
    'hong kong': 'Hong Kong',
    'hong_kong': 'Hong Kong',
    
    // Singapore
    'singapore': 'Singapore',
    'singapur': 'Singapore',
    
    // Dubai
    'dubai': 'Dubai',
    'dubái': 'Dubai',
    
    // Moscow/Moscú
    'moscow': 'Moscow',
    'moscú': 'Moscow',
    'moscu': 'Moscow',
    
    // Istanbul/Estambul
    'istanbul': 'Istanbul',
    'estambul': 'Istanbul',
    
    // Mexico City/Ciudad de México
    'mexico city': 'Mexico City',
    'ciudad de mexico': 'Mexico City',
    'ciudad de méxico': 'Mexico City',
    'mexico': 'Mexico City',
    
    // Buenos Aires
    'buenos aires': 'Buenos Aires',
    'buenos_aires': 'Buenos Aires',
    'bsas': 'Buenos Aires',
    
    // Toronto
    'toronto': 'Toronto',
    
    // San Francisco
    'san francisco': 'San Francisco',
    'san_francisco': 'San Francisco',
    
    // Chicago
    'chicago': 'Chicago',
    
    // Seoul/Seúl
    'seoul': 'Seoul',
    'seúl': 'Seoul',
    'seul': 'Seoul',
    
    // Mumbai/Bombay
    'mumbai': 'Mumbai',
    'bombay': 'Mumbai',
    
    // Cairo/El Cairo
    'cairo': 'Cairo',
    'el cairo': 'Cairo',
    'el_cairo': 'Cairo',
    
    
    // Bogotá
    'bogota': 'Bogotá',
    'bogotá': 'Bogotá',
    'bogotá dc': 'Bogotá',
    'bogota dc': 'Bogotá',
    
    // Lima
    'lima': 'Lima',
    
    // Santiago
    'santiago': 'Santiago',
    'santiago de chile': 'Santiago',
    
    // Rio de Janeiro
    'rio de janeiro': 'Rio de Janeiro',
    'rio_de_janeiro': 'Rio de Janeiro',
    'rio': 'Rio de Janeiro',
    
    // Monterrey
    'monterrey': 'Monterrey',
    
    // Quito
    'quito': 'Quito',
    
    // Panamá
    'panama': 'Panamá',
    'panamá': 'Panamá',
    'panama city': 'Panamá',
    'ciudad de panama': 'Panamá',
    'ciudad de panamá': 'Panamá',
    
    // Montevideo
    'montevideo': 'Montevideo',
    
    // Caracas
    'caracas': 'Caracas',
    
    // La Paz
    'la paz': 'La Paz',
    'la_paz': 'La Paz',
    
    // Cali
    'cali': 'Cali',
    'santiago de cali': 'Cali',
    
    // Santo Domingo
    'santo domingo': 'Santo Domingo',
    'santo_domingo': 'Santo Domingo',
    
    
    'mexico city': 'Mexico City',
    'ciudad de mexico': 'Mexico City',
    'ciudad de méxico': 'Mexico City',
    'mexico': 'Mexico City',
    'cdmx': 'Mexico City'
  }

  async function fetchCities({ search = '', skip = 0, limit = 100 } = {}) {
    loading.value = true
    try {
      const { data } = await api.get('/cities', { params: { search, skip, limit } })
      list.value = data
      console.log(`[Cities Store] Cargadas ${data.length} ciudades:`, data.map(c => c.name))
    } finally {
      loading.value = false
    }
  }

  async function fetchFavorites() {
    loading.value = true
    try {
      const { data } = await api.get('/cities/favorites/')
      favorites.value = data
    } finally {
      loading.value = false
    }
  }

  async function addFavorite(city_id) {
    const { data } = await api.post('/cities/favorites/', { city_id })
    favorites.value.push(data)
  }

  async function removeFavorite(city_id) {
    await api.delete(`/cities/favorites/${city_id}`)
    favorites.value = favorites.value.filter((f) => f.city_id !== city_id)
  }

  // Función para normalizar nombres de ciudad (case-insensitive)
  function normalizeCityName(cityName) {
    if (!cityName) return cityName
    const normalized = cityNameMap[cityName.toLowerCase()] || cityName
    return normalized
  }

  // Función para normalizar lista de ciudades
  function normalizeCityList(cities) {
    return cities.map(city => normalizeCityName(city))
  }

  // Función para refrescar todas las ciudades (útil cuando se agrega una nueva)
  async function refreshAllCities() {
    console.log('[Cities Store] Refrescando todas las ciudades...')
    await Promise.all([
      fetchCities({ limit: 500 }),
      fetchFavorites()
    ])
    console.log('[Cities Store] Ciudades refrescadas:', list.value.length, 'ciudades disponibles')
  }

  return { 
    list, 
    favorites, 
    loading, 
    cityNameMap,
    fetchCities, 
    fetchFavorites, 
    addFavorite, 
    removeFavorite,
    normalizeCityName,
    normalizeCityList,
    refreshAllCities
  }
})
