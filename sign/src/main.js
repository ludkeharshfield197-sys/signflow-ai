import { createApp } from 'vue'

import '@/styles/tokens.css'
import '@/styles/element-theme.scss'
import '@/styles/base.css'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(router)
app.mount('#app')
