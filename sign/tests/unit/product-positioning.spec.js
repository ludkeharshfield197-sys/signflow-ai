import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import HomeView from '@/views/HomeView.vue'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn().mockRejectedValue(new Error('offline test')),
  },
}))

const global = {
  stubs: {
    ElIcon: { template: '<i><slot /></i>' },
    RouterLink: { template: '<a><slot /></a>' },
    PublicHeader: { template: '<header />' },
    PublicFooter: { template: '<footer />' },
    DemoPreview: { template: '<div />' },
  },
}

describe('commercial product positioning', () => {
  it('presents a scenario-based sign-language product without competition framing', () => {
    const wrapper = mount(HomeView, { global })

    expect(wrapper.text()).toContain('无界手语 SignFlow AI')
    expect(wrapper.text()).toContain('多模态手语沟通平台')
    expect(wrapper.text()).toContain('让手语沟通自然进入每一次服务')
    expect(wrapper.text()).toContain('政务服务')
    expect(wrapper.text()).toContain('医疗导诊')
    expect(wrapper.text()).toContain('特殊教育')
    expect(wrapper.text()).not.toMatch(/赛题|比赛|竞赛|参赛|AI\+X/)
  })
})
