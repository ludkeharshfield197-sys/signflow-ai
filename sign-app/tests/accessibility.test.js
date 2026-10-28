import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import test from 'node:test'
import { fileURLToPath } from 'node:url'

import {
  accessibilityClass,
  enhanceH5Buttons,
  enhanceH5Inputs,
  loadAccessibilityPreferences,
  saveAccessibilityPreferences,
} from '../src/services/accessibility.js'

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')

function memoryStorage() {
  const values = new Map()
  return {
    getStorageSync(key) {
      return values.get(key)
    },
    setStorageSync(key, value) {
      values.set(key, value)
    },
  }
}

test('large-text and high-contrast preferences persist as an explicit page class', () => {
  const storage = memoryStorage()
  const saved = saveAccessibilityPreferences(
    { largeText: true, highContrast: true },
    storage,
  )

  assert.deepEqual(saved, { largeText: true, highContrast: true })
  assert.deepEqual(loadAccessibilityPreferences(storage), saved)
  assert.equal(accessibilityClass(saved), 'sf-a11y-large sf-a11y-high-contrast')
})

test('every mobile text input has a programmatic label, placeholder and aria-label', () => {
  for (const relativePath of [
    'src/pages/login/login.vue',
    'src/pages/register/register.vue',
    'src/pages/profile/profile.vue',
  ]) {
    const source = fs.readFileSync(path.join(projectRoot, relativePath), 'utf8')
    const inputs = source.match(/<input[\s\S]*?\/>/g) || []
    assert.ok(inputs.length > 0, `${relativePath} should contain tested inputs`)
    for (const input of inputs) {
      const id = input.match(/\bid="([^"]+)"/)?.[1]
      assert.ok(id, `${relativePath} input must have an id`)
      assert.match(input, /\bplaceholder="[^"]+"/)
      assert.match(input, /\baria-label="[^"]+"/)
      assert.match(
        source,
        new RegExp(`<label[^>]+for="${id}"[^>]*>`),
        `${relativePath} input ${id} must have a matching label`,
      )
    }
  }
})

test('global mobile interaction styles enforce 44px touch targets and keyboard focus', () => {
  const source = fs.readFileSync(path.join(projectRoot, 'src/App.vue'), 'utf8')

  assert.match(
    source,
    /\.sf-page button,[\s\S]*\.login-page uni-button\s*\{[\s\S]*min-height:\s*88rpx\s*!important/,
  )
  assert.match(source, /\.sf-page uni-button,\s*\.login-page uni-button/)
  assert.match(source, /:focus-visible/)
  assert.match(source, /\.sf-a11y-large/)
  assert.match(source, /\.sf-a11y-high-contrast/)
})

test('H5 enhancement transfers each uni-input label to its native text box', () => {
  const nativeAttributes = new Map()
  const native = {
    setAttribute(name, value) {
      nativeAttributes.set(name, value)
    },
  }
  const removed = []
  const wrapper = {
    querySelector(selector) {
      return selector === 'input' ? native : null
    },
    removeAttribute(name) {
      removed.push(name)
    },
  }
  const labelAttributes = new Map()
  const label = {
    setAttribute(name, value) {
      labelAttributes.set(name, value)
    },
  }
  const root = {
    querySelector(selector) {
      if (selector === '#login-username') return wrapper
      if (selector === 'label[for="login-username"]') return label
      return null
    },
  }

  enhanceH5Inputs(
    [
      {
        id: 'login-username',
        name: 'username',
        label: '登录账号',
        placeholder: '请输入账号',
        autocomplete: 'username',
      },
    ],
    root,
  )

  assert.equal(nativeAttributes.get('id'), 'login-username-native')
  assert.equal(nativeAttributes.get('name'), 'username')
  assert.equal(nativeAttributes.get('aria-label'), '登录账号')
  assert.equal(nativeAttributes.get('placeholder'), '请输入账号')
  assert.equal(nativeAttributes.get('autocomplete'), 'username')
  assert.equal(labelAttributes.get('for'), 'login-username-native')
  assert.deepEqual(removed, ['aria-label'])
})

test('H5 enhancement makes rendered uni-buttons keyboard-operable', () => {
  const attributes = new Map()
  const listeners = new Map()
  let clicks = 0
  const button = {
    textContent: '创建新账号',
    getAttribute(name) {
      return attributes.get(name) || null
    },
    setAttribute(name, value) {
      attributes.set(name, String(value))
    },
    addEventListener(name, listener) {
      listeners.set(name, listener)
    },
    click() {
      clicks += 1
    },
  }
  const root = {
    querySelectorAll(selector) {
      return selector === 'uni-button' ? [button] : []
    },
  }

  enhanceH5Buttons(root)
  listeners.get('keydown')({ key: 'Enter', preventDefault() {} })

  assert.equal(attributes.get('role'), 'button')
  assert.equal(attributes.get('tabindex'), '0')
  assert.equal(attributes.get('aria-label'), '创建新账号')
  assert.equal(attributes.get('data-sf-keyboard'), 'true')
  assert.equal(clicks, 1)
})
