import { flushPromises, mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import AnalyticsPage from '@/views/analytics/AnalyticsPage.vue'

const analyticsService = vi.hoisted(() => ({
  getAnalytics: vi.fn(),
}))

vi.mock('@/services/analytics', () => analyticsService)
vi.mock('@/components/charts/BaseChart.vue', () => ({
  default: {
    props: ['title'],
    template: '<article>{{ title }}</article>',
  },
}))

describe('AnalyticsPage', () => {
  it('uses aggregate task metrics instead of averaging zero-activity days', async () => {
    analyticsService.getAnalytics.mockResolvedValue({
      dataKind: 'live',
      source: 'SignFlow AI 实际识别任务',
      range: '最近 7 天',
      rangeKey: '7d',
      metrics: {
        tasks: 12,
        successRate: 100,
        averageLatencyMs: 1800,
      },
      daily: [
        { date: '08-19', tasks: 0, latencyMs: 0, successRate: 0 },
        { date: '08-20', tasks: 0, latencyMs: 0, successRate: 0 },
        { date: '08-21', tasks: 0, latencyMs: 0, successRate: 0 },
        { date: '08-22', tasks: 0, latencyMs: 0, successRate: 0 },
        { date: '08-23', tasks: 0, latencyMs: 0, successRate: 0 },
        { date: '08-24', tasks: 0, latencyMs: 0, successRate: 0 },
        { date: '08-25', tasks: 12, latencyMs: 1800, successRate: 100 },
      ],
      modes: [
        { name: '图片', value: 8 },
        { name: '视频', value: 4 },
      ],
      popularLabels: [],
      updatedAt: '2026-08-25T16:00:00+08:00',
    })

    const wrapper = mount(AnalyticsPage, {
      global: {
        stubs: {
          ElSelect: { template: '<div><slot /></div>' },
          ElOption: true,
        },
      },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('100.0%')
    expect(wrapper.text()).toContain('1.80 秒')
  })
})
