import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import ServiceContextBar from '@/components/workbench/ServiceContextBar.vue'

const global = {
  stubs: {
    ElIcon: { template: '<i><slot /></i>' },
  },
}

describe('service context bar', () => {
  it('offers three service scenarios and changes the active context', async () => {
    const wrapper = mount(ServiceContextBar, {
      props: {
        scenario: 'government',
        largeText: false,
        highContrast: false,
      },
      global,
    })

    const scenarios = wrapper.findAll('[data-testid^="scenario-"]')
    expect(scenarios).toHaveLength(3)
    expect(wrapper.get('[data-testid="scenario-government"]').attributes('aria-pressed')).toBe('true')

    await wrapper.get('[data-testid="scenario-medical"]').trigger('click')
    expect(wrapper.emitted('update:scenario')).toEqual([['medical']])
  })

  it('exposes working large-text and high-contrast controls', async () => {
    const wrapper = mount(ServiceContextBar, {
      props: {
        scenario: 'government',
        largeText: false,
        highContrast: false,
      },
      global,
    })

    await wrapper.get('[data-testid="toggle-large-text"]').trigger('click')
    await wrapper.get('[data-testid="toggle-high-contrast"]').trigger('click')

    expect(wrapper.emitted('update:largeText')).toEqual([[true]])
    expect(wrapper.emitted('update:highContrast')).toEqual([[true]])
  })
})
