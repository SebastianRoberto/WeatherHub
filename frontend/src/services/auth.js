import api, { setAuthToken } from './api'

export async function register({ email, password, full_name }) {
  const { data } = await api.post('/auth/register', { email, password, full_name })
  return data
}

export async function login({ email, password }) {
  const { data } = await api.post('/auth/login', { email, password })
  setAuthToken(data.access_token)
  return data
}

export async function me() {
  const { data } = await api.get('/auth/me')
  return data
}

export function logout() {
  setAuthToken(null)
}
