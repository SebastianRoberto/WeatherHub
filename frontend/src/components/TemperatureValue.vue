<template>
  <span class="temperature-value">
    <transition name="fade" mode="out-in">
      <span :key="displayValue" class="temperature-number">
        {{ displayValue }}<span class="temperature-unit">{{ unitSymbol }}</span>
      </span>
    </transition>
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  value: { type: Number, required: true }, // SIEMPRE EN CELSIUS
  unit: { type: String, required: true }
})

const unitSymbol = computed(() => {
  if (props.unit === 'c') return '°C'
  if (props.unit === 'f') return '°F'
  if (props.unit === 'k') return 'K'
  return ''
})

// Computed para conversión - ENFOQUE DECLARATIVO
const convertedValue = computed(() => {
  if (props.unit === 'c') return props.value
  if (props.unit === 'f') return (props.value * 9/5) + 32
  if (props.unit === 'k') return props.value + 273.15
  return props.value
})

// Display value como computed - NO MÁS REFS MANUALES
const displayValue = computed(() => {
  return convertedValue.value.toLocaleString(undefined, { 
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2 
  })
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.25s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
