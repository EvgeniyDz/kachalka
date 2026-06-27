<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { Activity, CalendarDays, Dumbbell, Flame, Plus, Trophy } from '@lucide/vue'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { getHealth } from '@/api/health'

const { t } = useI18n()

const healthQuery = useQuery({
  queryKey: ['health'],
  queryFn: getHealth,
  retry: 1,
  refetchInterval: 30_000,
})

const healthLabel = computed(() => {
  if (healthQuery.isPending.value) return t('dashboard.checking')
  if (healthQuery.isSuccess.value) return t('dashboard.connected')
  return t('dashboard.unavailable')
})

const healthClass = computed(() => {
  if (healthQuery.isPending.value) return 'status-dot--pending'
  if (healthQuery.isSuccess.value) return 'status-dot--success'
  return 'status-dot--error'
})

const stats = computed(() => [
  { labelKey: 'dashboard.totalWorkouts', value: '0', icon: CalendarDays, accent: 'text-sky-700' },
  {
    labelKey: 'dashboard.weeklyVolume',
    value: t('units.kilogramsValue', { value: 0 }),
    icon: Dumbbell,
    accent: 'text-violet-700',
  },
  { labelKey: 'dashboard.currentStreak', value: '0', icon: Flame, accent: 'text-rose-700' },
])
</script>

<template>
  <section class="space-y-6">
    <div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
      <div>
        <p class="text-sm font-semibold text-lime-700">{{ t('dashboard.eyebrow') }}</p>
        <h2 class="mt-1 text-2xl font-extrabold text-slate-950 sm:text-3xl">
          {{ t('dashboard.title') }}
        </h2>
        <p class="mt-2 text-sm text-slate-600 sm:text-base">{{ t('dashboard.subtitle') }}</p>
      </div>
      <div class="inline-flex items-center gap-2 text-sm text-slate-600">
        <span class="status-dot" :class="healthClass" />
        <span>{{ t('dashboard.apiStatus') }}: {{ healthLabel }}</span>
      </div>
    </div>

    <div class="grid gap-4 sm:grid-cols-3">
      <article v-for="stat in stats" :key="stat.labelKey" class="metric-card">
        <component :is="stat.icon" :size="21" :class="stat.accent" />
        <p class="mt-5 text-sm font-medium text-slate-500">{{ t(stat.labelKey) }}</p>
        <strong class="mt-1 block text-2xl font-extrabold text-slate-950">{{ stat.value }}</strong>
      </article>
    </div>

    <div class="grid gap-6 lg:grid-cols-[minmax(0,1.6fr)_minmax(280px,0.8fr)]">
      <section class="content-panel min-h-80">
        <div class="panel-heading">
          <div>
            <h3 class="panel-title">{{ t('dashboard.recentActivity') }}</h3>
            <p class="panel-subtitle">{{ t('dashboard.recentActivitySubtitle') }}</p>
          </div>
          <Activity :size="20" class="text-slate-400" />
        </div>

        <div class="grid min-h-60 place-items-center px-5 py-10 text-center">
          <div class="max-w-md">
            <span class="mx-auto grid size-12 place-items-center rounded-md bg-slate-100 text-slate-600">
              <Dumbbell :size="24" />
            </span>
            <h4 class="mt-4 text-base font-bold text-slate-900">{{ t('dashboard.emptyTitle') }}</h4>
            <p class="mt-2 text-sm leading-6 text-slate-500">{{ t('dashboard.emptyText') }}</p>
            <RouterLink to="/workouts" class="primary-button mt-5 inline-flex">
              <Plus :size="18" />
              {{ t('dashboard.startWorkout') }}
            </RouterLink>
          </div>
        </div>
      </section>

      <section class="content-panel min-h-80">
        <div class="panel-heading">
          <div>
            <h3 class="panel-title">{{ t('dashboard.latestRecord') }}</h3>
            <p class="panel-subtitle">{{ t('dashboard.latestRecordSubtitle') }}</p>
          </div>
          <Trophy :size="20" class="text-amber-600" />
        </div>
        <div class="grid min-h-60 place-items-center px-5 py-10 text-center">
          <div>
            <span class="mx-auto grid size-12 place-items-center rounded-md bg-amber-50 text-amber-700">
              <Trophy :size="24" />
            </span>
            <p class="mt-4 max-w-60 text-sm leading-6 text-slate-500">
              {{ t('dashboard.noRecords') }}
            </p>
          </div>
        </div>
      </section>
    </div>
  </section>
</template>
