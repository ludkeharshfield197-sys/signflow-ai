import { expect, test } from '@playwright/test'

import { mockAuthenticatedSession } from './support/auth'

test.beforeEach(async ({ page }) => {
  await mockAuthenticatedSession(page)
})

test('desktop sidebar is collapsible and hides admin navigation for users', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 })
  await page.goto('/app/overview')

  await expect(page.getByLabel('产品导航')).toBeVisible()
  await expect(page.getByText('识别工作台', { exact: true })).toBeVisible()
  await expect(page.getByText('管理后台', { exact: true })).toHaveCount(0)
  await expect(page.locator('.sf-chart__canvas canvas')).toHaveCount(1)

  await page.getByRole('button', { name: '收起侧栏' }).click()
  await expect(page.getByRole('button', { name: '展开侧栏' })).toBeVisible()

  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
  )
  expect(overflow).toBe(false)
})

test('mobile navigation uses a drawer without horizontal overflow', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/app/overview')

  await page.getByRole('button', { name: '打开导航' }).click()
  await expect(page.getByRole('dialog', { name: '移动导航' })).toBeVisible()
  await expect(page.getByText('结果中心', { exact: true })).toBeVisible()

  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
  )
  expect(overflow).toBe(false)
})
