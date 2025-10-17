import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { getCurrent, getHistory, compare, favoritesCurrent } from '@/services/weather'

export const useWeatherStore = defineStore('weather', () => {
  const unit = ref('c')
  const loading = ref(false)
  const current = ref(null)
  const favorites = ref([])
  const history = ref([])
  const compareData = ref({})

  // Estado para rastrear qué datos están cargados actualmente
  const currentCity = ref(null)
  const historyParams = ref(null)
  const compareParams = ref(null)

  // Recargar datos automáticamente al cambiar la unidad
  watch(unit, (newUnit, oldUnit) => {
    if (currentCity.value) fetchCurrent(currentCity.value)
    if (historyParams.value) fetchHistory(historyParams.value)
    if (compareParams.value) fetchCompare(compareParams.value)
    fetchFavoritesCurrent()
  })

  async function fetchCurrent(city) {
    loading.value = true
    try {
      current.value = await getCurrent(city, unit.value)
      currentCity.value = city
    } finally {
      loading.value = false
    }
  }

  async function fetchFavoritesCurrent() {
    loading.value = true
    try {
      favorites.value = await favoritesCurrent(unit.value)
    } finally {
      loading.value = false
    }
  }

  async function fetchHistory(payload) {
    loading.value = true
    try {
      history.value = await getHistory({ ...payload, unit: unit.value })
      historyParams.value = payload
    } finally {
      loading.value = false
    }
  }

  async function fetchCompare(payload) {
    loading.value = true
    try {
      compareData.value = await compare({ ...payload, unit: unit.value })
      compareParams.value = payload
    } finally {
      loading.value = false
    }
  }

  return { unit, loading, current, favorites, history, compareData, fetchCurrent, fetchFavoritesCurrent, fetchHistory, fetchCompare }
})
