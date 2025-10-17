import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useAlertsStore = defineStore('alerts', () => {
  const list = ref([])
  const history = ref([])
  const loading = ref(false)

  async function fetchAlerts(active_only = true) {
    loading.value = true
    try {
      const { data } = await api.get('/alerts', { params: { active_only } })
      list.value = data
    } finally {
      loading.value = false
    }
  }

  async function fetchHistory(params = {}) {
    loading.value = true
    try {
      const { data } = await api.get('/alerts/history/', { params })
      history.value = data
    } finally {
      loading.value = false
    }
  }

  async function createAlert(payload) {
    const { data } = await api.post('/alerts', payload)
    list.value.push(data)
  }

  async function updateAlert(id, payload) {
    const { data } = await api.patch(`/alerts/${id}`, payload)
    const idx = list.value.findIndex((a) => a.id === id)
    if (idx !== -1) list.value[idx] = data
  }

  async function deleteAlert(id) {
    await api.delete(`/alerts/${id}`)
    list.value = list.value.filter((a) => a.id !== id)
  }

  return { list, history, loading, fetchAlerts, fetchHistory, createAlert, updateAlert, deleteAlert }
})
