import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import RecognitionWorkbench from '@/views/workbench/RecognitionWorkbench.vue'
import api from '@/services/api'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn().mockRejectedValue(new Error('offline test')),
    post: vi.fn(),
  },
  getApiError: vi.fn(() => '服务暂时不可用'),
}))

const global = {
  stubs: {
    Teleport: true,
    ElIcon: { template: '<i><slot /></i>' },
    ElTooltip: { template: '<span><slot /></span>' },
  },
}

describe('recognition workbench', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    api.get.mockReset().mockRejectedValue(new Error('offline test'))
    api.post.mockClear()
  })
  afterEach(() => {
    vi.clearAllTimers()
    vi.useRealTimers()
  })

  it('keeps advanced thresholds hidden until requested', async () => {
    const wrapper = mount(RecognitionWorkbench, {
      props: { initialMode: 'image' },
      global,
    })

    expect(wrapper.get('[data-testid="advanced-settings"]').attributes('style')).toContain('display: none')
    await wrapper.get('[data-testid="open-advanced"]').trigger('click')
    expect(wrapper.get('[data-testid="advanced-settings"]').attributes('style') || '').not.toContain('display: none')
  })

  it('switches all three input modes in one workspace', async () => {
    const wrapper = mount(RecognitionWorkbench, {
      props: { initialMode: 'image' },
      global,
    })

    const tabs = wrapper.findAll('[role="tab"]')
    expect(tabs).toHaveLength(3)
    await tabs[2].trigger('click')
    expect(tabs[2].attributes('aria-selected')).toBe('true')
  })

  it('switches between Chinese and English sign language models', async () => {
    api.get.mockResolvedValueOnce({
      data: {
        data: {
          items: [
            {
              id: 2,
              name: 'SignFlow CSL 37',
              version: '11n-local',
              languageCode: 'csl',
              language: '中国手语（CSL）',
              status: 'active',
            },
            {
              id: 1,
              name: 'SignFlow Base',
              version: '2.1-local',
              languageCode: 'asl',
              language: '美国手语（ASL）',
              status: 'active',
            },
          ],
        },
      },
    })
    const wrapper = mount(RecognitionWorkbench, {
      props: { initialMode: 'image' },
      global,
    })
    await flushPromises()

    const chinese = wrapper.get('[data-testid="language-csl"]')
    const english = wrapper.get('[data-testid="language-asl"]')
    expect(chinese.attributes('aria-pressed')).toBe('true')

    await english.trigger('click')
    expect(english.attributes('aria-pressed')).toBe('true')

    await wrapper.get('[data-testid="open-advanced"]').trigger('click')
    expect(wrapper.get('#advanced-model').element.value).toBe('1')
  })

  it('switches public-service context and accessibility presentation', async () => {
    const wrapper = mount(RecognitionWorkbench, {
      props: { initialMode: 'image' },
      global,
    })

    await wrapper.get('[data-testid="scenario-education"]').trigger('click')
    expect(wrapper.get('[data-testid="scenario-education"]').attributes('aria-pressed')).toBe('true')

    await wrapper.get('[data-testid="toggle-large-text"]').trigger('click')
    await wrapper.get('[data-testid="toggle-high-contrast"]').trigger('click')
    expect(wrapper.classes()).toContain('sf-workbench--large-text')
    expect(wrapper.classes()).toContain('sf-workbench--high-contrast')
  })

  it('does not submit an upload with an unavailable model catalog', async () => {
    const wrapper = mount(RecognitionWorkbench, {
      props: { initialMode: 'image' },
      global,
    })
    await flushPromises()
    const file = new File(['image bytes'], 'gesture.jpg', { type: 'image/jpeg' })
    const input = wrapper.get('input[type="file"]')
    Object.defineProperty(input.element, 'files', { value: [file] })
    await input.trigger('change')

    await wrapper.get('button.sf-workbench__start').trigger('click')
    await flushPromises()

    expect(api.post).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('等待开始')
  })

  it('completes the curated official sample with an explicit demo label', async () => {
    const wrapper = mount(RecognitionWorkbench, {
      props: { initialMode: 'video', guest: true },
      global,
    })

    const inspector = wrapper.get('[aria-label="识别结果"]')
    await inspector.get('button').trigger('click')
    await vi.advanceTimersByTimeAsync(1500)
    await flushPromises()

    expect(wrapper.text()).toContain('你好，很高兴认识你。')
    expect(wrapper.text()).toContain('演示数据')
  })
})
