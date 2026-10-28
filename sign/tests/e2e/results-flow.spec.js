import { expect, test } from '@playwright/test'

import { mockAuthenticatedSession } from './support/auth'

test.beforeEach(async ({ page }) => {
  await mockAuthenticatedSession(page)
})

test('moves from actionable overview to result detail and export', async ({ page }) => {
  await page.goto('/app/overview')

  await expect(page.getByRole('heading', { name: /好，演示用户/ })).toBeVisible()
  await expect(page.getByRole('img', { name: /近 7 天完成任务/ })).toBeVisible()
  await page.getByRole('link', { name: /你好，很高兴认识你/ }).click()

  await expect(page.getByRole('heading', { name: '你好，很高兴认识你。' })).toBeVisible()
  await expect(page.getByText('模型版本')).toBeVisible()
  await expect(page.getByText('标签与时间轴')).toBeVisible()

  const downloadPromise = page.waitForEvent('download')
  await page.getByRole('button', { name: '导出结果' }).click()
  const download = await downloadPromise
  expect(download.suggestedFilename()).toContain('signflow-result-')
})

test('results center merges modes into one filterable list on mobile', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/app/results')

  await expect(page.getByRole('heading', { name: '结果中心' })).toBeVisible()
  await expect(page.getByText('你好，很高兴认识你。')).toBeVisible()
  await page.getByTestId('mode-filter').click()
  await page.getByText('视频', { exact: true }).last().click()

  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
  )
  expect(overflow).toBe(false)
})
