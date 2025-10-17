<script setup>
import TemperatureValue from '@/components/TemperatureValue.vue'
import { ref, computed, onMounted } from 'vue'
import { useWeatherStore } from '@/stores/weather'
import { useCitiesStore } from '@/stores/cities'
import CitySearch from '@/components/CitySearch.vue'
import WeatherCard from '@/components/WeatherCard.vue'
import DynamicBackground from '@/components/DynamicBackground.vue'
import { Loader2, CloudRain, RefreshCw, MapPin, ThermometerSun, Droplets, Gauge } from 'lucide-vue-next'
import { api } from '@/services/api'

const weather = useWeatherStore()
const cities = useCitiesStore()
const isRefreshing = ref(false)
const inlineNotice = ref("")
const noticeTimer = ref(null)


const favoritesWithData = computed(() => {
  return weather.favorites.filter(item => item.data && item.city)
})
const isNightTime = computed(() => {
  const hour = new Date().getHours()
  return hour < 6 || hour > 18
})
onMounted(async () => {
  await loadData()
})

async function loadData() {
  isRefreshing.value = true
  try {
    await Promise.all([
      cities.fetchFavorites(),
      cities.fetchCities({ limit: 500 }), 
      weather.fetchFavoritesCurrent()
    ])
  } finally {
    isRefreshing.value = false
  }
}

function getLatestFavoritesTs() {
  const items = weather.favorites || []
  const times = items
    .filter(item => item && item.timestamp)
    .map(item => new Date(item.timestamp).getTime())
    .filter(n => Number.isFinite(n))
  return times.length ? Math.max(...times) : null
}

function showInlineNotice(message) {
  inlineNotice.value = message
  if (noticeTimer.value) clearTimeout(noticeTimer.value)
  noticeTimer.value = setTimeout(() => {
    inlineNotice.value = ""
  }, 4000)
}

// Ejecutar ETL manual en background y refrescar
async function refreshData() {
  if (isRefreshing.value) return
  isRefreshing.value = true
  try {
    const beforeTs = getLatestFavoritesTs()
    await api.post('/etl/run/background', { force_update: false })
    // Espera breve para dar tiempo al job en segundo plano
    await new Promise(resolve => setTimeout(resolve, 5000))
    await loadData()
    const afterTs = getLatestFavoritesTs()
    if (beforeTs && afterTs && afterTs <= beforeTs) {
      showInlineNotice('Hay datos muy recientes, inténtalo de nuevo más tarde')
    } else {
      showInlineNotice('Datos actualizados')
    }
  } catch (e) {
    console.error('Error disparando ETL manual:', e)
    showInlineNotice('No se pudo ejecutar el ETL. Inténtalo de nuevo')
  } finally {
    if (!isRefreshing.value) return
    isRefreshing.value = false
  }
}
</script>

<template>
  <DynamicBackground 
    :condition="favoritesWithData.length > 0 ? favoritesWithData[0].data.weather_main : 'clear'"
    :isNight="isNightTime"
    class="dashboard-background"
  >
  <section>
    <!-- Encabezado de página -->
    <div class="page-title">
      <h1>Dashboard</h1>
      <button 
        class="btn btn-outline refresh-button" 
        @click="refreshData" 
        :disabled="isRefreshing || weather.loading"
      >
        <RefreshCw :class="{ 'animate-spin': isRefreshing }" size="18" />
        <span>Actualizar datos</span>
        <span class="refresh-tooltip">Ejecuta manualmente el ETL para refrescar datos</span>
      </button>
      <transition name="fade">
        <div v-if="inlineNotice" class="inline-notice">{{ inlineNotice }}</div>
      </transition>
    </div>
    

    <CitySearch />
    

    <div class="favorites-section">
      <div class="section-header">
        <h2>
          <MapPin size="20" />
          <span>Mis ciudades favoritas</span>
        </h2>
      </div>
      
      <div v-if="favoritesWithData.length" class="card-grid">
        <WeatherCard 
          v-for="item in favoritesWithData" 
          :key="item.city.id"
          :city="item.city"
          :data="item.data"
          :timestamp="item.timestamp"
          :isFavorite="true"
          @refresh="loadData"
        />
      </div>
      <!-- Estado de carga solo si no hay favoritos -->
      <div v-else-if="weather.loading && !isRefreshing" class="loading-state">
        <Loader2 class="animate-spin" size="32" />
        <p>Cargando datos meteorológicos...</p>
      </div>
      
      <!-- Estado vacío -->
      <div v-else class="empty-state card">
        <CloudRain size="48" color="var(--color-text-secondary)" />
        <h3>No tienes ciudades favoritas</h3>
        <p>Busca y añade ciudades para ver el clima actual en tu dashboard.</p>
      </div>
    </div>
    
    <!-- Sección de tendencias (opcional) -->
    <div v-if="favoritesWithData.length > 0" class="trends-section">
      <div class="section-header">
        <h2>Resumen de condiciones</h2>
      </div>
      
      <div class="summary-cards">
        <!-- Temperatura promedio -->
        <div class="summary-card">
          <div class="summary-icon" style="background-color: rgba(255, 160, 0, 0.1);">
            <ThermometerSun size="24" color="var(--color-accent)" />
          </div>
          <div class="summary-content">
            <h3>Temperatura promedio</h3>
            <p class="summary-value">
              <TemperatureValue 
                :value="favoritesWithData.length ? (favoritesWithData.reduce((sum, item) => sum + parseFloat(item.data.temperature), 0) / favoritesWithData.length) : 0"
                :unit="weather.unit"
              />
            </p>
          </div>
        </div>
        
        <!-- Humedad promedio -->
        <div class="summary-card">
          <div class="summary-icon" style="background-color: rgba(66, 165, 245, 0.1);">
            <Droplets size="24" color="#42A5F5" />
          </div>
          <div class="summary-content">
            <h3>Humedad promedio</h3>
            <p class="summary-value">
              {{ 
                (favoritesWithData.reduce((sum, item) => sum + parseFloat(item.data.humidity), 0) / 
                favoritesWithData.length).toFixed(0) 
              }}%
            </p>
          </div>
        </div>
        
        <!-- Presión promedio -->
        <div class="summary-card">
          <div class="summary-icon" style="background-color: rgba(38, 166, 154, 0.1);">
            <Gauge size="24" color="var(--color-secondary)" />
          </div>
          <div class="summary-content">
            <h3>Presión promedio</h3>
            <p class="summary-value">
              {{ 
                (favoritesWithData.reduce((sum, item) => sum + parseFloat(item.data.pressure), 0) / 
                favoritesWithData.length).toFixed(0) 
              }} hPa
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>
  </DynamicBackground>
</template>

<style scoped>
.dashboard-background {
  min-height: calc(100vh - var(--header-height) - var(--footer-height));
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-lg);
  padding: var(--space-lg);
}

.page-title {
  position: relative;
}

.refresh-button {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  position: relative;
}

.section-header {
  margin-bottom: var(--space-lg);
}

.section-header h2 {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: 1.5rem;
  color: var(--color-text-primary);
}

.favorites-section {
  margin-bottom: var(--space-xl);
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-xl);
  color: var(--color-text-secondary);
  gap: var(--space-md);
}

.empty-state {
  text-align: center;
  padding: var(--space-xl);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-md);
}

.empty-state h3 {
  margin-bottom: var(--space-xs);
  color: var(--color-text-primary);
}

.empty-state p {
  color: var(--color-text-secondary);
  max-width: 400px;
}

.trends-section {
  margin-bottom: var(--space-xl);
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--space-lg);
}

.summary-card {
  background-color: var(--color-card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  padding: var(--space-lg);
  display: flex;
  align-items: center;
  gap: var(--space-lg);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.summary-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
}

.summary-content h3 {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-xs);
  font-weight: 500;
}

.summary-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
}

/* Tooltip suave para botón actualizar datos */
.refresh-button .refresh-tooltip {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  top: calc(100% + 8px); /* mostrar por debajo del botón */
  background: var(--color-card-bg);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 12px;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.18s ease, transform 0.18s ease;
  box-shadow: var(--shadow-sm);
  white-space: nowrap;
}

.refresh-button:hover .refresh-tooltip {
  opacity: 1;
  transform: translateX(-50%) translateY(2px);
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.inline-notice {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: var(--color-card-bg);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 0.85rem;
  box-shadow: var(--shadow-lg);
  z-index: 1000;
  pointer-events: none;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity .18s ease;
}
.fade-enter-from, .fade-leave-to { opacity: 0; }

@media (max-width: 768px) {
  .summary-cards {
    grid-template-columns: 1fr;
  }
}
</style>
