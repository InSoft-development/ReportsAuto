import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('../views/HomeView.vue'),
    },
    {
      path: '/interval/:intervalsId',
      name: 'interval',
      component: () => import('../views/IntervalView.vue'),
    },
    {
      path: '/addition',
      name: 'addition',
      component: () => import('../views/AdditionView.vue'),
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/SettingsView.vue'),
    },
  ],
})

export default router
