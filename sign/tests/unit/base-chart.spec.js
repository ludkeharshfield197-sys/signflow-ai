import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const chartRuntime = vi.hoisted(() => ({
  dispose: vi.fn(),
  init: vi.fn(),
  resize: vi.fn(),
  setOption: vi.fn(),
  use: vi.fn(),
}))

vi.mock('echarts/core', () => ({
  init: chartRuntime.init,
  use: chartRuntime.use,
}))
vi.mock('echarts/charts', () => ({
  BarChart: {},
  LineChart: {},
  PieChart: {},
}))
vi.mock('echarts/components', () => ({
  AriaComponent: {},
  DatasetComponent: {},
  GridComponent: {},
  LegendComponent: {},
  TitleComponent: {},
  TooltipComponent: {},
}))
vi.mock('echarts/renderers', () => ({
  CanvasRenderer: {},
}))

describe('BaseChart', () => {
  beforeEach(() => {
    chartRuntime.dispose.mockReset()
    chartRuntime.init.mockReset()
    chartRuntime.resize.mockReset()
    chartRuntime.setOption.mockReset()
    chartRuntime.init.mockReturnValue({
      dispose: chartRuntime.dispose,
      resize: chartRuntime.resize,
      setOption: chartRuntime.setOption,
    })
  })

  it('initializes after an initial loading state is replaced by the canvas', async () => {
    const { default: BaseChart } = await import('@/components/charts/BaseChart.vue')
    const wrapper = mount(BaseChart, {
      props: {
        title: '近 7 天完成任务',
        loading: true,
        option: { series: [{ data: [0, 1] }] },
      },
    })

    expect(chartRuntime.init).not.toHaveBeenCalled()

    await wrapper.setProps({ loading: false })
    await nextTick()

    expect(chartRuntime.init).toHaveBeenCalledOnce()
    expect(chartRuntime.setOption).toHaveBeenCalled()

    wrapper.unmount()
    expect(chartRuntime.dispose).toHaveBeenCalledOnce()
  })
})
