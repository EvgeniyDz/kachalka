<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import {
  ChevronLeft,
  ChevronRight,
  Dumbbell,
  Pencil,
  Plus,
  RotateCcw,
  Save,
  Search,
  Trash2,
  X,
} from '@lucide/vue'
import { computed, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import {
  createExercise,
  deleteExercise,
  type ExercisePayload,
  type ExerciseRead,
  getExercises,
  getMuscleGroups,
  updateExercise,
} from '@/api/exercises'

const { locale, t } = useI18n()
const queryClient = useQueryClient()
const search = ref('')
const selectedMuscleGroup = ref('')
const includeCustom = ref(true)
const page = ref(0)
const editingExercise = ref<ExerciseRead | null>(null)
const formError = ref('')
const limit = 10

const form = reactive({
  muscleGroupCode: '',
  equipment: '',
  ukName: '',
  enName: '',
  ukDescription: '',
  enDescription: '',
})

const normalizedSearch = computed(() => search.value.trim())
const offset = computed(() => page.value * limit)
const isEditing = computed(() => editingExercise.value !== null)

const muscleGroupsQuery = useQuery({
  queryKey: computed(() => ['muscle-groups', locale.value]),
  queryFn: () => getMuscleGroups(locale.value),
})

const exercisesQuery = useQuery({
  queryKey: computed(() => [
    'exercises',
    locale.value,
    normalizedSearch.value,
    selectedMuscleGroup.value,
    includeCustom.value,
    offset.value,
  ]),
  queryFn: () =>
    getExercises({
      locale: locale.value,
      limit,
      offset: offset.value,
      search: normalizedSearch.value || undefined,
      muscleGroupCode: selectedMuscleGroup.value || undefined,
      includeCustom: includeCustom.value,
    }),
})

const exercises = computed(() => exercisesQuery.data.value?.items ?? [])
const total = computed(() => exercisesQuery.data.value?.total ?? 0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / limit)))
const currentPageLabel = computed(() => `${page.value + 1} / ${totalPages.value}`)
const isSaving = computed(() => createMutation.isPending.value || updateMutation.isPending.value)

const createMutation = useMutation({
  mutationFn: (payload: ExercisePayload) => createExercise(payload, locale.value),
  onSuccess: handleMutationSuccess,
})

const updateMutation = useMutation({
  mutationFn: ({ id, payload }: { id: number; payload: ExercisePayload }) =>
    updateExercise(id, payload, locale.value),
  onSuccess: handleMutationSuccess,
})

const deleteMutation = useMutation({
  mutationFn: deleteExercise,
  onSuccess: handleMutationSuccess,
})

watch([normalizedSearch, selectedMuscleGroup, includeCustom, locale], () => {
  page.value = 0
})

function invalidateExercises() {
  void queryClient.invalidateQueries({ queryKey: ['exercises'] })
}

function handleMutationSuccess() {
  resetForm()
  invalidateExercises()
}

function translation(exercise: ExerciseRead, targetLocale: string) {
  return exercise.translations.find((item) => item.locale === targetLocale)
}

function resetFilters() {
  search.value = ''
  selectedMuscleGroup.value = ''
  includeCustom.value = true
  page.value = 0
}

function resetForm() {
  editingExercise.value = null
  formError.value = ''
  form.muscleGroupCode = ''
  form.equipment = ''
  form.ukName = ''
  form.enName = ''
  form.ukDescription = ''
  form.enDescription = ''
}

function editExercise(exercise: ExerciseRead) {
  editingExercise.value = exercise
  formError.value = ''
  form.muscleGroupCode = exercise.muscle_group.code
  form.equipment = exercise.equipment ?? ''
  form.ukName = translation(exercise, 'uk')?.name ?? ''
  form.enName = translation(exercise, 'en')?.name ?? ''
  form.ukDescription = translation(exercise, 'uk')?.description ?? ''
  form.enDescription = translation(exercise, 'en')?.description ?? ''
}

function buildPayload(): ExercisePayload | null {
  if (!form.muscleGroupCode || !form.ukName.trim() || !form.enName.trim()) {
    formError.value = t('exercises.formRequired')
    return null
  }

  return {
    muscle_group_code: form.muscleGroupCode,
    equipment: form.equipment.trim() || null,
    translations: [
      {
        locale: 'uk',
        name: form.ukName.trim(),
        description: form.ukDescription.trim() || null,
      },
      {
        locale: 'en',
        name: form.enName.trim(),
        description: form.enDescription.trim() || null,
      },
    ],
  }
}

function submitForm() {
  const payload = buildPayload()
  if (payload === null) return

  formError.value = ''
  if (editingExercise.value) {
    updateMutation.mutate({ id: editingExercise.value.id, payload })
    return
  }

  createMutation.mutate(payload)
}

function removeExercise(exercise: ExerciseRead) {
  deleteMutation.mutate(exercise.id)
}

function previousPage() {
  page.value = Math.max(0, page.value - 1)
}

function nextPage() {
  if (page.value + 1 < totalPages.value) {
    page.value += 1
  }
}
</script>

<template>
  <section class="space-y-6">
    <div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
      <div>
        <p class="text-sm font-semibold text-lime-700">{{ t('exercises.eyebrow') }}</p>
        <h2 class="mt-1 text-2xl font-extrabold text-slate-950 sm:text-3xl">
          {{ t('exercises.title') }}
        </h2>
        <p class="mt-2 text-sm text-slate-600 sm:text-base">{{ t('exercises.subtitle') }}</p>
      </div>
      <button class="secondary-button inline-flex" type="button" @click="resetFilters">
        <RotateCcw :size="17" />
        {{ t('common.reset') }}
      </button>
    </div>

    <section class="content-panel overflow-hidden">
      <div class="panel-heading">
        <div>
          <h3 class="panel-title">
            {{ isEditing ? t('exercises.editCustom') : t('exercises.createCustom') }}
          </h3>
          <p class="panel-subtitle">{{ t('exercises.formSubtitle') }}</p>
        </div>
        <Plus v-if="!isEditing" :size="20" class="text-lime-700" />
        <Pencil v-else :size="20" class="text-slate-500" />
      </div>

      <form class="exercise-form" @submit.prevent="submitForm">
        <label class="field-label">
          <span>{{ t('exercises.muscleGroup') }}</span>
          <select v-model="form.muscleGroupCode" class="field-control">
            <option value="">{{ t('exercises.chooseGroup') }}</option>
            <option v-for="group in muscleGroupsQuery.data.value ?? []" :key="group.code" :value="group.code">
              {{ group.name }}
            </option>
          </select>
        </label>

        <label class="field-label">
          <span>{{ t('exercises.equipment') }}</span>
          <input v-model="form.equipment" class="field-control" type="text" :placeholder="t('exercises.equipmentPlaceholder')" />
        </label>

        <label class="field-label">
          <span>{{ t('exercises.ukName') }}</span>
          <input v-model="form.ukName" class="field-control" type="text" />
        </label>

        <label class="field-label">
          <span>{{ t('exercises.enName') }}</span>
          <input v-model="form.enName" class="field-control" type="text" />
        </label>

        <label class="field-label exercise-form__wide">
          <span>{{ t('exercises.ukDescription') }}</span>
          <textarea v-model="form.ukDescription" class="field-control field-control--textarea" />
        </label>

        <label class="field-label exercise-form__wide">
          <span>{{ t('exercises.enDescription') }}</span>
          <textarea v-model="form.enDescription" class="field-control field-control--textarea" />
        </label>

        <p v-if="formError" class="form-message form-message--error">{{ formError }}</p>
        <p v-else-if="createMutation.isError.value || updateMutation.isError.value" class="form-message form-message--error">
          {{ t('exercises.saveError') }}
        </p>

        <div class="form-actions exercise-form__wide">
          <button class="primary-button inline-flex" type="submit" :disabled="isSaving">
            <Save :size="17" />
            {{ isEditing ? t('common.save') : t('exercises.create') }}
          </button>
          <button v-if="isEditing" class="secondary-button inline-flex" type="button" @click="resetForm">
            <X :size="17" />
            {{ t('common.cancel') }}
          </button>
        </div>
      </form>
    </section>

    <section class="content-panel">
      <div class="filters-row">
        <label class="field-label">
          <span>{{ t('common.search') }}</span>
          <span class="field-control field-control--with-icon">
            <Search :size="17" class="text-slate-400" />
            <input v-model="search" type="search" :placeholder="t('exercises.searchPlaceholder')" />
          </span>
        </label>

        <label class="field-label">
          <span>{{ t('exercises.muscleGroup') }}</span>
          <select v-model="selectedMuscleGroup" class="field-control">
            <option value="">{{ t('exercises.allGroups') }}</option>
            <option v-for="group in muscleGroupsQuery.data.value ?? []" :key="group.code" :value="group.code">
              {{ group.name }}
            </option>
          </select>
        </label>

        <label class="toggle-control">
          <input v-model="includeCustom" type="checkbox" />
          <span>{{ t('exercises.includeCustom') }}</span>
        </label>
      </div>
    </section>

    <section class="content-panel overflow-hidden">
      <div class="panel-heading">
        <div>
          <h3 class="panel-title">{{ t('exercises.catalog') }}</h3>
          <p class="panel-subtitle">
            {{ t('exercises.total', { total }) }}
          </p>
        </div>
        <Dumbbell :size="20" class="text-slate-400" />
      </div>

      <div v-if="exercisesQuery.isPending.value" class="state-block">
        {{ t('common.loading') }}
      </div>

      <div v-else-if="exercisesQuery.isError.value" class="state-block text-rose-700">
        {{ t('common.loadError') }}
      </div>

      <div v-else-if="exercises.length === 0" class="state-block">
        {{ t('exercises.empty') }}
      </div>

      <div v-else class="divide-y divide-slate-200">
        <article v-for="exercise in exercises" :key="exercise.id" class="exercise-row">
          <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-2">
              <h4 class="truncate text-sm font-extrabold text-slate-950 sm:text-base">
                {{ exercise.name }}
              </h4>
              <span v-if="exercise.is_custom" class="badge">{{ t('exercises.custom') }}</span>
            </div>
            <p class="mt-1 text-xs text-slate-500">
              {{ exercise.muscle_group.name }} / {{ exercise.equipment ?? t('exercises.noEquipment') }}
            </p>
          </div>
          <div class="exercise-row__actions">
            <code class="hidden rounded bg-slate-100 px-2 py-1 text-xs text-slate-500 sm:block">
              {{ exercise.code }}
            </code>
            <button
              v-if="exercise.is_custom"
              class="icon-button border border-slate-200 bg-white"
              type="button"
              :aria-label="t('common.edit')"
              @click="editExercise(exercise)"
            >
              <Pencil :size="17" />
            </button>
            <button
              v-if="exercise.is_custom"
              class="icon-button border border-slate-200 bg-white text-rose-700"
              type="button"
              :aria-label="t('common.delete')"
              :disabled="deleteMutation.isPending.value"
              @click="removeExercise(exercise)"
            >
              <Trash2 :size="17" />
            </button>
          </div>
        </article>
      </div>

      <div class="pagination-row">
        <button class="icon-button border border-slate-200 bg-white" type="button" :disabled="page === 0" @click="previousPage">
          <ChevronLeft :size="18" />
        </button>
        <span class="text-sm font-bold text-slate-600">{{ currentPageLabel }}</span>
        <button
          class="icon-button border border-slate-200 bg-white"
          type="button"
          :disabled="page + 1 >= totalPages"
          @click="nextPage"
        >
          <ChevronRight :size="18" />
        </button>
      </div>
    </section>
  </section>
</template>