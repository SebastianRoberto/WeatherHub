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
  series: { type: Array, required: true } // [{label, data}]
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
      text: 'Historial de Temperatura'
    }
  }
}
</script>

<template>
  <div class="chart-container">
    <Line :data="{ labels, datasets: series }" :options="chartOptions" />
  </div>
</template>

<style scoped>
.chart-container {
  position: relative;
  height: 380px;
  width: 100%;
  max-width: 100%;
}

:deep(canvas) {
  max-height: 380px !important;
  max-width: 100% !important;
}
</style>
