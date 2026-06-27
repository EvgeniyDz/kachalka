import { defineStore } from 'pinia'
import { ref } from 'vue'

import { defaultLocale, type Locale } from '@/i18n'

export const useAppStore = defineStore('app', () => {
  const isMobileNavigationOpen = ref(false)
  const locale = ref<Locale>(defaultLocale)

  function toggleMobileNavigation(): void {
    isMobileNavigationOpen.value = !isMobileNavigationOpen.value
  }

  function closeMobileNavigation(): void {
    isMobileNavigationOpen.value = false
  }

  function setLocale(nextLocale: Locale): void {
    locale.value = nextLocale
  }

  return {
    isMobileNavigationOpen,
    locale,
    toggleMobileNavigation,
    closeMobileNavigation,
    setLocale,
  }
})
