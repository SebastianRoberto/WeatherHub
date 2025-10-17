<script setup>
import TemperatureValue from '@/components/TemperatureValue.vue'
import { computed } from 'vue'
import { Cloud, Droplets, Wind, Gauge, Clock, Star, StarOff } from 'lucide-vue-next'
import { useCitiesStore } from '@/stores/cities'
import WeatherIcon from '@/components/WeatherIcon.vue'

const props = defineProps({
  city: { type: Object, required: true },
  data: { type: Object, required: true },
  timestamp: { type: String, required: true },
  isFavorite: { type: Boolean, default: false }
})

const cities = useCitiesStore()

const emit = defineEmits(['refresh'])

const formattedDate = computed(() => {
  return new Date(props.timestamp).toLocaleString('es-ES', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
})

const temperatureUnit = computed(() => {
  switch(props.data.unit) {
    case 'c': return '°C'
    case 'f': return '°F'
    default: return 'K'
  }
})

// Esta función se mantiene como referencia para la lógica de clasificación del clima
// pero ahora usamos el componente WeatherIcon para la visualización

// Determinar si es de noche según la hora actual
const isNightTime = computed(() => {
  const hour = new Date(props.timestamp).getHours()
  return hour < 6 || hour > 18
})

// Clase de fondo dinámico según el clima
const weatherBgClass = computed(() => {
  const condition = props.data.weather_description?.toLowerCase() || props.data.weather_main?.toLowerCase() || ''
  
  if (isNightTime.value) {
    return 'weather-bg-night'
  }
  
  if (condition.includes('clear') || condition.includes('sunny')) {
    return 'weather-bg-clear'
  }
  
  if (condition.includes('cloud')) {
    return 'weather-bg-clouds'
  }
  
  if (condition.includes('rain') || condition.includes('shower') || condition.includes('drizzle')) {
    return 'weather-bg-rain'
  }
  
  if (condition.includes('snow') || condition.includes('sleet') || condition.includes('hail')) {
    return 'weather-bg-snow'
  }
  
  if (condition.includes('thunder') || condition.includes('lightning') || condition.includes('storm')) {
    return 'weather-bg-thunderstorm'
  }
  
  if (condition.includes('mist') || condition.includes('fog') || condition.includes('haze')) {
    return 'weather-bg-mist'
  }
  
  return ''
})

const temperatureColor = computed(() => {
  const temp = parseFloat(props.data.temperature)
  if (props.data.unit === 'c') {
    if (temp < 0) return '#42A5F5' // cold blue
    if (temp < 10) return '#64B5F6' // cool blue
    if (temp < 20) return '#26A69A' // moderate teal
    if (temp < 30) return '#FFA000' // warm amber
    return '#F57C00' // hot orange
  } else if (props.data.unit === 'f') {
    if (temp < 32) return '#42A5F5' // cold blue
    if (temp < 50) return '#64B5F6' // cool blue
    if (temp < 68) return '#26A69A' // moderate teal
    if (temp < 86) return '#FFA000' // warm amber
    return '#F57C00' // hot orange
  } else { // kelvin
    if (temp < 273.15) return '#42A5F5' // cold blue
    if (temp < 283.15) return '#64B5F6' // cool blue
    if (temp < 293.15) return '#26A69A' // moderate teal
    if (temp < 303.15) return '#FFA000' // warm amber
    return '#F57C00' // hot orange
  }
})

async function toggleFavorite() {
  if (props.isFavorite) {
    await cities.removeFavorite(props.city.id)
  } else {
    await cities.addFavorite(props.city.id)
  }
  emit('refresh')
}
</script>

<template>
  <div class="card weather-card" :class="weatherBgClass">
    <div class="weather-card-header">
      <div>
        <h3>{{ city.name }} <small v-if="city.country">({{ city.country }})</small></h3>
        <p class="weather-card-date">
          <Clock size="14" />
          <span>{{ formattedDate }}</span>
        </p>
      </div>
      <button class="favorite-button" @click="toggleFavorite" :title="isFavorite ? 'Quitar de favoritos' : 'Añadir a favoritos'">
        <Star v-if="isFavorite" size="20" fill="#FFA000" stroke="#FFA000" />
        <StarOff v-else size="20" />
      </button>
    </div>
    
    <div class="weather-card-main">
      <div class="weather-card-temp" :style="{ color: temperatureColor }">
        <TemperatureValue :value="data.temperature" :unit="data.unit" />
      </div>
      
      <div class="weather-icon">
        <WeatherIcon 
          :condition="props.data.weather_description || props.data.weather_main || 'Clear'" 
          :size="48" 
          :isNight="isNightTime" 
        />
      </div>
    </div>
    
    <p class="weather-card-desc">{{ data.weather_main }} – {{ data.weather_description }}</p>
    
    <div class="weather-card-grid">
      <div class="weather-card-grid-item">
        <Droplets size="16" />
        <span>Humedad: {{ data.humidity }}%</span>
      </div>
      <div class="weather-card-grid-item">
        <Gauge size="16" />
        <span>Presión: {{ data.pressure }} hPa</span>
      </div>
      <div class="weather-card-grid-item">
        <Wind size="16" />
        <span>Viento: {{ data.wind_speed }} m/s</span>
      </div>
      <div class="weather-card-grid-item">
        <Cloud size="16" />
        <span>Nubes: {{ data.clouds }}%</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.weather-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  transition: all var(--transition-fast);
}

.weather-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.weather-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-md);
}

.weather-card-header h3 {
  margin-bottom: var(--space-xs);
  font-size: 1.2rem;
}

.weather-card-header small {
  color: var(--color-text-secondary);
  font-weight: normal;
  font-size: 0.9rem;
}

.weather-card-date {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  color: var(--color-text-secondary);
  font-size: 0.85rem;
  margin: 0;
}

.favorite-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--space-xs);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}

.favorite-button:hover {
  background-color: var(--color-hover-bg);
  transform: scale(1.1);
}

.weather-card-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

.weather-card-temp {
  font-size: 2.5rem;
  font-weight: 700;
  line-height: 1;
}

.weather-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.weather-card-desc {
  margin-bottom: var(--space-md);
  color: var(--color-text-secondary);
  font-weight: 500;
}

.weather-card-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-sm) var(--space-md);
  margin-top: auto;
  padding-top: var(--space-md);
  border-top: 1px solid var(--color-border);
}

.weather-card-grid-item {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

/* Dynamic Weather Card Styles */
.weather-card.weather-bg-clear {
  background: linear-gradient(135deg, rgba(255, 213, 79, 0.1), rgba(255, 167, 38, 0.2));
  border-left: 3px solid #FFA726;
}

.weather-card.weather-bg-clouds {
  background: linear-gradient(135deg, rgba(144, 202, 249, 0.1), rgba(100, 181, 246, 0.2));
  border-left: 3px solid #64B5F6;
}

.weather-card.weather-bg-rain {
  background: linear-gradient(135deg, rgba(120, 144, 156, 0.1), rgba(84, 110, 122, 0.2));
  border-left: 3px solid #546E7A;
}

.weather-card.weather-bg-snow {
  background: linear-gradient(135deg, rgba(225, 245, 254, 0.1), rgba(179, 229, 252, 0.2));
  border-left: 3px solid #B3E5FC;
}

.weather-card.weather-bg-thunderstorm {
  background: linear-gradient(135deg, rgba(69, 90, 100, 0.1), rgba(38, 50, 56, 0.2));
  border-left: 3px solid #455A64;
}

.weather-card.weather-bg-mist {
  background: linear-gradient(135deg, rgba(207, 216, 220, 0.1), rgba(176, 190, 197, 0.2));
  border-left: 3px solid #B0BEC5;
}

.weather-card.weather-bg-night {
  background: linear-gradient(135deg, rgba(26, 35, 126, 0.1), rgba(40, 53, 147, 0.2));
  border-left: 3px solid #283593;
}

.dark-theme .weather-card.weather-bg-clear,
.dark-theme .weather-card.weather-bg-clouds,
.dark-theme .weather-card.weather-bg-rain,
.dark-theme .weather-card.weather-bg-snow,
.dark-theme .weather-card.weather-bg-thunderstorm,
.dark-theme .weather-card.weather-bg-mist,
.dark-theme .weather-card.weather-bg-night {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.1));
}
</style>