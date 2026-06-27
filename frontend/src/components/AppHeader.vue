<script setup lang="ts">
import { Languages, Menu, Plus } from '@lucide/vue'
import { storeToRefs } from 'pinia'
import { computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

import { availableLocales, type Locale } from '@/i18n'
import { useAppStore } from '@/stores/app'

const route = useRoute()
const { locale: activeI18nLocale, t } = useI18n()
const appStore = useAppStore()
const { locale } = storeToRefs(appStore)

const pageTitle = computed(() => t(String(route.meta.titleKey ?? 'navigation.dashboard')))

watch(
  locale,
  (nextLocale) => {
    activeI18nLocale.value = nextLocale
  },
  { immediate: true },
)

function selectLocale(nextLocale: Locale): void {
  appStore.setLocale(nextLocale)
}
</script>

<template>
  <header class="app-header">
    <div class="flex min-w-0 items-center gap-3">
      <button
        type="button"
        class="icon-button border border-slate-200 bg-white text-slate-700 lg:hidden"
        :aria-label="t('common.menu')"
        @click="appStore.toggleMobileNavigation"
      >
        <Menu :size="20" />
      </button>
      <h1 class="truncate text-lg font-bold text-slate-950">{{ pageTitle }}</h1>
    </div>

    <div class="flex items-center gap-2">
      <div class="language-switcher" :aria-label="t('common.language')">
        <Languages :size="17" class="text-slate-500" />
        <button
          v-for="availableLocale in availableLocales"
          :key="availableLocale"
          type="button"
          class="language-switcher__option"
          :class="{ 'language-switcher__option--active': locale === availableLocale }"
          @click="selectLocale(availableLocale)"
        >
          {{ t(`locales.${availableLocale}`) }}
        </button>
      </div>

      <RouterLink to="/workouts" class="primary-button">
        <Plus :size="18" />
        <span class="hidden sm:inline">{{ t('dashboard.newWorkout') }}</span>
      </RouterLink>
    </div>
  </header>
</template>
