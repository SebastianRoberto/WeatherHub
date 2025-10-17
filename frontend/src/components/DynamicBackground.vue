<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  condition: {
    type: String,
    default: 'clear'
  },
  isNight: {
    type: Boolean,
    default: false
  },
  animate: {
    type: Boolean,
    default: true
  }
})

const particles = ref([])
const containerRef = ref(null)
const animationFrameId = ref(null)

// Generar partículas según la condición meteorológica
const generateParticles = () => {
  if (!containerRef.value || !props.animate) return
  
  const container = containerRef.value
  const containerWidth = container.clientWidth
  const containerHeight = container.clientHeight
  
  const condition = props.condition.toLowerCase()
  const particleCount = getParticleCount(condition)
  
  particles.value = []
  
  for (let i = 0; i < particleCount; i++) {
    const x = Math.random() * containerWidth
    const y = Math.random() * containerHeight
    const size = getParticleSize(condition)
    const speed = getParticleSpeed(condition)
    const opacity = Math.random() * 0.7 + 0.3
    
    particles.value.push({
      id: i,
      x,
      y,
      size,
      speed,
      opacity,
      angle: Math.random() * 360
    })
  }
}

// Determinar la cantidad de partículas según la condición
const getParticleCount = (condition) => {
  if (condition.includes('rain') || condition.includes('shower')) {
    return 50
  } else if (condition.includes('snow')) {
    return 40
  } else if (condition.includes('cloud')) {
    return 8
  } else if (props.isNight) {
    return 20 // estrellas
  } else {
    return 5 // sol, rayos de sol
  }
}

// Determinar el tamaño de las partículas según la condición
const getParticleSize = (condition) => {
  if (condition.includes('rain') || condition.includes('shower')) {
    return Math.random() * 2 + 1
  } else if (condition.includes('snow')) {
    return Math.random() * 4 + 2
  } else if (condition.includes('cloud')) {
    return Math.random() * 40 + 20
  } else if (props.isNight) {
    return Math.random() * 2 + 1
  } else {
    return Math.random() * 10 + 5
  }
}

// Determinar la velocidad de las partículas según la condición
const getParticleSpeed = (condition) => {
  if (condition.includes('rain') || condition.includes('shower')) {
    return Math.random() * 3 + 2
  } else if (condition.includes('snow')) {
    return Math.random() * 1 + 0.5
  } else if (condition.includes('cloud')) {
    return Math.random() * 0.2 + 0.1
  } else {
    return Math.random() * 0.1 + 0.05
  }
}

// Animar las partículas
const animateParticles = () => {
  if (!containerRef.value || !props.animate) return
  
  const container = containerRef.value
  const containerWidth = container.clientWidth
  const containerHeight = container.clientHeight
  const condition = props.condition.toLowerCase()
  
  particles.value.forEach(particle => {
    if (condition.includes('rain') || condition.includes('shower')) {
      // Lluvia - caída vertical rápida
      particle.y += particle.speed
      if (particle.y > containerHeight) {
        particle.y = -10
        particle.x = Math.random() * containerWidth
      }
    } else if (condition.includes('snow')) {
      // Nieve - caída lenta con balanceo
      particle.y += particle.speed
      particle.x += Math.sin(particle.angle) * 0.5
      particle.angle += 0.01
      if (particle.y > containerHeight) {
        particle.y = -10
        particle.x = Math.random() * containerWidth
      }
    } else if (condition.includes('cloud')) {
      // Nubes - movimiento horizontal lento
      particle.x += particle.speed
      if (particle.x > containerWidth + 50) {
        particle.x = -50
      }
    } else if (props.isNight) {
      // Estrellas - parpadeo
      particle.opacity = 0.3 + Math.sin(Date.now() * 0.001 + particle.id) * 0.3
    } else {
      // Sol - rotación lenta
      particle.angle += 0.01
    }
  })
  
  animationFrameId.value = requestAnimationFrame(animateParticles)
}

// Clase de fondo según la condición meteorológica
const backgroundClass = computed(() => {
  const condition = props.condition.toLowerCase()
  
  if (props.isNight) {
    return 'bg-night'
  }
  
  if (condition.includes('clear') || condition.includes('sunny')) {
    return 'bg-clear'
  }
  
  if (condition.includes('cloud')) {
    return 'bg-clouds'
  }
  
  if (condition.includes('rain') || condition.includes('shower') || condition.includes('drizzle')) {
    return 'bg-rain'
  }
  
  if (condition.includes('snow') || condition.includes('sleet') || condition.includes('hail')) {
    return 'bg-snow'
  }
  
  if (condition.includes('thunder') || condition.includes('lightning') || condition.includes('storm')) {
    return 'bg-thunderstorm'
  }
  
  if (condition.includes('mist') || condition.includes('fog') || condition.includes('haze')) {
    return 'bg-mist'
  }
  
  return 'bg-default'
})

onMounted(() => {
  generateParticles()
  if (props.animate) {
    animateParticles()
  }
  
  window.addEventListener('resize', generateParticles)
})

onBeforeUnmount(() => {
  if (animationFrameId.value) {
    cancelAnimationFrame(animationFrameId.value)
  }
  
  window.removeEventListener('resize', generateParticles)
})
</script>

<template>
  <div class="dynamic-background" :class="backgroundClass" ref="containerRef">
    <div v-for="particle in particles" :key="particle.id" 
         class="particle" 
         :class="{ 
           'rain-particle': condition.toLowerCase().includes('rain') || condition.toLowerCase().includes('shower'),
           'snow-particle': condition.toLowerCase().includes('snow'),
           'cloud-particle': condition.toLowerCase().includes('cloud'),
           'star-particle': isNight,
           'sun-particle': !isNight && condition.toLowerCase().includes('clear')
         }"
         :style="{ 
           left: `${particle.x}px`, 
           top: `${particle.y}px`, 
           width: `${particle.size}px`, 
           height: condition.toLowerCase().includes('rain') ? `${particle.size * 5}px` : `${particle.size}px`,
           opacity: particle.opacity,
           transform: !condition.toLowerCase().includes('rain') ? `rotate(${particle.angle}deg)` : 'none'
         }">
    </div>
    <slot></slot>
  </div>
</template>

<style scoped>
.dynamic-background {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  transition: background-color var(--transition-normal);
}

.bg-clear {
  background: linear-gradient(to bottom right, rgba(255, 213, 79, 0.1), rgba(255, 167, 38, 0.2));
}

.bg-clouds {
  background: linear-gradient(to bottom right, rgba(144, 202, 249, 0.1), rgba(100, 181, 246, 0.2));
}

.bg-rain {
  background: linear-gradient(to bottom right, rgba(120, 144, 156, 0.1), rgba(84, 110, 122, 0.2));
}

.bg-snow {
  background: linear-gradient(to bottom right, rgba(225, 245, 254, 0.1), rgba(179, 229, 252, 0.2));
}

.bg-thunderstorm {
  background: linear-gradient(to bottom right, rgba(69, 90, 100, 0.1), rgba(38, 50, 56, 0.2));
}

.bg-mist {
  background: linear-gradient(to bottom right, rgba(207, 216, 220, 0.1), rgba(176, 190, 197, 0.2));
}

.bg-night {
  background: linear-gradient(to bottom right, rgba(26, 35, 126, 0.1), rgba(40, 53, 147, 0.2));
}

.bg-default {
  background: transparent;
}

.particle {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
}

.rain-particle {
  background-color: rgba(144, 202, 249, 0.6);
  border-radius: 0;
}

.snow-particle {
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
}

.cloud-particle {
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 50%;
  filter: blur(10px);
}

.star-particle {
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  box-shadow: 0 0 5px rgba(255, 255, 255, 0.8);
}

.sun-particle {
  background-color: rgba(255, 193, 7, 0.5);
  border-radius: 3px;
  box-shadow: 0 0 10px rgba(255, 193, 7, 0.5);
}

.dark-theme .bg-clear {
  background: linear-gradient(to bottom right, rgba(255, 213, 79, 0.05), rgba(255, 167, 38, 0.1));
}

.dark-theme .bg-clouds {
  background: linear-gradient(to bottom right, rgba(144, 202, 249, 0.05), rgba(100, 181, 246, 0.1));
}

.dark-theme .bg-rain {
  background: linear-gradient(to bottom right, rgba(120, 144, 156, 0.05), rgba(84, 110, 122, 0.1));
}

.dark-theme .bg-snow {
  background: linear-gradient(to bottom right, rgba(225, 245, 254, 0.05), rgba(179, 229, 252, 0.1));
}

.dark-theme .bg-thunderstorm {
  background: linear-gradient(to bottom right, rgba(69, 90, 100, 0.05), rgba(38, 50, 56, 0.1));
}

.dark-theme .bg-mist {
  background: linear-gradient(to bottom right, rgba(207, 216, 220, 0.05), rgba(176, 190, 197, 0.1));
}

.dark-theme .bg-night {
  background: linear-gradient(to bottom right, rgba(26, 35, 126, 0.05), rgba(40, 53, 147, 0.1));
}
</style>
