<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter, RouterLink } from 'vue-router'
import { Mail, Lock, User, AlertCircle, Loader2, UserPlus } from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()
const email = ref('')
const password = ref('')
const passwordConfirm = ref('')
const full_name = ref('')
const error = ref('')
const isLoading = ref(false)
// Eliminado: acuerdo de términos (ya no se requiere)

// Validación básica del formulario
const isEmailValid = computed(() => {
  if (!email.value) return true
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email.value)
})

const isPasswordValid = computed(() => {
  return !password.value || password.value.length >= 6
})

const doPasswordsMatch = computed(() => {
  return !passwordConfirm.value || password.value === passwordConfirm.value
})

const isFormValid = computed(() => {
  return email.value && 
         password.value && 
         passwordConfirm.value &&
         isEmailValid.value && 
         isPasswordValid.value && 
         doPasswordsMatch.value
})

// Enviar formulario
async function onSubmit() {
  if (!isFormValid.value) return
  
  error.value = ''
  isLoading.value = true
  
  try {
    await auth.register({ 
      email: email.value, 
      password: password.value, 
      full_name: full_name.value 
    })
    router.push({ name: 'dashboard' })
  } catch (error) {
    error.value = 'No se pudo completar el registro. El email podría estar en uso.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="auth-container">
    <div class="auth-card card">
      <div class="auth-header">
        <h1>Crear cuenta</h1>
        <p class="auth-subtitle">Únete a WeatherHub para acceder a todas las funcionalidades</p>
      </div>
      
      <form @submit.prevent="onSubmit" class="auth-form">
        <!-- Nombre completo -->
        <div class="form-group">
          <label for="full_name">Nombre completo</label>
          <div class="input-with-icon">
            <User size="18" class="input-icon" />
            <input 
              id="full_name" 
              v-model="full_name" 
              type="text" 
              placeholder="Tu nombre completo" 
              autocomplete="name"
            />
          </div>
        </div>
        
        <!-- Email -->
        <div class="form-group">
          <label for="email">Email</label>
          <div class="input-with-icon" :class="{ 'error': email && !isEmailValid }">
            <Mail size="18" class="input-icon" />
            <input 
              id="email" 
              v-model="email" 
              type="email" 
              placeholder="tu@email.com" 
              required
              autocomplete="email"
            />
          </div>
          <div class="error-message-container">
            <Transition name="error-fade">
              <p v-if="email && !isEmailValid" class="input-error">
                Por favor ingresa un email válido
              </p>
            </Transition>
          </div>
        </div>
        
        <!-- Contraseña -->
        <div class="form-group">
          <label for="password">Contraseña</label>
          <div class="input-with-icon" :class="{ 'error': password && !isPasswordValid }">
            <Lock size="18" class="input-icon" />
            <input 
              id="password" 
              v-model="password" 
              type="password" 
              placeholder="••••••••" 
              required
              autocomplete="new-password"
            />
          </div>
          <div class="error-message-container">
            <Transition name="error-fade">
              <p v-if="password && !isPasswordValid" class="input-error">
                La contraseña debe tener al menos 6 caracteres
              </p>
            </Transition>
          </div>
        </div>
        
        <!-- Confirmar contraseña -->
        <div class="form-group">
          <label for="passwordConfirm">Confirmar contraseña</label>
          <div class="input-with-icon" :class="{ 'error': passwordConfirm && !doPasswordsMatch }">
            <Lock size="18" class="input-icon" />
            <input 
              id="passwordConfirm" 
              v-model="passwordConfirm" 
              type="password" 
              placeholder="••••••••" 
              required
              autocomplete="new-password"
            />
          </div>
          <div class="error-message-container">
            <Transition name="error-fade">
              <p v-if="passwordConfirm && !doPasswordsMatch" class="input-error">
                Las contraseñas no coinciden
              </p>
            </Transition>
          </div>
        </div>
        
        <!-- Eliminado: Términos y condiciones -->
        
        <!-- Error general -->
        <div class="error-message-container">
          <Transition name="error-fade">
            <div v-if="error" class="auth-error">
              <AlertCircle size="16" />
              <span>{{ error }}</span>
            </div>
          </Transition>
        </div>
        
        <!-- Botón de envío -->
        <button 
          type="submit" 
          class="btn-auth" 
          :disabled="!isFormValid || isLoading"
        >
          <Loader2 v-if="isLoading" class="animate-spin" size="18" />
          <UserPlus v-else size="18" />
          <span>Crear cuenta</span>
        </button>
      </form>
      
      <!-- Enlace para login -->
      <div class="auth-footer">
        <p>¿Ya tienes una cuenta? <RouterLink to="/login" class="auth-link">Iniciar sesión</RouterLink></p>
      </div>
    </div>
    
    <!-- Información adicional -->
    <div class="auth-info">
      <div class="info-card card">
        <h3>Beneficios de registrarte</h3>
        <p>Crea una cuenta para acceder a todas las funcionalidades de WeatherHub y personalizar tu experiencia.</p>
        <ul class="feature-list">
          <li>Guarda tus ciudades favoritas</li>
          <li>Configura alertas personalizadas</li>
          <li>Accede a datos históricos detallados</li>
          <li>Exporta datos para tus análisis</li>
          <li>Personaliza tus preferencias</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-xl);
  max-width: 1000px;
  margin: 0 auto;
  padding: var(--space-xl) var(--space-md);
  min-height: calc(100vh - var(--header-height) - var(--footer-height));
  align-items: center;
}

.auth-card {
  padding: var(--space-xl);
}

.auth-header {
  margin-bottom: var(--space-xl);
  text-align: center;
}

.auth-header h1 {
  margin-bottom: var(--space-xs);
  font-size: 1.75rem;
}

.auth-subtitle {
  color: var(--color-text-secondary);
  margin: 0;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

label {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.input-with-icon {
  position: relative;
}

.input-icon {
  position: absolute;
  left: var(--space-md);
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-secondary);
}

.input-with-icon input {
  width: 100%;
  padding: var(--space-md) var(--space-md) var(--space-md) calc(var(--space-md) * 2 + 18px);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-card-bg);
  color: var(--color-text-primary);
  transition: all var(--transition-fast), color var(--transition-normal), background-color var(--transition-normal);
}

.input-with-icon input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(30, 136, 229, 0.2);
}

.input-with-icon.error input {
  border-color: var(--color-alert);
}

.error-message-container {
  min-height: 20px;
  display: flex;
  align-items: flex-start;
}

.input-error {
  color: var(--color-alert);
  font-size: 0.85rem;
  margin: var(--space-xs) 0 0;
}

.terms-agreement {
  margin-top: var(--space-xs);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  cursor: pointer;
  user-select: none;
  font-size: 0.9rem;
}

.checkbox-label input {
  margin: 0;
}

.terms-link {
  color: var(--color-primary);
  text-decoration: none;
}

.terms-link:hover {
  text-decoration: underline;
}

.auth-error {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  color: var(--color-alert);
  font-size: 0.9rem;
  padding: var(--space-sm);
  background-color: rgba(229, 57, 53, 0.1);
  border-radius: var(--radius-md);
  transition: background-color var(--transition-normal);
  width: 100%;
}

.dark-theme .auth-error {
  background-color: rgba(229, 57, 53, 0.2);
}

.btn-auth {
  padding: var(--space-md);
  border-radius: var(--radius-md);
  border: none;
  background-color: var(--color-secondary);
  color: white;
  font-weight: 700;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.btn-auth:hover:not(:disabled) {
  background-color: var(--color-secondary-dark);
}

.btn-auth:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.auth-footer {
  margin-top: var(--space-xl);
  text-align: center;
  color: var(--color-text-secondary);
}

.auth-link {
  color: var(--color-primary);
  font-weight: 500;
}

.auth-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.info-card {
  padding: var(--space-xl);
  background-color: var(--color-secondary);
  color: white;
}

.info-card h3 {
  margin-top: 0;
  margin-bottom: var(--space-md);
  font-size: 1.5rem;
}

.info-card p {
  margin-bottom: var(--space-lg);
  opacity: 0.9;
}

.feature-list {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.feature-list li {
  padding: var(--space-sm) 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
}

.feature-list li::before {
  content: "✓";
  margin-right: var(--space-sm);
  font-weight: bold;
}

.feature-list li:last-child {
  border-bottom: none;
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

/* Animaciones para mensajes de error */
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

/* Responsive adjustments */
@media (max-width: 768px) {
  .auth-container {
    grid-template-columns: 1fr;
    padding: var(--space-lg) var(--space-sm);
  }
  
  .auth-info {
    display: none;
  }
}
</style>