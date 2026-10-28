export async function mockAuthenticatedSession(page, overrides = {}) {
  const user = {
    id: 1,
    username: 'demo_user',
    displayName: '演示用户',
    email: 'demo@example.test',
    ...overrides.user,
  }
  const roles = overrides.roles || ['普通用户']

  await page.route('**/api/v1/**', async (route) => {
    const pathname = new URL(route.request().url()).pathname
    if (pathname.endsWith('/api/v1/auth/refresh/')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            access: 'e2e-memory-only-access-token',
            user,
            roles,
          },
          error: null,
          requestId: 'e2e-auth-restore',
        }),
      })
      return
    }

    await route.fulfill({
      status: 503,
      contentType: 'application/json',
      body: JSON.stringify({
        success: false,
        data: null,
        error: { code: 'E2E_OFFLINE', message: 'E2E 使用官方演示适配器。' },
        requestId: 'e2e-offline',
      }),
    })
  })

  await page.route('**/health/ready', (route) => route.fulfill({
    status: 503,
    contentType: 'application/json',
    body: JSON.stringify({ status: 'unavailable' }),
  }))
}
