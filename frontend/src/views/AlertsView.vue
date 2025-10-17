<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAlertsStore } from '@/stores/alerts'
import { useCitiesStore } from '@/stores/cities'
import { Bell, BellOff, AlertTriangle, Trash2, Clock, X, Loader2, Plus, Info, Thermometer, Droplets, Wind, Gauge, Calendar, Download } from 'lucide-vue-next'
import CustomDropdown from '@/components/CustomDropdown.vue'
import BeautifulDropdown from '@/components/BeautifulDropdown.vue'

const alerts = useAlertsStore()
const cities = useCitiesStore()

// Estado del formulario
const selectedCity = ref('')
const metric = ref('temp')
const operator = ref('>')
const threshold = ref('35')
const unit = ref('c')
const showForm = ref(false)
const isLoading = ref(false)
const formError = ref('')
const showHistory = ref(false)

// Variables para selección múltiple y filtros
const selectedAlerts = ref(new Set())
const selectedHistoryItems = ref(new Set())
const showBulkActions = ref(false)
const showHistoryBulkActions = ref(false)

// Filtros para gestión de alertas
const alertFilters = ref({
  status: 'all', // all, active, paused
  metric: 'all', // all, temp, humidity, wind, pressure
  city: 'all' // all, specific city
})

// Filtros para historial
const historyFilters = ref({
  dateRange: 'all', // all, today, week, month
  metric: 'all',
  city: 'all'
})


// Ordenamiento
const alertSortBy = ref('created_at') // created_at, metric, city, status
const alertSortOrder = ref('desc') // asc, desc
const historySortBy = ref('ts') // ts, metric, city, observed_value
const historySortOrder = ref('desc')

// Métricas disponibles
const availableMetrics = [
  { id: 'temp', label: 'Temperatura', icon: 'thermometer', color: '#FFA000' },
  { id: 'humidity', label: 'Humedad', icon: 'droplet', color: '#1E88E5' },
  { id: 'wind', label: 'Viento', icon: 'wind', color: '#7E57C2' },
  { id: 'pressure', label: 'Presión', icon: 'gauge', color: '#26A69A' }
]

// Valores por defecto dinámicos para umbrales según métrica
const defaultThresholds = {
  temp: '35',
  humidity: '70', 
  wind: '10',
  pressure: '1013'
}

// Operadores disponibles
const availableOperators = [
  { id: '>', label: 'Mayor que', symbol: '>' },
  { id: '<', label: 'Menor que', symbol: '<' },
  { id: '>=', label: 'Mayor o igual', symbol: '≥' },
  { id: '<=', label: 'Menor o igual', symbol: '≤' }
]

// Unidades disponibles
const availableUnits = [
  { id: 'c', label: 'Celsius', symbol: '°C' },
  { id: 'f', label: 'Fahrenheit', symbol: '°F' },
  { id: 'k', label: 'Kelvin', symbol: 'K' }
]

// Watcher para cambiar umbral cuando cambie la métrica
watch(metric, (newMetric) => {
  threshold.value = defaultThresholds[newMetric]
})

// Cargar datos iniciales
onMounted(async () => {
  isLoading.value = true
  try {
    await Promise.all([
      alerts.fetchAlerts(false), // Cargar TODAS las alertas (activas y pausadas)
      cities.fetchFavorites(),
      cities.fetchCities({ limit: 500 }) // Cargar todas las ciudades disponibles
    ])
  } finally {
    isLoading.value = false
  }
})

// Lista de ciudades para el selector (todas las ciudades disponibles)
const cityOptions = computed(() => {
  // Combinar ciudades favoritas y lista general, evitando duplicados
  const allCities = []
  
  // Agregar favoritas primero (con prioridad)
  cities.favorites.forEach(f => {
    if (f.city) {
      allCities.push({
        value: f.city_id,
        label: `${f.city.name}${f.city.country ? ` (${f.city.country})` : ''}`,
        name: f.city.name,
        country: f.city.country,
        isFavorite: true,
        cityId: f.city_id
      })
    }
  })
  
  // Agregar ciudades de la lista general que no estén en favoritas
  cities.list.forEach(city => {
    const alreadyExists = allCities.some(c => c.value === city.id)
    if (!alreadyExists) {
      allCities.push({
        value: city.id,
        label: `${city.name}${city.country ? ` (${city.country})` : ''}`,
        name: city.name,
        country: city.country,
        isFavorite: false,
        cityId: city.id
      })
    }
  })
  
  // Ordenar: favoritas primero, luego alfabéticamente
  return allCities.sort((a, b) => {
    if (a.isFavorite && !b.isFavorite) return -1
    if (!a.isFavorite && b.isFavorite) return 1
    return a.name.localeCompare(b.name)
  })
})


// Funciones helper para el preview
const getMetricLabel = (metricId) => {
  const metric = availableMetrics.find(m => m.id === metricId)
  return metric ? metric.label.toLowerCase() : metricId
}

const getOperatorSymbol = (operatorId) => {
  const op = availableOperators.find(o => o.id === operatorId)
  return op ? op.symbol : operatorId
}

const getCurrentUnit = () => {
  if (metric.value === 'temp') {
    const unitObj = availableUnits.find(u => u.id === unit.value)
    return unitObj ? unitObj.symbol : '°C'
  }
  return getMetricUnit(metric.value)
}

// Funciones de filtrado y ordenamiento
function getFilteredAlerts() {
  let filtered = [...alerts.list]
  
  // Filtrar por estado
  if (alertFilters.value.status !== 'all') {
    if (alertFilters.value.status === 'active') {
      filtered = filtered.filter(alert => !alert.paused)
    } else if (alertFilters.value.status === 'paused') {
      filtered = filtered.filter(alert => alert.paused)
    }
  }
  
  // Filtrar por métrica
  if (alertFilters.value.metric !== 'all') {
    filtered = filtered.filter(alert => alert.metric === alertFilters.value.metric)
  }
  
  // Filtrar por ciudad
  if (alertFilters.value.city !== 'all') {
    filtered = filtered.filter(alert => alert.city_id === parseInt(alertFilters.value.city))
  }
  
  // Ordenar
  filtered.sort((a, b) => {
    let aValue, bValue
    
    switch (alertSortBy.value) {
      case 'created_at':
        aValue = new Date(a.created_at)
        bValue = new Date(b.created_at)
        break
      case 'metric':
        aValue = a.metric
        bValue = b.metric
        break
      case 'city':
        aValue = getCityName(a.city_id)
        bValue = getCityName(b.city_id)
        break
      case 'status':
        aValue = a.paused ? 1 : 0
        bValue = b.paused ? 1 : 0
        break
      default:
        return 0
    }
    
    if (alertSortOrder.value === 'asc') {
      return aValue > bValue ? 1 : -1
    } else {
      return aValue < bValue ? 1 : -1
    }
  })
  
  return filtered
}

function getFilteredHistory() {
  let filtered = [...alerts.history]
  
  // Filtrar por rango de fechas
  if (historyFilters.value.dateRange !== 'all') {
    const now = new Date()
    const filterDate = new Date()
    
    switch (historyFilters.value.dateRange) {
      case 'today':
        filterDate.setHours(0, 0, 0, 0)
        break
      case 'week':
        filterDate.setDate(now.getDate() - 7)
        break
      case 'month':
        filterDate.setMonth(now.getMonth() - 1)
        break
    }
    
    filtered = filtered.filter(item => new Date(item.ts) >= filterDate)
  }
  
  // Filtrar por métrica
  if (historyFilters.value.metric !== 'all') {
    filtered = filtered.filter(item => item.metric === historyFilters.value.metric)
  }
  
  // Filtrar por ciudad
  if (historyFilters.value.city !== 'all') {
    filtered = filtered.filter(item => item.city_id === parseInt(historyFilters.value.city))
  }
  
  // Ordenar
  filtered.sort((a, b) => {
    let aValue, bValue
    
    switch (historySortBy.value) {
      case 'ts':
        aValue = new Date(a.ts)
        bValue = new Date(b.ts)
        break
      case 'metric':
        aValue = a.metric
        bValue = b.metric
        break
      case 'city':
        aValue = getCityName(a.city_id)
        bValue = getCityName(b.city_id)
        break
      case 'observed_value':
        aValue = a.observed_value
        bValue = b.observed_value
        break
      default:
        return 0
    }
    
    if (historySortOrder.value === 'asc') {
      return aValue > bValue ? 1 : -1
    } else {
      return aValue < bValue ? 1 : -1
    }
  })
  
  return filtered
}


// Función para exportar historial a CSV
function exportHistoryToCSV() {
  const filteredHistory = getFilteredHistory()
  
  if (filteredHistory.length === 0) {
    alert('No hay datos para exportar')
    return
  }
  
  const headers = ['Fecha', 'Ciudad', 'Métrica', 'Operador', 'Umbral', 'Valor Observado']
  const csvContent = [
    headers.join(','),
    ...filteredHistory.map(item => [
      formatDate(item.ts),
      getCityName(item.city_id),
      availableMetrics.find(m => m.id === item.metric)?.label || item.metric,
      formatOperator(item.operator),
      item.threshold,
      item.observed_value
    ].join(','))
  ].join('\n')
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `historial_alertas_${new Date().toISOString().split('T')[0]}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}


// Funciones para selección múltiple de alertas
function toggleAlertSelection(alertId) {
  if (selectedAlerts.value.has(alertId)) {
    selectedAlerts.value.delete(alertId)
  } else {
    selectedAlerts.value.add(alertId)
  }
  showBulkActions.value = selectedAlerts.value.size > 0
}

function selectAllAlerts() {
  const filteredAlerts = getFilteredAlerts()
  selectedAlerts.value = new Set(filteredAlerts.map(alert => alert.id))
  showBulkActions.value = selectedAlerts.value.size > 0
}

function clearAlertSelection() {
  selectedAlerts.value.clear()
  showBulkActions.value = false
}

// Eliminación masiva de alertas
async function deleteSelectedAlerts() {
  if (selectedAlerts.value.size === 0) return
  
  try {
    const promises = Array.from(selectedAlerts.value).map(alertId => 
      alerts.deleteAlert(alertId)
    )
    await Promise.all(promises)
    clearAlertSelection()
  } catch (error) {
    console.error('Error deleting selected alerts:', error)
  }
}

async function deleteAllAlerts() {
  try {
    const filteredAlerts = getFilteredAlerts()
    const promises = filteredAlerts.map(alert => alerts.deleteAlert(alert.id))
    await Promise.all(promises)
    clearAlertSelection()
  } catch (error) {
    console.error('Error deleting all alerts:', error)
  }
}

// Funciones para selección múltiple de historial
function toggleHistorySelection(itemId) {
  if (selectedHistoryItems.value.has(itemId)) {
    selectedHistoryItems.value.delete(itemId)
  } else {
    selectedHistoryItems.value.add(itemId)
  }
  showHistoryBulkActions.value = selectedHistoryItems.value.size > 0
}

function selectAllHistoryItems() {
  const filteredHistory = getFilteredHistory()
  selectedHistoryItems.value = new Set(filteredHistory.map((item, index) => index))
  showHistoryBulkActions.value = selectedHistoryItems.value.size > 0
}

function clearHistorySelection() {
  selectedHistoryItems.value.clear()
  showHistoryBulkActions.value = false
}

// Eliminación masiva de historial
async function deleteSelectedHistoryItems() {
  if (selectedHistoryItems.value.size === 0) return
  
  try {
    // Nota: Necesitaríamos un endpoint para eliminar elementos del historial
    // Por ahora, solo mostramos un mensaje
    console.log('Eliminar elementos del historial:', Array.from(selectedHistoryItems.value))
    clearHistorySelection()
  } catch (error) {
    console.error('Error deleting selected history items:', error)
  }
}

const getMetricUnit = (metricId) => {
  const units = {
    'temp': '°C',
    'humidity': '%',
    'wind': ' m/s',
    'pressure': ' hPa'
  }
  return units[metricId] || ''
}

const getCityName = (cityId) => {
  const city = cityOptions.value.find(c => c.value === cityId)
  return city ? city.name : 'Ciudad seleccionada'
}


// Formatear operador para mostrar
const formatOperator = (op) => {
  if (!op) return 'N/A' // Manejar valores null/undefined
  const operatorObj = availableOperators.find(o => o.id === op)
  return operatorObj ? operatorObj.symbol : op
}

// Formatear unidad para mostrar
const formatUnit = (metricType, unitValue) => {
  if (metricType !== 'temp') return ''
  const unitObj = availableUnits.find(u => u.id === unitValue)
  return unitObj ? unitObj.symbol : unitValue
}

// Formatear fecha para mostrar
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('es-ES', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Obtener color para la métrica
const getMetricColor = (metricType) => {
  const metric = availableMetrics.find(m => m.id === metricType)
  return metric ? metric.color : '#9E9E9E'
}

// Crear nueva alerta
async function createAlert() {
  if (!selectedCity.value) {
    formError.value = 'Selecciona una ciudad'
    return
  }
  
  if (!threshold.value) {
    formError.value = 'Ingresa un valor de umbral'
    return
  }
  
  formError.value = ''
  isLoading.value = true
  
  try {
    const newAlert = await alerts.createAlert({ 
      city_id: Number(selectedCity.value), 
      metric: metric.value, 
      operator: operator.value, 
      threshold: Number(threshold.value), 
      unit: metric.value === 'temp' ? unit.value : undefined 
    })
    
    // Limpiar formulario y cerrar
    selectedCity.value = null
    threshold.value = '35'
    showForm.value = false
    
    // Agregar animación de entrada a la nueva alerta
    setTimeout(() => {
      const newAlertElement = document.querySelector(`[data-alert-id="${newAlert.id}"]`)
      if (newAlertElement) {
        newAlertElement.classList.add('new-alert')
        // Remover la clase después de la animación
        setTimeout(() => {
          newAlertElement.classList.remove('new-alert')
        }, 800)
      }
    }, 50)
  } catch (error) {
    formError.value = 'Error al crear la alerta'
    console.error('Error creating alert:', error)
  } finally {
    isLoading.value = false
  }
}

// Actualizar estado de alerta (pausada/activa)
async function toggleAlertStatus(alert) {
  // No usar isLoading global, solo actualizar la alerta específica
  try {
    await alerts.updateAlert(alert.id, { paused: !alert.paused })
    // La alerta se actualiza automáticamente en el store
  } catch (error) {
    console.error('Error updating alert:', error)
  }
}

// Eliminar alerta
async function deleteAlert(alertId) {
  try {
    // Encontrar el elemento de la alerta y agregar clase de animación
    const alertElement = document.querySelector(`[data-alert-id="${alertId}"]`)
    if (alertElement) {
      alertElement.classList.add('deleting')
      
      // Esperar a que termine la animación antes de eliminar del DOM
      setTimeout(async () => {
    await alerts.deleteAlert(alertId)
      }, 600) // Duración de la animación
    } else {
      // Si no se encuentra el elemento, eliminar directamente
      await alerts.deleteAlert(alertId)
    }
  } catch (error) {
    console.error('Error deleting alert:', error)
  }
}

// Opciones de ciudades para filtros
const sortedCityOptions = computed(() => {
  // Usar la misma lógica que cityOptions pero simplificada para filtros
  const allCities = []
  
  // Agregar favoritas primero (con prioridad)
  cities.favorites.forEach(f => {
    if (f.city) {
      allCities.push({
        value: f.city.id,
        label: `${f.city.name}${f.city.country ? ` (${f.city.country})` : ''}`,
        name: f.city.name,
        country: f.city.country,
        isFavorite: true
      })
    }
  })
  
  // Agregar ciudades de la lista general (evitando duplicados)
  cities.list.forEach(city => {
    const alreadyExists = allCities.some(c => c.value === city.id)
    if (!alreadyExists && city.name) { // Solo agregar si tiene nombre
      allCities.push({
        value: city.id,
        label: `${city.name}${city.country ? ` (${city.country})` : ''}`,
        name: city.name,
        country: city.country,
        isFavorite: false
      })
    }
  })
  
  return allCities.sort((a, b) => {
    // Favoritas primero, luego alfabético
    if (a.isFavorite && !b.isFavorite) return -1
    if (!a.isFavorite && b.isFavorite) return 1
    return (a.name || '').localeCompare(b.name || '')
  })
})

// Cargar historial de alertas
async function loadAlertHistory() {
  isLoading.value = true
  try {
    await alerts.fetchHistory()
    showHistory.value = true
  } finally {
    isLoading.value = false
  }
}

</script>

<template>
  <section>
    <!-- Encabezado de página -->
    <div class="page-title">
      <div class="title-with-icon">
        <AlertTriangle size="24" />
        <h1>Gestión de Alertas</h1>
      </div>
      
      <div class="page-actions">
        <button 
          v-if="!showForm" 
          class="btn btn-primary" 
          @click="showForm = true"
        >
          <Plus size="18" />
          <span>Nueva Alerta</span>
        </button>
        
        <button 
          v-if="!showHistory" 
          class="btn btn-outline" 
          @click="loadAlertHistory"
        >
          <Clock size="18" />
          <span>Ver Historial</span>
        </button>
      </div>
    </div>
    
    <!-- Formulario para crear alerta -->
    <div v-if="showForm" class="alert-form card">
      <div class="form-header">
        <div class="header-content">
          <h2 class="form-title">Crear Nueva Alerta</h2>
          <p class="form-subtitle">Se notificará cuando se cumpla la condición seleccionada</p>
        </div>
        <button class="btn-close" @click="showForm = false" aria-label="Cerrar formulario">
          <X size="20" />
        </button>
      </div>
      
       <div class="form-content">
         <div class="form-row">
           <!-- Ciudad -->
           <div class="field">
             <label class="field-label">Ciudad</label>
             <CustomDropdown 
            v-model="selectedCity" 
               :options="sortedCityOptions"
               placeholder="Busca una ciudad..."
            :class="{ 'error': formError && !selectedCity }"
             />
             <p class="helper-text">Selecciona la ciudad donde quieres aplicar la alerta</p>
           </div>
           <!-- Métrica -->
           <div class="field">
             <label class="field-label">Métrica</label>
             <div class="field-control">
               <div class="metric-selector-grid">
                 <button 
                   class="metric-chip"
                   :class="{ active: metric === 'temp' }"
                   :style="{ '--metric-color': '#FF6B35' }"
                   @click="metric = 'temp'"
                   :aria-pressed="metric === 'temp'"
                 >
                   <Thermometer size="16" class="metric-icon-svg" />
                   <span class="metric-label">Temperatura</span>
                 </button>
                 <button 
                   class="metric-chip"
                   :class="{ active: metric === 'humidity' }"
                   :style="{ '--metric-color': '#4A90E2' }"
                   @click="metric = 'humidity'"
                   :aria-pressed="metric === 'humidity'"
                 >
                   <Droplets size="16" class="metric-icon-svg" />
                   <span class="metric-label">Humedad</span>
                 </button>
            <button 
                   class="metric-chip"
                   :class="{ active: metric === 'wind' }"
                   :style="{ '--metric-color': '#7ED321' }"
                   @click="metric = 'wind'"
                   :aria-pressed="metric === 'wind'"
                 >
                   <Wind size="16" class="metric-icon-svg" />
                   <span class="metric-label">Viento</span>
                 </button>
                 <button 
                   class="metric-chip"
                   :class="{ active: metric === 'pressure' }"
                   :style="{ '--metric-color': '#F5A623' }"
                   @click="metric = 'pressure'"
                   :aria-pressed="metric === 'pressure'"
                 >
                   <Gauge size="16" class="metric-icon-svg" />
                   <span class="metric-label">Presión</span>
            </button>
          </div>
        </div>
           </div>
           <!-- Condición -->
           <div class="field">
             <label class="field-label">Condición</label>
             <div class="field-control condition-controls" role="group" aria-label="Condición">
               <div class="operators">
            <button 
              v-for="op in availableOperators" 
              :key="op.id"
                   class="operator-chip"
              :class="{ active: operator === op.id }"
              @click="operator = op.id"
                   :aria-pressed="operator === op.id"
                   :title="op.label"
            >
              {{ op.symbol }}
            </button>
          </div>
               <div class="value-row">
                 <div class="threshold-input-container">
            <input 
              v-model="threshold" 
              type="number" 
                     class="threshold-input"
              :class="{ 'error': formError && !threshold }"
                     placeholder="35"
                     step="0.1"
                   />
                   <div class="threshold-unit">
                     <span v-if="metric !== 'temp'" class="unit-text">{{ getMetricUnit(metric) }}</span>
                     <div v-else class="unit-selector-compact">
              <button 
                v-for="u in availableUnits" 
                :key="u.id"
                         class="unit-chip"
                :class="{ active: unit === u.id }"
                @click="unit = u.id"
              >
                {{ u.symbol }}
              </button>
                     </div>
                   </div>
                 </div>
            </div>
          </div>
           </div>
         </div>
         
         <!-- Preview en tiempo real -->
         <div class="alert-preview" v-if="selectedCity && threshold">
           <div class="preview-icon">ℹ️</div>
           <span class="preview-text">
             Se activará si la {{ getMetricLabel(metric) }} {{ getOperatorSymbol(operator) }} {{ threshold }}{{ getCurrentUnit() }} en {{ getCityName(selectedCity) }}
           </span>
        </div>
      </div>
      
      <!-- Error y botones de acción -->
      <div class="form-footer">
        <p v-if="formError" class="form-error">
          <Info size="16" />
          <span>{{ formError }}</span>
        </p>
        
        <div class="form-actions">
          <button class="btn btn-danger" @click="showForm = false">Cancelar</button>
          <button 
            class="btn btn-primary" 
            @click="createAlert" 
            :disabled="isLoading"
            :class="{ 'loading': isLoading }"
          >
            <span>{{ isLoading ? 'Creando...' : 'Crear Alerta' }}</span>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Lista de alertas activas -->
    <div v-if="!showHistory" class="alerts-list card">
      <div class="card-header">
        <h3>
          <Bell size="18" />
          <span>Mis Alertas</span>
        </h3>
        <div class="alert-count">
          {{ getFilteredAlerts().length }} alertas configuradas
        </div>
      </div>
      
      <!-- Controles de filtrado y ordenamiento -->
      <div class="filters-section">
        <div class="filters-row">
          <div class="filter-group">
            <label>Estado:</label>
            <BeautifulDropdown
              v-model="alertFilters.status"
              :options="[
                { value: 'all', label: 'Todas' },
                { value: 'active', label: 'Activas' },
                { value: 'paused', label: 'Pausadas' }
              ]"
              placeholder="Seleccionar estado"
            />
          </div>
          
          <div class="filter-group">
            <label>Métrica:</label>
            <BeautifulDropdown
              v-model="alertFilters.metric"
              :options="[
                { value: 'all', label: 'Todas' },
                { value: 'temp', label: 'Temperatura' },
                { value: 'humidity', label: 'Humedad' },
                { value: 'wind', label: 'Viento' },
                { value: 'pressure', label: 'Presión' }
              ]"
              placeholder="Seleccionar métrica"
            />
          </div>
          
          <div class="filter-group">
            <label>Ciudad:</label>
            <BeautifulDropdown
              v-model="alertFilters.city"
              :options="[
                { value: 'all', label: 'Todas' },
                ...sortedCityOptions
              ]"
              placeholder="Seleccionar ciudad"
            />
          </div>
          
          <div class="filter-group">
            <label>Ordenar por:</label>
            <div class="sort-group">
              <BeautifulDropdown
                v-model="alertSortBy"
                :options="[
                  { value: 'created_at', label: 'Fecha de creación' }
                ]"
                placeholder="Seleccionar orden"
              />
              <button 
                @click="alertSortOrder = alertSortOrder === 'asc' ? 'desc' : 'asc'"
                class="sort-order-btn"
                :title="alertSortOrder === 'asc' ? 'Ascendente' : 'Descendente'"
              >
                {{ alertSortOrder === 'asc' ? '↑' : '↓' }}
              </button>
            </div>
          </div>
        </div>
        
        <!-- Acciones masivas -->
        <div class="bulk-actions" v-if="showBulkActions">
          <div class="bulk-info">
            {{ selectedAlerts.size }} seleccionadas
          </div>
          <div class="bulk-buttons">
            <button @click="deleteSelectedAlerts" class="btn btn-danger btn-sm">
              <Trash2 size="16" />
              Eliminar seleccionadas
            </button>
            <button @click="clearAlertSelection" class="btn btn-outline btn-sm">
              Cancelar
            </button>
          </div>
        </div>
        
        <div class="bulk-actions" v-else>
          <div class="bulk-buttons">
            <button @click="selectAllAlerts" class="btn btn-outline btn-sm">
              Seleccionar todas
            </button>
            <button @click="deleteAllAlerts" class="btn btn-danger btn-sm">
              <Trash2 size="16" />
              Eliminar todas
            </button>
          </div>
        </div>
      </div>
      
      <!-- Estado de carga -->
      <div v-if="isLoading" class="loading-state">
        <Loader2 class="animate-spin" size="32" />
        <p>Cargando alertas...</p>
      </div>
      
      <!-- Lista de alertas -->
      <div v-if="getFilteredAlerts().length > 0">
        <Transition name="alerts-section" appear>
          <div class="alerts-grid">
        <div 
            v-for="alert in getFilteredAlerts()" 
          :key="alert.id" 
            :data-alert-id="alert.id"
          class="alert-card"
            :class="{ 'paused': alert.paused, 'selected': selectedAlerts.has(alert.id) }"
        >
          <div class="alert-header">
            <div class="alert-city">{{ getCityName(alert.city_id) }}</div>
            <div class="alert-status" :class="{ 'paused': alert.paused }">
              {{ alert.paused ? 'Pausada' : 'Activa' }}
            </div>
          </div>
          
          <div class="alert-created">
            <Calendar size="14" />
            <span>Creada: {{ formatDate(alert.created_at) }}</span>
          </div>
          
          <div class="alert-condition" :style="{ '--alert-color': getMetricColor(alert.metric) }">
            <div class="metric-name">{{ availableMetrics.find(m => m.id === alert.metric)?.label }}</div>
            <div class="condition">
              {{ formatOperator(alert.operator) }} {{ alert.threshold }}{{ formatUnit(alert.metric, alert.unit) }}
            </div>
          </div>
          
          <div class="alert-actions">
            <!-- Checkbox de selección en la parte inferior izquierda -->
            <div class="alert-selection-bottom">
              <input 
                type="checkbox" 
                :checked="selectedAlerts.has(alert.id)"
                @change="toggleAlertSelection(alert.id)"
                class="alert-checkbox"
              />
            </div>
            <div class="alert-buttons">
            <button 
              class="btn btn-outline btn-sm"
              @click="toggleAlertStatus(alert)"
            >
              <BellOff v-if="!alert.paused" size="16" />
              <Bell v-else size="16" />
              <span>{{ alert.paused ? 'Reanudar' : 'Pausar' }}</span>
            </button>
            
            <button 
              class="btn btn-danger btn-sm"
              @click="deleteAlert(alert.id)"
            >
              <Trash2 size="16" />
              <span>Eliminar</span>
            </button>
          </div>
        </div>
        </div>
          </div>
        </Transition>
      </div>
      
      <!-- Sin resultados de filtros -->
      <div v-else-if="alerts.list.length > 0" class="empty-state">
        <Bell size="48" color="var(--color-text-secondary)" />
        <h3>No hay alertas que coincidan con los filtros</h3>
        <p>Intenta ajustar los filtros para ver más resultados.</p>
        <button class="btn btn-outline" @click="alertFilters = { status: 'all', metric: 'all', city: 'all' }">
          <span>Limpiar Filtros</span>
        </button>
      </div>
      
      <!-- Estado vacío -->
      <div v-else class="empty-state card">
        <Bell size="48" color="var(--color-text-secondary)" />
        <h3>No tienes alertas configuradas</h3>
        <p>Crea una alerta para recibir notificaciones cuando las condiciones meteorológicas cumplan ciertos criterios.</p>
        <button class="btn btn-primary" @click="showForm = true">
          <Plus size="18" />
          <span>Crear Primera Alerta</span>
        </button>
      </div>
    </div>
    
    <!-- Historial de alertas -->
    <div v-if="showHistory" class="alerts-history card">
      <div class="card-header">
        <h3>
          <Clock size="18" />
          <span>Historial de Alertas</span>
        </h3>
        <div class="header-actions">
          <button class="btn btn-outline btn-sm" @click="exportHistoryToCSV">
            <Download size="16" />
            <span>Exportar CSV</span>
          </button>
        <button class="btn btn-outline btn-sm" @click="showHistory = false">
          <Bell size="16" />
          <span>Ver Alertas Activas</span>
        </button>
        </div>
      </div>
      
      <!-- Controles de filtrado para historial -->
      <div class="filters-section">
        <div class="filters-row">
          <div class="filter-group">
            <label>Período:</label>
            <BeautifulDropdown
              v-model="historyFilters.dateRange"
              :options="[
                { value: 'all', label: 'Todos' },
                { value: 'today', label: 'Hoy' },
                { value: 'week', label: 'Última semana' },
                { value: 'month', label: 'Último mes' }
              ]"
              placeholder="Seleccionar período"
            />
          </div>
          
          <div class="filter-group">
            <label>Métrica:</label>
            <BeautifulDropdown
              v-model="historyFilters.metric"
              :options="[
                { value: 'all', label: 'Todas' },
                { value: 'temp', label: 'Temperatura' },
                { value: 'humidity', label: 'Humedad' },
                { value: 'wind', label: 'Viento' },
                { value: 'pressure', label: 'Presión' }
              ]"
              placeholder="Seleccionar métrica"
            />
          </div>
          
          <div class="filter-group">
            <label>Ciudad:</label>
            <BeautifulDropdown
              v-model="historyFilters.city"
              :options="[
                { value: 'all', label: 'Todas' },
                ...sortedCityOptions
              ]"
              placeholder="Seleccionar ciudad"
            />
          </div>
          
          <div class="filter-group">
            <label>Ordenar por:</label>
            <div class="sort-group">
              <BeautifulDropdown
                v-model="historySortBy"
                :options="[
                  { value: 'ts', label: 'Fecha' }
                ]"
                placeholder="Seleccionar orden"
              />
              <button 
                @click="historySortOrder = historySortOrder === 'asc' ? 'desc' : 'asc'"
                class="sort-order-btn"
                :title="historySortOrder === 'asc' ? 'Ascendente' : 'Descendente'"
              >
                {{ historySortOrder === 'asc' ? '↑' : '↓' }}
              </button>
            </div>
          </div>
        </div>
        
        <!-- Acciones masivas para historial -->
        <div class="bulk-actions" v-if="showHistoryBulkActions">
          <div class="bulk-info">
            {{ selectedHistoryItems.size }} seleccionados
          </div>
          <div class="bulk-buttons">
            <button @click="deleteSelectedHistoryItems" class="btn btn-danger btn-sm">
              <Trash2 size="16" />
              Eliminar seleccionados
            </button>
            <button @click="clearHistorySelection" class="btn btn-outline btn-sm">
              Cancelar
            </button>
          </div>
        </div>
        
        <div class="bulk-actions" v-else>
          <div class="bulk-buttons">
            <button @click="selectAllHistoryItems" class="btn btn-outline btn-sm">
              Seleccionar todos
            </button>
          </div>
        </div>
      </div>
      
      <!-- Estado de carga -->
      <div v-if="isLoading" class="loading-state">
        <Loader2 class="animate-spin" size="32" />
        <p>Cargando historial...</p>
      </div>
      
      <!-- Tabla de historial -->
      <div v-else-if="alerts.history.length > 0" class="history-table-container">
        <table class="history-table">
          <thead>
            <tr>
              <th>
                <input 
                  type="checkbox" 
                  @change="selectAllHistoryItems"
                  class="select-all-checkbox"
                />
              </th>
              <th>Fecha</th>
              <th>Ciudad</th>
              <th>Métrica</th>
              <th>Condición</th>
              <th>Valor Observado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(entry, index) in getFilteredHistory()" :key="index" 
                :class="{ 'selected': selectedHistoryItems.has(index) }">
              <td>
                <input 
                  type="checkbox" 
                  :checked="selectedHistoryItems.has(index)"
                  @change="toggleHistorySelection(index)"
                  class="history-checkbox"
                />
              </td>
              <td>{{ formatDate(entry.ts) }}</td>
              <td>{{ getCityName(entry.city_id) }}</td>
              <td>{{ availableMetrics.find(m => m.id === entry.metric)?.label }}</td>
              <td>{{ formatOperator(entry.operator) }} {{ entry.threshold }}{{ formatUnit(entry.metric, entry.unit) }}</td>
              <td>
                <span class="observed-value">
                  {{ entry.observed_value }}{{ formatUnit(entry.metric, entry.unit) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Estado vacío -->
      <div v-else class="empty-state">
        <Clock size="48" color="var(--color-text-secondary)" />
        <h3>No hay historial de alertas</h3>
        <p>Cuando tus alertas se activen, aparecerán aquí.</p>
      </div>
      
    </div>
    
    <!-- Información sobre alertas -->
    <div class="alert-info card">
      <div class="info-header">
        <h3>
          <Info size="18" />
          <span>¿Cómo funcionan las alertas?</span>
        </h3>
      </div>
      
      <div class="info-content">
        <p>Las alertas te permiten monitorear condiciones meteorológicas específicas para tus ciudades favoritas.</p>
        
        <div class="info-steps">
          <div class="info-step">
            <div class="step-number">1</div>
            <div class="step-content">
              <h4>Selecciona una ciudad</h4>
              <p>Elige una de tus ciudades favoritas para monitorear.</p>
            </div>
          </div>
          
          <div class="info-step">
            <div class="step-number">2</div>
            <div class="step-content">
              <h4>Define una condición</h4>
              <p>Especifica qué métrica (temperatura, humedad, etc.) quieres monitorear y bajo qué condiciones.</p>
            </div>
          </div>
          
          <div class="info-step">
            <div class="step-number">3</div>
            <div class="step-content">
              <h4>Recibe notificaciones</h4>
              <p>Cuando las condiciones se cumplan, se registrará en el historial de alertas.</p>
            </div>
          </div>
        </div>
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

.page-actions {
  display: flex;
  gap: var(--space-sm);
}

/* Formulario de alertas rediseñado */
.alert-form {
  margin-bottom: var(--space-xl);
  position: relative;
  border-radius: var(--radius-lg);
  overflow: hidden;
}

/* Header mejorado */
.form-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: var(--space-md) var(--space-lg);
  background: var(--color-card-bg);
  border-bottom: 1px solid var(--color-border);
}

.header-content {
  flex: 1;
}

.form-title {
  margin: 0 0 var(--space-xs) 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.2;
}

.form-subtitle {
  margin: 0;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  line-height: 1.3;
}

.btn-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  color: var(--color-text-secondary);
}

.btn-close:hover {
  background-color: var(--color-border);
  color: var(--color-text-primary);
  transform: scale(1.05);
}

.form-header h3 {
  margin: 0;
}

.btn-icon {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: var(--space-xs);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: var(--color-text-primary);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

@media (min-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (min-width: 1024px) {
  .form-grid {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .form-group.span-2 {
    grid-column: span 2;
  }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.form-group label {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  font-weight: 500;
}

/* Estilos para CustomDropdown en formulario de alertas */
.form-group .custom-dropdown.error .dropdown-trigger {
  border-color: var(--color-alert);
}

.form-input {
  padding: var(--space-sm) var(--space-md);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-card-bg);
  color: var(--color-text-primary);
  font-size: 0.95rem;
  font-weight: 500;
  min-height: 44px;
  transition: all var(--transition-fast);
}

.form-input:hover {
  border-color: var(--color-primary);
  background-color: var(--color-bg-secondary);
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.1);
}

.form-input.error {
  border-color: var(--color-alert);
}

.metric-buttons, .operator-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
}

.metric-button {
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  border: 2px solid var(--color-border);
  background-color: var(--color-card-bg);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
  flex: 1;
  min-width: 100px;
  min-height: 44px;
  text-align: center;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
}

.metric-button:hover {
  border-color: var(--color-primary);
  background-color: var(--color-bg-secondary);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.metric-button.active {
  background-color: var(--metric-color);
  color: white;
  border-color: var(--metric-color);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}

.operator-button {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  border: 2px solid var(--color-border);
  background-color: var(--color-card-bg);
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.operator-button:hover {
  border-color: var(--color-primary);
  background-color: var(--color-bg-secondary);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.operator-button.active {
  background-color: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}

.threshold-input-group {
  display: flex;
  gap: var(--space-sm);
}

.threshold-group .form-input {
  flex: 1;
}

.unit-selector {
  display: flex;
  gap: var(--space-xs);
}

.unit-button {
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  border: 2px solid var(--color-border);
  background-color: var(--color-card-bg);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-weight: 500;
  min-height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.unit-button:hover {
  border-color: var(--color-primary);
  background-color: var(--color-bg-secondary);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.unit-button.active {
  background-color: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}

.form-footer {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.form-error {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  color: var(--color-alert);
  margin: 0;
  font-size: 0.9rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-sm);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-lg);
}

.card-header h3 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.alert-count {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

.alerts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-md);
}

.alert-card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-md);
  background-color: var(--color-card-bg);
  transition: all var(--transition-fast);
}

.alert-card.paused {
  opacity: 0.7;
  background-color: #f5f5f5;
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

.alert-city {
  font-weight: 600;
  font-size: 1.1rem;
}

.alert-status {
  font-size: 0.8rem;
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-full);
  background-color: var(--color-success);
  color: white;
}

.alert-status.paused {
  background-color: #ff9800;
  color: white;
  border: 1px solid #ff9800;
  box-shadow: 0 2px 4px rgba(255, 152, 0, 0.3);
}

.dark-theme .alert-status.paused {
  background-color: #ff9800;
  color: white;
  border: 1px solid #ff9800;
  box-shadow: 0 2px 4px rgba(255, 152, 0, 0.4);
}

.alert-created {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-sm);
}

/* Estilos para filtros y acciones masivas */
.filters-section {
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  padding: var(--space-md);
  margin-bottom: var(--space-lg);
}

.filters-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-md);
  margin-bottom: var(--space-md);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.filter-group label {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.filter-select {
  padding: var(--space-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background-color: var(--color-bg);
  color: var(--color-text);
  font-size: 0.9rem;
}

.sort-order-btn {
  padding: var(--space-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background-color: var(--color-bg);
  color: var(--color-text);
  cursor: pointer;
  margin-left: var(--space-xs);
  min-width: 40px;
}

.bulk-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-sm);
  background-color: var(--color-bg);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
}

.bulk-info {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

.bulk-buttons {
  display: flex;
  gap: var(--space-sm);
}

.header-actions {
  display: flex;
  gap: var(--space-sm);
}

/* Estilos para checkboxes */
.alert-selection {
  position: absolute;
  top: var(--space-sm);
  left: var(--space-sm);
}

.alert-selection-bottom {
  display: flex;
  align-items: center;
  justify-content: center;
}

.alert-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--color-primary);
  transition: all 0.2s ease;
}

.alert-checkbox:hover {
  transform: scale(1.1);
}

.select-all-checkbox,
.history-checkbox {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: var(--color-primary);
  transition: all 0.2s ease;
}

.select-all-checkbox:hover,
.history-checkbox:hover {
  transform: scale(1.1);
}

.alert-card {
  position: relative;
}

.alert-card.selected {
  border-color: var(--color-primary);
  background-color: var(--color-primary-light);
}

.history-table tr.selected {
  background-color: var(--color-primary-light);
}

/* Mejorar el layout de alert-actions */
.alert-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
  margin-top: var(--space-md);
  padding-top: var(--space-md);
  border-top: 1px solid var(--color-border);
}

.alert-buttons {
  display: flex;
  gap: var(--space-sm);
}

/* Mejorar el grupo de ordenamiento */
.sort-group {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.sort-group .beautiful-dropdown {
  flex: 1;
}

.sort-order-btn {
  padding: 12px 16px;
  border: 2px solid var(--color-border);
  border-radius: 8px;
  background-color: var(--color-bg);
  color: var(--color-text);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 600;
  min-width: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sort-order-btn:hover {
  border-color: var(--color-primary);
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.sort-order-btn:active {
  transform: translateY(0);
}

/* Mejorar los filtros */
.filters-section {
  background: linear-gradient(135deg, var(--color-bg-secondary) 0%, var(--color-bg) 100%);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: var(--space-lg);
  margin-bottom: var(--space-xl);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.filters-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--space-lg);
  margin-bottom: var(--space-lg);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.filter-group label {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: var(--space-xs);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Mejorar las acciones masivas */
.bulk-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-md);
  background: linear-gradient(135deg, var(--color-bg) 0%, var(--color-bg-secondary) 100%);
  border-radius: 8px;
  border: 1px solid var(--color-border);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.bulk-info {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.bulk-buttons {
  display: flex;
  gap: var(--space-sm);
}

/* Mejorar las tarjetas de alertas */
.alert-card {
  background: linear-gradient(135deg, var(--color-bg) 0%, var(--color-bg-secondary) 100%);
  border: 2px solid var(--color-border);
  border-radius: 12px;
  padding: var(--space-lg);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.alert-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--color-primary), var(--color-secondary));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.alert-card:hover::before {
  opacity: 1;
}

.alert-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  border-color: var(--color-primary);
}

.alert-card.selected {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(var(--color-primary-rgb), 0.2);
  border-color: var(--color-primary);
}

.alert-card.selected::before {
  opacity: 1;
}

/* Mejorar el header de alertas */
.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

.alert-city {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--color-text);
}

.alert-status {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background-color: #10b981;
  color: white;
}

.alert-status.paused {
  background-color: #f59e0b;
  color: white;
}

/* Mejorar la condición de alerta */
.alert-condition {
  background: linear-gradient(135deg, var(--color-primary-light) 0%, rgba(var(--color-primary-rgb), 0.1) 100%);
  border-left: 4px solid var(--color-primary);
  padding: var(--space-md);
  border-radius: 8px;
  margin: var(--space-md) 0;
}

.condition {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text);
}

/* Mejorar la tabla de historial */
.history-table-container {
  background: linear-gradient(135deg, var(--color-bg) 0%, var(--color-bg-secondary) 100%);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--color-border);
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  background-color: transparent;
}

.history-table th {
  background: linear-gradient(135deg, var(--color-bg-secondary) 0%, var(--color-bg) 100%);
  font-weight: 700;
  color: var(--color-text);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.8rem;
  padding: var(--space-lg);
  border-bottom: 2px solid var(--color-border);
}

.history-table td {
  padding: var(--space-lg);
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  transition: all 0.2s ease;
}

.history-table tr:hover {
  background-color: var(--color-bg-secondary);
}

.history-table tr:hover td {
  color: var(--color-text);
}

.history-table tr.selected {
  background-color: var(--color-primary-light);
}

.history-table tr.selected td {
  color: var(--color-text);
}

.observed-value {
  font-weight: 600;
  color: var(--color-primary);
  font-size: 1.1rem;
}


/* Mejorar el estilo de las tarjetas de alertas pausadas en modo oscuro */
.dark-theme .alert-card.paused {
  background-color: #2a2a2a;
  border: 1px solid #ff9800;
  box-shadow: 0 4px 8px rgba(255, 152, 0, 0.2);
}

.dark-theme .alert-card.paused .alert-city {
  color: #ff9800;
  font-weight: 600;
}

.dark-theme .alert-card.paused .alert-condition {
  background-color: rgba(255, 152, 0, 0.1);
  border-left-color: #ff9800;
  color: #ff9800;
}

/* Animaciones suaves para transiciones de estado */
.alert-card {
  transition: all 0.3s ease;
}

.alert-status {
  transition: all 0.3s ease;
}

.alert-card.paused {
  transition: all 0.3s ease;
}

.alert-card.paused .alert-city {
  transition: color 0.3s ease;
}

.alert-card.paused .alert-condition {
  transition: all 0.3s ease;
}

/* Animaciones para eliminación de alertas */
.alert-card.deleting {
  animation: elegantDelete 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
  transform-origin: center;
  overflow: hidden;
}

@keyframes elegantDelete {
  0% {
    opacity: 1;
    transform: translateX(0) scale(1);
    max-height: 200px;
    margin-bottom: var(--space-md);
    padding: var(--space-md);
    border-radius: var(--radius-md);
  }
  30% {
    opacity: 0.8;
    transform: translateX(-15px) scale(0.98);
  }
  60% {
    opacity: 0.4;
    transform: translateX(-40px) scale(0.92);
  }
  100% {
    opacity: 0;
    transform: translateX(-80px) scale(0.85);
    max-height: 0;
    margin-bottom: 0;
    padding: 0;
    border: none;
    border-radius: 0;
  }
}

/* Animación de reacomodo suave para las alertas restantes */
.alert-card:not(.deleting) {
  transition: all 0.3s ease;
}

/* Transición suave para la sección de alertas */
.alerts-section-enter-active {
  transition: all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.alerts-section-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.alerts-section-enter-to {
  opacity: 1;
  transform: translateY(0);
}

/* Animación para nuevas alertas */
.alert-card.new-alert {
  animation: elegantAppear 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
  transform-origin: center;
}

@keyframes elegantAppear {
  0% {
    opacity: 0;
    transform: translateY(-20px) scale(0.9);
    max-height: 0;
    margin-bottom: 0;
    padding: 0;
    border-radius: 0;
  }
  50% {
    opacity: 0.8;
    transform: translateY(-5px) scale(1.02);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
    max-height: 200px;
    margin-bottom: var(--space-md);
    padding: var(--space-md);
    border-radius: var(--radius-md);
  }
}

/* Efecto hover mejorado para botón de eliminar */
.btn-danger:hover {
  background-color: #c82333;
  border-color: #bd2130;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3);
}

.btn-danger:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(220, 53, 69, 0.2);
}

/* Botón de carga elegante */
.btn.loading {
  position: relative;
  overflow: hidden;
  cursor: not-allowed;
}

.btn.loading::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: loading-shimmer 1.5s infinite;
}

@keyframes loading-shimmer {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
}

.alert-condition {
  margin-bottom: var(--space-md);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  background-color: rgba(0, 0, 0, 0.03);
  border-left: 3px solid var(--alert-color);
}

.metric-name {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-xs);
}

.condition {
  font-size: 1.2rem;
  font-weight: 600;
}

.alert-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-sm);
}

.btn-sm {
  padding: var(--space-xs) var(--space-sm);
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.btn-danger {
  background-color: var(--color-alert);
  color: white;
  border: none;
}

.btn-danger:hover {
  background-color: #d32f2f;
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
  margin-bottom: var(--space-md);
}

.history-table-container {
  overflow-x: auto;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
}

.history-table th, .history-table td {
  padding: var(--space-sm) var(--space-md);
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.history-table th {
  background-color: rgba(0, 0, 0, 0.02);
  font-weight: 600;
  color: var(--color-text-primary);
}

.history-table td {
  color: var(--color-text-secondary);
}

.observed-value {
  font-weight: 500;
  color: var(--color-text-primary);
}

.alert-info {
  margin-top: var(--space-xl);
}

.info-header {
  margin-bottom: var(--space-md);
}

.info-header h3 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.info-content p {
  color: var(--color-text-secondary);
}

.info-steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--space-lg);
  margin-top: var(--space-lg);
}

.info-step {
  display: flex;
  gap: var(--space-md);
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
}

.step-content h4 {
  margin: 0 0 var(--space-xs) 0;
  font-size: 1rem;
}

.step-content p {
  margin: 0;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
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

/* Responsive adjustments */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .alerts-grid {
    grid-template-columns: 1fr;
  }
  
  .info-steps {
    grid-template-columns: 1fr;
  }
}

/* Estilos del nuevo formulario */
.form-content {
  padding: var(--space-md);
}

/* Balancear el contenido de las columnas */
.form-section {
  padding: 0 var(--space-sm);
}

/* Primera columna: padding izquierdo mínimo */
.form-section:first-child {
  padding-left: 0;
  padding-right: var(--space-md);
}

/* Última columna: padding derecho mínimo */
.form-section:last-child {
  padding-right: 0;
  padding-left: var(--space-md);
}

/* Layout horizontal: Ciudad | Métrica | Condición */
.form-grid-horizontal {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-md);
}

@media (min-width: 768px) {
  .form-grid-horizontal {
    grid-template-columns: 1fr 1fr 1fr;
    gap: var(--space-lg);
    align-items: start;
  }
  
  /* Alinear columna de condición a la derecha */
  .form-section:last-child {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
  }
  
  /* Centrar el título de la columna de condición */
  .form-section:last-child .section-label {
    align-self: center;
    text-align: center;
  }
}

/* Centrar la columna de métricas */
.form-section-centered {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

/* Grid 2x2 para métricas */
.metric-selector-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: var(--space-sm);
  width: 100%;
  max-width: 300px;
}

/* Grupo de condición vertical */
.condition-group-vertical {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  align-items: flex-start;
  width: 100%;
  max-width: 300px;
}

.form-column {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.section-label {
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-xs);
}

.helper-text {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  margin-top: var(--space-xs);
  line-height: 1.4;
}

/* Selector de métricas mejorado */
.metric-selector {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
}

.metric-chip {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-sm) var(--space-md);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-card-bg);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-weight: 500;
  min-height: 40px;
  flex: 1;
  min-width: 100px;
}

.metric-chip:hover {
  border-color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.metric-chip.active {
  border-color: var(--metric-color);
  background: var(--metric-color);
  color: white;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.metric-icon {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.metric-icon-svg {
  flex-shrink: 0;
  color: var(--color-text-secondary);
  transition: color var(--transition-fast);
}

.metric-chip.active .metric-icon-svg {
  color: white;
}

.metric-label {
  font-size: 0.9rem;
}

/* Grupo de condición compacto */
.condition-group {
  display: flex;
  gap: var(--space-md);
  align-items: flex-start;
}

.condition-group-horizontal {
  display: flex;
  gap: var(--space-sm);
  align-items: flex-start;
  flex-wrap: wrap;
}

.operator-selector {
  display: flex;
  gap: var(--space-xs);
}

.operator-chip {
  width: 44px;
  height: 44px;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-card-bg);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-weight: 600;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.operator-chip:hover {
  border-color: var(--color-primary);
  background: var(--color-bg-secondary);
  transform: scale(1.05);
}

.operator-chip.active {
  border-color: var(--color-primary);
  background: var(--color-primary);
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* Input de umbral compacto */
.threshold-input-container {
  display: flex;
  align-items: center;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-card-bg);
  overflow: hidden;
  transition: all var(--transition-fast);
  flex: 1;
  max-width: 200px;
}

.threshold-input-container:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.1);
}

.threshold-input {
  border: none;
  background: transparent;
  padding: var(--space-sm) var(--space-md);
  color: var(--color-text-primary);
  font-size: 1rem;
  font-weight: 500;
  width: 80px;
  text-align: center;
}

.threshold-input:focus {
  outline: none;
}

.threshold-unit {
  display: flex;
  align-items: center;
  padding-right: var(--space-sm);
  border-left: 1px solid var(--color-border);
}

.unit-text {
  padding: 0 var(--space-sm);
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.unit-selector-compact {
  display: flex;
}

.unit-chip {
  padding: var(--space-xs) var(--space-sm);
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-size: 0.85rem;
  font-weight: 500;
}

.unit-chip:hover {
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.unit-chip.active {
  background: var(--color-primary);
  color: white;
}

/* Preview de alerta */
.alert-preview {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md);
  background: linear-gradient(135deg, var(--color-bg-secondary) 0%, var(--color-card-bg) 100%);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  margin-top: var(--space-md);
}

.preview-icon {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.preview-text {
  font-size: 0.9rem;
  color: var(--color-text-primary);
  line-height: 1.4;
  font-weight: 500;
}

/* Modo oscuro específico */
.dark-theme .threshold-input-container {
  background: var(--color-card-bg);
  border-color: var(--color-border);
}

/* --- NUEVO LAYOUT PROFESIONAL PARA FORMULARIO DE ALERTAS --- */
.form-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 2rem;
  align-items: start;
}

.field {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.field-label {
  margin-bottom: 8px;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  text-align: center;
  width: 100%;
  display: block;
}

.field-control {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  align-items: center;
}

.condition-controls {
  width: 100%;
  align-items: center;
}

.operators {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.value-row {
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: center;
}

/* Estilos mejorados para modo claro */
.light-theme .alert-card {
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  color: #333333;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.light-theme .alert-card.paused {
  background-color: #fff3e0;
  border: 1px solid #ff9800;
  color: #333333;
  box-shadow: 0 2px 4px rgba(255, 152, 0, 0.2);
}

.light-theme .alert-card.selected {
  border-color: var(--color-primary);
  background-color: #e3f2fd;
}

.light-theme .filters-section {
  background-color: #f5f5f5;
  border: 1px solid #e0e0e0;
}

.light-theme .filter-select {
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  color: #333333;
}

.light-theme .sort-order-btn {
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  color: #333333;
}

.light-theme .bulk-actions {
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
}

.light-theme .history-table tr.selected {
  background-color: #e3f2fd;
}

/* Mejorar la transición de carga */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-xl);
  color: var(--color-text-secondary);
}

.loading-state .animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Mejorar el estado vacío */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-xl);
  text-align: center;
  color: var(--color-text-secondary);
}

.empty-state h3 {
  margin: var(--space-md) 0 var(--space-sm) 0;
  color: var(--color-text);
}

.empty-state p {
  margin-bottom: var(--space-lg);
  max-width: 400px;
  line-height: 1.5;
}

/* Mejorar las tarjetas de alertas */
.alert-card {
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.alert-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.alert-card.selected {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(var(--color-primary-rgb), 0.3);
}

/* Mejorar los botones */
.btn {
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.btn:active {
  transform: translateY(0);
}

/* Mejorar los filtros */
.filters-section {
  transition: all 0.3s ease;
}

.filter-group {
  transition: all 0.2s ease;
}

.filter-group:hover label {
  color: var(--color-primary);
}

/* Mejorar la tabla de historial */
.history-table {
  border-collapse: collapse;
  width: 100%;
  background-color: var(--color-bg);
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.history-table th {
  background-color: var(--color-bg-secondary);
  font-weight: 600;
  text-align: left;
  padding: var(--space-md);
  border-bottom: 2px solid var(--color-border);
}

.history-table td {
  padding: var(--space-md);
  border-bottom: 1px solid var(--color-border);
  transition: background-color 0.2s ease;
}

.history-table tr:hover {
  background-color: var(--color-bg-secondary);
}

.history-table tr.selected {
  background-color: var(--color-primary-light);
}

/* Mejorar los checkboxes */
.alert-checkbox,
.history-checkbox,
.select-all-checkbox {
  accent-color: var(--color-primary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.alert-checkbox:hover,
.history-checkbox:hover,
.select-all-checkbox:hover {
  transform: scale(1.1);
}

/* Mejorar las animaciones */
.alerts-section-enter-active,
.alerts-section-leave-active {
  transition: all 0.3s ease;
}

.alerts-section-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.alerts-section-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* Mejorar el formulario de crear alerta */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: var(--space-lg);
  margin-bottom: var(--space-lg);
}

.field {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.field label {
  font-weight: 600;
  color: var(--color-text);
  font-size: 0.9rem;
}

.field .form-input,
.field .form-select {
  padding: var(--space-md);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-bg);
  color: var(--color-text);
  font-size: 1rem;
  transition: all 0.2s ease;
}

.field .form-input:focus,
.field .form-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.1);
}

/* Mejorar los botones de métricas */
.metric-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-sm);
}

.metric-button {
  padding: var(--space-md);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-bg);
  color: var(--color-text);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  font-weight: 500;
}

.metric-button:hover {
  border-color: var(--color-primary);
  background-color: var(--color-primary-light);
}

.metric-button.selected {
  border-color: var(--color-primary);
  background-color: var(--color-primary);
  color: white;
}

/* Mejorar los botones de operador */
.operator-buttons {
  display: flex;
  gap: var(--space-sm);
  margin-bottom: var(--space-md);
}

.operator-button {
  padding: var(--space-sm) var(--space-md);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-sm);
  background-color: var(--color-bg);
  color: var(--color-text);
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 600;
  min-width: 40px;
}

.operator-button:hover {
  border-color: var(--color-primary);
  background-color: var(--color-primary-light);
}

.operator-button.selected {
  border-color: var(--color-primary);
  background-color: var(--color-primary);
  color: white;
}
</style>