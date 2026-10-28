import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'
import globals from 'globals'


export default [
  {
    ignores: [
      'dist/**',
      'node_modules/**',
      'node_modules-pre-redesign/**',
      'playwright-report/**',
      'test-results/**',
      'src/api/**',
      'src/store/**',
      'src/util/**',
      'src/layout/footer/**',
      'src/layout/header/**',
      'src/components/HelloWorld.vue',
      'src/components/index.vue',
      'src/views/AboutView.vue',
      'src/views/Agent/**',
      'src/views/bsns/**',
      'src/views/history/**',
      'src/views/index/**',
      'src/views/sys/**',
      'src/views/userCenter/**',
    ],
  },
  js.configs.recommended,
  ...pluginVue.configs['flat/recommended'],
  {
    files: ['**/*.{js,vue}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
    rules: {
      'no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      'vue/html-indent': ['error', 2],
      'vue/html-self-closing': 'off',
      'vue/max-attributes-per-line': 'off',
      'vue/multi-word-component-names': 'off',
      'vue/singleline-html-element-content-newline': 'off',
    },
  },
]
