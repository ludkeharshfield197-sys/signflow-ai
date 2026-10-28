import { describe, expect, it } from 'vitest'


describe('post-login navigation', () => {
  it('rejects scheme-relative and external redirect targets', async () => {
    const { safeRedirectPath } = await import('@/services/navigation')

    expect(safeRedirectPath('/app/results?status=done')).toBe('/app/results?status=done')
    expect(safeRedirectPath('//evil.example/path')).toBe('/app/overview')
    expect(safeRedirectPath('https://evil.example/path')).toBe('/app/overview')
    expect(safeRedirectPath('javascript:alert(1)')).toBe('/app/overview')
  })
})

