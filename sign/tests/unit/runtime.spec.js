import { describe, expect, it } from 'vitest'

describe('frontend runtime', () => {
  it('provides a browser-like DOM for component tests', () => {
    const root = document.createElement('main')
    root.dataset.app = 'signflow'

    expect(root.dataset.app).toBe('signflow')
    expect(root).toBeInstanceOf(HTMLElement)
  })
})
