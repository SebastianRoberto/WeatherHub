<script setup>
import { exportHistoryCsv } from '@/services/weather'

const props = defineProps({
  cityIds: { type: Array, default: () => [] },
  from: { type: String, default: '' },
  to: { type: String, default: '' },
  unit: { type: String, default: 'c' },
})

async function download() {
  const blob = await exportHistoryCsv({ cityIds: props.cityIds, from: props.from, to: props.to, unit: props.unit })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'weather_history.csv'
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <button class="export" @click="download">Exportar CSV</button>
</template>

<style scoped>
.export { padding: 0.5rem 0.75rem; border-radius: 8px; border: 0; background: #16a34a; color: #fff; cursor: pointer; }
</style>
