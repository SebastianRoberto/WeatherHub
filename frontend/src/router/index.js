import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue'), meta: { guest: true } },
  { path: '/register', name: 'register', component: () => import('@/views/RegisterView.vue'), meta: { guest: true } },
  { path: '/dashboard', name: 'dashboard', component: () => import('@/views/DashboardView.vue'), meta: { requiresAuth: true } },
  { path: '/history', name: 'history', component: () => import('@/views/HistoryView.vue'), meta: { requiresAuth: true } },
  { path: '/compare', name: 'compare', component: () => import('@/views/CompareView.vue'), meta: { requiresAuth: true } },
  { path: '/alerts', name: 'alerts', component: () => import('@/views/AlertsView.vue'), meta: { requiresAuth: true } },
  { path: '/profile', name: 'profile', component: () => import('@/views/ProfileView.vue'), meta: { requiresAuth: true } },
  { path: '/:pathMatch(.*)*', name: 'not-found', redirect: '/dashboard' }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login' }
  }
  if (to.meta.guest && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
  return true
})

export default router
