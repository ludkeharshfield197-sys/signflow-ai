import { expect, test } from '@playwright/test'

test.describe('authentication experience', () => {
  test('login has visible labels and no mobile overflow', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 })
    await page.goto('/auth/login')

    await expect(page.getByLabel('账号', { exact: true })).toBeVisible()
    await expect(page.getByLabel('密码')).toBeVisible()
    await expect(page.getByRole('button', { name: '登录' })).toBeVisible()

    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
    )
    expect(overflow).toBe(false)
  })

  test('registration explains password and privacy requirements', async ({ page }) => {
    await page.goto('/auth/register')

    await expect(page.getByLabel('账号', { exact: true })).toBeVisible()
    await expect(page.getByLabel('邮箱（选填）')).toBeVisible()
    await expect(page.getByLabel('密码', { exact: true })).toBeVisible()
    await expect(page.getByLabel('确认密码')).toBeVisible()
    await expect(page.getByText('隐私与数据保留说明')).toBeVisible()
  })
})
