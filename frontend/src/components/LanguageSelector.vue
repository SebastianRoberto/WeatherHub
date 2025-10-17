<template>
  <div class="language-dropdown">
    <button 
      class="dropdown-trigger"
      @click="toggleDropdown"
      :class="{ open: isOpen }"
    >
      <span class="selected-option">
        <span class="flag">{{ currentOption.flag }}</span>
        <span>{{ currentOption.label }}</span>
      </span>
      <svg class="dropdown-arrow" :class="{ rotated: isOpen }" width="12" height="12" viewBox="0 0 12 12" fill="none">
        <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>
    
    <Transition name="dropdown">
      <div v-if="isOpen" class="dropdown-menu">
        <button 
          v-for="option in languageOptions" 
          :key="option.value"
          class="dropdown-option"
          :class="{ active: selectedLanguage === option.value }"
          @click="selectOption(option.value)"
        >
          <span class="flag">{{ option.flag }}</span>
          <span>{{ option.label }}</span>
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18nStore } from '@/stores/i18n'

const i18n = useI18nStore()

const languageOptions = [
  { value: 'es', label: 'Español', flag: '🇪🇸' },
  { value: 'en', label: 'English', flag: '🇺🇸' }
]

const selectedLanguage = ref(i18n.currentLanguage)
const isOpen = ref(false)

// Computed para obtener la opción actual
const currentOption = computed(() => {
  return languageOptions.find(option => option.value === selectedLanguage.value) || languageOptions[0]
})

// Cargar idioma guardado al montar
onMounted(() => {
  i18n.loadLanguage()
  selectedLanguage.value = i18n.currentLanguage
})

// Toggle dropdown
function toggleDropdown() {
  isOpen.value = !isOpen.value
}

// Seleccionar opción
function selectOption(lang) {
  i18n.setLanguage(lang)
  selectedLanguage.value = lang
  isOpen.value = false
  
  // Animación de transición
  document.body.style.transition = 'all 0.3s ease'
  document.body.style.opacity = '0.8'
  
  setTimeout(() => {
    document.body.style.opacity = '1'
    setTimeout(() => {
      document.body.style.transition = ''
    }, 300)
  }, 150)
}

// Cerrar dropdown al hacer click fuera
function handleClickOutside(event) {
  if (!event.target.closest('.language-dropdown')) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* Dropdown como el de unidades de temperatura */
.language-dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-trigger {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-card-bg);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
  min-width: 120px;
}

.dropdown-trigger:hover {
  background-color: var(--color-hover-bg);
  border-color: var(--color-primary);
}

.dropdown-trigger.open {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(var(--color-primary-rgb), 0.1);
}

.selected-option {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  flex: 1;
}

.dropdown-arrow {
  transition: transform var(--transition-fast);
  color: var(--color-text-secondary);
}

.dropdown-arrow.rotated {
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
  overflow: hidden;
  margin-top: 2px;
}

.dropdown-option {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  width: 100%;
  padding: var(--space-sm) var(--space-md);
  border: none;
  background: none;
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-align: left;
}

.dropdown-option:hover {
  background-color: var(--color-hover-bg);
}

.dropdown-option.active {
  background-color: var(--color-primary);
  color: white;
  border-radius: 0;
}

.flag {
  font-size: 1.125rem;
  line-height: 1;
}

/* Transiciones del dropdown */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
