<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useCitiesStore } from '@/stores/cities'
import { useWeatherStore } from '@/stores/weather'
import { Search, MapPin, Star, StarOff, Loader2 } from 'lucide-vue-next'

const cities = useCitiesStore()
const weather = useWeatherStore()
const query = ref('')
const isSearching = ref(false)
const showResults = ref(false)
const recentSearches = ref([])
const searchTimeout = ref(null)

// Cargar búsquedas recientes desde localStorage al iniciar
onMounted(() => {
  const saved = localStorage.getItem('wh_recent_searches')
  if (saved) {
    try {
      recentSearches.value = JSON.parse(saved)
    } catch (e) {
      console.error('Error loading recent searches', e)
    }
  }
})

// Filtrar resultados para mostrar solo los que coinciden con la búsqueda
const filteredResults = computed(() => {
  if (!query.value.trim()) return []
  
  return cities.list.filter(city => {
    const searchLower = query.value.toLowerCase()
    return city.name.toLowerCase().includes(searchLower) || 
           (city.country && city.country.toLowerCase().includes(searchLower))
  })
})

// Verificar si una ciudad es favorita
const isFavorite = (cityId) => {
  return cities.favorites.some(f => f.city_id === cityId)
}

// Realizar búsqueda con debounce
function debouncedSearch() {
  clearTimeout(searchTimeout.value)
  
  if (!query.value.trim()) {
    isSearching.value = false
    return
  }
  
  isSearching.value = true
  
  searchTimeout.value = setTimeout(async () => {
    await cities.fetchCities({ search: query.value })
    isSearching.value = false
    showResults.value = true
  }, 300)
}

// Observar cambios en la consulta para realizar búsqueda automática
watch(query, () => {
  debouncedSearch()
})

// Añadir o quitar de favoritos
async function toggleFavorite(city) {
  if (isFavorite(city.id)) {
    await cities.removeFavorite(city.id)
  } else {
    await cities.addFavorite(city.id)
  }
  
  // Actualizar inmediatamente los datos meteorológicos de favoritos
  // para que el cambio se refleje en el Dashboard
  await weather.fetchFavoritesCurrent()
}

// Seleccionar una ciudad y cargar su clima
async function selectCity(city) {
  // Guardar en búsquedas recientes
  const existingIndex = recentSearches.value.findIndex(s => s.id === city.id)
  if (existingIndex !== -1) {
    recentSearches.value.splice(existingIndex, 1)
  }
  
  recentSearches.value.unshift({
    id: city.id,
    name: city.name,
    country: city.country
  })
  
  // Limitar a 5 búsquedas recientes
  if (recentSearches.value.length > 5) {
    recentSearches.value = recentSearches.value.slice(0, 5)
  }
  
  // Guardar en localStorage
  localStorage.setItem('wh_recent_searches', JSON.stringify(recentSearches.value))
  
  // Cargar clima
  await weather.fetchCurrent(city.name)
  
  // Limpiar búsqueda
  query.value = ''
  showResults.value = false
}

// Cerrar resultados al hacer clic fuera
function handleClickOutside(event) {
  if (!event.target.closest('.search-container')) {
    showResults.value = false
  }
}

// Registrar evento para cerrar resultados al hacer clic fuera
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})
</script>

<template>
  <div class="search-container">
    <div class="search-input-wrapper">
      <input 
        v-model="query" 
        class="search-input" 
        placeholder="Buscar ciudad (ej. Madrid, París, Londres...)" 
        @keyup.enter="debouncedSearch"
        @focus="showResults = !!query.trim()"
      />
      <div class="search-icon">
        <Loader2 v-if="isSearching" class="animate-spin" size="18" />
        <Search v-else size="18" />
      </div>
    </div>
    
    <div v-if="showResults" class="search-results">
      <!-- Resultados de búsqueda -->
      <div v-if="filteredResults.length > 0">
        <div class="search-results-header">
          <h4>Resultados</h4>
        </div>
        <div class="search-results-list">
          <div 
            v-for="city in filteredResults" 
            :key="city.id" 
            class="search-result-item"
            @click="selectCity(city)"
          >
            <div class="search-result-info">
              <MapPin size="16" />
              <span>{{ city.name }} <small v-if="city.country">({{ city.country }})</small></span>
            </div>
            <button 
              class="favorite-button" 
              @click.stop="toggleFavorite(city)"
              :title="isFavorite(city.id) ? 'Quitar de favoritos' : 'Añadir a favoritos'"
            >
              <Star v-if="isFavorite(city.id)" size="18" fill="#FFA000" stroke="#FFA000" />
              <StarOff v-else size="18" />
            </button>
          </div>
        </div>
      </div>
      
      <!-- Búsquedas recientes -->
      <div v-else-if="recentSearches.length > 0 && !query.trim()">
        <div class="search-results-header">
          <h4>Búsquedas recientes</h4>
        </div>
        <div class="search-results-list">
          <div 
            v-for="city in recentSearches" 
            :key="city.id" 
            class="search-result-item"
            @click="selectCity(city)"
          >
            <div class="search-result-info">
              <MapPin size="16" />
              <span>{{ city.name }} <small v-if="city.country">({{ city.country }})</small></span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- No hay resultados -->
      <div v-else-if="query.trim() && !isSearching" class="search-empty">
        <p>No se encontraron ciudades que coincidan con "{{ query }}"</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-container {
  position: relative;
  width: 100%;
  max-width: 600px;
  margin: 0 auto var(--space-lg);
}

.search-input-wrapper {
  position: relative;
  overflow: visible;
}

.search-input {
  width: 100%;
  padding: var(--space-md);
  padding-right: 40px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  font-size: 1rem;
  transition: all var(--transition-fast);
  background-color: var(--color-card-bg);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(30, 136, 229, 0.2);
}

.search-icon {
  position: absolute;
  right: var(--space-md);
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-results {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  width: 100%;
  background-color: var(--color-card-bg);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  z-index: 1001;
  overflow: hidden;
  border: 1px solid var(--color-border);
}

.search-results-header {
  padding: var(--space-sm) var(--space-md);
  background-color: rgba(0, 0, 0, 0.02);
  border-bottom: 1px solid var(--color-border);
}

.search-results-header h4 {
  margin: 0;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.search-results-list {
  max-height: 250px;
  overflow-y: auto;
}

/* Scrollbar personalizado para mejor UX */
.search-results-list::-webkit-scrollbar {
  width: 6px;
}
.search-results-list::-webkit-scrollbar-track {
  background: transparent;
}
.search-results-list::-webkit-scrollbar-thumb {
  background-color: var(--color-border);
  border-radius: 3px;
}
.search-results-list::-webkit-scrollbar-thumb:hover {
  background-color: var(--color-text-secondary);
}

.dark-theme .search-results-list::-webkit-scrollbar-thumb {
  background-color: #444;
}
.dark-theme .search-results-list::-webkit-scrollbar-thumb:hover {
  background-color: #666;
}

.search-result-item {
  padding: var(--space-md);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.search-result-item:last-child {
  border-bottom: none;
}

.search-result-item:hover {
  background-color: rgba(0, 0, 0, 0.03);
}

.search-result-info {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.search-result-info small {
  color: var(--color-text-secondary);
  font-size: 0.85rem;
}

.favorite-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--space-xs);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}

.favorite-button:hover {
  background-color: rgba(0, 0, 0, 0.05);
  transform: scale(1.1);
}

.search-empty {
  padding: var(--space-lg);
  text-align: center;
  color: var(--color-text-secondary);
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
