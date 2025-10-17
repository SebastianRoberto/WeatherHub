import api from './api'

export async function getCurrent(city, unit = 'c') {
  const { data } = await api.get('/weather/current', { params: { city, unit } })
  return data
}

export async function getHistory({ city, from, to, days = 7, unit = 'c', limit = 1000 }) {
  const params = { city, days, unit, limit }
  if (from) params.from_date = from
  if (to) params.to_date = to
  const { data } = await api.get('/weather/history', { params })
  return data
}

export async function compare({ cities, from, to, days = 7, unit = 'c', limit = 1000 }) {
  const params = { cities: cities.join(','), days, unit, limit }
  if (from) params.from_date = from
  if (to) params.to_date = to
  const { data } = await api.get('/weather/compare', { params })
  return data
}

export async function favoritesCurrent(unit = 'c') {
  const { data } = await api.get('/weather/favorites/current', { params: { unit } })
  return data
}

export async function exportHistoryCsv({ cityIds, from, to, unit = 'c' }) {
  const params = {}
  if (cityIds?.length) params.city_ids = cityIds.join(',')
  if (from) params.from_date = from
  if (to) params.to_date = to
  params.unit = unit
  const res = await api.get('/export/history', { params, responseType: 'blob' })
  return res.data
}
