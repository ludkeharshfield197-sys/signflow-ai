import { expect, test } from '@playwright/test'

test('guest completes the guided product loop', async ({ page }) => {
  await page.goto('/product-tour')

  await expect(page.getByRole('heading', { name: /从识别到确认/ })).toBeVisible()
  await page.getByRole('button', { name: '体验图片识别' }).click()
  await page.getByLabel('识别结果').getByRole('button', { name: '开始识别' }).click()

  await expect(
    page.getByLabel('识别结果').getByText('识别完成', { exact: true }),
  ).toBeVisible({ timeout: 5000 })
  await expect(page.getByRole('button', { name: '查看完整结果' })).toBeVisible()
  await expect(page.getByText('AI 生成授权素材')).toBeVisible()
})
