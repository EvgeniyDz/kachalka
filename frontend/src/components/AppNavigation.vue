<script setup lang="ts">
import {
  BarChart3,
  Bot,
  Dumbbell,
  LayoutDashboard,
  Settings,
  X,
} from '@lucide/vue'
import { storeToRefs } from 'pinia'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'

import { useAppStore } from '@/stores/app'

const { t } = useI18n()
const appStore = useAppStore()
const { isMobileNavigationOpen } = storeToRefs(appStore)

const navigationItems = [
  { to: '/', labelKey: 'navigation.dashboard', icon: LayoutDashboard },
  { to: '/workouts', labelKey: 'navigation.workouts', icon: Dumbbell },
  { to: '/exercises', labelKey: 'navigation.exercises', icon: Dumbbell },
  { to: '/analytics', labelKey: 'navigation.analytics', icon: BarChart3 },
  { to: '/assistant', labelKey: 'navigation.assistant', icon: Bot },
  { to: '/settings', labelKey: 'navigation.settings', icon: Settings },
] as const
</script>

<template>
  <div
    v-if="isMobileNavigationOpen"
    class="fixed inset-0 z-30 bg-slate-950/50 lg:hidden"
    aria-hidden="true"
    @click="appStore.closeMobileNavigation"
  />

  <aside class="app-sidebar" :class="{ 'app-sidebar--open': isMobileNavigationOpen }">
    <div class="flex h-18 items-center justify-between border-b border-slate-800 px-5">
      <RouterLink to="/" class="flex items-center gap-3" @click="appStore.closeMobileNavigation">
        <span class="grid size-9 place-items-center rounded-md bg-lime-400 text-slate-950">
          <Dumbbell :size="20" :stroke-width="2.4" />
        </span>
        <span>
          <strong class="block text-base font-extrabold text-white">{{ t('app.name') }}</strong>
          <small class="block text-xs text-slate-400">{{ t('app.subtitle') }}</small>
        </span>
      </RouterLink>

      <button
        type="button"
        class="icon-button text-slate-300 lg:hidden"
        :aria-label="t('common.close')"
        @click="appStore.closeMobileNavigation"
      >
        <X :size="20" />
      </button>
    </div>

    <nav class="flex flex-1 flex-col gap-1 p-3" :aria-label="t('common.mainNavigation')">
      <RouterLink
        v-for="item in navigationItems"
        :key="item.to"
        :to="item.to"
        class="navigation-link"
        @click="appStore.closeMobileNavigation"
      >
        <component :is="item.icon" :size="19" />
        <span>{{ t(item.labelKey) }}</span>
      </RouterLink>
    </nav>

    <div class="border-t border-slate-800 p-4 text-xs leading-5 text-slate-500">
      {{ t('common.version', { version: '0.1.0' }) }}
    </div>
  </aside>
</template>
