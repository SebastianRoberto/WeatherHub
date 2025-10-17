import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, register as apiRegister, me as apiMe, logout as apiLogout } from '@/services/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('wh_token') || null)
  const user = ref(null)
  const loading = ref(false)
  const isAuthenticated = computed(() => !!token.value)

  async function fetchMe() {
    if (!token.value) {
      user.value = null
      return null
    }
    try {
      loading.value = true
      user.value = await apiMe()
      return user.value
    } finally {
      loading.value = false
    }
  }

  async function login(credentials) {
    loading.value = true
    try {
      const { access_token } = await apiLogin(credentials)
      token.value = access_token
      await fetchMe()
      return true
    } finally {
      loading.value = false
    }
  }

  async function register(payload) {
    loading.value = true
    try {
      await apiRegister(payload)
      return await login({ email: payload.email, password: payload.password })
    } finally {
      loading.value = false
    }
  }

  function logout() {
    apiLogout()
    token.value = null
    user.value = null
  }

  return { token, user, loading, isAuthenticated, fetchMe, login, register, logout }
})
