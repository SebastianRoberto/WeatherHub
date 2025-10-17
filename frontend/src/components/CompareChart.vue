<script setup>
import { Line } from 'vue-chartjs'
import {
  Chart,
  LineElement,
  PointElement,
  LinearScale,
  TimeScale,
  Title,
  Tooltip,
  Legend,
  CategoryScale
} from 'chart.js'

Chart.register(
  LineElement,
  PointElement,
  LinearScale,
  TimeScale,
  Title,
  Tooltip,
  Legend,
  CategoryScale
)

defineProps({
  labels: { type: Array, required: true },
  datasets: { type: Array, required: true }, // [{label, data, borderColor}]
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: false,
      title: {
        display: true,
        text: 'Temperatura (°C)'
      }
    },
    x: {
      title: {
        display: true,
        text: 'Tiempo'
      }
    }
  },
  plugins: {
    legend: {
      position: 'top'
    },
    title: {
      display: true,
      text: 'Comparación de Temperaturas'
    }
  }
}
</script>

<template>
  <div class="chart-container">
    <Line :data="{ labels, datasets }" :options="chartOptions" />
  </div>
</template>

<style scoped>
.chart-container {
  position: relative;
  height: 400px;
  width: 100%;
  max-width: 100%;
}

:deep(canvas) {
  max-height: 400px !important;
  max-width: 100% !important;
}
</style>
