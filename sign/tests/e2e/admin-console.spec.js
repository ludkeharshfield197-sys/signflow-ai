import { expect, test } from '@playwright/test'

import { mockAuthenticatedSession } from './support/auth'

function apiBody(data) {
  return JSON.stringify({
    success: true,
    data,
    error: null,
    requestId: 'e2e-admin',
  })
}

test('administrator can inspect users, roles, and live system state', async ({ page }) => {
  await mockAuthenticatedSession(page, {
    roles: ['超级管理员'],
    user: { username: 'platform_admin', displayName: '平台管理员' },
  })
  await page.route('**/api/v1/admin/users/**', (route) => route.fulfill({
    contentType: 'application/json',
    body: apiBody({
      total: 1,
      source: 'SignFlow AI 用户数据库',
      items: [{
        id: 1,
        username: 'platform_admin',
        email: 'c***@example.test',
        roles: ['超级管理员'],
        status: 'active',
        statusLabel: '正常',
        lastLoginAt: '2026-07-29',
      }],
    }),
  }))
  await page.route('**/api/v1/admin/roles/**', (route) => route.fulfill({
    contentType: 'application/json',
    body: apiBody({
      total: 1,
      source: 'SignFlow AI 权限数据库',
      items: [{
        id: 1,
        name: '超级管理员',
        code: 'superadmin',
        description: '平台环境管理角色',
        userCount: 1,
      }],
    }),
  }))
  await page.route('**/api/v1/admin/system/**', (route) => route.fulfill({
    contentType: 'application/json',
    body: apiBody({
      status: 'ready',
      service: 'signflow-api',
      environment: 'production',
      retentionDays: 30,
      source: 'SignFlow AI 健康检查与业务数据库',
      counts: { users: 1, roles: 1, models: 1, tasks: 3 },
      checks: {
        database: { ok: true, latencyMs: 1 },
        redis: { ok: true, latencyMs: 1 },
        objectStorage: { ok: true, latencyMs: 1 },
        modelService: { ok: true, latencyMs: 2 },
      },
    }),
  }))

  await page.goto('/admin/users')
  await expect(page.getByRole('heading', { name: '用户管理' })).toBeVisible()
  await expect(page.getByText('c***@example.test')).toBeVisible()

  await page.getByRole('link', { name: '角色权限' }).click()
  await expect(page.getByRole('heading', { name: '超级管理员' })).toBeVisible()

  await page.getByRole('link', { name: '系统运行' }).click()
  await expect(page.getByText('全部依赖就绪')).toBeVisible()
  await expect(page.getByText('modelService')).toBeVisible()
})
