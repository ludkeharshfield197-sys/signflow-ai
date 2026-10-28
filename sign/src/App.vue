<script setup>
import zhCn from 'element-plus/es/locale/lang/zh-cn'

const debounce = (fn, delay) => {
  let timer
  return (...args) => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }
}

if (typeof window !== 'undefined' && window.ResizeObserver) {
  const NativeResizeObserver = window.ResizeObserver
  window.ResizeObserver = class ResizeObserver extends NativeResizeObserver {
    constructor(callback) {
      super(debounce(callback, 120))
    }
  }
}
</script>

<template>
  <el-config-provider :locale="zhCn">
    <router-view />
  </el-config-provider>
</template>
