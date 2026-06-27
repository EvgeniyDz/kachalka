import { createI18n } from 'vue-i18n'

import { en } from '@/locales/en'
import { uk } from '@/locales/uk'

export const messages = {
  uk,
  en,
} as const

export type Locale = keyof typeof messages

export const defaultLocale: Locale = 'uk'
export const availableLocales = Object.keys(messages) as Locale[]

export const i18n = createI18n({
  legacy: false,
  locale: defaultLocale,
  fallbackLocale: defaultLocale,
  messages,
})
