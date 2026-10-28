const STORAGE_KEY = 'signflow.accessibility'
let h5AccessibilityObserver = null

function normalize(preferences = {}) {
  return {
    largeText: preferences.largeText === true,
    highContrast: preferences.highContrast === true,
  }
}

export function loadAccessibilityPreferences(storage = globalThis.uni) {
  if (!storage?.getStorageSync) return normalize()
  try {
    const stored = storage.getStorageSync(STORAGE_KEY)
    return normalize(typeof stored === 'string' ? JSON.parse(stored) : stored)
  } catch {
    return normalize()
  }
}

export function saveAccessibilityPreferences(preferences, storage = globalThis.uni) {
  const normalized = normalize(preferences)
  if (storage?.setStorageSync) storage.setStorageSync(STORAGE_KEY, normalized)
  return normalized
}

export function accessibilityClass(preferences) {
  const normalized = normalize(preferences)
  return [
    normalized.largeText ? 'sf-a11y-large' : '',
    normalized.highContrast ? 'sf-a11y-high-contrast' : '',
  ]
    .filter(Boolean)
    .join(' ')
}

export function enhanceH5Inputs(fields, root = globalThis.document) {
  if (!root?.querySelector) return
  for (const field of fields) {
    if (!/^[a-z0-9-]+$/i.test(field.id)) continue
    const wrapper = root.querySelector(`#${field.id}`)
    const nativeInput = wrapper?.querySelector?.('input')
    if (!nativeInput) continue
    const nativeId = `${field.id}-native`
    nativeInput.setAttribute('id', nativeId)
    nativeInput.setAttribute('name', field.name)
    nativeInput.setAttribute('aria-label', field.label)
    nativeInput.setAttribute('placeholder', field.placeholder)
    if (field.autocomplete) {
      nativeInput.setAttribute('autocomplete', field.autocomplete)
    }
    root.querySelector(`label[for="${field.id}"]`)?.setAttribute('for', nativeId)
    wrapper.removeAttribute?.('aria-label')
  }
}

export function enhanceH5Buttons(root = globalThis.document) {
  if (!root?.querySelectorAll) return
  for (const button of root.querySelectorAll('uni-button')) {
    button.setAttribute('role', 'button')
    button.setAttribute('tabindex', '0')
    if (!button.getAttribute('aria-label')) {
      button.setAttribute('aria-label', String(button.textContent || '').trim())
    }
    if (button.getAttribute('data-sf-keyboard') === 'true') continue
    button.setAttribute('data-sf-keyboard', 'true')
    button.addEventListener('keydown', (event) => {
      if (!['Enter', ' ', 'Spacebar'].includes(event.key)) return
      event.preventDefault()
      button.click()
    })
  }
}

export function startH5AccessibilityObserver(
  root = globalThis.document,
  Observer = globalThis.MutationObserver,
) {
  if (!root?.body || !Observer) return
  enhanceH5Buttons(root)
  if (h5AccessibilityObserver) return
  h5AccessibilityObserver = new Observer(() => enhanceH5Buttons(root))
  h5AccessibilityObserver.observe(root.body, { childList: true, subtree: true })
}
