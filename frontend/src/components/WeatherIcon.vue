<script setup>
import { computed } from 'vue'
import { 
  Sun, 
  Cloud, 
  CloudRain, 
  CloudSnow, 
  CloudLightning, 
  CloudFog, 
  CloudDrizzle, 
  Sunrise, 
  Sunset, 
  Moon 
} from 'lucide-vue-next'

const props = defineProps({
  condition: {
    type: String,
    required: true
  },
  size: {
    type: Number,
    default: 24
  },
  isNight: {
    type: Boolean,
    default: false
  }
})

const icon = computed(() => {
  // Normalizar la condición a minúsculas para facilitar la comparación
  const condition = props.condition.toLowerCase()
  
  // Determinar el icono según la condición meteorológica
  if (condition.includes('clear') || condition.includes('sunny')) {
    return props.isNight ? Moon : Sun
  }
  
  if (condition.includes('few clouds') || condition.includes('partly cloudy')) {
    return Cloud
  }
  
  if (condition.includes('clouds') || condition.includes('overcast')) {
    return Cloud
  }
  
  if (condition.includes('drizzle')) {
    return CloudDrizzle
  }
  
  if (condition.includes('rain') || condition.includes('shower')) {
    return CloudRain
  }
  
  if (condition.includes('snow') || condition.includes('sleet') || condition.includes('hail')) {
    return CloudSnow
  }
  
  if (condition.includes('thunder') || condition.includes('lightning') || condition.includes('storm')) {
    return CloudLightning
  }
  
  if (condition.includes('mist') || condition.includes('fog') || condition.includes('haze')) {
    return CloudFog
  }
  
  if (condition.includes('sunrise')) {
    return Sunrise
  }
  
  if (condition.includes('sunset')) {
    return Sunset
  }
  
  // Por defecto, devolver el icono de sol o luna según sea de día o de noche
  return props.isNight ? Moon : Sun
})

const iconColor = computed(() => {
  const condition = props.condition.toLowerCase()
  
  if (condition.includes('clear') || condition.includes('sunny')) {
    return props.isNight ? '#5C6BC0' : '#FFA000'
  }
  
  if (condition.includes('clouds') || condition.includes('overcast')) {
    return '#78909C'
  }
  
  if (condition.includes('rain') || condition.includes('shower') || condition.includes('drizzle')) {
    return '#1E88E5'
  }
  
  if (condition.includes('snow') || condition.includes('sleet') || condition.includes('hail')) {
    return '#90A4AE'
  }
  
  if (condition.includes('thunder') || condition.includes('lightning') || condition.includes('storm')) {
    return '#5E35B1'
  }
  
  if (condition.includes('mist') || condition.includes('fog') || condition.includes('haze')) {
    return '#B0BEC5'
  }
  
  return props.isNight ? '#5C6BC0' : '#FFA000'
})

const animationClass = computed(() => {
  const condition = props.condition.toLowerCase()
  
  if (condition.includes('rain') || condition.includes('shower') || condition.includes('drizzle')) {
    return 'weather-icon-rain'
  }
  
  if (condition.includes('snow')) {
    return 'weather-icon-snow'
  }
  
  if (condition.includes('thunder') || condition.includes('lightning')) {
    return 'weather-icon-lightning'
  }
  
  if (condition.includes('clear') || condition.includes('sunny')) {
    return props.isNight ? 'weather-icon-night' : 'weather-icon-day'
  }
  
  return ''
})
</script>

<template>
  <div class="weather-icon-container" :class="animationClass">
    <component :is="icon" :size="size" :color="iconColor" />
  </div>
</template>

<style scoped>
.weather-icon-container {
  display: inline-flex;
  transition: transform var(--transition-normal);
}

.weather-icon-container:hover {
  transform: scale(1.1);
}

.weather-icon-day {
  animation: pulse 3s infinite ease-in-out;
}

.weather-icon-night {
  animation: glow 3s infinite ease-in-out;
}

.weather-icon-rain {
  animation: bounce 2s infinite ease-in-out;
}

.weather-icon-snow {
  animation: float 3s infinite ease-in-out;
}

.weather-icon-lightning {
  animation: flash 3s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

@keyframes glow {
  0%, 100% { filter: drop-shadow(0 0 2px rgba(92, 107, 192, 0.3)); }
  50% { filter: drop-shadow(0 0 8px rgba(92, 107, 192, 0.6)); }
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  25% { transform: translateY(-2px) rotate(2deg); }
  50% { transform: translateY(0) rotate(0deg); }
  75% { transform: translateY(-2px) rotate(-2deg); }
}

@keyframes flash {
  0%, 50%, 100% { filter: brightness(1); }
  25%, 75% { filter: brightness(1.5) drop-shadow(0 0 5px rgba(94, 53, 177, 0.7)); }
}
</style>
