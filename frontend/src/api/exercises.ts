import { apiRequest } from '@/api/client'

export interface TranslationRead {
  locale: string
  name: string
  description: string | null
}

export interface TranslationInput {
  locale: string
  name: string
  description?: string | null
}

export interface MuscleGroupRead {
  id: number
  code: string
  name: string
  translations: TranslationRead[]
}

export interface ExerciseRead {
  id: number
  code: string
  name: string
  description: string | null
  equipment: string | null
  is_custom: boolean
  muscle_group: MuscleGroupRead
  translations: TranslationRead[]
}

export interface ExerciseListRead {
  items: ExerciseRead[]
  total: number
  limit: number
  offset: number
}

export interface ExerciseListParams {
  locale: string
  limit?: number
  offset?: number
  search?: string
  muscleGroupCode?: string
  includeCustom?: boolean
}

export interface ExercisePayload {
  code?: string | null
  muscle_group_code: string
  equipment?: string | null
  translations: TranslationInput[]
}

function buildQuery(params: Record<string, string | number | boolean | undefined>): string {
  const searchParams = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== '') {
      searchParams.set(key, String(value))
    }
  })

  const query = searchParams.toString()
  return query ? `?${query}` : ''
}

export function getMuscleGroups(locale: string): Promise<MuscleGroupRead[]> {
  return apiRequest<MuscleGroupRead[]>(`/muscle-groups${buildQuery({ locale })}`)
}

export function getExercises(params: ExerciseListParams): Promise<ExerciseListRead> {
  return apiRequest<ExerciseListRead>(
    `/exercises${buildQuery({
      locale: params.locale,
      limit: params.limit,
      offset: params.offset,
      search: params.search,
      muscle_group_code: params.muscleGroupCode,
      include_custom: params.includeCustom,
    })}`,
  )
}

export function createExercise(payload: ExercisePayload, locale: string): Promise<ExerciseRead> {
  return apiRequest<ExerciseRead>(`/exercises${buildQuery({ locale })}`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updateExercise(
  exerciseId: number,
  payload: ExercisePayload,
  locale: string,
): Promise<ExerciseRead> {
  return apiRequest<ExerciseRead>(`/exercises/${exerciseId}${buildQuery({ locale })}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export function deleteExercise(exerciseId: number): Promise<void> {
  return apiRequest<void>(`/exercises/${exerciseId}`, { method: 'DELETE' })
}