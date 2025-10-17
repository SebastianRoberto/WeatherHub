<template>
  <div class="custom-dropdown" :class="{ 'is-open': isOpen }">
    <div class="dropdown-trigger" @click="toggleDropdown">
      <div class="dropdown-icon" v-if="icon">
        <component :is="icon" size="16" />
      </div>
      <span class="dropdown-value">{{ displayValue }}</span>
      <div class="dropdown-arrow" :class="{ 'is-open': isOpen }">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="m6 9 6 6 6-6"/>
        </svg>
      </div>
    </div>
    
    <Transition name="dropdown">
      <div v-if="isOpen" class="dropdown-menu">
        <div 
          v-for="option in options" 
          :key="option.value"
          class="dropdown-option"
          :class="{ 'is-selected': option.value === modelValue }"
          @click="selectOption(option)"
        >
          <span class="option-label">{{ option.label }}</span>
          <button 
            v-if="option.cityId" 
            class="favorite-button" 
            @click.stop="toggleFavorite(option)"
            :title="option.isFavorite ? 'Quitar de favoritos' : 'Añadir a favoritos'"
          >
            <Star v-if="option.isFavorite" size="16" fill="#FFA000" stroke="#FFA000" />
            <StarOff v-else size="16" />
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Star, StarOff } from 'lucide-vue-next'
import { useCitiesStore } from '@/stores/cities'

const cities = useCitiesStore()

const props = defineProps({
  modelValue: {
    type: [String, Number],
    required: true
  },
  options: {
    type: Array,
    required: true
  },
  placeholder: {
    type: String,
    default: 'Seleccionar...'
  },
  icon: {
    type: [String, Object, Function],
    default: null
  }
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)

const displayValue = computed(() => {
  const selectedOption = props.options.find(option => option.value === props.modelValue)
  return selectedOption ? selectedOption.label : props.placeholder
})

function toggleDropdown() {
  isOpen.value = !isOpen.value
}

function selectOption(option) {
  emit('update:modelValue', option.value)
  isOpen.value = false
}

function closeDropdown(event) {
  if (!event.target.closest('.custom-dropdown')) {
    isOpen.value = false
  }
}

// Función para alternar favoritos
async function toggleFavorite(option) {
  if (option.cityId) {
    if (option.isFavorite) {
      await cities.removeFavorite(option.cityId)
    } else {
      await cities.addFavorite(option.cityId)
    }
  }
}

onMounted(() => {
  document.addEventListener('click', closeDropdown)
})

onUnmounted(() => {
  document.removeEventListener('click', closeDropdown)
})
</script>

<style scoped>
.custom-dropdown {
  position: relative;
  width: 100%;
  min-width: 0; /* Permite que se comprima si es necesario */
}

.dropdown-trigger {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-xs) var(--space-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-card-bg);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  min-height: 32px;
  font-size: 14px;
  line-height: 1.4;
}

.dropdown-trigger:hover {
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.dropdown-trigger:focus-within {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.1);
}

.dropdown-icon {
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.dropdown-value {
  flex: 1;
  text-align: center; /* Centrar el texto para que se vea bien con ancho fijo */
  font-size: 14px;
  line-height: 1.4;
}

.dropdown-arrow {
  flex-shrink: 0;
  color: var(--color-text-secondary);
  transition: transform var(--transition-fast);
}

.dropdown-arrow.is-open {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 1000;
  background-color: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  margin-top: 4px;
  overflow: hidden;
  max-height: 200px; /* Limitar a ~5 elementos */
  overflow-y: auto;
}

.dropdown-option {
  padding: var(--space-xs) var(--space-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-size: 14px;
  line-height: 1.4;
  color: var(--color-text-primary);
  border-bottom: 1px solid var(--color-border);
  min-height: 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.option-label {
  flex: 1;
}

.favorite-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
  margin-left: 8px;
}

.favorite-button:hover {
  background-color: rgba(0, 0, 0, 0.05);
  transform: scale(1.1);
}

.dropdown-option:last-child {
  border-bottom: none;
}

.dropdown-option:hover {
  background-color: var(--color-hover-bg);
}

.dropdown-option.is-selected {
  background-color: var(--color-primary);
  color: white;
}

/* Dark theme */
.dark-theme .dropdown-trigger {
  background-color: #181A1B;
  color: #fff;
  border-color: #333;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.dark-theme .dropdown-trigger:hover {
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}

.dark-theme .dropdown-trigger:focus-within {
  box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.2);
}

.dark-theme .dropdown-menu {
  background-color: #181A1B;
  border-color: #333;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}

.dark-theme .dropdown-option {
  color: #fff;
  border-bottom-color: #333;
}

.dark-theme .dropdown-option:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.dark-theme .dropdown-option.is-selected {
  background-color: var(--color-primary);
  color: white;
}

/* Scrollbar personalizado para mejor UX */
.dropdown-menu::-webkit-scrollbar {
  width: 6px;
}

.dropdown-menu::-webkit-scrollbar-track {
  background: transparent;
}

.dropdown-menu::-webkit-scrollbar-thumb {
  background-color: var(--color-border);
  border-radius: 3px;
}

.dropdown-menu::-webkit-scrollbar-thumb:hover {
  background-color: var(--color-text-secondary);
}

.dark-theme .dropdown-menu::-webkit-scrollbar-thumb {
  background-color: #444;
}

.dark-theme .dropdown-menu::-webkit-scrollbar-thumb:hover {
  background-color: #666;
}

/* Animations */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all var(--transition-normal);
  transform-origin: top;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: scaleY(0) translateY(-10px);
}

.dropdown-enter-to,
.dropdown-leave-from {
  opacity: 1;
  transform: scaleY(1) translateY(0);
}
</style>
