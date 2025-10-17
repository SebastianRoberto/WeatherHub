<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useWeatherStore } from '@/stores/weather'
import { useCitiesStore } from '@/stores/cities'
import { useI18nStore } from '@/stores/i18n'
import LanguageSelector from '@/components/LanguageSelector.vue'
import { api } from '@/services/api'
import { User, Settings, MapPin, LogOut, Edit, Save, X, ThermometerSun, Mail, UserCheck, Lock, Key, Check } from 'lucide-vue-next'

const auth = useAuthStore()
const weather = useWeatherStore()
const cities = useCitiesStore()
const i18n = useI18nStore()

// Estado de edición
const isEditing = ref(false)
const editedName = ref('')
const isLoading = ref(false)
const saveError = ref('')

// Estado de cambio de contraseña
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const passwordError = ref('')
const passwordSuccess = ref('')

// Nuevo flujo de cambio de contraseña
const isPasswordFormEnabled = ref(false)
const isCurrentPasswordValid = ref(false)
const passwordStrength = ref('')
const passwordStrengthLevel = ref(0)
const isConfirmPasswordValid = ref(false)
const confirmPasswordMessage = ref('')
const isPasswordFormValid = ref(false)
const passwordFormStep = ref('edit') // 'edit' | 'confirm'

// Preferencias
const temperatureUnits = [
  { id: 'c', label: 'Celsius', symbol: '°C' },
  { id: 'f', label: 'Fahrenheit', symbol: '°F' },
  { id: 'k', label: 'Kelvin', symbol: 'K' }
]

// Cargar datos iniciales
onMounted(async () => {
  isLoading.value = true
  try {
    // Cargar favoritos para mostrar en el perfil
    await cities.fetchFavorites()
    
    // Inicializar datos de edición
    if (auth.user) {
      editedName.value = auth.user.full_name || ''
    }
  } finally {
    isLoading.value = false
  }
})

// Iniciar edición
function startEditing() {
  editedName.value = auth.user?.full_name || ''
  isEditing.value = true
  saveError.value = ''
}

// Cancelar edición
function cancelEditing() {
  isEditing.value = false
  saveError.value = ''
}

// Limpiar formulario de contraseña
function clearPasswordForm() {
  currentPassword.value = ''
  newPassword.value = ''
  confirmPassword.value = ''
  passwordError.value = ''
  passwordSuccess.value = ''
  isPasswordFormEnabled.value = false
  isCurrentPasswordValid.value = false
  passwordStrength.value = ''
  passwordStrengthLevel.value = 0
  isConfirmPasswordValid.value = false
  confirmPasswordMessage.value = ''
  isPasswordFormValid.value = false
  passwordFormStep.value = 'edit'
}

// Cancelar cambio de contraseña
function cancelPasswordChange() {
  clearPasswordForm()
}

// Habilitar formulario de contraseña
function enablePasswordForm() {
  isPasswordFormEnabled.value = true
  passwordFormStep.value = 'edit'
}

// Validar contraseña actual
async function validateCurrentPassword() {
  if (!currentPassword.value) {
    isCurrentPasswordValid.value = false
    return
  }
  
  // Aquí iría la validación con el backend
  // Por ahora simulamos que es válida si tiene al menos 6 caracteres
  isCurrentPasswordValid.value = currentPassword.value.length >= 6
  
  if (isCurrentPasswordValid.value) {
    // Habilitar campos de nueva contraseña
    passwordFormStep.value = 'confirm'
  }
}

// Calcular fortaleza de contraseña
function calculatePasswordStrength(password) {
  if (!password) {
    passwordStrength.value = ''
    passwordStrengthLevel.value = 0
    return
  }
  
  let strength = 0
  let level = 0
  
  if (password.length >= 6) strength += 1
  if (password.length >= 8) strength += 1
  if (/[a-z]/.test(password)) strength += 1
  if (/[A-Z]/.test(password)) strength += 1
  if (/[0-9]/.test(password)) strength += 1
  if (/[^A-Za-z0-9]/.test(password)) strength += 1
  
  if (strength <= 2) {
    passwordStrength.value = 'Débil'
    level = 1
  } else if (strength <= 4) {
    passwordStrength.value = 'Media'
    level = 2
  } else {
    passwordStrength.value = 'Fuerte'
    level = 3
  }
  
  passwordStrengthLevel.value = level
}

// Validar confirmación de contraseña
function validateConfirmPassword() {
  if (!confirmPassword.value) {
    isConfirmPasswordValid.value = false
    confirmPasswordMessage.value = ''
    return
  }
  
  if (newPassword.value === confirmPassword.value) {
    isConfirmPasswordValid.value = true
    confirmPasswordMessage.value = 'Las contraseñas coinciden'
  } else {
    isConfirmPasswordValid.value = false
    confirmPasswordMessage.value = 'Las contraseñas no coinciden'
  }
  
  // Actualizar validez del formulario
  updatePasswordFormValidity()
}

// Actualizar validez del formulario
function updatePasswordFormValidity() {
  isPasswordFormValid.value = isCurrentPasswordValid.value && 
                              newPassword.value.length >= 6 && 
                              isConfirmPasswordValid.value
}

// Guardar cambios
async function saveProfile() {
  isLoading.value = true
  saveError.value = ''
  
  try {
    // Aquí iría la lógica para guardar el perfil
    // Por ahora, simulamos un guardado exitoso
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // Actualizar el usuario en el store
    // auth.updateUser({ full_name: editedName.value })
    
    isEditing.value = false
  } catch (error) {
    saveError.value = 'Error al guardar los cambios'
    console.error('Error saving profile:', error)
  } finally {
    isLoading.value = false
  }
}

// Computed para fortaleza de contraseña (compatible con el nuevo flujo)
const passwordStrengthClass = computed(() => {
  if (passwordStrengthLevel.value === 1) return 'weak'
  if (passwordStrengthLevel.value === 2) return 'medium'
  if (passwordStrengthLevel.value === 3) return 'strong'
  return 'weak'
})

const passwordStrengthText = computed(() => passwordStrength.value)

// Microinteracciones de input
function onInputFocus(event) {
  event.target.parentElement.classList.add('focused')
}

function onInputBlur(event) {
  event.target.parentElement.classList.remove('focused')
}

// Cambiar contraseña (nuevo flujo)
async function changePassword() {
  if (!isPasswordFormValid.value) return
  
  passwordError.value = ''
  passwordSuccess.value = ''
  isLoading.value = true
  
  try {
    // Llamada real al API para cambiar contraseña
    const response = await api.post('/auth/change-password', {
      current_password: currentPassword.value,
      new_password: newPassword.value
    })
    
    passwordSuccess.value = response.data.message || 'Contraseña cambiada exitosamente'
    
    // Limpiar formulario después de un momento
    setTimeout(() => {
      clearPasswordForm()
    }, 2000)
    
  } catch (error) {
    console.error('Error changing password:', error)
    
    // Manejar diferentes tipos de errores
    if (error.response?.status === 400) {
      passwordError.value = error.response.data.detail || 'Error al cambiar la contraseña'
    } else if (error.response?.status === 401) {
      passwordError.value = 'Sesión expirada. Por favor, inicia sesión nuevamente.'
    } else {
      passwordError.value = 'Error al cambiar la contraseña. Inténtalo de nuevo.'
    }
  } finally {
    isLoading.value = false
  }
}

// Cerrar sesión
function logout() {
  auth.logout()
}

// Formatear fecha
function formatDate(dateStr) {
  if (!dateStr) return '—'
  const date = new Date(dateStr)
  return date.toLocaleDateString('es-ES', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}
</script>

<template>
  <section>
    <!-- Encabezado de página -->
    <div class="page-title">
      <div class="title-with-icon">
        <User size="24" />
        <h1>{{ i18n.t.profile.title }}</h1>
      </div>
      
      <button class="btn btn-danger logout-btn" @click="logout">
        <LogOut size="18" />
        <span>{{ i18n.t.nav.logout }}</span>
      </button>
    </div>
    
    <div class="profile-layout">
      <!-- Información de perfil -->
      <div class="profile-card card">
        <div class="card-header">
          <h3>
            <UserCheck size="18" />
            <span>{{ i18n.t.profile.personalInfo }}</span>
          </h3>
          
          <button 
            v-if="!isEditing" 
            class="btn btn-outline btn-sm"
            @click="startEditing"
          >
            <Edit size="16" />
            <span>{{ i18n.t.common.edit }}</span>
          </button>
        </div>
        
        <div v-if="isEditing" class="profile-edit-form">
          <div class="form-group">
            <label for="name-input">Nombre completo</label>
            <input 
              id="name-input"
              v-model="editedName"
              type="text"
              class="form-input"
              placeholder="Tu nombre completo"
            />
          </div>
          
          <div class="form-group">
            <label for="email-input">Email</label>
            <input 
              id="email-input"
              :value="auth.user?.email"
              type="email"
              class="form-input"
              disabled
              title="El email no se puede cambiar"
            />
            <small>El email no se puede cambiar</small>
          </div>
          
          <div v-if="saveError" class="form-error">
            {{ saveError }}
          </div>
          
          <div class="form-actions">
            <button 
              class="btn btn-outline btn-sm" 
              @click="cancelEditing"
              :disabled="isLoading"
            >
              <X size="16" />
              <span>Cancelar</span>
            </button>
            
            <button 
              class="btn btn-primary btn-sm" 
              @click="saveProfile"
              :disabled="isLoading"
            >
              <Save size="16" />
              <span>Guardar</span>
            </button>
          </div>
        </div>
        
        <div v-else class="profile-info">
          <div class="profile-avatar">
            <div class="avatar">
              {{ auth.user?.full_name?.[0]?.toUpperCase() || auth.user?.email?.[0]?.toUpperCase() || '?' }}
            </div>
          </div>
          
          <div class="profile-details">
            <div class="detail-item">
              <div class="detail-label">{{ i18n.t.profile.name }}</div>
              <div class="detail-value">{{ auth.user?.full_name || '—' }}</div>
            </div>
            
            <div class="detail-item">
              <div class="detail-label">{{ i18n.t.profile.email }}</div>
              <div class="detail-value">
                <Mail size="16" />
                <span>{{ auth.user?.email }}</span>
              </div>
            </div>
            
            <div class="detail-item">
              <div class="detail-label">{{ i18n.t.profile.memberSince }}</div>
              <div class="detail-value">{{ formatDate(auth.user?.created_at) }}</div>
            </div>
            
          </div>
        </div>
        
         <!-- Formulario de cambio de contraseña - Nuevo flujo -->
         <div class="password-change-form-fixed">
           <div class="password-header">
             <h4 class="password-title">
               <Key size="16" />
               <span>Cambiar contraseña</span>
             </h4>
             
             <div class="form-actions-fixed">
               <button 
                 class="btn btn-danger" 
                 @click="cancelPasswordChange"
                 :disabled="isLoading"
               >
                 <X size="16" />
                 <span>Cancelar</span>
               </button>
               
               <!-- Botón principal que cambia entre "Editar" y "Confirmar" -->
               <button 
                 v-if="!isPasswordFormEnabled"
                 class="btn btn-outline" 
                 @click="enablePasswordForm"
                 :disabled="isLoading"
               >
                 <Edit size="16" />
                 <span>Editar</span>
               </button>
               
               <button 
                 v-else
                 class="btn btn-primary" 
                 :class="{ 
                   'btn-disabled': !isPasswordFormValid,
                   'loading': isLoading 
                 }"
                 @click="changePassword"
                 :disabled="isLoading || !isPasswordFormValid"
               >
                 <svg v-if="isLoading" class="animate-spin" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                   <path d="M21 12a9 9 0 11-6.219-8.56"/>
                 </svg>
                 <Key v-else size="16" />
                 <span>{{ isLoading ? 'Cambiando...' : 'Confirmar' }}</span>
               </button>
             </div>
           </div>
           
           <div class="password-form-fixed">
            <div class="form-row-fixed">
              <!-- Campo de contraseña actual - se habilita al hacer click en "Editar" -->
              <div class="form-group-fixed">
                <label for="current-password">Contraseña actual</label>
                <div class="input-with-icon">
                  <Lock size="14" class="input-icon" />
                  <input 
                    id="current-password"
                    v-model="currentPassword"
                    type="password"
                    class="form-input-fixed"
                    :class="{ 'disabled': !isPasswordFormEnabled }"
                    :disabled="!isPasswordFormEnabled"
                    placeholder="••••••••"
                    autocomplete="current-password"
                    @focus="onInputFocus"
                    @blur="onInputBlur"
                    @input="validateCurrentPassword"
                  />
                </div>
              </div>
              
              <!-- Campo de nueva contraseña - se habilita cuando la actual es válida -->
              <div class="form-group-fixed">
                <label for="new-password">Nueva contraseña</label>
                <div class="input-with-icon">
                  <Lock size="14" class="input-icon" />
                  <input 
                    id="new-password"
                    v-model="newPassword"
                    type="password"
                    class="form-input-fixed"
                    :class="{ 'disabled': !isCurrentPasswordValid }"
                    :disabled="!isCurrentPasswordValid"
                    placeholder="••••••••"
                    autocomplete="new-password"
                    @focus="onInputFocus"
                    @blur="onInputBlur"
                    @input="calculatePasswordStrength(newPassword)"
                  />
                </div>
                
                <!-- Indicador de fortaleza de contraseña -->
                <div v-if="newPassword && isCurrentPasswordValid" class="password-strength">
                  <div class="strength-bar">
                    <div 
                      class="strength-fill" 
                      :class="passwordStrengthClass"
                      :style="{ width: passwordStrengthLevel * 33.33 + '%' }"
                    ></div>
                  </div>
                  <span class="strength-text" :class="passwordStrengthClass">
                    {{ passwordStrengthText }}
                  </span>
                </div>
              </div>
              
              <!-- Campo de confirmación - se habilita cuando la nueva contraseña es válida -->
              <div class="form-group-fixed">
                <label for="confirm-password">Confirmar contraseña</label>
                <div class="input-with-icon">
                  <Lock size="14" class="input-icon" />
                  <input 
                    id="confirm-password"
                    v-model="confirmPassword"
                    type="password"
                    class="form-input-fixed"
                    :class="{ 
                      'disabled': !isCurrentPasswordValid,
                      'match': isConfirmPasswordValid,
                      'mismatch': confirmPassword && !isConfirmPasswordValid
                    }"
                    :disabled="!isCurrentPasswordValid"
                    placeholder="••••••••"
                    autocomplete="new-password"
                    @focus="onInputFocus"
                    @blur="onInputBlur"
                    @input="validateConfirmPassword"
                  />
                </div>
                
                <!-- Mensaje de confirmación -->
                <div v-if="confirmPassword && isCurrentPasswordValid" class="confirm-message" :class="{ 'valid': isConfirmPasswordValid, 'invalid': !isConfirmPasswordValid }">
                  <Check v-if="isConfirmPasswordValid" size="14" />
                  <X v-else size="14" />
                  <span>{{ confirmPasswordMessage }}</span>
                </div>
              </div>
            </div>
            
            
            <Transition name="error-fade">
              <div v-if="passwordError" class="form-error-fixed">
                {{ passwordError }}
              </div>
            </Transition>
            
            <Transition name="success-fade">
              <div v-if="passwordSuccess" class="form-success-fixed">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 6L9 17l-5-5"/>
                </svg>
                <span>{{ passwordSuccess }}</span>
              </div>
            </Transition>
            
          </div>
        </div>
      </div>
      
      <!-- Preferencias -->
      <div class="preferences-card card">
        <div class="card-header">
          <h3>
            <Settings size="18" />
            <span>Preferencias</span>
          </h3>
          
          <!-- Selector de idioma en la esquina superior derecha -->
          <div class="header-language-selector">
            <LanguageSelector />
          </div>
        </div>
        
        <div class="preferences-content">
          <div class="preference-group">
            <h4>{{ i18n.t.profile.units }}</h4>
            <p class="preference-description">
              {{ i18n.t.profile.unitsDescription }}
            </p>
            
            <div class="temperature-units">
              <button 
                v-for="unit in temperatureUnits" 
                :key="unit.id"
                class="unit-button"
                :class="{ active: weather.unit === unit.id }"
                @click="weather.unit = unit.id"
              >
                <ThermometerSun size="18" />
                <span>{{ unit.label }} ({{ unit.symbol }})</span>
              </button>
            </div>
          </div>
          
          <div class="preference-group">
            <h4>Ciudades favoritas</h4>
            <p class="preference-description">
              Estas son tus ciudades favoritas. Puedes añadir más desde el buscador en el Dashboard.
            </p>
            
            <div class="favorite-cities">
              <div v-if="cities.favorites.length === 0" class="no-favorites">
                No tienes ciudades favoritas aún.
              </div>
              
              <div v-else class="cities-grid">
                <div 
                  v-for="favorite in cities.favorites" 
                  :key="favorite.city_id"
                  class="city-item"
                >
                  <MapPin size="16" />
                  <span>{{ favorite.city?.name }} {{ favorite.city?.country ? `(${favorite.city?.country})` : '' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.title-with-icon {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.profile-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-xl);
  margin-bottom: var(--space-xl);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-lg);
}

.card-header h3 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.profile-info {
  display: flex;
  gap: var(--space-lg);
}

.profile-avatar {
  flex-shrink: 0;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: var(--radius-full);
  background-color: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 600;
}

.profile-details {
  flex: 1;
}

.detail-item {
  margin-bottom: var(--space-md);
}

.detail-label {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-xs);
}

.detail-value {
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.profile-edit-form {
  display: grid;
  gap: var(--space-md);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.form-group label {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.form-group small {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  margin-top: var(--space-xs);
}

.form-input {
  padding: var(--space-sm) var(--space-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-card-bg);
}

.form-input:disabled {
  background-color: var(--color-hover-bg);
  cursor: not-allowed;
}

.form-error {
  color: var(--color-alert);
  font-size: 0.9rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-sm);
  margin-top: var(--space-sm);
}

.btn-sm {
  padding: var(--space-xs) var(--space-sm);
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.preferences-content {
  display: grid;
  gap: var(--space-xl);
}

.preference-group h4 {
  margin: 0 0 var(--space-xs) 0;
  font-size: 1.1rem;
}

.preference-description {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
  margin-bottom: var(--space-md);
}

.temperature-units {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.unit-button {
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background-color: var(--color-card-bg);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-fast), color var(--transition-normal), background-color var(--transition-normal), border-color var(--transition-normal);
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.unit-button:hover:not(.active) {
  background-color: var(--color-hover-bg);
  border-color: var(--color-primary);
}

.unit-button.active {
  background-color: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.cities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--space-sm);
}

.city-item {
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  background-color: var(--color-hover-bg);
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: 0.9rem;
  transition: background-color var(--transition-normal);
}

.no-favorites {
  color: var(--color-text-secondary);
  font-style: italic;
}

/* Estilos para cambio de contraseña - Siempre visible y fijo */
.password-change-form-fixed {
  margin-top: var(--space-lg);
  padding-top: var(--space-lg);
  border-top: 1px solid var(--color-border);
}

.password-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

.password-title {
  margin: 0;
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-size: 1rem;
  color: var(--color-text-primary);
}

.password-form-fixed {
  display: grid;
  gap: var(--space-md);
}

.form-row-fixed {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: var(--space-md);
}

.form-group-fixed {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-group-fixed label {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.form-input-fixed {
  padding: 8px 10px 8px 30px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background-color: var(--color-card-bg);
  color: var(--color-text-primary);
  font-size: 0.85rem;
  height: 36px;
  transition: all var(--transition-fast);
}

.form-input-fixed:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(30, 136, 229, 0.1);
}

.form-input-fixed.match {
  border-color: var(--color-success);
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
}

.form-input-fixed.mismatch {
  border-color: var(--color-alert);
  box-shadow: 0 0 0 2px rgba(229, 57, 53, 0.1);
}

.input-with-icon .input-icon {
  left: 10px;
  font-size: 14px;
}

.input-with-icon .form-input-fixed {
  padding-left: 30px;
}

.form-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

.form-section-header h4 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-size: 1rem;
  color: var(--color-primary);
}

.password-form-compact {
  display: grid;
  gap: var(--space-sm);
  height: calc(100% - 40px); /* Restar altura del header */
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-sm);
}

.form-group-compact {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-group-compact label {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.form-input-compact {
  padding: 6px 8px 6px 28px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background-color: var(--color-card-bg);
  font-size: 0.85rem;
  height: 32px;
  transition: all var(--transition-fast);
}

.form-input-compact:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(30, 136, 229, 0.1);
}

.form-input-compact.match {
  border-color: var(--color-success);
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
}

.form-input-compact.mismatch {
  border-color: var(--color-alert);
  box-shadow: 0 0 0 2px rgba(229, 57, 53, 0.1);
}

.input-with-icon .input-icon {
  left: 8px;
  font-size: 14px;
}

.input-with-icon .form-input-compact {
  padding-left: 28px;
}

.input-with-icon {
  position: relative;
  transition: all var(--transition-fast);
}

.input-with-icon.focused {
  transform: translateY(-1px);
}

.input-with-icon.focused .input-icon {
  color: var(--color-primary);
  transform: translateY(-50%) scale(1.1);
}

.input-icon {
  position: absolute;
  left: var(--space-md);
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}

.input-with-icon .form-input {
  padding-left: calc(var(--space-md) * 2 + 18px);
  transition: all var(--transition-fast);
}

.input-with-icon .form-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.1);
  transform: translateY(-1px);
}

.input-with-icon .form-input.match {
  border-color: var(--color-success);
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}

.input-with-icon .form-input.mismatch {
  border-color: var(--color-alert);
  box-shadow: 0 0 0 3px rgba(229, 57, 53, 0.1);
}

/* Indicador de fortaleza de contraseña - Fijo */
.password-strength-fixed {
  margin-top: var(--space-xs);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.strength-bar {
  height: 4px;
  background-color: var(--color-hover-bg);
  border-radius: var(--radius-full);
  overflow: hidden;
  position: relative;
}

.strength-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: all var(--transition-normal);
  position: relative;
}

.strength-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.3) 50%, transparent 100%);
  animation: shimmer 2s infinite;
}

.strength-fill.weak {
  background: linear-gradient(90deg, #f44336, #ff9800);
}

.strength-fill.medium {
  background: linear-gradient(90deg, #ff9800, #ffc107);
}

.strength-fill.strong {
  background: linear-gradient(90deg, #4caf50, #8bc34a);
}

.strength-text {
  font-size: 0.8rem;
  font-weight: 500;
  transition: color var(--transition-fast);
}

.strength-text.weak {
  color: #f44336;
}

.strength-text.medium {
  color: #ff9800;
}

.strength-text.strong {
  color: #4caf50;
}

/* Indicador de coincidencia de contraseñas - Fijo */
.password-match-fixed {
  margin-top: var(--space-xs);
}

.match-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.7rem;
  font-weight: 500;
  padding: 4px 6px;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.match-indicator.success {
  color: var(--color-success);
  background-color: rgba(76, 175, 80, 0.1);
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.match-indicator.error {
  color: var(--color-alert);
  background-color: rgba(229, 57, 53, 0.1);
  border: 1px solid rgba(229, 57, 53, 0.3);
}

.dark-theme .match-indicator.success {
  background-color: rgba(76, 175, 80, 0.2);
  border-color: rgba(76, 175, 80, 0.4);
}

.dark-theme .match-indicator.error {
  background-color: rgba(229, 57, 53, 0.2);
  border-color: rgba(229, 57, 53, 0.4);
}

.form-success {
  color: var(--color-success);
  font-size: 0.9rem;
  padding: var(--space-sm);
  background-color: rgba(76, 175, 80, 0.1);
  border-radius: var(--radius-md);
  border: 1px solid rgba(76, 175, 80, 0.3);
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-weight: 500;
}

.form-error-compact {
  color: var(--color-alert);
  font-size: 0.75rem;
  padding: 4px 6px;
  background-color: rgba(229, 57, 53, 0.1);
  border-radius: var(--radius-sm);
  border: 1px solid rgba(229, 57, 53, 0.3);
}

.form-success-compact {
  color: var(--color-success);
  font-size: 0.75rem;
  padding: 4px 6px;
  background-color: rgba(76, 175, 80, 0.1);
  border-radius: var(--radius-sm);
  border: 1px solid rgba(76, 175, 80, 0.3);
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
}

.form-actions-fixed {
  display: flex;
  gap: var(--space-sm);
}

.form-error-fixed {
  color: var(--color-alert);
  font-size: 0.8rem;
  padding: 6px 8px;
  background-color: rgba(229, 57, 53, 0.1);
  border-radius: var(--radius-sm);
  border: 1px solid rgba(229, 57, 53, 0.3);
}

.form-success-fixed {
  color: var(--color-success);
  font-size: 0.8rem;
  padding: 6px 8px;
  background-color: rgba(76, 175, 80, 0.1);
  border-radius: var(--radius-sm);
  border: 1px solid rgba(76, 175, 80, 0.3);
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
}

.dark-theme .form-success {
  background-color: rgba(76, 175, 80, 0.2);
  border-color: rgba(76, 175, 80, 0.4);
}

.profile-actions {
  margin-top: var(--space-lg);
  padding-top: var(--space-lg);
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: center;
}

/* Botón de cerrar sesión */
/* Botón de cerrar sesión */
.logout-btn {
  background-color: #dc3545;
  color: white;
  border: 1px solid #dc3545;
  transition: all var(--transition-fast);
}

.logout-btn:hover {
  background-color: #c82333;
  border-color: #bd2130;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3);
}

.dark-theme .logout-btn {
  background-color: #dc3545;
  color: white;
  border-color: #dc3545;
}

.dark-theme .logout-btn:hover {
  background-color: #c82333;
  border-color: #bd2130;
  box-shadow: 0 4px 8px rgba(220, 53, 69, 0.4);
}

/* Botón de cancelar en cambio de contraseña */
.btn-danger {
  background-color: #dc3545;
  color: white;
  border: 1px solid #dc3545;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  font-weight: 500;
}

.btn-danger:hover {
  background-color: #c82333;
  border-color: #bd2130;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3);
}

.btn-danger:disabled {
  background-color: #6c757d;
  border-color: #6c757d;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.dark-theme .btn-danger {
  background-color: #dc3545;
  color: white;
  border-color: #dc3545;
}

.dark-theme .btn-danger:hover {
  background-color: #c82333;
  border-color: #bd2130;
  box-shadow: 0 4px 8px rgba(220, 53, 69, 0.4);
}

/* Animaciones del formulario independiente */
.password-form-enter-active,
.password-form-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  transform-origin: center;
}

.password-form-enter-from {
  opacity: 0;
  transform: scale(0.95) translateY(20px);
}

.password-form-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-20px);
}

.password-form-enter-to,
.password-form-leave-from {
  opacity: 1;
  transform: scale(1) translateY(0);
}

.error-fade-enter-active,
.error-fade-leave-active {
  transition: all 0.3s ease;
}

.error-fade-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.error-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.success-fade-enter-active,
.success-fade-leave-active {
  transition: all 0.3s ease;
}

.success-fade-enter-from {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

.success-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

/* Animación de shimmer para la barra de fortaleza */
@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* Botón de carga */
.btn.loading {
  position: relative;
  overflow: hidden;
}

.btn.loading::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: loading-shimmer 1.5s infinite;
}

@keyframes loading-shimmer {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
}

/* Estilos para el selector de idioma en el header */
.header-language-selector {
  display: flex;
  align-items: center;
}

/* Estilos para el card-header con selector */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Animación de transición para el cambio de idioma */
.language-transition {
  transition: all 0.3s ease;
}

.language-transition-enter-active,
.language-transition-leave-active {
  transition: all 0.3s ease;
}

.language-transition-enter-from,
.language-transition-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* Estilos para el nuevo flujo de cambio de contraseña */
.form-input-fixed.disabled {
  background-color: var(--color-bg-secondary);
  color: var(--color-text-disabled);
  cursor: not-allowed;
  opacity: 0.6;
}

.password-strength {
  margin-top: var(--space-xs);
}

.strength-bar {
  height: 4px;
  background-color: var(--color-border);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: var(--space-xs);
}

.strength-fill {
  height: 100%;
  transition: all 0.3s ease;
  border-radius: 2px;
}

.strength-fill.weak {
  background-color: #dc3545;
}

.strength-fill.medium {
  background-color: #ffc107;
}

.strength-fill.strong {
  background-color: #28a745;
}

.strength-text {
  font-size: 0.8rem;
  font-weight: 500;
}

.strength-text.weak {
  color: #dc3545;
}

.strength-text.medium {
  color: #ffc107;
}

.strength-text.strong {
  color: #28a745;
}

.confirm-message {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  margin-top: var(--space-xs);
  font-size: 0.8rem;
  font-weight: 500;
}

.confirm-message.valid {
  color: #28a745;
}

.confirm-message.invalid {
  color: #dc3545;
}

.form-input-fixed.match {
  border-color: #28a745;
  box-shadow: 0 0 0 2px rgba(40, 167, 69, 0.2);
}

.form-input-fixed.mismatch {
  border-color: #dc3545;
  box-shadow: 0 0 0 2px rgba(220, 53, 69, 0.2);
}

/* Botón deshabilitado para el flujo de contraseña */
.btn-disabled {
  background-color: #6c757d !important;
  border-color: #6c757d !important;
  color: #fff !important;
  cursor: not-allowed !important;
  opacity: 0.6 !important;
}

.btn-disabled:hover {
  background-color: #6c757d !important;
  border-color: #6c757d !important;
  transform: none !important;
  box-shadow: none !important;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .profile-layout {
    grid-template-columns: 1fr;
  }
  
  .profile-info {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .profile-details {
    width: 100%;
  }
  
  .detail-value {
    justify-content: center;
  }
  
  .cities-grid {
    grid-template-columns: 1fr;
  }
}
</style>