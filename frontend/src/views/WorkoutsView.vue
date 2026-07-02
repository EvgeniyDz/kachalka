<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import {
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  Copy,
  Dumbbell,
  Eye,
  Plus,
  RotateCcw,
  Save,
  Trash2,
} from '@lucide/vue'
import { computed, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import { getExercises } from '@/api/exercises'
import {
  createWorkout,
  deleteWorkout,
  getWorkout,
  getWorkouts,
  updateWorkout,
  type WorkoutPayload,
  type WorkoutRead,
} from '@/api/workouts'

interface SetDraft {
  set_number: number
  weight: number | null
  reps: number | null
  rpe: number | null
  notes: string
}

interface WorkoutExerciseDraft {
  exercise_id: number | null
  notes: string
  sets: SetDraft[]
}

interface WorkoutDraft {
  date: string
  title: string
  notes: string
  exercises: WorkoutExerciseDraft[]
}

const PAGE_SIZE = 8

const { locale, t } = useI18n()
const queryClient = useQueryClient()

const page = ref(0)
const selectedWorkoutId = ref<number | null>(null)
const editingWorkoutId = ref<number | null>(null)
const formError = ref('')

const draft = reactive<WorkoutDraft>(createEmptyDraft())

const workoutsQuery = useQuery({
  queryKey: ['workouts', page],
  queryFn: () => getWorkouts({ limit: PAGE_SIZE, offset: page.value * PAGE_SIZE }),
})

const exercisesQuery = useQuery({
  queryKey: ['workout-form', 'exercises', locale],
  queryFn: () => getExercises({ locale: locale.value, limit: 100, includeCustom: true }),
})

const detailQuery = useQuery({
  queryKey: ['workout', selectedWorkoutId, locale],
  queryFn: () => getWorkout(selectedWorkoutId.value ?? 0, locale.value),
  enabled: computed(() => selectedWorkoutId.value !== null),
})

const saveMutation = useMutation({
  mutationFn: (payload: WorkoutPayload) =>
    editingWorkoutId.value
      ? updateWorkout(editingWorkoutId.value, payload, locale.value)
      : createWorkout(payload, locale.value),
  onSuccess: (workout) => {
    selectedWorkoutId.value = workout.id
    editingWorkoutId.value = null
    resetDraft()
    void queryClient.invalidateQueries({ queryKey: ['workouts'] })
    void queryClient.invalidateQueries({ queryKey: ['workout'] })
    void queryClient.invalidateQueries({ queryKey: ['dashboard'] })
  },
  onError: () => {
    formError.value = t('workouts.saveError')
  },
})

const deleteMutation = useMutation({
  mutationFn: deleteWorkout,
  onSuccess: () => {
    selectedWorkoutId.value = null
    editingWorkoutId.value = null
    void queryClient.invalidateQueries({ queryKey: ['workouts'] })
    void queryClient.invalidateQueries({ queryKey: ['dashboard'] })
  },
})

const exerciseOptions = computed(() => exercisesQuery.data.value?.items ?? [])
const workouts = computed(() => workoutsQuery.data.value?.items ?? [])
const total = computed(() => workoutsQuery.data.value?.total ?? 0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)))
const selectedWorkout = computed(() => detailQuery.data.value ?? null)
const isEditing = computed(() => editingWorkoutId.value !== null)

watch(workouts, (items) => {
  if (selectedWorkoutId.value === null && items.length > 0) {
    selectedWorkoutId.value = items[0].id
  }
})

function createEmptyDraft(): WorkoutDraft {
  return {
    date: new Date().toISOString().slice(0, 10),
    title: '',
    notes: '',
    exercises: [createExerciseDraft()],
  }
}

function createExerciseDraft(exerciseId: number | null = null): WorkoutExerciseDraft {
  return {
    exercise_id: exerciseId,
    notes: '',
    sets: [createSetDraft(1)],
  }
}

function createSetDraft(setNumber: number): SetDraft {
  return {
    set_number: setNumber,
    weight: null,
    reps: null,
    rpe: null,
    notes: '',
  }
}

function resetDraft(): void {
  const empty = createEmptyDraft()
  draft.date = empty.date
  draft.title = empty.title
  draft.notes = empty.notes
  draft.exercises = empty.exercises
  formError.value = ''
}

function addWorkoutExercise(): void {
  draft.exercises.push(createExerciseDraft())
}

function removeWorkoutExercise(index: number): void {
  draft.exercises.splice(index, 1)
  if (draft.exercises.length === 0) {
    addWorkoutExercise()
  }
}

function addSet(exercise: WorkoutExerciseDraft): void {
  exercise.sets.push(createSetDraft(exercise.sets.length + 1))
  renumberSets(exercise)
}

function duplicateSet(exercise: WorkoutExerciseDraft, set: SetDraft): void {
  exercise.sets.push({ ...set, set_number: exercise.sets.length + 1 })
  renumberSets(exercise)
}

function removeSet(exercise: WorkoutExerciseDraft, setIndex: number): void {
  exercise.sets.splice(setIndex, 1)
  if (exercise.sets.length === 0) {
    addSet(exercise)
  }
  renumberSets(exercise)
}

function renumberSets(exercise: WorkoutExerciseDraft): void {
  exercise.sets.forEach((set, index) => {
    set.set_number = index + 1
  })
}

function buildPayload(): WorkoutPayload | null {
  const exercises = draft.exercises
    .filter((exercise) => exercise.exercise_id !== null)
    .map((exercise, index) => ({
      exercise_id: Number(exercise.exercise_id),
      order_index: index,
      notes: exercise.notes.trim() || null,
      sets: exercise.sets.map((set) => ({
        set_number: set.set_number,
        weight: set.weight,
        reps: set.reps,
        rpe: set.rpe,
        notes: set.notes.trim() || null,
      })),
    }))

  if (!draft.date || exercises.length === 0) {
    formError.value = t('workouts.formRequired')
    return null
  }

  formError.value = ''
  return {
    date: draft.date,
    title: draft.title.trim() || null,
    notes: draft.notes.trim() || null,
    exercises,
  }
}

function saveWorkout(): void {
  const payload = buildPayload()
  if (payload) {
    saveMutation.mutate(payload)
  }
}

function startCreate(): void {
  editingWorkoutId.value = null
  resetDraft()
}

function startEdit(workout: WorkoutRead): void {
  editingWorkoutId.value = workout.id
  selectedWorkoutId.value = workout.id
  draft.date = workout.date
  draft.title = workout.title ?? ''
  draft.notes = workout.notes ?? ''
  draft.exercises = workout.exercises.map((workoutExercise) => ({
    exercise_id: workoutExercise.exercise.id,
    notes: workoutExercise.notes ?? '',
    sets: workoutExercise.sets.map((set) => ({
      set_number: set.set_number,
      weight: set.weight === null ? null : Number(set.weight),
      reps: set.reps,
      rpe: set.rpe === null ? null : Number(set.rpe),
      notes: set.notes ?? '',
    })),
  }))
}

function selectWorkout(workoutId: number): void {
  selectedWorkoutId.value = workoutId
}

function removeWorkout(workoutId: number): void {
  deleteMutation.mutate(workoutId)
}

function previousPage(): void {
  page.value = Math.max(0, page.value - 1)
}

function nextPage(): void {
  page.value = Math.min(totalPages.value - 1, page.value + 1)
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat(locale.value, { day: '2-digit', month: 'short', year: 'numeric' }).format(
    new Date(value),
  )
}
</script>

<template>
  <section class="space-y-6">
    <div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
      <div>
        <p class="text-sm font-semibold text-lime-700">{{ t('workouts.eyebrow') }}</p>
        <h2 class="mt-1 text-2xl font-extrabold text-slate-950 sm:text-3xl">
          {{ t('workouts.title') }}
        </h2>
        <p class="mt-2 text-sm text-slate-600 sm:text-base">{{ t('workouts.subtitle') }}</p>
      </div>
      <button class="primary-button inline-flex" type="button" @click="startCreate">
        <Plus :size="18" />
        {{ t('workouts.newWorkout') }}
      </button>
    </div>

    <div class="grid gap-6 xl:grid-cols-[minmax(20rem,0.85fr)_minmax(0,1.15fr)]">
      <section class="content-panel">
        <div class="panel-heading">
          <div>
            <h3 class="panel-title">{{ t('workouts.history') }}</h3>
            <p class="panel-subtitle">{{ t('workouts.total', { total }) }}</p>
          </div>
          <CalendarDays :size="20" class="text-slate-400" />
        </div>

        <div v-if="workoutsQuery.isPending.value" class="state-block">{{ t('common.loading') }}</div>
        <div v-else-if="workoutsQuery.isError.value" class="state-block">{{ t('common.loadError') }}</div>
        <div v-else-if="workouts.length" class="dashboard-list">
          <article
            v-for="workout in workouts"
            :key="workout.id"
            class="dashboard-row workout-history-row"
            :class="{ 'workout-history-row--active': workout.id === selectedWorkoutId }"
          >
            <button type="button" class="workout-history-row__main" @click="selectWorkout(workout.id)">
              <strong>{{ workout.title || t('workouts.untitled') }}</strong>
              <span>{{ formatDate(workout.date) }}</span>
              <p>{{ t('workouts.summary', { exercises: workout.exercise_count, sets: workout.set_count }) }}</p>
            </button>
            <button class="icon-button" type="button" :title="t('workouts.viewDetails')" @click="selectWorkout(workout.id)">
              <Eye :size="18" />
            </button>
          </article>
        </div>
        <div v-else class="state-block">{{ t('workouts.empty') }}</div>

        <div class="pagination-row">
          <button class="icon-button" type="button" :disabled="page === 0" @click="previousPage">
            <ChevronLeft :size="18" />
          </button>
          <span class="text-sm font-bold text-slate-600">{{ page + 1 }} / {{ totalPages }}</span>
          <button class="icon-button" type="button" :disabled="page >= totalPages - 1" @click="nextPage">
            <ChevronRight :size="18" />
          </button>
        </div>
      </section>

      <section class="content-panel">
        <div class="panel-heading">
          <div>
            <h3 class="panel-title">{{ isEditing ? t('workouts.editWorkout') : t('workouts.formTitle') }}</h3>
            <p class="panel-subtitle">{{ t('workouts.formSubtitle') }}</p>
          </div>
          <Dumbbell :size="20" class="text-lime-700" />
        </div>

        <form class="workout-form" @submit.prevent="saveWorkout">
          <label class="field-label">
            {{ t('workouts.date') }}
            <input v-model="draft.date" class="field-control" type="date" />
          </label>
          <label class="field-label">
            {{ t('workouts.workoutTitle') }}
            <input v-model="draft.title" class="field-control" :placeholder="t('workouts.titlePlaceholder')" />
          </label>
          <label class="field-label workout-form__wide">
            {{ t('workouts.notes') }}
            <textarea v-model="draft.notes" class="field-control field-control--textarea" :placeholder="t('workouts.notesPlaceholder')" />
          </label>

          <div class="workout-form__wide workout-builder">
            <div class="workout-builder__heading">
              <strong>{{ t('workouts.exercises') }}</strong>
              <button class="secondary-button inline-flex" type="button" @click="addWorkoutExercise">
                <Plus :size="17" />
                {{ t('workouts.addExercise') }}
              </button>
            </div>

            <article v-for="(exercise, exerciseIndex) in draft.exercises" :key="exerciseIndex" class="workout-exercise-card">
              <div class="workout-exercise-card__header">
                <label class="field-label">
                  {{ t('workouts.exercise') }}
                  <select v-model.number="exercise.exercise_id" class="field-control">
                    <option :value="null">{{ t('workouts.chooseExercise') }}</option>
                    <option v-for="option in exerciseOptions" :key="option.id" :value="option.id">
                      {{ option.name }}
                    </option>
                  </select>
                </label>
                <button class="icon-button" type="button" :title="t('workouts.removeExercise')" @click="removeWorkoutExercise(exerciseIndex)">
                  <Trash2 :size="18" />
                </button>
              </div>

              <label class="field-label">
                {{ t('workouts.exerciseNotes') }}
                <input v-model="exercise.notes" class="field-control" :placeholder="t('workouts.exerciseNotesPlaceholder')" />
              </label>

              <div class="workout-sets">
                <div class="workout-sets__head">
                  <span>{{ t('workouts.sets') }}</span>
                  <button class="secondary-button inline-flex" type="button" @click="addSet(exercise)">
                    <Plus :size="16" />
                    {{ t('workouts.addSet') }}
                  </button>
                </div>

                <div v-for="(set, setIndex) in exercise.sets" :key="setIndex" class="workout-set-row">
                  <strong>{{ t('workouts.setNumber', { number: set.set_number }) }}</strong>
                  <input v-model.number="set.weight" class="field-control" type="number" min="0" step="0.5" :placeholder="t('workouts.weight')" />
                  <input v-model.number="set.reps" class="field-control" type="number" min="0" step="1" :placeholder="t('workouts.reps')" />
                  <input v-model.number="set.rpe" class="field-control" type="number" min="0" max="10" step="0.5" :placeholder="t('workouts.rpe')" />
                  <input v-model="set.notes" class="field-control" :placeholder="t('workouts.setNotes')" />
                  <button class="icon-button" type="button" :title="t('workouts.duplicateSet')" @click="duplicateSet(exercise, set)">
                    <Copy :size="17" />
                  </button>
                  <button class="icon-button" type="button" :title="t('workouts.removeSet')" @click="removeSet(exercise, setIndex)">
                    <Trash2 :size="17" />
                  </button>
                </div>
              </div>
            </article>
          </div>

          <p v-if="formError" class="form-message form-message--error workout-form__wide">{{ formError }}</p>

          <div class="form-actions workout-form__wide">
            <button class="primary-button inline-flex" type="submit" :disabled="saveMutation.isPending.value">
              <Save :size="18" />
              {{ t('common.save') }}
            </button>
            <button class="secondary-button inline-flex" type="button" @click="resetDraft">
              <RotateCcw :size="18" />
              {{ t('common.reset') }}
            </button>
          </div>
        </form>
      </section>
    </div>

    <section class="content-panel">
      <div class="panel-heading">
        <div>
          <h3 class="panel-title">{{ t('workouts.details') }}</h3>
          <p class="panel-subtitle">{{ t('workouts.detailsSubtitle') }}</p>
        </div>
        <div v-if="selectedWorkout" class="exercise-row__actions">
          <button class="secondary-button inline-flex" type="button" @click="startEdit(selectedWorkout)">
            {{ t('common.edit') }}
          </button>
          <button class="secondary-button inline-flex" type="button" :disabled="deleteMutation.isPending.value" @click="removeWorkout(selectedWorkout.id)">
            {{ t('common.delete') }}
          </button>
        </div>
      </div>

      <div v-if="detailQuery.isPending.value && selectedWorkoutId !== null" class="state-block">{{ t('common.loading') }}</div>
      <div v-else-if="detailQuery.isError.value" class="state-block">{{ t('common.loadError') }}</div>
      <div v-else-if="selectedWorkout" class="workout-details">
        <div class="workout-details__summary">
          <div>
            <strong>{{ selectedWorkout.title || t('workouts.untitled') }}</strong>
            <span>{{ formatDate(selectedWorkout.date) }}</span>
          </div>
          <p v-if="selectedWorkout.notes">{{ selectedWorkout.notes }}</p>
        </div>

        <article v-for="workoutExercise in selectedWorkout.exercises" :key="workoutExercise.id" class="workout-detail-exercise">
          <div>
            <strong>{{ workoutExercise.exercise.name }}</strong>
            <span>{{ workoutExercise.exercise.muscle_group.name }}</span>
            <p v-if="workoutExercise.notes">{{ workoutExercise.notes }}</p>
          </div>
          <div class="workout-detail-sets">
            <span v-for="set in workoutExercise.sets" :key="set.id">
              {{ t('workouts.setNumber', { number: set.set_number }) }}:
              {{ set.weight ?? t('exercises.noWeight') }} / {{ set.reps ?? 0 }} {{ t('exercises.repsShort') }}
            </span>
          </div>
        </article>
      </div>
      <div v-else class="state-block">{{ t('workouts.selectWorkout') }}</div>
    </section>
  </section>
</template>