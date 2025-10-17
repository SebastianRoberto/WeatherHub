<template>
  <div class="beautiful-dropdown" :class="{ 'open': isOpen, 'disabled': disabled }">
    <button 
      class="dropdown-trigger"
      @click="toggleDropdown"
      :disabled="disabled"
      type="button"
    >
      <span class="dropdown-value">{{ displayValue }}</span>
      <div class="dropdown-arrow" :class="{ 'rotated': isOpen }">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
          <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
    </button>
    
    <Transition name="dropdown">
      <div v-if="isOpen" class="dropdown-menu">
        <div class="dropdown-options">
          <button
            v-for="option in options"
            :key="option.value"
            class="dropdown-option"
            :class="{ 'selected': option.value === modelValue }"
            @click="selectOption(option)"
            type="button"
          >
            <span class="option-text">{{ option.label }}</span>
            <div v-if="option.value === modelValue" class="option-check">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M13.5 4.5L6 12L2.5 8.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  options: {
    type: Array,
    required: true
  },
  placeholder: {
    type: String,
    default: 'Seleccionar...'
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)

const displayValue = computed(() => {
  const selectedOption = props.options.find(option => option.value === props.modelValue)
  return selectedOption ? selectedOption.label : props.placeholder
})

const toggleDropdown = () => {
  if (!props.disabled) {
    isOpen.value = !isOpen.value
  }
}

const selectOption = (option) => {
  emit('update:modelValue', option.value)
  isOpen.value = false
}

const closeDropdown = (event) => {
  if (!event.target.closest('.beautiful-dropdown')) {
    isOpen.value = false
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
.beautiful-dropdown {
  position: relative;
  width: 100%;
  min-width: 120px;
}

.dropdown-trigger {
  width: 100%;
  padding: 12px 16px;
  background-color: var(--color-bg);
  border: 2px solid var(--color-border);
  border-radius: 8px;
  color: var(--color-text);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  outline: none;
}

.dropdown-trigger:hover:not(:disabled) {
  border-color: var(--color-primary);
  background-color: var(--color-bg-secondary);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.dropdown-trigger:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.1);
}

.dropdown-trigger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.dropdown-value {
  flex: 1;
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dropdown-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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
  margin-top: 4px;
  background-color: var(--color-bg);
  border: 2px solid var(--color-border);
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  overflow: hidden;
  backdrop-filter: blur(8px);
}

.dropdown-options {
  max-height: 200px;
  overflow-y: auto;
  padding: 4px 0;
}

.dropdown-option {
  width: 100%;
  padding: 12px 16px;
  background: none;
  border: none;
  color: var(--color-text);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  text-align: left;
  outline: none;
}

.dropdown-option:hover {
  background-color: var(--color-bg-secondary);
  color: var(--color-primary);
}

.dropdown-option.selected {
  background-color: var(--color-primary);
  color: white;
}

.dropdown-option.selected:hover {
  background-color: var(--color-primary);
  color: white;
}

.option-text {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.option-check {
  display: flex;
  align-items: center;
  justify-content: center;
  color: currentColor;
}

/* Transiciones suaves */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.dropdown-enter-from {
  opacity: 0;
  transform: translateY(-8px) scale(0.95);
}

.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.95);
}

/* Scrollbar personalizado */
.dropdown-options::-webkit-scrollbar {
  width: 6px;
}

.dropdown-options::-webkit-scrollbar-track {
  background: transparent;
}

.dropdown-options::-webkit-scrollbar-thumb {
  background-color: var(--color-border);
  border-radius: 3px;
}

.dropdown-options::-webkit-scrollbar-thumb:hover {
  background-color: var(--color-text-secondary);
}

/* Estados especiales */
.beautiful-dropdown.open .dropdown-trigger {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.1);
}

.beautiful-dropdown.disabled .dropdown-trigger {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Modo claro */
.light-theme .dropdown-trigger {
  background-color: #ffffff;
  border-color: #e0e0e0;
  color: #333333;
}

.light-theme .dropdown-trigger:hover:not(:disabled) {
  border-color: var(--color-primary);
  background-color: #f8f9fa;
}

.light-theme .dropdown-menu {
  background-color: #ffffff;
  border-color: #e0e0e0;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}

.light-theme .dropdown-option {
  color: #333333;
}

.light-theme .dropdown-option:hover {
  background-color: #f8f9fa;
  color: var(--color-primary);
}

.light-theme .dropdown-option.selected {
  background-color: var(--color-primary);
  color: white;
}

/* Modo oscuro */
.dark-theme .dropdown-trigger {
  background-color: #2a2a2a;
  border-color: #404040;
  color: #ffffff;
}

.dark-theme .dropdown-trigger:hover:not(:disabled) {
  border-color: var(--color-primary);
  background-color: #333333;
}

.dark-theme .dropdown-menu {
  background-color: #2a2a2a;
  border-color: #404040;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.dark-theme .dropdown-option {
  color: #ffffff;
}

.dark-theme .dropdown-option:hover {
  background-color: #333333;
  color: var(--color-primary);
}

.dark-theme .dropdown-option.selected {
  background-color: var(--color-primary);
  color: white;
}
</style>
