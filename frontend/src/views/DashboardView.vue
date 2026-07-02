<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { Activity, BarChart3, CalendarDays, Dumbbell, Flame, Plus, Trophy } from '@lucide/vue'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import {
  getLatestRecords,
  getMuscleGroupFrequency,
  getWeeklyVolume,
  type PersonalRecordRead,
} from '@/api/analytics'
import { getHealth } from '@/api/health'
import { getWorkouts } from '@/api/workouts'

const { locale, t } = useI18n()

const today = computed(() => formatDateInput(new Date()))

const monthStart = computed(() => {
  const date = new Date()
  date.setDate(1)
  return formatDateInput(date)
})

const healthQuery = useQuery({
  queryKey: ['health'],
  queryFn: getHealth,
  retry: 1,
  refetchInterval: 30_000,
})

const workoutsQuery = useQuery({
  queryKey: ['dashboard', 'workouts'],
  queryFn: () => getWorkouts({ limit: 5, offset: 0 }),
})

const monthlyWorkoutsQuery = useQuery({
  queryKey: ['dashboard', 'workouts', 'month'],
  queryFn: () => getWorkouts({ limit: 1, offset: 0, dateFrom: monthStart.value, dateTo: today.value }),
})

const weeklyVolumeQuery = useQuery({
  queryKey: ['dashboard', 'weekly-volume'],
  queryFn: getWeeklyVolume,
})

const recordsQuery = useQuery({
  queryKey: ['dashboard', 'records', locale],
  queryFn: () => getLatestRecords(locale.value, 5),
})

const muscleGroupsQuery = useQuery({
  queryKey: ['dashboard', 'muscle-groups', locale],
  queryFn: () => getMuscleGroupFrequency(locale.value, 5),
})


const recentWorkouts = computed(() => workoutsQuery.data.value?.items ?? [])
const weeklyVolume = computed(() => weeklyVolumeQuery.data.value ?? [])
const latestRecords = computed(() => recordsQuery.data.value ?? [])
const frequentGroups = computed(() => muscleGroupsQuery.data.value ?? [])

const currentWeekVolume = computed(() => {
  const point = weeklyVolume.value.at(-1)
  return point ? Number(point.volume) : 0
})

const currentStreak = computed(() => {
  let streak = 0
  const weeks = [...weeklyVolume.value].reverse()

  for (const week of weeks) {
    if (week.workout_count === 0) break
    streak += 1
  }

  return streak
})

const maxWeeklyVolume = computed(() => {
  const volumes = weeklyVolume.value.map((week) => Number(week.volume))
  return Math.max(1, ...volumes)
})

const hasDashboardData = computed(
  () =>
    recentWorkouts.value.length > 0 ||
    weeklyVolume.value.length > 0 ||
    latestRecords.value.length > 0 ||
    frequentGroups.value.length > 0,
)

const isDashboardLoading = computed(
  () =>
    workoutsQuery.isPending.value ||
    weeklyVolumeQuery.isPending.value ||
    recordsQuery.isPending.value ||
    muscleGroupsQuery.isPending.value,
)

const hasDashboardError = computed(
  () =>
    workoutsQuery.isError.value ||
    weeklyVolumeQuery.isError.value ||
    recordsQuery.isError.value ||
    muscleGroupsQuery.isError.value,
)

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
  {
    labelKey: 'dashboard.totalWorkouts',
    value: String(workoutsQuery.data.value?.total ?? 0),
    icon: CalendarDays,
    accent: 'text-sky-700',
  },
  {
    labelKey: 'dashboard.weeklyVolume',
    value: t('units.kilogramsValue', { value: formatNumber(currentWeekVolume.value) }),
    icon: Dumbbell,
    accent: 'text-violet-700',
  },
  {
    labelKey: 'dashboard.currentStreak',
    value: String(currentStreak.value),
    icon: Flame,
    accent: 'text-rose-700',
  },
])

function formatDateInput(date: Date): string {
  return date.toISOString().slice(0, 10)
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat(locale.value, { day: '2-digit', month: 'short', year: 'numeric' }).format(
    new Date(value),
  )
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat(locale.value, { maximumFractionDigits: 1 }).format(value)
}

function formatRecordValue(record: PersonalRecordRead): string {
  if (record.record_type === 'max_reps') {
    return t('units.repsValue', { value: formatNumber(Number(record.value)) })
  }

  return t('units.kilogramsValue', { value: formatNumber(Number(record.value)) })
}

function recordTypeLabel(recordType: string): string {
  return t(`dashboard.recordTypes.${recordType}`)
}
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

    <div v-if="isDashboardLoading" class="state-block content-panel">
      {{ t('common.loading') }}
    </div>

    <div v-else-if="hasDashboardError" class="state-block content-panel">
      {{ t('common.loadError') }}
    </div>

    <div v-else class="grid gap-6 xl:grid-cols-[minmax(0,1.35fr)_minmax(21rem,0.65fr)]">
      <div class="space-y-6">
        <section class="content-panel">
          <div class="panel-heading">
            <div>
              <h3 class="panel-title">{{ t('dashboard.recentActivity') }}</h3>
              <p class="panel-subtitle">{{ t('dashboard.recentActivitySubtitle') }}</p>
            </div>
            <Activity :size="20" class="text-slate-400" />
          </div>

          <div v-if="recentWorkouts.length" class="dashboard-list">
            <article v-for="workout in recentWorkouts" :key="workout.id" class="dashboard-row">
              <div>
                <strong>{{ workout.title || t('dashboard.untitledWorkout') }}</strong>
                <span>{{ formatDate(workout.date) }}</span>
                <p v-if="workout.notes">{{ workout.notes }}</p>
              </div>
              <div class="dashboard-row__meta">
                <span>{{ t('dashboard.exerciseCount', { count: workout.exercise_count }) }}</span>
                <span>{{ t('dashboard.setsCount', { count: workout.set_count }) }}</span>
              </div>
            </article>
          </div>

          <div v-else class="grid min-h-60 place-items-center px-5 py-10 text-center">
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

        <section class="content-panel">
          <div class="panel-heading">
            <div>
              <h3 class="panel-title">{{ t('dashboard.weeklyVolumeChart') }}</h3>
              <p class="panel-subtitle">
                {{ t('dashboard.monthlyWorkouts', { count: monthlyWorkoutsQuery.data.value?.total ?? 0 }) }}
              </p>
            </div>
            <BarChart3 :size="20" class="text-violet-700" />
          </div>

          <div v-if="weeklyVolume.length" class="volume-chart">
            <div v-for="week in weeklyVolume.slice(-8)" :key="week.week_start" class="volume-bar">
              <span>{{ t('units.kilogramsValue', { value: formatNumber(Number(week.volume)) }) }}</span>
              <div class="volume-bar__track">
                <div
                  class="volume-bar__fill"
                  :style="{ width: `${Math.max(6, (Number(week.volume) / maxWeeklyVolume) * 100)}%` }"
                />
              </div>
              <small>{{ t('dashboard.weekOf', { date: formatDate(week.week_start) }) }}</small>
            </div>
          </div>

          <div v-else class="state-block">{{ t('dashboard.noAnalytics') }}</div>
        </section>
      </div>

      <div class="space-y-6">
        <section class="content-panel">
          <div class="panel-heading">
            <div>
              <h3 class="panel-title">{{ t('dashboard.latestRecord') }}</h3>
              <p class="panel-subtitle">{{ t('dashboard.latestRecordSubtitle') }}</p>
            </div>
            <Trophy :size="20" class="text-amber-600" />
          </div>

          <div v-if="latestRecords.length" class="dashboard-list">
            <article v-for="record in latestRecords" :key="record.id" class="record-row">
              <div>
                <strong>{{ record.exercise.name }}</strong>
                <span>{{ recordTypeLabel(record.record_type) }}</span>
              </div>
              <b>{{ formatRecordValue(record) }}</b>
            </article>
          </div>

          <div v-else class="state-block">{{ t('dashboard.noRecords') }}</div>
        </section>

        <section class="content-panel">
          <div class="panel-heading">
            <div>
              <h3 class="panel-title">{{ t('dashboard.frequentGroups') }}</h3>
              <p class="panel-subtitle">{{ t('dashboard.frequentGroupsSubtitle') }}</p>
            </div>
            <Dumbbell :size="20" class="text-lime-700" />
          </div>

          <div v-if="frequentGroups.length" class="dashboard-list">
            <article v-for="group in frequentGroups" :key="group.muscle_group.id" class="record-row">
              <div>
                <strong>{{ group.muscle_group.name }}</strong>
                <span>{{ group.muscle_group.code }}</span>
              </div>
              <b>{{ t('dashboard.exerciseCount', { count: group.exercise_count }) }}</b>
            </article>
          </div>

          <div v-else class="state-block">{{ t('dashboard.noAnalytics') }}</div>
        </section>
      </div>
    </div>

    <p v-if="!isDashboardLoading && !hasDashboardError && !hasDashboardData" class="sr-only">
      {{ t('dashboard.noAnalytics') }}
    </p>
  </section>
</template>