<script setup>
import TemperatureValue from '@/components/TemperatureValue.vue'
import MetricChart from '@/components/MetricChart.vue'
import { ref, computed, onMounted, watch } from 'vue'
import { useWeatherStore } from '@/stores/weather'
import { useCitiesStore } from '@/stores/cities'
import { METRIC_CONFIGS } from '@/stores/metrics'
import { api } from '@/services/api'
import CustomDropdown from '@/components/CustomDropdown.vue'
import { Calendar, Loader2, History, Filter, MapPin, Download } from 'lucide-vue-next'

const weather = useWeatherStore()
const cities = useCitiesStore()
const city = ref('Madrid')
const days = ref(7)
const isLoading = ref(false)
const loadingMetrics = ref(new Set())
const showDatePicker = ref(false)
const customStartDate = ref('')
const customEndDate = ref('')
const selectedMetrics = ref(['temperature'])
const metricData = ref({})
const actualDateRange = ref({ from: '', to: '' })

// Variables para filtros de la tabla
const showFilters = ref(false)
const tableFilters = ref({
  dateRange: 'all',
  metric: 'all'
})
const tableSortBy = ref('timestamp')
const tableSortOrder = ref('desc')

const tableFilterCustomStart = ref('')
const tableFilterCustomEnd = ref('')

// Configuración de métricas desde el store
const availableMetrics = computed(() => {
  return Object.values(METRIC_CONFIGS).map(config => ({
    id: config.key,
    label: config.title,
    color: config.color,
    icon: config.icon
  }))
})

// Formatear fecha para input date
const today = new Date()
const todayFormatted = today.toISOString().split('T')[0]
const defaultStartDate = new Date(today)
defaultStartDate.setDate(today.getDate() - 7)
const defaultStartFormatted = defaultStartDate.toISOString().split('T')[0]

// Inicializar fechas
customStartDate.value = defaultStartFormatted
customEndDate.value = todayFormatted

// Cargar favoritos al iniciar
onMounted(async () => {
  await Promise.all([
    cities.fetchFavorites(),
    cities.fetchCities({ limit: 500 }) // Cargar todas las ciudades disponibles
  ])
  await fetchData()
})

// Observar cambios en la selección de días para actualizar fechas personalizadas
watch(days, (newValue) => {
  if (newValue !== 'custom') {
    const end = new Date()
    const start = new Date()
    start.setDate(end.getDate() - parseInt(newValue))
    
    customStartDate.value = start.toISOString().split('T')[0]
    customEndDate.value = end.toISOString().split('T')[0]
    showDatePicker.value = false
  } else {
    showDatePicker.value = true
  }
})

// Función para cargar datos por métrica
async function fetchMetricData(metric) {
  try {
    console.log(`🔍 [HISTORY] Iniciando carga de ${metric} para ${city.value}...`)
    
    // Construir URL según si es rango personalizado o días predefinidos
    let url = `/weather/history/${metric}?city=${city.value}`
    if (days.value === 'custom') {
      // Convertir fechas a formato ISO datetime
      const fromDateTime = `${customStartDate.value}T00:00:00`
      const toDateTime = `${customEndDate.value}T23:59:59`
      url += `&from_date=${fromDateTime}&to_date=${toDateTime}`
    } else {
      url += `&days=${days.value}`
    }
    console.log(`📡 [HISTORY] URL: ${url}`)
    
    const response = await api.get(url)
    console.log(`📊 [HISTORY] Response status: ${response.status}`)
    
    const data = response.data
    console.log(`✅ [HISTORY] Datos recibidos para ${metric}:`, data)
    console.log(`📈 [HISTORY] Cantidad de registros:`, data.data?.length || 0)
    
    if (!data.data || !Array.isArray(data.data)) {
      console.warn(`⚠️ [HISTORY] No hay datos en la respuesta para ${metric}`)
      return []
    }
    
    console.log(`🎯 [HISTORY] Datos procesados para ${metric}:`, data.data.length, 'registros')
    
    if (data.from_date && data.to_date) {
      const fromDate = new Date(data.from_date).toISOString().split('T')[0]
      const toDate = new Date(data.to_date).toISOString().split('T')[0]
      actualDateRange.value = { from: fromDate, to: toDate }
      console.log(`📅 [HISTORY] Rango real actualizado: ${fromDate} - ${toDate}`)
      // Inicializar límites por defecto del rango personalizado del filtro hijo
      if (!tableFilterCustomStart.value) tableFilterCustomStart.value = fromDate
      if (!tableFilterCustomEnd.value) tableFilterCustomEnd.value = toDate
    }
    
    return data.data
  } catch (error) {
    console.error(`❌ [HISTORY] Error cargando datos de ${metric}:`, error)
    return []
  }
}

// Cargar datos para todas las métricas seleccionadas
async function loadMetricData() {
  isLoading.value = true
  metricData.value = {}
  // Limpiar rango real al iniciar nueva carga
  actualDateRange.value = { from: '', to: '' }
  
  try {
    const promises = selectedMetrics.value.map(async (metric) => {
      const data = await fetchMetricData(metric)
      metricData.value[metric] = data
    })
    
    await Promise.all(promises)
  } catch (error) {
    console.error('Error cargando datos de métricas:', error)
  } finally {
    isLoading.value = false
  }
}

// Cargar datos para una métrica específica
async function loadSingleMetric(metric) {
  loadingMetrics.value.add(metric)
  
  try {
    const data = await fetchMetricData(metric)
    metricData.value[metric] = data
  } catch (error) {
    console.error(`Error cargando datos de ${metric}:`, error)
  } finally {
    loadingMetrics.value.delete(metric)
  }
}

// Eliminar datos de una métrica específica
function removeMetricData(metric) {
  delete metricData.value[metric]
}

// Opciones para los desplegables - usar store de cities
const cityOptions = computed(() => {
  console.log('[HistoryView] Generando cityOptions...')
  console.log('[HistoryView] Favoritas:', cities.favorites.length)
  console.log('[HistoryView] Lista general:', cities.list.length)
  
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
  console.log('[HistoryView] Opciones generadas:', sorted.length, 'ciudades')
  return sorted
})

const periodOptions = [
  { value: 3, label: 'Últimos 3 días' },
  { value: 7, label: 'Últimos 7 días' },
  { value: 14, label: 'Últimos 14 días' },
  { value: 30, label: 'Últimos 30 días' },
  { value: 'custom', label: 'Rango personalizado' }
]

// Fecha de inicio y fin para mostrar (basado en datos reales cargados)
const dateRangeText = computed(() => {
  if (actualDateRange.value.from && actualDateRange.value.to) {
    return `${formatDate(actualDateRange.value.from)} - ${formatDate(actualDateRange.value.to)}`
  } else if (days.value === 'custom') {
    return `${formatDate(customStartDate.value)} - ${formatDate(customEndDate.value)}`
  } else {
    return `Últimos ${days.value} días`
  }
})

// Formatear fecha para mostrar
function formatDate(dateStr) {
  if (!dateStr) return 'Fecha no disponible'
  
  // Usar formato YYYY-MM-DD directamente para evitar problemas de zona horaria
  const [year, month, day] = dateStr.split('-')
  if (!year || !month || !day) return 'Fecha no disponible'
  
  const date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day))
  if (isNaN(date.getTime())) return 'Fecha no disponible'
  
  return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
}

// Formatear fecha para tabla
function formatTableDate(dateValue) {
  if (!dateValue) return `Sin fecha`
  
  const date = new Date(dateValue)
  if (isNaN(date.getTime())) return `Fecha inválida`
  
  return date.toLocaleDateString('es-ES', { 
    day: 'numeric', 
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}


// Buscar datos históricos (función original mantenida para compatibilidad)
async function fetchData() {
  isLoading.value = true
  
  try {
    if (days.value === 'custom') {
      await weather.fetchHistory({ 
        city: city.value, 
        from: customStartDate.value, 
        to: customEndDate.value 
      })
    } else {
      await weather.fetchHistory({ 
        city: city.value, 
        days: parseInt(days.value) 
      })
    }
  } finally {
    isLoading.value = false
  }
}
async function loadData() {
  await loadMetricData()
}

// Cargar datos automáticamente al montar el componente
onMounted(() => {
  loadData()
})

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

// Función para obtener datos filtrados de la tabla
function getFilteredTableData() {
  if (!selectedMetrics.value.length || !metricData.value[selectedMetrics.value[0]]) {
    return []
  }
  
  let data = [...metricData.value[selectedMetrics.value[0]]]
  
  // Filtrar por rango de fechas
  if (tableFilters.value.dateRange !== 'all') {
    const parentFrom = days.value === 'custom'
      ? new Date(`${customStartDate.value}T00:00:00`)
      : new Date(new Date().setDate(new Date().getDate() - parseInt(days.value)))
    const parentTo = days.value === 'custom'
      ? new Date(`${customEndDate.value}T23:59:59`)
      : new Date()

    const clampStart = (d) => (d < parentFrom ? parentFrom : d)
    const clampEnd = (d) => (d > parentTo ? parentTo : d)

    let rangeStart = new Date(parentFrom)
    let rangeEnd = new Date(parentTo)

    switch (tableFilters.value.dateRange) {
      case 'today': {
        const todayStart = new Date()
        todayStart.setHours(0, 0, 0, 0)
        rangeStart = clampStart(todayStart)
        rangeEnd = parentTo
        break
      }
      case 'week': {
        const start = new Date(parentTo)
        start.setDate(start.getDate() - 7)
        rangeStart = clampStart(start)
        rangeEnd = parentTo
        break
      }
      case '14days': {
        const start = new Date(parentTo)
        start.setDate(start.getDate() - 14)
        rangeStart = clampStart(start)
        rangeEnd = parentTo
        break
      }
      case 'month': {
        const start = new Date(parentTo)
        start.setMonth(start.getMonth() - 1)
        rangeStart = clampStart(start)
        rangeEnd = parentTo
        break
      }
      case 'custom': {
        const start = new Date(`${tableFilterCustomStart.value || actualDateRange.value.from}T00:00:00`)
        const end = new Date(`${tableFilterCustomEnd.value || actualDateRange.value.to}T23:59:59`)
        rangeStart = clampStart(start)
        rangeEnd = clampEnd(end)
        break
      }
    }

    data = data.filter(item => {
      const itemDate = new Date(item.timestamp || item.ts)
      return itemDate >= rangeStart && itemDate <= rangeEnd
    })
  }
  
  // Filtrar por métrica (si hay múltiples métricas seleccionadas)
  if (tableFilters.value.metric !== 'all' && selectedMetrics.value.length > 1) {
    // Si hay filtro de métrica específica, mostrar solo esa métrica
    data = metricData.value[tableFilters.value.metric] || []
  }
  
  // Ordenar
  data.sort((a, b) => {
    let aValue, bValue
    
    switch (tableSortBy.value) {
      case 'timestamp':
        aValue = new Date(a.timestamp || a.ts)
        bValue = new Date(b.timestamp || b.ts)
        break
      case 'temperature':
        aValue = a.temp_c || a.temperature || 0
        bValue = b.temp_c || b.temperature || 0
        break
      case 'humidity':
        aValue = a.humidity || 0
        bValue = b.humidity || 0
        break
      case 'pressure':
        aValue = a.pressure || 0
        bValue = b.pressure || 0
        break
      case 'wind':
        aValue = a.wind_speed || 0
        bValue = b.wind_speed || 0
        break
      default:
        return 0
    }
    
    if (tableSortOrder.value === 'asc') {
      return aValue > bValue ? 1 : -1
    } else {
      return aValue < bValue ? 1 : -1
    }
  })
  
  return data
}

// Función para alternar filtros
function toggleFilters() {
  showFilters.value = !showFilters.value
}

// Función para limpiar filtros
function clearFilters() {
  tableFilters.value = {
    dateRange: 'all',
    metric: 'all'
  }
  tableSortBy.value = 'timestamp'
  tableSortOrder.value = 'desc'
}

// Función para exportar todos los datos de métricas habilitadas
async function exportAllMetricsData() {
  if (!selectedMetrics.value.length) {
    alert('No hay métricas seleccionadas')
    return
  }
  const metricsStr = selectedMetrics.value.join(',')
  const params = {
    city: city.value,
    metrics: metricsStr,
    unit: weather.unit || 'c'
  }
  if (days.value === 'custom') {
    params.from_date = `${customStartDate.value}T00:00:00`
    params.to_date = `${customEndDate.value}T23:59:59`
  } else {
    params.days = days.value
  }
  const filename = (() => {
    const metricsSlug = selectedMetrics.value.join('_')
    const periodInfo = days.value === 'custom' ? `${customStartDate.value}_${customEndDate.value}` : `${days.value}dias`
    return `historial_general_${city.value}_${metricsSlug}_${periodInfo}_${new Date().toISOString().split('T')[0]}.csv`
  })()
  const res = await api.get('/export/history', { params: { ...params, mode: 'standard', filename }, responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([res.data]))
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

// Función para exportar datos de la tabla
async function exportTableData() {
  // Para alinear con el backend, exportamos "detallado" desde API para toda la ventana padre
  const metricsStr = selectedMetrics.value.join(',')
  const params = {
    city: city.value,
    metrics: metricsStr,
    unit: weather.unit || 'c',
    mode: 'detailed'
  }
  if (days.value === 'custom') {
    params.from_date = `${customStartDate.value}T00:00:00`
    params.to_date = `${customEndDate.value}T23:59:59`
  } else {
    params.days = days.value
  }
  const sortInfo = tableSortBy.value === 'timestamp' ? 'fecha' : tableSortBy.value
  const orderInfo = tableSortOrder.value === 'asc' ? 'asc' : 'desc'
  const periodInfo = days.value === 'custom' ? `${customStartDate.value}_${customEndDate.value}` : `${days.value}dias`
  const filename = `datos_historial_${city.value}_${periodInfo}_${sortInfo}_${orderInfo}_${new Date().toISOString().split('T')[0]}.csv`
  const res = await api.get('/export/history', { params: { ...params, filename }, responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([res.data]))
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

// Computed para opciones de período dependientes
const availablePeriodOptions = computed(() => {
  const opts = [
    { value: 'all', label: 'Todos' },
    { value: 'today', label: 'Hoy' }
  ]

  const pushIf = (cond, opt) => { if (cond) opts.push(opt) }

  if (days.value === 'custom') {
    // Calcular días de diferencia entre fechas padre
    const start = new Date(`${customStartDate.value}T00:00:00`)
    const end = new Date(`${customEndDate.value}T23:59:59`)
    const diffDays = Math.max(1, Math.ceil((end - start) / (1000 * 60 * 60 * 24)))
    pushIf(diffDays >= 7, { value: 'week', label: 'Última semana' })
    pushIf(diffDays >= 14, { value: '14days', label: 'Últimos 14 días' })
    pushIf(diffDays >= 30, { value: 'month', label: 'Último mes' })
    // Siempre permitir rango personalizado dentro del padre
    opts.push({ value: 'custom', label: 'Rango personalizado' })
    return opts
  }

  const selectedDays = parseInt(days.value)
  pushIf(selectedDays >= 7, { value: 'week', label: 'Última semana' })
  pushIf(selectedDays >= 14, { value: '14days', label: 'Últimos 14 días' })
  pushIf(selectedDays >= 30, { value: 'month', label: 'Último mes' })
  // Siempre permitir rango personalizado dentro del padre
  opts.push({ value: 'custom', label: 'Rango personalizado' })
  return opts
})

// Computed para opciones de ordenamiento dinámicas según métricas activas
const availableSortOptions = computed(() => {
  const options = [
    { value: 'timestamp', label: 'Fecha' }
  ]
  if (selectedMetrics.value.includes('temperature')) options.push({ value: 'temperature', label: 'Temperatura' })
  if (selectedMetrics.value.includes('humidity')) options.push({ value: 'humidity', label: 'Humedad' })
  if (selectedMetrics.value.includes('pressure')) options.push({ value: 'pressure', label: 'Presión' })
  if (selectedMetrics.value.includes('wind')) options.push({ value: 'wind', label: 'Viento' })
  return options
})

// Mantener tableSortBy coherente con métricas activas
watch([selectedMetrics, tableSortBy], () => {
  const exists = availableSortOptions.value.some(o => o.value === tableSortBy.value)
  if (!exists) tableSortBy.value = 'timestamp'
})
</script>

<template>
  <section>
    <!-- Encabezado de página -->
    <div class="page-title">
      <div class="title-with-icon">
        <History size="24" />
        <h1>Historial Meteorológico</h1>
      </div>
      
      <button 
        v-if="Object.keys(metricData).length > 0"
        class="btn btn-primary btn-sm"
        @click="exportAllMetricsData"
        title="Exportar todos los datos históricos"
      >
        <Download size="16" />
        <span>Exportar</span>
      </button>
    </div>
    
    <!-- Filtros -->
    <div class="filters-panel card">
      <div class="filters-grid">
        <!-- Selector de ciudad -->
        <div class="filter-group">
          <label>Ciudad</label>
          <CustomDropdown 
            v-model="city" 
            :options="cityOptions"
            :icon="MapPin"
            placeholder="Seleccionar ciudad..."
          />
        </div>
        
        <!-- Selector de período -->
        <div class="filter-group">
          <label>Período</label>
          <CustomDropdown 
            v-model="days" 
            :options="periodOptions"
            :icon="Calendar"
            placeholder="Seleccionar período..."
          />
        </div>
        
        <!-- Selector de métricas -->
        <div class="filter-group">
          <label>Métricas</label>
          <div class="metrics-selector">
            <button 
              v-for="metric in availableMetrics" 
              :key="metric.id"
              class="metric-chip"
              :class="{ active: selectedMetrics.includes(metric.id) }"
              @click="toggleMetric(metric.id)"
              :style="{ '--metric-color': metric.color }"
            >
              {{ metric.label }}
            </button>
          </div>
        </div>
        
        <!-- Botón de búsqueda -->
        <div class="filter-group filter-actions">
          <button @click="loadData" class="btn btn-primary" :disabled="isLoading">
            <span v-if="isLoading">
              <Loader2 class="animate-spin" size="16" />
              Cargando...
            </span>
            <span v-else>Buscar</span>
          </button>
        </div>
      </div>
      
      <!-- Selector de fecha personalizado -->
      <div v-if="days === 'custom'" class="date-range-picker">
        <div class="date-inputs">
          <div class="filter-group">
            <label for="start-date">Fecha inicio</label>
            <input 
              type="date" 
              id="start-date" 
              v-model="customStartDate" 
              class="date-input"
              :max="customEndDate"
            />
          </div>
          <div class="filter-group">
            <label for="end-date">Fecha fin</label>
            <input 
              type="date" 
              id="end-date" 
              v-model="customEndDate" 
              class="date-input"
              :min="customStartDate"
              :max="todayFormatted"
            />
          </div>
        </div>
      </div>
    </div>
    
    <!-- Contenido principal -->
    <div class="history-content">
      <!-- Estado de carga -->
      <div v-if="isLoading" class="loading-state">
        <Loader2 class="animate-spin" size="32" />
        <p>Cargando datos históricos...</p>
      </div>
      
      <!-- Datos históricos -->
      <template v-else-if="Object.keys(metricData).length > 0">
        <!-- Resumen -->
        <div class="history-summary card">
          <div class="summary-header">
            <h2>{{ city }}</h2>
            <div class="date-range">
              <Calendar size="16" />
              <span>{{ dateRangeText }}</span>
            </div>
          </div>
          
          <!-- Estadísticas rápidas -->
          <div class="quick-stats">
            <div class="stat-item">
              <div class="stat-label">Métricas seleccionadas</div>
              <div class="stat-value">
                {{ selectedMetrics.length }} métrica{{ selectedMetrics.length !== 1 ? 's' : '' }}
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-label">Período</div>
              <div class="stat-value">
                {{ days === 'custom' ? 'Personalizado' : `${days} días` }}
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-label">Datos disponibles</div>
              <div class="stat-value">
                {{ Object.values(metricData).reduce((sum, data) => sum + data.length, 0) }} registros
              </div>
            </div>
          </div>
        </div>
        
        <div class="metrics-container">
          <MetricChart 
            v-for="metric in selectedMetrics"
            :key="metric"
            :metric="metric"
            :data="metricData[metric] || []"
            :loading="loadingMetrics.has(metric)"
            :cities="[city]"
            :period="days === 'custom' ? 'personalizado' : `${days}dias`"
            :view-type="'history'"
            class="metric-chart-item"
          />
        </div>
        

        <div class="data-table card">
          <div class="table-header">
            <h3>Datos detallados</h3>
            <div class="table-actions">
              <button 
                class="btn btn-outline btn-sm"
                @click="exportTableData"
                title="Exportar datos de la tabla"
              >
                <Download size="16" />
                <span>Exportar</span>
              </button>
              <button 
                class="btn btn-outline btn-sm"
                @click="toggleFilters"
                :class="{ 'active': showFilters }"
              >
                <Filter size="16" />
                <span>{{ showFilters ? 'Ocultar filtros' : 'Filtrar' }}</span>
              </button>
            </div>
          </div>
          
          <!-- Panel de filtros -->
          <Transition name="filters-slide">
            <div v-if="showFilters" class="table-filters">
            <div class="filters-container">
              <div class="filters-row">
                <!-- Sección: Ordenar por -->
                <div class="filter-section">
                  <h4>Ordenar por:</h4>
                  <div class="sort-controls">
                    <CustomDropdown
                      v-model="tableSortBy"
                      :options="availableSortOptions"
                      placeholder="Ordenar por..."
                    />
                    <button 
                      @click="tableSortOrder = tableSortOrder === 'asc' ? 'desc' : 'asc'"
                      class="sort-order-btn"
                      :title="tableSortOrder === 'asc' ? 'Ascendente' : 'Descendente'"
                    >
                      {{ tableSortOrder === 'asc' ? '↑' : '↓' }}
                    </button>
                  </div>
                </div>
                
                <!-- Sección: Filtrar por -->
                <div class="filter-section">
                  <h4>Filtrar por período:</h4>
                  <div class="filter-controls">
                    <CustomDropdown
                      v-model="tableFilters.dateRange"
                      :options="availablePeriodOptions"
                      placeholder="Período..."
                    />
                    <div v-if="tableFilters.dateRange === 'custom'" class="filter-custom-range">
                      <div class="filter-group">
                        <label>Desde</label>
                        <input type="date" class="date-input"
                          v-model="tableFilterCustomStart"
                          :min="actualDateRange.from || customStartDate"
                          :max="tableFilterCustomEnd || actualDateRange.to || customEndDate"
                        />
                      </div>
                      <div class="filter-group">
                        <label>Hasta</label>
                        <input type="date" class="date-input"
                          v-model="tableFilterCustomEnd"
                          :min="tableFilterCustomStart || actualDateRange.from || customStartDate"
                          :max="actualDateRange.to || customEndDate || todayFormatted"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Acciones -->
              <div class="filter-actions">
                <button @click="clearFilters" class="btn btn-outline btn-sm">
                  Limpiar filtros
                </button>
              </div>
            </div>
            </div>
          </Transition>
          
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th v-if="selectedMetrics.includes('temperature')">Temperatura</th>
                  <th v-if="selectedMetrics.includes('humidity')">Humedad</th>
                  <th v-if="selectedMetrics.includes('pressure')">Presión</th>
                  <th v-if="selectedMetrics.includes('wind')">Viento</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(d, i) in getFilteredTableData()" :key="i">
                  <td>{{ formatTableDate(d.timestamp || d.ts) }}</td>
                  <td v-if="selectedMetrics.includes('temperature')">
                    <TemperatureValue :value="d.temp_c || d.temperature" :unit="weather.unit" />
                  </td>
                  <td v-if="selectedMetrics.includes('humidity')">{{ d.humidity }}%</td>
                  <td v-if="selectedMetrics.includes('pressure')">{{ d.pressure }} hPa</td>
                  <td v-if="selectedMetrics.includes('wind')">{{ d.wind_speed }} m/s</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>
      
      <!-- Estado vacío -->
      <div v-else class="empty-state card">
        <History size="48" color="var(--color-text-secondary)" />
        <h3>Sin datos históricos</h3>
        <p>No hay datos históricos disponibles para {{ city }}. Intenta con otra ciudad o un rango de fechas diferente.</p>
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

.filters-panel {
  margin-bottom: var(--space-xl);
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-md);
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.filter-group label {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  font-weight: 500;
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
  width: 100%;
  padding: var(--space-sm) var(--space-md);
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
  color: var(--color-text-primary);
}

.dark-theme .metric-chip {
  background-color: #181A1B;
  color: #fff;
  border-color: #333;
}

.metric-chip.active {
  background-color: var(--metric-color);
  color: white;
  border-color: var(--metric-color);
}

.filter-actions {
  display: flex;
  justify-content: flex-end;
}

.date-range-picker {
  margin-top: var(--space-md);
  padding-top: var(--space-md);
  border-top: 1px solid var(--color-border);
}

.date-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-md);
}

.date-input {
  width: 100%;
  padding: var(--space-sm) var(--space-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-card-bg);
  color: var(--color-text-primary);
  font-size: 0.9rem;
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.date-input:hover {
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.date-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.1);
}

.dark-theme .date-input {
  background-color: #181A1B;
  color: #fff;
  border-color: #333;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.dark-theme .date-input:hover {
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
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

.history-content {
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

.history-summary {
  margin-bottom: var(--space-lg);
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

.date-range {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

.quick-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--space-md);
}

.stat-item {
  background-color: rgba(0, 0, 0, 0.02);
  padding: var(--space-md);
  border-radius: var(--radius-md);
}

.stat-label {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-xs);
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.chart-header, .table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

.table-actions {
  display: flex;
  gap: var(--space-sm);
  align-items: center;
}

.table-actions .btn.active {
  background-color: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.table-filters {
  background: linear-gradient(135deg, var(--color-bg-secondary) 0%, var(--color-bg) 100%);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: var(--space-md);
  margin-bottom: var(--space-md);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.filters-container {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.filters-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-lg);
}

.filter-section {
  background: linear-gradient(135deg, var(--color-bg-secondary) 0%, var(--color-bg) 100%);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: var(--space-md);
}

.filter-section h4 {
  margin: 0 0 var(--space-sm) 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-text);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.sort-controls .filter-select {
  flex: 1;
}

.filter-controls {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.filter-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: var(--space-sm);
  border-top: 1px solid var(--color-border);
}

.table-filters .filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.table-filters .filter-group label {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.table-filters .filter-select {
  width: 100%;
  padding: var(--space-xs) var(--space-sm);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background-color: var(--color-card-bg);
  color: var(--color-text-primary);
  font-size: 0.9rem;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.table-filters .filter-select:hover {
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.table-filters .filter-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(30, 136, 229, 0.1);
}

.sort-order-btn {
  padding: var(--space-xs) var(--space-sm);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background-color: var(--color-card-bg);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-weight: 600;
  min-width: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sort-order-btn:hover {
  border-color: var(--color-primary);
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.sort-order-btn:active {
  transform: translateY(0);
}

/* Animaciones para filtros */
.filters-slide-enter-active,
.filters-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform-origin: top;
}

.filters-slide-enter-from {
  opacity: 0;
  transform: translateY(-10px) scaleY(0.95);
}

.filters-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px) scaleY(0.95);
}

/* Rango personalizado dentro del filtro: disposición lado a lado */
.filter-custom-range {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-md);
  margin-top: var(--space-sm);
}

@media (max-width: 768px) {
  .filter-custom-range {
    grid-template-columns: 1fr;
  }
}

/* Mejorar estilos de desplegables */
.table-filters .filter-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23546E7A' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 16px;
  padding-right: 32px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.table-filters .filter-select:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.table-filters .filter-select:focus {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.table-filters .filter-select option {
  background-color: var(--color-bg);
  color: var(--color-text);
  padding: 8px 12px;
  border: none;
  transition: all 0.2s ease;
}

.table-filters .filter-select option:checked {
  background-color: var(--color-primary);
  color: white;
}

.table-filters .filter-select option:hover {
  background-color: var(--color-bg-secondary);
  color: var(--color-primary);
}


/* Modo oscuro para filtros de tabla */
.dark-theme .table-filters {
  background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%);
  border-color: #404040;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.dark-theme .table-filters .filter-select {
  background-color: #2a2a2a;
  color: #ffffff;
  border-color: #404040;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
}

.dark-theme .table-filters .filter-select:hover {
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}

.dark-theme .table-filters .filter-select:focus {
  box-shadow: 0 0 0 2px rgba(30, 136, 229, 0.2);
}

.dark-theme .table-filters .filter-select option {
  background-color: #2a2a2a;
  color: #ffffff;
}

.dark-theme .table-filters .filter-select option:checked {
  background-color: var(--color-primary);
  color: white;
}

.dark-theme .sort-order-btn {
  background-color: #2a2a2a;
  color: #ffffff;
  border-color: #404040;
}

.dark-theme .sort-order-btn:hover {
  border-color: var(--color-primary);
  background-color: rgba(var(--color-primary-rgb), 0.1);
  color: var(--color-primary);
}

/* Modo oscuro para nuevas secciones */
.dark-theme .filter-section {
  background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%);
  border-color: #404040;
}

.dark-theme .filter-section h4 {
  color: #ffffff;
}

.dark-theme .filter-actions {
  border-color: #404040;
}

/* Responsive para filtros */
@media (max-width: 768px) {
  .filters-row {
    grid-template-columns: 1fr;
    gap: var(--space-md);
  }
}


.chart-title, .table-header h3 {
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

/* NUEVOS ESTILOS PARA GRÁFICOS POR MÉTRICA */
.metrics-container {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
  margin-top: var(--space-lg);
}

.metric-chart-item {
  width: 100%;
  min-height: 400px;
}

@media (min-width: 1200px) {
  .metrics-container {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-lg);
  }
  
  .metric-chart-item {
    min-height: 500px;
  }
}

/* TABLET: 1 columna */
@media (max-width: 1199px) {
  .metrics-container {
    display: flex;
    flex-direction: column;
  }
  
  .metric-chart-item {
    min-height: 400px;
  }
}

@media (max-width: 768px) {
  .filters-grid {
    grid-template-columns: 1fr;
  }
  
  .date-inputs {
    grid-template-columns: 1fr;
  }
  
  .quick-stats {
    grid-template-columns: 1fr;
  }
  
  .metrics-container {
    gap: var(--space-md);
  }
  
  .metric-chart-item {
    min-height: 300px;
  }
}
</style>
