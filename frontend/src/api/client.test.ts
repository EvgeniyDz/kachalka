import { afterEach, describe, expect, it, vi } from 'vitest'

import { apiRequest } from '@/api/client'

afterEach(() => {
  vi.restoreAllMocks()
})

describe('apiRequest', () => {
  it('handles 204 responses without JSON body', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(new Response(null, { status: 204 })),
    )

    await expect(apiRequest<void>('/resource/1', { method: 'DELETE' })).resolves.toBeUndefined()
  })
})