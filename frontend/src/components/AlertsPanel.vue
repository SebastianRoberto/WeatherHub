<script setup>
import { onMounted } from 'vue'
import { useAlertsStore } from '@/stores/alerts'

const alerts = useAlertsStore()

onMounted(() => alerts.fetchAlerts(true))
</script>

<template>
  <div class="panel">
    <h3>Mis alertas</h3>
    <ul class="list">
      <li v-for="a in alerts.list" :key="a.id">
        <div>
          <strong>#{{ a.id }}</strong> – Ciudad {{ a.city_id }} – {{ a.metric }} {{ a.operator }} {{ a.threshold }} {{ a.unit || '' }}
        </div>
        <div class="actions">
          <button @click="alerts.updateAlert(a.id, { paused: !a.paused })">{{ a.paused ? 'Reanudar' : 'Pausar' }}</button>
          <button class="danger" @click="alerts.deleteAlert(a.id)">Eliminar</button>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.panel { border: 1px solid #eee; border-radius: 12px; padding: 1rem; background: #fff; }
.list { display: grid; gap: 0.5rem; }
.list li { display:flex; align-items:center; justify-content:space-between; padding: 0.5rem; border: 1px solid #f3f3f3; border-radius: 10px; }
.actions { display:flex; gap: 0.5rem; }
button { padding: 0.4rem 0.6rem; border-radius: 8px; border: 0; background: #2c7be5; color: #fff; cursor: pointer; }
button.danger { background: #d64545; }
</style>
