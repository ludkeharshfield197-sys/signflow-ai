import { describe, expect, it } from 'vitest'

import { routes } from '@/router/routes'

describe('public product routes', () => {
  it('uses a product tour as the public experience and keeps the legacy demo URL compatible', () => {
    const publicTour = routes.find((route) => route.path === '/product-tour')
    const privacy = routes.find((route) => route.path === '/privacy')
    const legacyDemo = routes.find((route) => route.path === '/demo')

    expect(publicTour?.meta?.title).toContain('产品导览')
    expect(privacy?.meta?.title).toContain('隐私与数据保留')
    expect(legacyDemo?.redirect).toBe('/product-tour')

    const visibleTitles = routes
      .map((route) => route.meta?.title)
      .filter(Boolean)
      .join(' ')
    expect(visibleTitles).not.toMatch(/赛题|比赛|竞赛|参赛|AI\+X/)
  })
})
