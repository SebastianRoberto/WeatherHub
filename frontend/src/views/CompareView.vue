<script setup>
import MetricChart from '@/components/MetricChart.vue'
import TemperatureValue from '@/components/TemperatureValue.vue'
import { ref, computed, onMounted, watch } from 'vue'
import { useWeatherStore } from '@/stores/weather'
import { useCitiesStore } from '@/stores/cities'
import { METRIC_CONFIGS } from '@/stores/metrics'
import { api } from '@/services/api'
import ExportButton from '@/components/ExportButton.vue'
import CustomDropdown from '@/components/CustomDropdown.vue'
import { Loader2, BarChart2, Trash2, MapPin, Calendar, Download } from 'lucide-vue-next'

// Función para escribir logs automáticamente al archivo
async function writeToLogFile(message) {
  const timestamp = new Date().toISOString()
  const logEntry = `[${timestamp}] ${message}\n`
  
  // Usar console.log con prefijo especial para identificar logs automáticos
  console.log(`[AUTO-LOG] ${message}`)
  
  // Escribir a localStorage para backup
  try {
    const existingLogs = localStorage.getItem('comparacion_logs') || ''
    const newLogs = existingLogs + logEntry
    localStorage.setItem('comparacion_logs', newLogs)
  } catch (e) {
    console.warn('No se pudo escribir a localStorage:', e)
  }
  
}

const weather = useWeatherStore()
const cities = useCitiesStore()
const selectedCities = ref([])
const cityInput = ref('')
const isLoading = ref(false)
const loadingMetrics = ref(new Set())
const days = ref(7)
const selectedMetrics = ref(['temperature'])
const metricData = ref({})
const showCustomDateRange = ref(false)
const customFromDate = ref('')
const customToDate = ref('')

// Configuración de métricas desde el store
const availableMetrics = computed(() => {
  return Object.values(METRIC_CONFIGS).map(config => ({
    id: config.key,
    label: config.title,
    unit: config.unit,
    color: config.color,
    icon: config.icon
  }))
})

// Colores para las ciudades
const cityColors = [
  '#1E88E5', // azul primario
  '#26A69A', // verde-azulado secundario
  '#FFA000', // ámbar acento
  '#7E57C2', // púrpura
  '#EC407A', // rosa
  '#F57C00', // naranja
  '#5C6BC0', // índigo
  '#43A047', // verde
]

// Opciones para el desplegable de período
const periodOptions = [
  { value: 3, label: 'Últimos 3 días' },
  { value: 7, label: 'Últimos 7 días' },
  { value: 14, label: 'Últimos 14 días' },
  { value: 30, label: 'Últimos 30 días' },
  { value: 'custom', label: 'Rango personalizado' }
]

// Cargar favoritos al iniciar
onMounted(async () => {
  await Promise.all([
    cities.fetchFavorites(),
    cities.fetchCities({ limit: 500 }) // Cargar todas las ciudades disponibles
  ])
  
  // Inicializar con Madrid y Londres
  selectedCities.value = ['Madrid', 'Londres']
  await loadData()
})

// Opciones para el desplegable de ciudades
const cityOptions = computed(() => {
  console.log('[CompareView] Generando cityOptions...')
  console.log('[CompareView] Favoritas:', cities.favorites.length)
  console.log('[CompareView] Lista general:', cities.list.length)
  
  // Combinar ciudades favoritas y lista general, evitando duplicados
  const allCities = []
  const addedNames = new Set() // Para evitar duplicados
  
  // Agregar favoritas primero (con prioridad)
  cities.favorites.forEach(f => {
    if (f.city && f.city.name && !addedNames.has(f.city.name)) {
      allCities.push({
        value: f.city.name,
        label: `${f.city.name}${f.city.country ? ` (${f.city.country})` : ''}`,
        name: f.city.name,
        country: f.city.country,
        isFavorite: true,
        cityId: f.city.id
      })
      addedNames.add(f.city.name)
    }
  })
  
  // Agregar ciudades de la lista general (evitando duplicados)
  cities.list.forEach(city => {
    if (city.name && !addedNames.has(city.name)) {
      allCities.push({
        value: city.name,
        label: `${city.name}${city.country ? ` (${city.country})` : ''}`,
        name: city.name,
        country: city.country,
        isFavorite: false,
        cityId: city.id
      })
      addedNames.add(city.name)
    }
  })
  
  // Ordenar alfabéticamente por nombre
  const sorted = allCities.sort((a, b) => a.name.localeCompare(b.name))
  console.log('[CompareView] Opciones generadas:', sorted.length, 'ciudades')
  return sorted
})

// Observar cambios en las ciudades seleccionadas para actualizar el gráfico
watch(selectedCities, async () => {
  if (selectedCities.value.length >= 2) {
    await loadData()
  }
}, { deep: true })

// Datos para el gráfico (mantenido para compatibilidad - no usado en nueva implementación)
// const chartData = computed(() => { ... })

// Unidad para la métrica seleccionada (removido - no se usa)

// Función para cargar datos por métrica para comparación
async function fetchMetricCompareData(metric) {
  try {
    console.log(`🔍 [COMPARE] Iniciando carga de ${metric} para ciudades:`, selectedCities.value)
    writeToLogFile(`🔍 [COMPARE] Iniciando carga de ${metric} para ciudades: ${JSON.stringify(selectedCities.value)}`)
    
    const citiesParam = selectedCities.value.join(',')
    
    // Construir URL según si es rango personalizado o días predefinidos
    let url = `/weather/compare/${metric}?cities=${citiesParam}`
    if (days.value === 'custom') {
      // Convertir fechas a formato ISO datetime
      const fromDateTime = `${customFromDate.value}T00:00:00`
      const toDateTime = `${customToDate.value}T23:59:59`
      url += `&from_date=${fromDateTime}&to_date=${toDateTime}`
    } else {
      url += `&days=${days.value}`
    }
    console.log(`📡 [COMPARE] URL: ${url}`)
    writeToLogFile(`📡 [COMPARE] URL: ${url}`)
    
    const response = await api.get(url)
    console.log(`📊 [COMPARE] Response status: ${response.status}`)
    writeToLogFile(`📊 [COMPARE] Response status: ${response.status}`)
    
    const data = response.data
    console.log(`✅ [COMPARE] Datos recibidos para ${metric}:`, data)
    writeToLogFile(`✅ [COMPARE] Datos recibidos para ${metric}: ${JSON.stringify(data).substring(0, 200)}...`)
    console.log(`📈 [COMPARE] Ciudades en respuesta:`, Object.keys(data.data || {}))
    
    // DEBUG: Verificar estructura de datos del backend
    if (data.data && Object.keys(data.data).length > 0) {
      const firstCity = Object.keys(data.data)[0]
      const firstCityData = data.data[firstCity]
      console.log(`🔍 [COMPARE] ${metric} - Estructura de datos del backend para ${firstCity}:`, firstCityData.slice(0, 2))
      console.log(`🔍 [COMPARE] ${metric} - Campos disponibles en primer item:`, Object.keys(firstCityData[0] || {}))
      
      // DEBUG ESPECÍFICO: Verificar si hay timestamps
      if (firstCityData.length > 0) {
        const firstItem = firstCityData[0]
        console.log(`🔍 [COMPARE] ${metric} - Primer item completo:`, firstItem)
        console.log(`🔍 [COMPARE] ${metric} - ¿Tiene ts?:`, 'ts' in firstItem, firstItem.ts)
        console.log(`🔍 [COMPARE] ${metric} - ¿Tiene timestamp?:`, 'timestamp' in firstItem, firstItem.timestamp)
        console.log(`🔍 [COMPARE] ${metric} - ¿Tiene date?:`, 'date' in firstItem, firstItem.date)
        console.log(`🔍 [COMPARE] ${metric} - ¿Tiene time?:`, 'time' in firstItem, firstItem.time)
      }
    }
    
    if (!data.data || typeof data.data !== 'object') {
      console.warn(`⚠️ [COMPARE] No hay datos en la respuesta para ${metric}`)
      return {}
    }
    
    console.log(`🎯 [COMPARE] Datos procesados para ${metric}:`, Object.keys(data.data).length, 'ciudades')
    
    // CONVERTIR A FORMATO ESTRUCTURADO PARA MÚLTIPLES LÍNEAS
    const processedData = []
    // Extraer nombres de ciudad del array de objetos o strings
    const cityNames = (data.cities || []).map(c => typeof c === 'string' ? c : (c.name || c))
    console.log(`[COMPARE] Nombres de ciudad en respuesta:`, cityNames)
    
    // Usar el store de ciudades para normalización (ya no necesitamos cityNameMap local)
    
    // Procesar cada ciudad y mantener estructura para múltiples líneas
    selectedCities.value.forEach(cityName => {
      // Normalizar nombre de ciudad usando el store
      const normalizedName = cities.normalizeCityName ? cities.normalizeCityName(cityName) : cityName
      console.log(`[COMPARE] Ciudad original: ${cityName} -> normalizada: ${normalizedName}`)
      
      // Buscar el nombre real (case-insensitive) - el backend ya normaliza
      const match = cityNames.find(n => n.toLowerCase() === normalizedName.toLowerCase())
      console.log(`[COMPARE] Buscando ${normalizedName} en:`, cityNames, '-> match:', match)
      if (match && data.data[match]) {
        const cityData = data.data[match].map((item) => {
          console.log(`[COMPARE] ${metric} - Item original para ${cityName}:`, {
            ts: item.ts,
            timestamp: item.timestamp,
            temperature: item.temperature,
            humidity: item.humidity,
            pressure: item.pressure,
            wind_speed: item.wind_speed,
            value: item.value
          })
          
       
          let timestamp = item.timestamp || item.ts
          if (!timestamp) {
            console.error(`❌ [COMPARE] ${metric} - TIMESTAMP UNDEFINED para ${cityName}:`, item)
            // No generar timestamp fallback - esto indica un problema real
            return null
          }
          
          // Extraer el valor específico de la métrica actual
          let value = ''
          switch (metric) {
            case 'temperature': 
              value = item.temperature || item.temp_c || ''
              break
            case 'humidity': 
              value = item.humidity || ''
              break
            case 'pressure': 
              value = item.pressure || ''
              break
            case 'wind': 
              value = item.wind_speed || ''
              break
            default: 
              value = item.value || ''
          }
          
          return {
            timestamp: timestamp,
            value: value,
            city: cityName, // Mantener referencia a la ciudad original
            // Mantener también los campos originales para compatibilidad
            temperature: item.temperature || item.temp_c,
            humidity: item.humidity,
            pressure: item.pressure,
            wind_speed: item.wind_speed
          }
        }).filter(item => item !== null) // Filtrar elementos null
        // Mantener estructura por ciudad para múltiples líneas
        processedData.push({
          city: cityName,
          data: cityData
        })
        console.log(`[COMPARE] Datos para ciudad ${match}:`, cityData.length, 'registros')
      } else {
        console.warn(`[COMPARE] No se encontró data para ciudad:`, cityName, 'normalizado:', normalizedName, 'en', cityNames)
      }
    })
    
    console.log(`📊 [COMPARE] Datos finales para ${metric}:`, processedData.length, 'ciudades')
    console.log(`📊 [COMPARE] Datos finales completos:`, processedData)
    
    // MANTENER ESTRUCTURA ORIGINAL PARA MetricChart (NO APLANAR)
    // MetricChart detecta múltiples ciudades por la propiedad 'city' en cada item
    const flattenedData = []
    processedData.forEach(cityGroup => {
      // Agregar propiedad 'city' a cada item para que MetricChart pueda detectar múltiples ciudades
      const cityDataWithCity = cityGroup.data.map(item => ({
        ...item,
        city: cityGroup.city
      }))
      flattenedData.push(...cityDataWithCity)
    })
    
    console.log(`📊 [COMPARE] Datos con city property para MetricChart:`, flattenedData.length, 'registros')
    console.log(`📊 [COMPARE] Primeros 3 items:`, flattenedData.slice(0, 3))
    
    // Log detallado de timestamps para debugging
    const timestamps = flattenedData.map(item => item.timestamp).sort()
    console.log(`🕐 [COMPARE] Timestamps ordenados:`, timestamps)
    writeToLogFile(`🕐 [COMPARE] Timestamps ordenados: ${JSON.stringify(timestamps)}`)
    console.log(`🕐 [COMPARE] Timestamp más antiguo:`, timestamps[0])
    writeToLogFile(`🕐 [COMPARE] Timestamp más antiguo: ${timestamps[0]}`)
    console.log(`🕐 [COMPARE] Timestamp más reciente:`, timestamps[timestamps.length - 1])
    writeToLogFile(`🕐 [COMPARE] Timestamp más reciente: ${timestamps[timestamps.length - 1]}`)
    
    return flattenedData
  } catch (error) {
    console.error(`❌ [COMPARE] Error cargando datos de comparación de ${metric}:`, error)
    return []
  }
}

// Cargar datos para todas las métricas seleccionadas
async function loadMetricData() {
  if (selectedCities.value.length < 2) return
  
  isLoading.value = true
  metricData.value = {}
  
  try {
    const promises = selectedMetrics.value.map(async (metric) => {
      const data = await fetchMetricCompareData(metric)
      metricData.value[metric] = data
      
      // Almacenar estructura original para getCityAverage
      // Necesitamos reconstruir la estructura desde los datos aplanados
      const cityGroups = {}
      if (Array.isArray(data)) {
        data.forEach(item => {
          if (item.city && !cityGroups[item.city]) {
            cityGroups[item.city] = { city: item.city, data: [] }
          }
          if (item.city) {
            cityGroups[item.city].data.push(item)
          }
        })
        metricData.value[`${metric}_structured`] = Object.values(cityGroups)
      }
    })
    
    await Promise.all(promises)
  } catch (error) {
    console.error('Error cargando datos de comparación:', error)
  } finally {
    isLoading.value = false
  }
}

// Cargar datos para una métrica específica
async function loadSingleMetric(metric) {
  if (selectedCities.value.length < 2) return
  
  loadingMetrics.value.add(metric)
  
  try {
    const data = await fetchMetricCompareData(metric)
    metricData.value[metric] = data
    
    // Almacenar estructura original para getCityAverage
    const cityGroups = {}
    if (Array.isArray(data)) {
      data.forEach(item => {
        if (item.city && !cityGroups[item.city]) {
          cityGroups[item.city] = { city: item.city, data: [] }
        }
        if (item.city) {
          cityGroups[item.city].data.push(item)
        }
      })
      metricData.value[`${metric}_structured`] = Object.values(cityGroups)
    }
  } catch (error) {
    console.error(`Error cargando datos de ${metric}:`, error)
  } finally {
    loadingMetrics.value.delete(metric)
  }
}

// Eliminar datos de una métrica específica
function removeMetricData(metric) {
  delete metricData.value[metric]
  delete metricData.value[`${metric}_structured`]
}

// Buscar datos de comparación (función original mantenida para compatibilidad - no usado)
// async function fetchCompareData() { ... }

// Función principal para cargar datos (nueva)
async function loadData() {
  await loadMetricData()
}

// Cargar datos automáticamente al montar el componente
onMounted(() => {
  loadData()
})


// Añadir ciudad desde el desplegable
function addCityFromDropdown(selectedCity) {
  if (!selectedCity || !selectedCity.trim()) return
  
  // Evitar duplicados
  if (!selectedCities.value.includes(selectedCity)) {
    selectedCities.value.push(selectedCity)
  }
  
  cityInput.value = '' // Limpiar el input
}

// Eliminar ciudad
function removeCity(index) {
  selectedCities.value.splice(index, 1)
}

// Alternar métrica con transición suave
async function toggleMetric(metricId) {
  const index = selectedMetrics.value.indexOf(metricId)
  if (index === -1) {
    // Añadir métrica
    selectedMetrics.value.push(metricId)
    // Cargar solo esta métrica sin afectar las demás
    await loadSingleMetric(metricId)
  } else {
    // Quitar métrica
    selectedMetrics.value.splice(index, 1)
    // Eliminar datos de esta métrica
    removeMetricData(metricId)
  }
}

// Manejar cambio de período
function handlePeriodChange(newPeriod) {
  if (newPeriod === 'custom') {
    showCustomDateRange.value = true
    // Inicializar fechas por defecto
    const today = new Date()
    const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
    customToDate.value = today.toISOString().split('T')[0]
    customFromDate.value = weekAgo.toISOString().split('T')[0]
  } else {
    showCustomDateRange.value = false
    days.value = newPeriod
    loadData()
  }
}

// Aplicar rango personalizado
function applyCustomDateRange() {
  if (customFromDate.value && customToDate.value) {
    // Validar que la fecha de inicio sea anterior a la fecha de fin
    if (new Date(customFromDate.value) > new Date(customToDate.value)) {
      alert('La fecha de inicio debe ser anterior a la fecha de fin')
      return
    }
    showCustomDateRange.value = false
    loadData()
  } else {
    alert('Por favor selecciona ambas fechas')
  }
}

// Toggle ciudad favorita
function toggleFavoriteCity(cityName) {
  const idx = selectedCities.value.indexOf(cityName)
  if (idx === -1) {
    selectedCities.value.push(cityName)
  } else {
    selectedCities.value.splice(idx, 1)
  }
}

// Calcular estadísticas (mantenido para compatibilidad - no usado)
// function calculateStats(cityName) { ... }

// Calcular promedio de una métrica para una ciudad específica
function getCityAverage(cityName, metric) {
  // Usar estructura almacenada para cálculos
  const structuredData = metricData.value[`${metric}_structured`]
  if (!structuredData || !Array.isArray(structuredData)) return 'N/A'
  
  const cityData = structuredData.find(city => city.city === cityName)
  if (!cityData || !cityData.data || cityData.data.length === 0) return 'N/A'
  
  const values = cityData.data.map(item => item.value).filter(v => !isNaN(v))
  if (values.length === 0) return 'N/A'
  
  const average = values.reduce((sum, val) => sum + val, 0) / values.length
  return average.toFixed(1)
}

// Exportar todos los datos de métricas habilitadas
async function exportAllMetricsData() {
  if (!selectedCities.value.length || !selectedMetrics.value.length) {
    alert('Selecciona ciudades y métricas')
    return
  }
  const params = {
    cities: selectedCities.value.join(','),
    metrics: selectedMetrics.value.join(','),
    unit: weather.unit || 'c'
  }
  if (days.value === 'custom') {
    params.from_date = `${customFromDate.value}T00:00:00`
    params.to_date = `${customToDate.value}T23:59:59`
  } else {
    params.days = days.value
  }
  const citiesStr = selectedCities.value.join('_')
  const metricsStr = selectedMetrics.value.join('_')
  const periodInfo = days.value === 'custom' ? `${customFromDate.value}_${customToDate.value}` : `${days.value}dias`
  const filename = `comparacion_general_${citiesStr}_${metricsStr}_${periodInfo}_${new Date().toISOString().split('T')[0]}.csv`
  const res = await api.get('/export/compare', { params: { ...params, filename }, responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([res.data]))
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

// Exportar resumen de ciudades
async function exportCitiesSummaryData() {
  if (!selectedCities.value.length || !selectedMetrics.value.length) {
    alert('Selecciona ciudades y métricas')
    return
  }
  const params = {
    cities: selectedCities.value.join(','),
    metrics: selectedMetrics.value.join(','),
    unit: weather.unit || 'c'
  }
  if (days.value === 'custom') {
    params.from_date = `${customFromDate.value}T00:00:00`
    params.to_date = `${customToDate.value}T23:59:59`
  } else {
    params.days = days.value
  }
  const citiesStr = selectedCities.value.join('_')
  const metricsStr = selectedMetrics.value.join('_')
  const periodInfo = days.value === 'custom' ? `${customFromDate.value}_${customToDate.value}` : `${days.value}dias`
  const filename = `resumen_ciudades_${citiesStr}_${metricsStr}_${periodInfo}_${new Date().toISOString().split('T')[0]}.csv`
  const res = await api.get('/export/compare-summary', { params: { ...params, filename }, responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([res.data]))
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}
</script>

<template>
  <section>
    <!-- Encabezado de página -->
    <div class="page-title">
      <div class="title-with-icon">
        <BarChart2 size="24" />
        <h1>Comparación de Ciudades</h1>
      </div>
      
      <ExportButton 
        v-if="Object.keys(weather.compareData?.data || {}).length"
        :city-ids="weather.compareData?.cities?.map(c => c.id) || []"
        :from="weather.compareData?.from_date"
        :to="weather.compareData?.to_date"
        :unit="weather.unit"
      />
    </div>
    
    <!-- Panel de selección de ciudades -->
    <div class="city-selection-panel card">
      <div class="panel-header">
        <h3>Seleccionar ciudades para comparar</h3>
      </div>
      
      <!-- Ciudades seleccionadas -->
      <div class="selected-cities">
        <div 
          v-for="(city, index) in selectedCities" 
          :key="index" 
          class="city-chip"
          :style="{ '--city-color': cityColors[index % cityColors.length] }"
        >
          <span class="city-chip-color"></span>
          <span>{{ city }}</span>
          <button class="remove-city" @click="removeCity(index)" title="Eliminar ciudad">
            <Trash2 size="14" />
          </button>
        </div>
        
        <!-- Añadir ciudad -->
        <div class="add-city">
          <CustomDropdown 
            v-model="cityInput" 
            :options="cityOptions"
            placeholder="Añadir ciudad..." 
            :icon="MapPin"
            @update:modelValue="addCityFromDropdown"
          />
        </div>
      </div>
      
      <!-- Favoritas -->
      <div class="favorites-section" v-if="cities.favorites.length">
        <h4>Ciudades favoritas</h4>
        <div class="favorite-chips">
          <button 
            v-for="favorite in cities.favorites" 
            :key="favorite.city_id"
            class="favorite-chip"
            :class="{ active: selectedCities.includes(favorite.city?.name) }"
            @click="toggleFavoriteCity(favorite.city?.name)"
          >
            <MapPin size="14" />
            <span>{{ favorite.city?.name }}</span>
          </button>
        </div>
      </div>
      
      <!-- Opciones de comparación -->
      <div class="compare-options">
        <div class="option-group">
          <label>Período</label>
          <CustomDropdown 
            v-model="days" 
            :options="periodOptions"
            :icon="Calendar"
            placeholder="Seleccionar período..."
            @update:modelValue="handlePeriodChange"
          />
        </div>
        
        <div class="option-group">
          <label>Métricas</label>
          <div class="metrics-selector">
            <button 
              v-for="metric in availableMetrics" 
              :key="metric.id"
              class="metric-chip"
              :class="{ active: selectedMetrics.includes(metric.id) }"
              @click="toggleMetric(metric.id)"
            >
              {{ metric.label }}
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Modal de rango personalizado -->
    <div v-if="showCustomDateRange" class="modal-overlay" @click="showCustomDateRange = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Seleccionar rango personalizado</h3>
          <button @click="showCustomDateRange = false" class="modal-close">×</button>
        </div>
        
        <div class="modal-body">
          <div class="date-inputs">
            <div class="date-input-group">
              <label>Fecha de inicio</label>
              <input 
                type="date" 
                v-model="customFromDate"
                class="date-input"
              />
            </div>
            
            <div class="date-input-group">
              <label>Fecha de fin</label>
              <input 
                type="date" 
                v-model="customToDate"
                class="date-input"
              />
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="showCustomDateRange = false" class="btn-secondary">
            Cancelar
          </button>
          <button @click="applyCustomDateRange" class="btn-primary">
            Aplicar
          </button>
        </div>
      </div>
    </div>
    
    <!-- Contenido principal -->
    <div class="compare-content">
      <!-- Estado de carga -->
      <div v-if="isLoading" class="loading-state">
        <Loader2 class="animate-spin" size="32" />
        <p>Cargando datos de comparación...</p>
      </div>
      
      <!-- Datos de comparación -->
      <template v-else-if="Object.keys(metricData).length > 0">
        <!-- Resumen -->
        <div class="compare-summary card">
          <div class="summary-header">
            <h2>Comparación de {{ selectedCities.length }} ciudades</h2>
            <div class="summary-actions">
              <div class="summary-info">
                <span>{{ selectedMetrics.length }} métrica{{ selectedMetrics.length !== 1 ? 's' : '' }} seleccionada{{ selectedMetrics.length !== 1 ? 's' : '' }}</span>
              </div>
              <button 
                class="btn btn-primary btn-sm"
                @click="exportAllMetricsData"
                title="Exportar todos los datos de comparación"
              >
                <Download size="16" />
                <span>Exportar</span>
              </button>
            </div>
          </div>
        </div>
        
        <!-- Gráficos por Métrica -->
        <div class="compare-metrics-container">
            <MetricChart 
              v-for="metric in selectedMetrics"
              :key="metric"
              :metric="metric"
              :data="metricData[metric] || []"
              :loading="loadingMetrics.has(metric)"
              :cities="selectedCities"
              :period="days === 'custom' ? 'personalizado' : `${days}dias`"
              :view-type="'compare'"
              class="metric-chart-item"
            />
        </div>
        
        <!-- Resumen de ciudades (mantenido para compatibilidad) -->
        <div class="cities-summary card">
          <div class="summary-header">
            <h3>Resumen por ciudad</h3>
            <button 
              class="btn btn-outline btn-sm"
              @click="exportCitiesSummaryData"
              title="Exportar resumen de ciudades"
            >
              <Download size="16" />
              <span>Exportar</span>
            </button>
          </div>
          
          <div class="cities-grid">
            <div 
              v-for="(cityName, index) in selectedCities" 
              :key="cityName" 
              class="city-summary-card"
              :style="{ '--city-color': cityColors[index % cityColors.length] }"
            >
              <div class="city-summary-header">
                <h4>{{ cityName }}</h4>
                <div class="city-color-indicator"></div>
              </div>
              
              <div class="city-stats">
                <!-- Mostrar solo estadísticas de métricas seleccionadas -->
                <div v-if="selectedMetrics.includes('temperature')" class="stat-row">
                  <div class="stat-label">Temperatura promedio:</div>
                  <div class="stat-value">
                    <TemperatureValue :value="getCityAverage(cityName, 'temperature')" :unit="weather.unit" />
                </div>
                </div>
                <div v-if="selectedMetrics.includes('humidity')" class="stat-row">
                  <div class="stat-label">Humedad promedio:</div>
                  <div class="stat-value">{{ getCityAverage(cityName, 'humidity') }}%</div>
                </div>
                <div v-if="selectedMetrics.includes('pressure')" class="stat-row">
                  <div class="stat-label">Presión promedio:</div>
                  <div class="stat-value">{{ getCityAverage(cityName, 'pressure') }} hPa</div>
              </div>
                <div v-if="selectedMetrics.includes('wind')" class="stat-row">
                  <div class="stat-label">Viento promedio:</div>
                  <div class="stat-value">{{ getCityAverage(cityName, 'wind') }} m/s</div>
            </div>
          </div>
        </div>
          </div>
        </div>
      </template>
      
      <!-- Estado vacío -->
      <div v-else class="empty-state card">
        <BarChart2 size="48" color="var(--color-text-secondary)" />
        <h3>Sin datos de comparación</h3>
        <p>Seleccione al menos dos ciudades y métricas para comparar sus datos meteorológicos.</p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.title-with-icon {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.city-selection-panel {
  margin-bottom: var(--space-xl);
}

.panel-header {
  margin-bottom: var(--space-md);
}

.panel-header h3 {
  margin: 0;
}

.selected-cities {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
  margin-bottom: var(--space-md);
}

.city-chip {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-full);
  background-color: #f5f7fa;
  border: 1px solid var(--color-border);
  font-size: 0.9rem;
  transition: background-color var(--transition-normal), color var(--transition-normal);
}

.dark-theme .city-chip {
  background-color: #181A1B;
  color: #fff;
  border-color: #333;
}

.city-chip-color {
  width: 12px;
  height: 12px;
  border-radius: var(--radius-full);
  background-color: var(--city-color);
  border: 2px solid transparent;
}

.dark-theme .city-chip-color {
  border: 2px solid #fff;
}

.remove-city {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
}

.remove-city:hover {
  color: var(--color-alert);
  background-color: rgba(229, 57, 53, 0.1);
}

.add-city {
  display: flex;
  gap: var(--space-xs);
}

.city-input {
  padding: var(--space-xs) var(--space-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  background-color: var(--color-card-bg);
  min-width: 150px;
}

.add-city-btn {
  padding: var(--space-xs);
  display: flex;
  align-items: center;
  justify-content: center;
}

.favorites-section {
  margin-bottom: var(--space-md);
}

.favorites-section h4 {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-xs);
  font-weight: 500;
}

.favorite-chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
}

.favorite-chip {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-full);
  background-color: var(--color-card-bg);
  border: 1px solid var(--color-border);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.dark-theme .favorite-chip {
  background-color: #181A1B;
  color: #fff;
  border-color: #333;
}

.favorite-chip.active {
  background-color: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.compare-options {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-md);
  margin-top: var(--space-md);
  padding-top: var(--space-md);
  border-top: 1px solid var(--color-border);
}

/* Contenedor de gráficos de comparación */
.compare-metrics-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: var(--space-lg);
  margin-top: var(--space-lg);
}

.metric-chart-item {
  background-color: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: box-shadow var(--transition-normal);
}

.metric-chart-item:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.dark-theme .metric-chart-item {
  background-color: #1a1a1a;
  border-color: #333;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.dark-theme .metric-chart-item:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
}

.option-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.option-group label {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.dark-theme .option-group label {
  color: #e1e1e1;
}

.select-wrapper {
  position: relative;
}

.select-icon {
  position: absolute;
  left: var(--space-sm);
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-secondary);
}

.filter-select {
  padding: var(--space-xs) var(--space-md);
  padding-left: calc(var(--space-sm) + 20px);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-card-bg);
  color: var(--color-text-primary);
  font-size: 0.9rem;
  appearance: none;
  cursor: pointer;
  transition: all var(--transition-fast);
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23546E7A' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right var(--space-sm) center;
  background-size: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.filter-select:hover {
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.filter-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.1);
}

.dark-theme .filter-select {
  background-color: #181A1B;
  color: #fff;
  border-color: #333;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.dark-theme .filter-select:hover {
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}

.dark-theme .filter-select:focus {
  box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.2);
}

.metrics-selector {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
}

.metric-chip {
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border);
  background-color: var(--color-card-bg);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.dark-theme .metric-chip {
  background-color: #181A1B;
  color: #fff;
  border-color: #333;
}

.metric-chip.active {
  background-color: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.compare-content {
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

.chart-header, .table-header, .summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

.summary-actions {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.chart-title, .table-header h3, .summary-header h3 {
  margin: 0;
  font-size: 1.1rem;
}

.btn-sm {
  padding: var(--space-xs) var(--space-sm);
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.cities-summary {
  margin-bottom: var(--space-lg);
}

.cities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: var(--space-md);
}

.city-summary-card {
  border-radius: var(--radius-md);
  padding: var(--space-md);
  background-color: #f8f9fa;
  border-left: 4px solid var(--city-color);
  transition: background-color var(--transition-normal), color var(--transition-normal);
}

.dark-theme .city-summary-card {
  background-color: #181A1B;
  color: #fff;
}

.city-summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-sm);
}

.city-summary-header h4 {
  margin: 0;
  font-size: 1rem;
}

.dark-theme .city-summary-header h4 {
  color: #fff;
}

.city-color-indicator {
  width: 12px;
  height: 12px;
  border-radius: var(--radius-full);
  background-color: var(--city-color);
  border: 2px solid transparent;
}

.dark-theme .city-color-indicator {
  border: 2px solid #fff;
}

.city-stats {
  display: grid;
  gap: var(--space-xs);
}

.stat-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
}

.stat-label {
  color: var(--color-text-secondary);
}

.dark-theme .stat-label {
  color: #e1e1e1;
}

.stat-value {
  font-weight: 500;
}

.dark-theme .stat-value {
  color: #fff;
}

.differences-table {
  margin-bottom: var(--space-lg);
}

.table-responsive {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th, .table td {
  padding: var(--space-sm) var(--space-md);
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.table th {
  background-color: rgba(0, 0, 0, 0.02);
  font-weight: 600;
  color: var(--color-text-primary);
}

.table td {
  color: var(--color-text-secondary);
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

/* NUEVOS ESTILOS PARA COMPARACIÓN POR MÉTRICA */
.compare-metrics-container {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
  margin-top: var(--space-lg);
}

.metric-comparison-item {
  width: 100%;
  min-height: 400px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  background-color: var(--color-card-bg);
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--color-border);
}

.metric-header h3 {
  margin: 0;
  color: var(--color-text-primary);
  font-size: 1.125rem;
  font-weight: 600;
}

.metric-actions {
  display: flex;
  gap: var(--space-sm);
}

.btn-export {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-sm);
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-export:hover {
  background-color: var(--color-primary-hover);
  transform: translateY(-1px);
}

/* DESKTOP: 2 columnas para comparaciones */
@media (min-width: 1200px) {
  .compare-metrics-container {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-lg);
  }
  
  .metric-comparison-item {
    min-height: 500px;
  }
}

/* TABLET Y MÓVIL: 1 columna */
@media (max-width: 1199px) {
  .compare-metrics-container {
    display: flex;
    flex-direction: column;
  }
  
  .metric-comparison-item {
    min-height: 400px;
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .compare-options {
    flex-direction: column;
  }
  
  .cities-grid {
    grid-template-columns: 1fr;
  }
  
  .compare-metrics-container {
    gap: var(--space-md);
  }
  
  .metric-comparison-item {
    min-height: 300px;
    padding: var(--space-md);
  }
}

/* Modal de rango personalizado */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: var(--color-card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-lg);
  border-bottom: 1px solid var(--color-border);
}

.modal-header h3 {
  margin: 0;
  color: var(--color-text-primary);
  font-size: 1.25rem;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: var(--space-xs);
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
}

.modal-close:hover {
  background-color: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.modal-body {
  padding: var(--space-lg);
}

.date-inputs {
  display: flex;
  gap: var(--space-md);
}

.date-input-group {
  flex: 1;
}

.date-input-group label {
  display: block;
  margin-bottom: var(--space-xs);
  color: var(--color-text-primary);
  font-weight: 500;
  font-size: 0.875rem;
}

.date-input {
  width: 100%;
  padding: var(--space-sm);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-card-bg);
  color: var(--color-text-primary);
  font-size: 0.875rem;
  transition: all 0.2s ease;
  cursor: pointer;
}

.date-input:hover {
  border-color: var(--color-primary);
  background-color: var(--color-bg-secondary);
}

.date-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.1);
}

/* Estilos específicos para modo oscuro */
.dark-theme .date-input {
  background-color: #181A1B;
  color: #fff;
  border-color: #333;
}

.dark-theme .date-input:hover {
  border-color: var(--color-primary);
  background-color: #1f2122;
}

.dark-theme .date-input:focus {
  box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.2);
}

/* Mejorar visibilidad del icono de calendario en modo oscuro */
.dark-theme .date-input::-webkit-calendar-picker-indicator {
  filter: invert(1);
  opacity: 0.8;
}

.date-input::-webkit-calendar-picker-indicator {
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.date-input::-webkit-calendar-picker-indicator:hover {
  opacity: 1;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-sm);
  padding: var(--space-lg);
  border-top: 1px solid var(--color-border);
}

.btn-secondary {
  padding: var(--space-sm) var(--space-md);
  background-color: transparent;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background-color: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.btn-primary {
  padding: var(--space-sm) var(--space-md);
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background-color: var(--color-primary-hover);
}

@media (max-width: 768px) {
  .date-inputs {
    flex-direction: column;
  }
  
  .modal-content {
    width: 95%;
    margin: var(--space-md);
  }
}
</style>
