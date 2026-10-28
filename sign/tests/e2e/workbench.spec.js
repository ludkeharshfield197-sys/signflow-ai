import { expect, test } from '@playwright/test'

test('official sample completes the full recognition loop', async ({ page }) => {
  await page.goto('/product-tour?mode=video')

  await expect(page.getByRole('heading', { name: '手语沟通在线体验' })).toBeVisible()
  await expect(page.getByText('演示模式', { exact: true })).toBeVisible()
  await page.getByLabel('识别结果').getByRole('button', { name: '开始识别' }).click()

  await expect(page.getByText('您好，我需要服务台帮助。')).toBeVisible({ timeout: 5000 })
  await expect(page.getByText('官方样例演示结果，不作为公开模型准确率证明')).toBeVisible()
  await expect(page.getByRole('button', { name: /保存到结果中心/ })).toBeVisible()
  await expect(page.getByRole('button', { name: /导出报告/ })).toBeVisible()
  await expect(page.getByRole('button', { name: '确认含义一致' })).toBeVisible()
  await expect(page.getByRole('button', { name: '请求重新表达' })).toBeVisible()
})

test('workbench switches modes and stacks without mobile overflow', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/product-tour?mode=image')

  await page.getByRole('tab', { name: '视频' }).click()
  await expect(page.getByRole('tab', { name: '视频' })).toHaveAttribute('aria-selected', 'true')
  await expect(page.getByText('上传手语视频')).toBeVisible()

  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
  )
  expect(overflow).toBe(false)
})

test('workbench header does not overflow at the compact tablet breakpoint', async ({ page }) => {
  await page.setViewportSize({ width: 656, height: 900 })
  await page.goto('/product-tour?mode=video')

  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
  )
  expect(overflow).toBe(false)
})
