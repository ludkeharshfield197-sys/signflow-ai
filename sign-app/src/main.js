import { createSSRApp } from 'vue'

import App from './App.vue'
import {
  accessibilityClass,
  loadAccessibilityPreferences,
  saveAccessibilityPreferences,
  startH5AccessibilityObserver,
} from './services/accessibility'

export function createApp() {
  const app = createSSRApp(App)
  app.mixin({
    data() {
      return {
        sfAccessibilityPreferences: loadAccessibilityPreferences(),
      }
    },
    computed: {
      sfAccessibilityClass() {
        return accessibilityClass(this.sfAccessibilityPreferences)
      },
    },
    onShow() {
      this.sfAccessibilityPreferences = loadAccessibilityPreferences()
      this.$nextTick(() => startH5AccessibilityObserver())
    },
    onReady() {
      this.$nextTick(() => startH5AccessibilityObserver())
    },
    methods: {
      sfSetAccessibilityPreferences(preferences) {
        this.sfAccessibilityPreferences = saveAccessibilityPreferences(preferences)
      },
    },
  })
  return { app }
}
