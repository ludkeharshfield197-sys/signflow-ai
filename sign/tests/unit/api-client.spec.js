import { describe, expect, it } from 'vitest'

import api, { getApiError } from '@/services/api'


describe('API client security', () => {
  it('sends same-origin HttpOnly refresh cookies', () => {
    expect(api.defaults.withCredentials).toBe(true)
  })

  it('surfaces the standardized backend error message', () => {
    const message = getApiError({
      response: {
        status: 400,
        data: {
          success: false,
          data: null,
          error: { code: 'VALIDATION_ERROR', message: '注册信息不符合要求。' },
          requestId: 'request-test-validation',
        },
      },
    })

    expect(message).toBe('注册信息不符合要求。')
  })
})
