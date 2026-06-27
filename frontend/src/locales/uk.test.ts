import { describe, expect, it } from 'vitest'

import { en } from '@/locales/en'
import { uk } from '@/locales/uk'

describe('локалі', () => {
  it('містять ключі головної навігації', () => {
    expect(uk.navigation).toMatchObject({
      dashboard: 'Панель',
      workouts: 'Тренування',
      exercises: 'Вправи',
      analytics: 'Аналітика',
      assistant: 'AI-асистент',
      settings: 'Налаштування',
    })

    expect(en.navigation).toMatchObject({
      dashboard: 'Dashboard',
      workouts: 'Workouts',
      exercises: 'Exercises',
      analytics: 'Analytics',
      assistant: 'AI assistant',
      settings: 'Settings',
    })
  })
})
