<template>
  <div class="metric-chart">
    <div class="chart-header">
      <div class="chart-title">
        <component :is="metricConfig.icon" size="20" />
        <h3>{{ metricConfig.title }}</h3>
      </div>
      <div class="chart-actions">
        <button @click="exportChart" class="btn-export" :disabled="!chartData">
          <Download size="16" />
          Exportar
        </button>
      </div>
    </div>
    
    <div class="chart-content">
      <Transition name="chart-fade" mode="out-in">
        <div v-if="loading" key="loading" class="chart-loading">
          <div class="loading-spinner"></div>
          <p>Cargando datos de {{ metricConfig.title.toLowerCase() }}...</p>
        </div>
        
        <div v-else-if="!chartData || chartData.length === 0" key="empty" class="chart-empty">
          <component :is="metricConfig.icon" size="48" class="empty-icon" />
          <p>No hay datos de {{ metricConfig.title.toLowerCase() }} disponibles</p>
        </div>
        
        <div v-else key="chart" class="chart-container">
          <Line 
            :data="chartData" 
            :options="chartOptions"
            :key="chartKey"
            class="chart-canvas"
          />
        </div>
      </Transition>
    </div>
    
    <div v-if="chartData && chartData.length > 0" class="chart-stats">
      <div class="stat-item">
        <span class="stat-label">Máximo:</span>
        <span class="stat-value">{{ maxValue }} {{ metricConfig.unit }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Mínimo:</span>
        <span class="stat-value">{{ minValue }} {{ metricConfig.unit }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Promedio:</span>
        <span class="stat-value">{{ avgValue }} {{ metricConfig.unit }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  TimeScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import zoomPlugin from 'chartjs-plugin-zoom'
import 'chartjs-adapter-date-fns'
import { Download } from 'lucide-vue-next'
import { METRIC_CONFIGS } from '@/stores/metrics'

// Eliminar la función writeToLogFile y sus imports relacionados
import { useWeatherStore } from '@/stores/weather'

// Rangos fijos para vista comparativa
const fixedRangesExtreme = {
  temperature: { min: -90, max: 60 },   // cubre récords históricos (-89.2 °C) y extremos calientes
  humidity:    { min: 0,   max: 100 }, // siempre
  pressure:    { min: 800, max: 1100 }, // 800 hPa cubre caídas locales extremas; 1100 hPa cubre sobremesas raras
  wind:        { min: 0,   max: 160 }   // 160 m/s ≈ 576 km/h, cubre tornados EF5 y ráfagas extremas
}

// Función para calcular rango sugerido con padding
function getSuggestedRange(data, padPercent = 0.1) {
  if (!data || data.length === 0) return { suggestedMin: 0, suggestedMax: 100 }
  
  const values = data.filter(val => val !== null && val !== undefined)
  if (values.length === 0) return { suggestedMin: 0, suggestedMax: 100 }
  
  const min = Math.min(...values)
  const max = Math.max(...values)
  const pad = Math.max((max - min) * padPercent, 1) // Mínimo padding de 1 unidad
  
  return {
    suggestedMin: min - pad,
    suggestedMax: max + pad
  }
}

// Registrar componentes de Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  TimeScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  zoomPlugin
)

const props = defineProps({
  metric: {
    type: String,
    required: true,
    validator: (value) => Object.keys(METRIC_CONFIGS).includes(value)
  },
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  // Información adicional para nombres de archivo
  cities: {
    type: Array,
    default: () => []
  },
  period: {
    type: String,
    default: ''
  },
  viewType: {
    type: String,
    default: 'history', // 'history' o 'compare'
    validator: (value) => ['history', 'compare'].includes(value)
  }
})

const chartKey = ref(0)
const weather = useWeatherStore()

// Configuración de la métrica
const metricConfig = computed(() => METRIC_CONFIGS[props.metric])

// Recargar gráfico cuando cambie la unidad de temperatura
watch(() => weather.unit, () => {
  if (props.metric === 'temperature') {
    chartKey.value++
  }
})

// Datos del gráfico
const chartData = computed(() => {
  if (!props.data || props.data.length === 0) return null
  
  // DETECTAR SI SON DATOS DE MÚLTIPLES CIUDADES O UNA SOLA
  const hasMultipleCities = props.data.some(item => item.city)
  console.log(`[MetricChart] ${props.metric}: hasMultipleCities = ${hasMultipleCities}`)
  console.log(`[MetricChart] ${props.metric}: datos recibidos:`, props.data.slice(0, 3))
  
  if (hasMultipleCities) {
    console.log(`[MetricChart] ${props.metric}: Procesando múltiples ciudades`)
    // MÚLTIPLES CIUDADES: Crear datasets separados
    const cityGroups = {}
    const allLabels = new Set()
    const allTimestamps = new Set()
    
    // Agrupar datos por ciudad
    props.data.forEach(item => {
      if (!cityGroups[item.city]) {
        cityGroups[item.city] = []
      }
      cityGroups[item.city].push(item)
      
      // Recopilar todas las fechas
      const timestampValue = item.timestamp || item.ts
      console.log(`[MetricChart] ${props.metric} - Procesando timestamp para ${item.city}:`, timestampValue)
      
      if (!timestampValue) {
        console.error(`[MetricChart] ${props.metric} - TIMESTAMP UNDEFINED para ${item.city}:`, item)
      }
      
      const date = new Date(timestampValue)
      if (isNaN(date.getTime())) {
        console.error(`[MetricChart] ${props.metric} - Invalid Date para ${item.city}:`, timestampValue)
      }
      
      // Guardar timestamp original para ordenamiento
      allTimestamps.add(timestampValue)
      
      allLabels.add(date.toLocaleDateString('es-ES', {
        day: 'numeric',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit'
      }))
    })
    
    // DEBUG: Verificar datos por ciudad
    console.log(`🔍 [MetricChart] ${props.metric} - Datos por ciudad:`)
    Object.keys(cityGroups).forEach(city => {
      const cityData = cityGroups[city]
      console.log(`🔍 [MetricChart] ${props.metric} - ${city}: ${cityData.length} registros`)
      console.log(`🔍 [MetricChart] ${props.metric} - ${city} - Primer timestamp:`, cityData[0]?.timestamp || cityData[0]?.ts)
      console.log(`🔍 [MetricChart] ${props.metric} - ${city} - Último timestamp:`, cityData[cityData.length - 1]?.timestamp || cityData[cityData.length - 1]?.ts)
    })
    
    // Crear datasets para cada ciudad usando TimeScale
    const datasets = []
    const cityColors = ['#1E88E5', '#26A69A', '#FFA000', '#7E57C2', '#EC407A', '#F57C00', '#5C6BC0', '#43A047']
    const cities = Object.keys(cityGroups)
    
    cities.forEach((cityName, index) => {
      const cityData = cityGroups[cityName]
      
      // Crear puntos con timestamps individuales para cada ciudad
      const dataPoints = cityData.map(item => {
        let value = item.value || 0
        if (props.metric === 'temperature') {
          if (weather.unit === 'f') value = (value * 9/5) + 32
          else if (weather.unit === 'k') value = value + 273.15
          value = Math.round(value * 100) / 100
        }
        
        // Asegurar que el timestamp sea un objeto Date válido
        const timestamp = item.timestamp || item.ts
        const date = new Date(timestamp)
        
        if (isNaN(date.getTime())) {
          console.error(`[MetricChart] ${props.metric} - Invalid timestamp for ${cityName}:`, timestamp)
          return null // Filtrar puntos con timestamps inválidos
        }
        
        return {
          x: date, // Usar objeto Date, no string
          y: value
        }
      }).filter(point => point !== null) // Filtrar puntos con timestamps inválidos
      
      datasets.push({
        label: cityName,
        data: dataPoints,
        borderColor: cityColors[index % cityColors.length],
        backgroundColor: cityColors[index % cityColors.length] + '20',
        borderWidth: 2,
        fill: false,
        tension: 0.1,
        pointBackgroundColor: cityColors[index % cityColors.length],
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      })
    })
    
    return {
      datasets // No necesitamos labels con TimeScale
    }
  } else {
    // UNA SOLA CIUDAD: Usar TimeScale también
    
    // Crear puntos con timestamps para TimeScale (una sola ciudad)
    const dataPoints = props.data.map(item => {
      // Extraer valor según la métrica específica
      let value = 0
      switch (props.metric) {
        case 'temperature':
          value = item.temp_c || item.temperature || item.value || 0
          // Aplicar conversión de unidades para temperatura
          if (weather.unit === 'f') {
            value = (value * 9/5) + 32
          } else if (weather.unit === 'k') {
            value = value + 273.15
          }
          value = Math.round(value * 100) / 100
          break
        case 'humidity':
          value = item.humidity || item.value || 0
          break
        case 'pressure':
          value = item.pressure || item.value || 0
          break
        case 'wind':
          value = item.wind_speed || item.value || 0
          break
        default:
          value = item.value || 0
      }
      
      // Asegurar que el timestamp sea un objeto Date válido
      const timestamp = item.timestamp || item.ts
      const date = new Date(timestamp)
      
      if (isNaN(date.getTime())) {
        console.error(`[MetricChart] ${props.metric} - Invalid timestamp:`, timestamp)
        return null // Filtrar puntos con timestamps inválidos
      }
      
      return {
        x: date, // Usar objeto Date, no string
        y: value
      }
    }).filter(point => point !== null) // Filtrar puntos con timestamps inválidos
    
    return {
      datasets: [{
        label: metricConfig.value.title,
        data: dataPoints, // Data ahora contiene {x, y} objects
        borderColor: metricConfig.value.color,
        backgroundColor: metricConfig.value.color + '20',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: metricConfig.value.color,
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
        spanGaps: false // No conectar puntos a través de nulls
      }]
    }
  }
})

// Opciones del gráfico
const chartOptions = computed(() => {
  const hasMultipleCities = props.data && props.data.some(item => item.city)
  
  return {
    responsive: true,
    maintainAspectRatio: false,
    // Habilitar zoom y pan para navegación
    interaction: {
      intersect: true,
      mode: 'nearest'
    },
    plugins: {
      legend: {
        display: hasMultipleCities, // Mostrar leyenda solo para múltiples ciudades
        position: 'top',
        labels: {
          usePointStyle: true,
          padding: 20,
          font: {
            size: 12
          }
        }
      },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: '#fff',
      bodyColor: '#fff',
      borderColor: metricConfig.value.color,
      borderWidth: 1,
      callbacks: {
        label: (context) => {
          // Obtener unidad correcta según la métrica y configuración
          let unit = metricConfig.value.unit
          if (props.metric === 'temperature') {
            if (weather.unit === 'f') unit = '°F'
            else if (weather.unit === 'k') unit = 'K'
            else unit = '°C'
          }
          return `${metricConfig.value.title}: ${context.parsed.y} ${unit}`
        }
      }
    }
  },
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'day', // Mostrar días en el eje X
          tooltipFormat: 'dd MMM yyyy HH:mm',
          displayFormats: {
            day: 'dd MMM',
            hour: 'HH:mm',
            minute: 'HH:mm'
          }
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
          drawBorder: false
        },
        ticks: {
          color: '#9CA3AF',
          maxTicksLimit: undefined // Eliminar limitación de puntos
        }
      },
    y: {
      beginAtZero: props.metric === 'humidity',
      grid: {
        color: 'rgba(255, 255, 255, 0.1)',
        drawBorder: false
      },
      ticks: {
        color: '#9CA3AF',
        callback: (value) => {
          // Obtener unidad correcta según la métrica y configuración
          let unit = metricConfig.value.unit
          if (props.metric === 'temperature') {
            if (weather.unit === 'f') unit = '°F'
            else if (weather.unit === 'k') unit = 'K'
            else unit = '°C'
          }
          return `${value} ${unit}`
        }
      },
      title: {
        display: true,
        text: (() => {
          // Obtener etiqueta correcta según la métrica y configuración
          if (props.metric === 'temperature') {
            if (weather.unit === 'f') return 'Temperatura (°F)'
            else if (weather.unit === 'k') return 'Temperatura (K)'
            else return 'Temperatura (°C)'
          }
          return metricConfig.value.yAxisLabel
        })(),
        color: '#9CA3AF',
        font: {
          size: 12
        }
      },
      // Configuración de escala según el tipo de vista
      ...(() => {
        if (props.viewType === 'compare') {
          // Vista comparativa: usar rangos fijos
          const fixedRange = fixedRangesExtreme[props.metric]
          if (fixedRange) {
            return {
              min: fixedRange.min,
              max: fixedRange.max
            }
          }
        } else {
          // Vista individual: usar escala dinámica con padding
          const currentChartData = chartData.value
          if (currentChartData && currentChartData.datasets && currentChartData.datasets.length > 0) {
            const dataset = currentChartData.datasets[0]
            if (dataset.data && dataset.data.length > 0) {
              const values = dataset.data
                .filter(point => point && typeof point.y === 'number')
                .map(point => point.y)
              
              if (values.length > 0) {
                const range = getSuggestedRange(values, 0.1)
                return {
                  suggestedMin: range.suggestedMin,
                  suggestedMax: range.suggestedMax
                }
              }
            }
          }
        }
        return {}
      })()
    }
  },
  interaction: {
    intersect: true,
    mode: 'nearest'
  },
  // Configuración de zoom y pan para navegación
  plugins: {
    zoom: {
      zoom: {
        wheel: {
          enabled: true,
        },
        pinch: {
          enabled: true
        },
        mode: 'x',
      },
      pan: {
        enabled: true,
        mode: 'x',
      }
    }
  }
  }
})

// Estadísticas
const maxValue = computed(() => {
  if (!props.data || props.data.length === 0) return 0
  const values = props.data.map(item => {
    let value = 0
    switch (props.metric) {
      case 'temperature':
        value = item.temp_c || item.temperature || item.value
        // Aplicar conversión de unidades para temperatura
        if (weather.unit === 'f') {
          value = (value * 9/5) + 32
        } else if (weather.unit === 'k') {
          value = value + 273.15
        }
        // Redondear a 2 decimales para consistencia
        return Math.round(value * 100) / 100
      case 'humidity': return item.humidity || item.value
      case 'pressure': return item.pressure || item.value
      case 'wind': return item.wind_speed || item.value
      default: return 0
    }
  })
  return Math.max(...values).toFixed(1)
})

const minValue = computed(() => {
  if (!props.data || props.data.length === 0) return 0
  const values = props.data.map(item => {
    let value = 0
    switch (props.metric) {
      case 'temperature':
        value = item.temp_c || item.temperature || item.value
        // Aplicar conversión de unidades para temperatura
        if (weather.unit === 'f') {
          value = (value * 9/5) + 32
        } else if (weather.unit === 'k') {
          value = value + 273.15
        }
        // Redondear a 2 decimales para consistencia
        return Math.round(value * 100) / 100
      case 'humidity': return item.humidity || item.value
      case 'pressure': return item.pressure || item.value
      case 'wind': return item.wind_speed || item.value
      default: return 0
    }
  })
  return Math.min(...values).toFixed(1)
})

const avgValue = computed(() => {
  if (!props.data || props.data.length === 0) return 0
  const values = props.data.map(item => {
    let value = 0
    switch (props.metric) {
      case 'temperature':
        value = item.temp_c || item.temperature || item.value
        // Aplicar conversión de unidades para temperatura
        if (weather.unit === 'f') {
          value = (value * 9/5) + 32
        } else if (weather.unit === 'k') {
          value = value + 273.15
        }
        // Redondear a 2 decimales para consistencia
        return Math.round(value * 100) / 100
      case 'humidity': return item.humidity || item.value
      case 'pressure': return item.pressure || item.value
      case 'wind': return item.wind_speed || item.value
      default: return 0
    }
  })
  return (values.reduce((a, b) => a + b, 0) / values.length).toFixed(1)
})

// Exportar gráfico
function exportChart() {
  if (!chartData.value) return
  
  try {
    // Crear canvas temporal para exportar
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    canvas.width = 800
    canvas.height = 400
    
    // Crear imagen del gráfico
    const chartCanvas = document.querySelector(`#chart-${props.metric}`)
    if (chartCanvas) {
      const chartCtx = chartCanvas.getContext('2d')
      const imageData = chartCtx.getImageData(0, 0, chartCanvas.width, chartCanvas.height)
      ctx.putImageData(imageData, 0, 0)
      
      // Convertir a blob y descargar
      canvas.toBlob((blob) => {
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `${metricConfig.value.title.toLowerCase().replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.png`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
      }, 'image/png')
    } else {
      // Fallback: exportar datos como CSV
      exportAsCSV()
    }
  } catch (error) {
    console.error('Error exportando gráfico:', error)
    // Fallback: exportar datos como CSV
    exportAsCSV()
  }
}

// Exportar como CSV
function exportAsCSV() {
  if (!props.data || props.data.length === 0) return
  
  // DETECTAR SI SON DATOS DE MÚLTIPLES CIUDADES O UNA SOLA
  const hasMultipleCities = props.data.some(item => item.city)
  
  if (hasMultipleCities) {
    // MÚLTIPLES CIUDADES (Comparar)
    const headers = ['Ciudad', 'Fecha', metricConfig.value.title]
    const rows = props.data.map(item => {
      const date = new Date(item.timestamp || item.ts)
      const value = (() => {
        switch (props.metric) {
          case 'temperature': 
            return item.temp_c || item.temperature
          case 'humidity': 
            return item.humidity
          case 'pressure': 
            return item.pressure
          case 'wind': 
            return item.wind_speed
          default: 
            return item.value || ''
        }
      })()
      
      return [
        item.city || '',
        date.toLocaleDateString('es-ES', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        }),
        value
      ]
    })
    
    // Ordenar por ciudad y fecha
    rows.sort((a, b) => {
      if (a[0] !== b[0]) return a[0].localeCompare(b[0])
      return new Date(a[1]) - new Date(b[1])
    })
    
    const csvContent = [headers, ...rows]
      .map(row => row.map(cell => `"${cell}"`).join(','))
      .join('\n')
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    // Para múltiples ciudades (Comparar), usar nombres de ciudades y período
    const citiesStr = props.cities.length > 0 ? props.cities.join('_') : 'multiples'
    const periodInfo = props.period || '7dias'
    link.download = `${props.metric}_${citiesStr}_${periodInfo}_${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
  } else {
    // UNA SOLA CIUDAD (Historial)
    const headers = ['Fecha', metricConfig.value.title]
    const rows = props.data.map(item => {
      const date = new Date(item.timestamp || item.ts)
      const value = (() => {
        switch (props.metric) {
          case 'temperature': 
            return item.temp_c || item.temperature
          case 'humidity': 
            return item.humidity
          case 'pressure': 
            return item.pressure
          case 'wind': 
            return item.wind_speed
          default: 
            return item.value || ''
        }
      })()
      
      return [
        date.toLocaleDateString('es-ES', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        }),
        value
      ]
    })
    
    // Ordenar por fecha
    rows.sort((a, b) => new Date(a[0]) - new Date(b[0]))
    
    const csvContent = [headers, ...rows]
      .map(row => row.map(cell => `"${cell}"`).join(','))
      .join('\n')
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    // Para una sola ciudad (Historial), usar el nombre de la ciudad y período
    const cityName = props.cities.length > 0 ? props.cities[0] : (props.data[0]?.city || 'ciudad')
    const periodInfo = props.period || '7dias'
    link.download = `${props.metric}_${cityName}_${periodInfo}_${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }
}

// Forzar re-render cuando cambien los datos
watch(() => props.data, () => {
  chartKey.value++
}, { deep: true })
</script>

<style scoped>
.metric-chart {
  background-color: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  margin-bottom: var(--space-lg);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--color-border);
}

.chart-title {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.chart-title h3 {
  margin: 0;
  color: var(--color-text-primary);
  font-size: 1.125rem;
  font-weight: 600;
}

.chart-actions {
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

.btn-export:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
  transform: translateY(-1px);
}

.btn-export:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.chart-content {
  position: relative;
  min-height: 300px;
}

.chart-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  gap: var(--space-md);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border);
  border-top: 3px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Transiciones suaves para el gráfico */
.chart-fade-enter-active,
.chart-fade-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.chart-fade-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}

.chart-fade-leave-to {
  opacity: 0;
  transform: translateY(-20px) scale(0.95);
}

.chart-fade-enter-to,
.chart-fade-leave-from {
  opacity: 1;
  transform: translateY(0) scale(1);
}

.chart-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  gap: var(--space-md);
  color: var(--color-text-secondary);
}

.empty-icon {
  opacity: 0.5;
}

.chart-container {
  position: relative;
  height: 400px;
}

.chart-canvas {
  width: 100% !important;
  height: 100% !important;
}

.chart-stats {
  display: flex;
  justify-content: space-around;
  margin-top: var(--space-md);
  padding-top: var(--space-md);
  border-top: 1px solid var(--color-border);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xs);
}

.stat-label {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.stat-value {
  font-size: 1.125rem;
  color: var(--color-text-primary);
  font-weight: 600;
}

/* Responsive */
@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    gap: var(--space-sm);
    align-items: flex-start;
  }
  
  .chart-stats {
    flex-direction: column;
    gap: var(--space-sm);
  }
  
  .chart-container {
    height: 250px;
  }
}
</style>
