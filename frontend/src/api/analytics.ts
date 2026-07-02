import { apiRequest } from '@/api/client'
import type { ExerciseRead, MuscleGroupRead } from '@/api/exercises'

export interface ExerciseProgressPointRead {
  workout_id: number
  workout_date: string
  exercise_set_id: number
  set_number: number
  weight: string | null
  reps: number | null
  volume: string | null
  estimated_1rm: string | null
}

export interface WeeklyVolumeRead {
  week_start: string
  volume: string
  workout_count: number
}

export interface PersonalRecordRead {
  id: number
  record_type: string
  value: string
  workout_id: number | null
  exercise_set_id: number | null
  exercise: ExerciseRead
}

export interface MuscleGroupFrequencyRead {
  muscle_group: MuscleGroupRead
  exercise_count: number
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

export function getExerciseProgress(exerciseId: number): Promise<ExerciseProgressPointRead[]> {
  return apiRequest<ExerciseProgressPointRead[]>(`/analytics/exercises/${exerciseId}/progress`)
}

export function getWeeklyVolume(): Promise<WeeklyVolumeRead[]> {
  return apiRequest<WeeklyVolumeRead[]>('/analytics/weekly-volume')
}

export function getLatestRecords(locale: string, limit = 5): Promise<PersonalRecordRead[]> {
  return apiRequest<PersonalRecordRead[]>(`/analytics/records${buildQuery({ locale, limit })}`)
}

export function getMuscleGroupFrequency(
  locale: string,
  limit = 5,
): Promise<MuscleGroupFrequencyRead[]> {
  return apiRequest<MuscleGroupFrequencyRead[]>(
    `/analytics/muscle-groups/frequency${buildQuery({ locale, limit })}`,
  )
}