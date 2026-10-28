import { expect, test } from '@playwright/test'

test.describe('public navigation', () => {
  test('public and authentication pages never render empty anchor destinations', async ({ page }) => {
    for (const route of ['/', '/product-tour', '/privacy', '/auth/login', '/auth/register']) {
      await page.goto(route)

      const invalidAnchors = page.locator(
        'a:not([href]), a[href=""], a[href="#"], a[href^="javascript:"]',
      )
      await expect(invalidAnchors, `${route} should only contain real link destinations`).toHaveCount(
        0,
      )
    }
  })

  test('product tour footer uses real capability and privacy destinations', async ({ page }) => {
    await page.goto('/product-tour')

    const footer = page.getByRole('contentinfo')
    await footer.getByRole('link', { name: '产品能力' }).click()
    await expect(page).toHaveURL(/\/#capabilities$/)
    await expect(page.locator('#capabilities')).toBeVisible()

    await page.goto('/product-tour')
    await footer.getByRole('link', { name: '隐私政策' }).click()
    await expect(page).toHaveURL(/\/privacy$/)
    await expect(page.getByRole('heading', { name: '隐私与数据保留' })).toBeVisible()
  })

  test('authentication pages use the canonical privacy and service routes', async ({ page }) => {
    await page.goto('/auth/login')
    const authFooter = page.getByRole('contentinfo')

    await expect(authFooter.getByRole('link', { name: '隐私政策' })).toHaveAttribute(
      'href',
      '/privacy',
    )
    await expect(authFooter.getByRole('link', { name: '服务状态' })).toHaveAttribute(
      'href',
      '/health/ready',
    )

    await page.goto('/auth/register')
    await page.getByRole('link', { name: '隐私与数据保留说明' }).click()
    await expect(page).toHaveURL(/\/privacy$/)
  })
})
