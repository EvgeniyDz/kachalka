import { createRouter, createWebHistory } from 'vue-router'

import DashboardView from '@/views/DashboardView.vue'
import ExercisesView from '@/views/ExercisesView.vue'
import PlaceholderView from '@/views/PlaceholderView.vue'
import WorkoutsView from '@/views/WorkoutsView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView,
      meta: { titleKey: 'navigation.dashboard' },
    },
    {
      path: '/workouts',
      name: 'workouts',
      component: WorkoutsView,
      meta: { titleKey: 'navigation.workouts' },
    },
    {
      path: '/exercises',
      name: 'exercises',
      component: ExercisesView,
      meta: { titleKey: 'navigation.exercises' },
    },
    {
      path: '/analytics',
      name: 'analytics',
      component: PlaceholderView,
      meta: { titleKey: 'navigation.analytics' },
    },
    {
      path: '/assistant',
      name: 'assistant',
      component: PlaceholderView,
      meta: { titleKey: 'navigation.assistant' },
    },
    {
      path: '/settings',
      name: 'settings',
      component: PlaceholderView,
      meta: { titleKey: 'navigation.settings' },
    },
  ],
})
