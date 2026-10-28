const DEFAULT_APP_PATH = '/app/overview'


export function safeRedirectPath(value, fallback = DEFAULT_APP_PATH) {
  if (typeof value !== 'string' || !value.startsWith('/') || value.startsWith('//') || value.includes('\\')) {
    return fallback
  }
  try {
    const origin = typeof window === 'undefined' ? 'https://signflow.invalid' : window.location.origin
    const target = new URL(value, origin)
    if (target.origin !== origin) return fallback
    return `${target.pathname}${target.search}${target.hash}`
  } catch {
    return fallback
  }
}

