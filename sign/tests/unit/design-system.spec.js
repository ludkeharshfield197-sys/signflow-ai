import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import EmptyState from '@/components/ui/EmptyState.vue'
import MetricCard from '@/components/ui/MetricCard.vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import tokens from '@/styles/tokens.css?raw'

describe('design tokens', () => {
  it('defines the required commercial theme tokens', () => {
    expect(tokens).toContain('--sf-color-primary: #5b5bd6')
    expect(tokens).toContain('--sf-radius-card: 16px')
    expect(tokens).toContain('--sf-color-text: #182230')
    expect(tokens).toContain('--sf-color-accent: #0e9384')
  })
})

describe('commercial UI primitives', () => {
  it('renders a semantic page heading and action region', () => {
    const wrapper = mount(PageHeader, {
      props: { title: '识别工作台', description: '完成一次识别任务' },
      slots: { actions: '<button type="button">开始识别</button>' },
    })

    expect(wrapper.get('h1').text()).toBe('识别工作台')
    expect(wrapper.text()).toContain('开始识别')
  })

  it('renders metrics and status with explicit meaning', () => {
    const metric = mount(MetricCard, {
      props: { label: '完成任务', value: 28, trend: '+3', tone: 'positive', source: '任务接口' },
    })
    const status = mount(StatusBadge, {
      props: { label: '服务正常', tone: 'success' },
    })

    expect(metric.text()).toContain('完成任务')
    expect(metric.attributes('data-tone')).toBe('positive')
    expect(status.get('[role="status"]').text()).toBe('服务正常')
  })

  it('does not present a metric as trustworthy without source metadata', () => {
    const wrapper = mount(MetricCard, {
      props: { label: '系统准确率', value: '96.8%' },
    })

    expect(wrapper.text()).toContain('数据来源未配置')
  })

  it('supports keyboard activation in an empty state', async () => {
    const wrapper = mount(EmptyState, {
      props: {
        title: '暂无结果',
        description: '开始一次识别后，结果会显示在这里。',
        actionLabel: '开始识别',
      },
    })

    await wrapper.get('button').trigger('keydown', { key: 'Enter' })
    expect(wrapper.emitted('action')).toHaveLength(1)
  })
})
