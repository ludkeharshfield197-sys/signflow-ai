import { config } from '@vue/test-utils'

class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}

globalThis.ResizeObserver = ResizeObserverMock
globalThis.matchMedia =
  globalThis.matchMedia ||
  (() => ({
    matches: false,
    addEventListener() {},
    removeEventListener() {},
  }))

config.global.stubs = {
  transition: false,
  'transition-group': false,
}
