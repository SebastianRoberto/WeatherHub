import { defineStore } from 'pinia'
import { ref } from 'vue'
import { Thermometer, Droplets, Gauge, Wind } from 'lucide-vue-next'

export const METRIC_CONFIGS = {
  temperature: {
    key: 'temperature',
    title: 'Temperatura',
    unit: '°C',
    color: '#3B82F6',
    icon: Thermometer,
    yAxisLabel: 'Temperatura (°C)',
    min: -20,
    max: 50,
    step: 5,
    description: 'Temperatura del aire en grados Celsius'
  },
  humidity: {
    key: 'humidity',
    title: 'Humedad',
    unit: '%',
    color: '#10B981',
    icon: Droplets,
    yAxisLabel: 'Humedad (%)',
    min: 0,
    max: 100,
    step: 10,
    description: 'Humedad relativa del aire en porcentaje'
  },
  pressure: {
    key: 'pressure',
    title: 'Presión',
    unit: 'hPa',
    color: '#8B5CF6',
    icon: Gauge,
    yAxisLabel: 'Presión (hPa)',
    min: 950,
    max: 1050,
    step: 10,
    description: 'Presión atmosférica en hectopascales'
  },
  wind: {
    key: 'wind',
    title: 'Viento',
    unit: 'm/s',
    color: '#F59E0B',
    icon: Wind,
    yAxisLabel: 'Velocidad (m/s)',
    min: 0,
    max: 30,
    step: 5,
    description: 'Velocidad del viento en metros por segundo'
  }
}

export const useMetricsStore = defineStore('metrics', () => {
  const selectedMetrics = ref(['temperature'])
  
  function setSelectedMetrics(metrics) {
    selectedMetrics.value = metrics
  }
  
  function addMetric(metric) {
    if (!selectedMetrics.value.includes(metric)) {
      selectedMetrics.value.push(metric)
    }
  }
  
  function removeMetric(metric) {
    const index = selectedMetrics.value.indexOf(metric)
    if (index > -1) {
      selectedMetrics.value.splice(index, 1)
    }
  }
  
  function toggleMetric(metric) {
    if (selectedMetrics.value.includes(metric)) {
      removeMetric(metric)
    } else {
      addMetric(metric)
    }
  }
  
  function getMetricConfig(metric) {
    return METRIC_CONFIGS[metric]
  }
  
  function getAllMetrics() {
    return Object.keys(METRIC_CONFIGS)
  }
  
  function getAvailableMetrics() {
    return Object.values(METRIC_CONFIGS)
  }
  
  return {
    selectedMetrics,
    setSelectedMetrics,
    addMetric,
    removeMetric,
    toggleMetric,
    getMetricConfig,
    getAllMetrics,
    getAvailableMetrics
  }
})
