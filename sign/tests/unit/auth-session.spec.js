import { beforeEach, describe, expect, it, vi } from 'vitest'


describe('secure authentication session', () => {
  beforeEach(() => {
    window.localStorage.clear()
    window.sessionStorage.clear()
    vi.resetModules()
    vi.doUnmock('@/services/api')
  })

  it('keeps bearer tokens out of browser storage', async () => {
    const { getSession, setSession } = await import('@/services/session')

    setSession({
      accessToken: 'short-lived-access-token',
      refreshToken: 'long-lived-refresh-token',
      user: { id: 1, username: 'platform_admin', role: 'superadmin' },
    })

    expect(getSession().accessToken).toBe('short-lived-access-token')
    expect(window.localStorage.getItem('signflow.session')).toBeNull()
    expect(window.sessionStorage.getItem('signflow.session')).toBeNull()
    expect(JSON.stringify(window.localStorage)).not.toContain('long-lived-refresh-token')
  })

  it('restores an expired page session through the refresh cookie', async () => {
    vi.doMock('@/services/api', () => ({
      default: {
        post: vi.fn().mockResolvedValue({
          data: {
            success: true,
            data: {
              access: 'restored-access-token',
              user: {
                id: 8,
                username: 'restored_admin',
                email: 'restored@example.test',
                avatar: '',
              },
              roles: ['超级管理员'],
            },
            error: null,
            requestId: 'request-test-restore',
          },
        }),
      },
    }))
    const { restoreSession } = await import('@/services/auth')
    const { getSession } = await import('@/services/session')

    const restored = await restoreSession()

    expect(restored).toBe(true)
    expect(getSession()).toEqual({
      accessToken: 'restored-access-token',
      user: expect.objectContaining({ username: 'restored_admin', role: 'superadmin' }),
    })
  })

  it('renews an existing in-memory session after an access-token expiry', async () => {
    vi.doMock('@/services/api', () => ({
      default: {
        post: vi.fn().mockResolvedValue({
          data: {
            success: true,
            data: {
              access: 'rotated-access-token',
              user: {
                id: 9,
                username: 'active_user',
                email: '',
                avatar: '',
              },
              roles: ['普通用户'],
            },
            error: null,
            requestId: 'request-test-renew',
          },
        }),
      },
    }))
    const { renewSession } = await import('@/services/auth')
    const { getSession, setSession } = await import('@/services/session')
    setSession({
      accessToken: 'expired-access-token',
      user: { id: 9, username: 'active_user', role: 'user' },
    })

    const renewed = await renewSession()

    expect(renewed).toBe(true)
    expect(getSession().accessToken).toBe('rotated-access-token')
  })

  it('clears local state after the server revokes the browser session', async () => {
    vi.doMock('@/services/api', () => ({
      default: {
        post: vi.fn().mockResolvedValue({
          data: {
            success: true,
            data: { loggedOut: true },
            error: null,
            requestId: 'request-test-logout',
          },
        }),
      },
    }))
    const { logout } = await import('@/services/auth')
    const { getSession, setSession } = await import('@/services/session')
    setSession({
      accessToken: 'active-access-token',
      user: { id: 9, username: 'active_user', role: 'user' },
    })

    await logout()

    expect(getSession()).toEqual({ accessToken: '', user: null })
  })
})
