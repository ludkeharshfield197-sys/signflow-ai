import { expect, test } from '@playwright/test'

test('public and auth routes render without console errors', async ({ page }) => {
  const errors = []
  page.on('console', (message) => {
    if (message.type() === 'error') errors.push(message.text())
  })
  page.on('pageerror', (error) => errors.push(error.message))

  await page.goto('/')
  await expect(page.getByRole('heading', { name: /让每一次手语表达/ })).toBeVisible()

  await page.goto('/auth/login')
  await expect(page.getByRole('heading', { name: '登录 SignFlow AI' })).toBeVisible()
  expect(errors).toEqual([])
})

