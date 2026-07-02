import { apiRequest } from '@/api/client'
import type { ExerciseRead } from '@/api/exercises'

export interface ExerciseSetRead {
  id: number
  set_number: number
  weight: string | null
  reps: number | null
  rpe: string | null
  notes: string | null
}

export interface WorkoutExerciseRead {
  id: number
  order_index: number
  notes: string | null
  exercise: ExerciseRead
  sets: ExerciseSetRead[]
}

export interface WorkoutRead {
  id: number
  date: string
  title: string | null
  notes: string | null
  exercises: WorkoutExerciseRead[]
}

export interface WorkoutSummaryRead {
  id: number
  date: string
  title: string | null
  notes: string | null
  exercise_count: number
  set_count: number
}

export interface WorkoutListRead {
  items: WorkoutSummaryRead[]
  total: number
  limit: number
  offset: number
}

export interface ExerciseSetInput {
  set_number?: number | null
  weight?: number | null
  reps?: number | null
  rpe?: number | null
  notes?: string | null
}

export interface WorkoutExerciseInput {
  exercise_id: number
  order_index?: number | null
  notes?: string | null
  sets: ExerciseSetInput[]
}

export interface WorkoutPayload {
  date: string
  title?: string | null
  notes?: string | null
  exercises: WorkoutExerciseInput[]
}

export interface WorkoutListParams {
  limit?: number
  offset?: number
  dateFrom?: string
  dateTo?: string
}

function buildQuery(params: Record<string, string | number | undefined>): string {
  const searchParams = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== '') {
      searchParams.set(key, String(value))
    }
  })

  const query = searchParams.toString()
  return query ? `?${query}` : ''
}

export function getWorkouts(params: WorkoutListParams = {}): Promise<WorkoutListRead> {
  return apiRequest<WorkoutListRead>(
    `/workouts${buildQuery({
      limit: params.limit,
      offset: params.offset,
      date_from: params.dateFrom,
      date_to: params.dateTo,
    })}`,
  )
}

export function getWorkout(workoutId: number, locale: string): Promise<WorkoutRead> {
  return apiRequest<WorkoutRead>(`/workouts/${workoutId}${buildQuery({ locale })}`)
}

export function createWorkout(payload: WorkoutPayload, locale: string): Promise<WorkoutRead> {
  return apiRequest<WorkoutRead>(`/workouts${buildQuery({ locale })}`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updateWorkout(
  workoutId: number,
  payload: WorkoutPayload,
  locale: string,
): Promise<WorkoutRead> {
  return apiRequest<WorkoutRead>(`/workouts/${workoutId}${buildQuery({ locale })}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export function deleteWorkout(workoutId: number): Promise<void> {
  return apiRequest<void>(`/workouts/${workoutId}`, { method: 'DELETE' })
}