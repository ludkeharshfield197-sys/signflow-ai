import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import AppSidebar from '@/layout/app/AppSidebar.vue'
import { canAccessAdmin, productNavigation } from '@/layout/app/navigation'

const global = {
  stubs: {
    RouterLink: {
      props: ['to'],
      template: '<a :href="to"><slot /></a>',
    },
    ElIcon: {
      template: '<i><slot /></i>',
    },
  },
}

describe('application navigation', () => {
  it('keeps the primary product navigation shallow', () => {
    expect(productNavigation.map((item) => item.label)).toEqual([
      '概览',
      '识别工作台',
      '结果中心',
      '数据洞察',
      '模型中心',
      '设置',
    ])
  })

  it('hides admin navigation for a normal user', () => {
    const wrapper = mount(AppSidebar, {
      props: { role: 'user', collapsed: false },
      global,
    })

    expect(wrapper.text()).toContain('识别工作台')
    expect(wrapper.text()).not.toContain('管理后台')
    expect(wrapper.text()).not.toContain('用户管理')
  })

  it('shows a separate admin entry for administrators', () => {
    const wrapper = mount(AppSidebar, {
      props: { role: 'superadmin', collapsed: false },
      global,
    })

    expect(wrapper.text()).toContain('管理后台')
    expect(canAccessAdmin('superadmin')).toBe(true)
    expect(canAccessAdmin('user')).toBe(false)
  })

  it('retains accessible labels when the sidebar is collapsed', () => {
    const wrapper = mount(AppSidebar, {
      props: { role: 'user', collapsed: true },
      global,
    })

    expect(wrapper.get('aside').attributes('aria-label')).toBe('产品导航')
    expect(wrapper.get('button').attributes('aria-label')).toBe('展开侧栏')
  })
})

