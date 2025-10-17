import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
})

export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`
    localStorage.setItem('wh_token', token)
  } else {
    delete api.defaults.headers.common.Authorization
    localStorage.removeItem('wh_token')
  }
}

// Cargar token en arranque si existe
const saved = localStorage.getItem('wh_token')
if (saved) setAuthToken(saved)

// Interceptor de errores básicos
api.interceptors.response.use(
  (r) => r,
  (error) => {
    if (error?.response?.status === 401) {
      // token inválido/expirado
      setAuthToken(null)
    }
    return Promise.reject(error)
  }
)

export default api
