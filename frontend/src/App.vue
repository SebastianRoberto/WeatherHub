<script setup>

import { ref, onMounted, watch } from 'vue'
import { RouterView, RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useI18nStore } from '@/stores/i18n'
import UnitSelector from '@/components/UnitSelector.vue'
import { Menu, X, Cloud, Sun, Moon, User, LogOut, Github, Linkedin, Globe } from 'lucide-vue-next'

const auth = useAuthStore()
const i18n = useI18nStore()
const router = useRouter()
const mobileMenuOpen = ref(false)
const darkMode = ref(false)
// Redirigir al login si el usuario deja de estar autenticado
watch(
  () => auth.isAuthenticated,
  (isAuth) => {
    if (!isAuth) {
      router.push({ name: 'login' })
    }
  }
)

// Inicializar el tema según la preferencia guardada o la preferencia del sistema
onMounted(() => {
  // Cargar idioma guardado
  i18n.loadLanguage()
  
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    darkMode.value = savedTheme === 'dark'
  } else {
    // Usar preferencia del sistema
    darkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  }
  applyTheme()
})

// Observar cambios en el tema y aplicarlos
watch(darkMode, () => {
  applyTheme()
  localStorage.setItem('theme', darkMode.value ? 'dark' : 'light')
})

function applyTheme() {
  if (darkMode.value) {
    document.documentElement.classList.add('dark-theme')
  } else {
    document.documentElement.classList.remove('dark-theme')
  }
}

function toggleDarkMode() {
  darkMode.value = !darkMode.value
}

function toggleMobileMenu() {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

function logout() {
  auth.logout()
  mobileMenuOpen.value = false
}
</script>

<template>
  <div id="app">
    <header class="app-header">
      <div class="container">
        <RouterLink to="/" class="brand">
          <Cloud size="24" color="var(--color-primary)" />
          <span>WeatherHub</span>
        </RouterLink>
        
        <nav class="app-nav">
          <RouterLink to="/dashboard">{{ i18n.t.nav.dashboard }}</RouterLink>
          <RouterLink to="/history">{{ i18n.t.nav.history }}</RouterLink>
          <RouterLink to="/compare">{{ i18n.t.nav.compare }}</RouterLink>
          <RouterLink to="/alerts">{{ i18n.t.nav.alerts }}</RouterLink>
          
          <div class="nav-divider"></div>
          
          <button @click="toggleDarkMode" class="theme-toggle" :aria-label="darkMode ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'">
            <Sun v-if="darkMode" size="28" />
            <Moon v-else size="28" />
          </button>
          
          <div class="nav-divider"></div>
          
              <UnitSelector />
          
          <div class="user-menu" v-if="auth.isAuthenticated">
            <RouterLink to="/profile" class="user-button">
              <User size="18" />
              <span>{{ auth.user?.full_name || auth.user?.email }}</span>
            </RouterLink>
            <button class="logout-button" @click="logout">
              <LogOut size="18" />
              <span>{{ i18n.t.nav.logout }}</span>
            </button>
          </div>
          <template v-else>
            <RouterLink to="/login" class="btn btn-outline">{{ i18n.t.nav.login }}</RouterLink>
            <RouterLink to="/register" class="btn btn-primary">{{ i18n.t.nav.register }}</RouterLink>
          </template>
        </nav>
        
        <!-- Mobile menu button -->
        <button class="mobile-menu-button" @click="toggleMobileMenu" aria-label="Menú">
          <Menu v-if="!mobileMenuOpen" size="24" />
          <X v-else size="24" />
        </button>
      </div>
    </header>
    
    <!-- Mobile menu -->
    <div class="mobile-menu" :class="{ 'is-open': mobileMenuOpen }">
      <nav class="mobile-nav">
        <RouterLink @click="mobileMenuOpen = false" to="/dashboard">Dashboard</RouterLink>
        <RouterLink @click="mobileMenuOpen = false" to="/history">Historial</RouterLink>
        <RouterLink @click="mobileMenuOpen = false" to="/compare">Comparar</RouterLink>
        <RouterLink @click="mobileMenuOpen = false" to="/alerts">Alertas</RouterLink>
        <RouterLink @click="mobileMenuOpen = false" to="/profile">Perfil</RouterLink>
        
        <div class="mobile-nav-footer">
          <button @click="toggleDarkMode" class="theme-toggle mobile-theme-toggle" :aria-label="darkMode ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'">
            <Sun v-if="darkMode" size="28" />
            <Moon v-else size="28" />
            <span>{{ darkMode ? 'Tema claro' : 'Tema oscuro' }}</span>
          </button>
          
              <div class="unit-selector">
                <label>Unidad de temperatura</label>
                <UnitSelector />
              </div>
          
          <button v-if="auth.isAuthenticated" class="btn btn-outline btn-block" @click="logout">
            <LogOut size="18" />
            <span>Cerrar sesión</span>
          </button>
          <template v-else>
            <RouterLink @click="mobileMenuOpen = false" to="/login" class="btn btn-outline btn-block">Iniciar sesión</RouterLink>
            <RouterLink @click="mobileMenuOpen = false" to="/register" class="btn btn-primary btn-block">Registrarse</RouterLink>
          </template>
        </div>
      </nav>
    </div>
    
    <main class="main-content">
      <div class="container">
        <RouterView v-slot="{ Component }">
          <Transition name="fade" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </div>
    </main>
    
    <footer class="app-footer">
      <div class="container">
        <div>© {{ new Date().getFullYear() }} Hecho por Sebastian Palomino</div>
        <div class="footer-links">
          <a href="https://github.com/SebastianRoberto" target="_blank" rel="noopener noreferrer" class="footer-link social-link" aria-label="GitHub">
            <Github size="20" />
          </a>
          <a href="https://www.linkedin.com/in/sebastianrpp/" target="_blank" rel="noopener noreferrer" class="footer-link social-link" aria-label="LinkedIn">
            <Linkedin size="20" />
          </a>
          <a href="https://sebastianroberto.netlify.app/" target="_blank" rel="noopener noreferrer" class="footer-link social-link" aria-label="Sitio web">
            <Globe size="20" />
          </a>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: var(--color-text-primary);
  cursor: pointer;
  width: 48px;
  height: 40px;
  border-radius: 50%;
  transition: all var(--transition-normal);
}

.theme-toggle:hover {
  background-color: var(--color-hover-bg);
  transform: rotate(12deg);
}

.social-link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  transition: all var(--transition-normal);
  color: var(--color-text-secondary);
}

.social-link:hover {
  color: var(--color-primary);
  background-color: var(--color-hover-bg);
  transform: translateY(-3px);
}

.nav-divider {
  width: 1px;
  height: 24px;
  background-color: var(--color-border);
  margin: 0 var(--space-md);
}

.unit-selector {
  display: flex;
  align-items: center;
  width: 80px; /* Ancho fijo para evitar que cambie el layout */
  flex-shrink: 0; /* Evita que se comprima */
}

.unit-selector select {
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background-color: var(--color-card-bg);
  color: var(--color-text-primary);
  font-size: 0.9rem;
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.unit-selector select:hover {
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.unit-selector select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.1);
}

.dark-theme .unit-selector select {
  background-color: #181A1B;
  color: #fff;
  border-color: #333;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.dark-theme .unit-selector select:hover {
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}

.dark-theme .unit-selector select:focus {
  box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.2);
}

.user-menu {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.user-button {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-weight: 500;
}

.logout-button {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-md);
  color: var(--color-alert);
  font-weight: 500;
  background: transparent;
  border: none;
  cursor: pointer;
}

.logout-button:hover {
  background-color: rgba(229, 57, 53, 0.1);
}

.mobile-menu-button {
  display: none;
  background: none;
  border: none;
  color: var(--color-text-primary);
  cursor: pointer;
}

.mobile-menu {
  display: none;
  position: fixed;
  top: var(--header-height);
  left: 0;
  width: 100%;
  height: calc(100vh - var(--header-height));
  background-color: var(--color-card-bg);
  z-index: 99;
  transform: translateX(100%);
  transition: transform var(--transition-normal);
}

.mobile-menu.is-open {
  transform: translateX(0);
}

.mobile-nav {
  display: flex;
  flex-direction: column;
  padding: var(--space-lg);
  height: 100%;
}

.mobile-nav a {
  padding: var(--space-md);
  border-bottom: 1px solid var(--color-border);
  font-size: 1.1rem;
  font-weight: 500;
}

.mobile-nav-footer {
  margin-top: auto;
  padding-top: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.btn-block {
  width: 100%;
  text-align: center;
  justify-content: center;
}

.footer-links {
  display: flex;
  gap: var(--space-md);
}

.footer-link {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

/* Responsive Styles */
.mobile-theme-toggle {
  width: 100%;
  border-radius: var(--radius-md);
  padding: var(--space-md);
  justify-content: flex-start;
  gap: var(--space-sm);
  margin-bottom: var(--space-md);
  background-color: var(--color-hover-bg);
}

.mobile-theme-toggle:hover {
  transform: none;
}

@media (max-width: 768px) {
  .app-nav {
    display: none;
  }
  
  .mobile-menu-button {
    display: block;
  }
  
  .mobile-menu {
    display: block;
  }
}

@media (min-width: 769px) {
  .app-footer .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
