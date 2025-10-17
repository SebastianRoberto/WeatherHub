<template>
  <div class="unit-selector">
    <CustomDropdown 
      v-model="selectedUnit" 
      :options="unitOptions"
      placeholder="°C"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useWeatherStore } from '@/stores/weather'
import CustomDropdown from '@/components/CustomDropdown.vue'

const weather = useWeatherStore()

const unitOptions = [
  { value: 'c', label: '°C' },
  { value: 'f', label: '°F' },
  { value: 'k', label: 'K' }
]

const selectedUnit = computed({
  get: () => weather.unit,
  set: (value) => {
    weather.unit = value
  }
})
</script>

<style scoped>
.unit-selector {
  display: flex;
  align-items: center;
}
</style>
