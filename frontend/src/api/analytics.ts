import { apiRequest } from '@/api/client'

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

export function getExerciseProgress(exerciseId: number): Promise<ExerciseProgressPointRead[]> {
  return apiRequest<ExerciseProgressPointRead[]>(`/analytics/exercises/${exerciseId}/progress`)
}