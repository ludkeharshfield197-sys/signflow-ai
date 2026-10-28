import test from 'node:test'
import assert from 'node:assert/strict'

import {
  buildCameraSocketUrl,
  createSessionId,
  normalizeServerOrigin,
  toWebSocketOrigin,
} from '../src/services/config.js'

test('normalizes API origins without allowing credentials or paths', () => {
  assert.equal(normalizeServerOrigin(' HTTPS://api.example.test/ '), 'https://api.example.test')
  assert.throws(() => normalizeServerOrigin('https://name:secret@example.test'))
  assert.throws(() => normalizeServerOrigin('https://api.example.test/private'))
})

test('builds encoded WSS camera ticket URLs', () => {
  assert.equal(toWebSocketOrigin('https://api.example.test'), 'wss://api.example.test')
  const url = buildCameraSocketUrl({
    serverOrigin: 'https://api.example.test',
    sessionId: 'session-1',
    ticket: 'a+b/=?',
    modelId: 7,
  })
  assert.match(url, /^wss:\/\/api\.example\.test\/ws\/camera\/session-1\//)
  assert.match(url, /ticket=a%2Bb%2F%3D%3F/)
  assert.match(url, /modelId=7/)
})

test('creates database-safe 36-character session identifiers', () => {
  const id = createSessionId(() => 1_700_000_000_000, () => 0.123456)
  assert.equal(id.length, 36)
  assert.match(id, /^[a-f0-9-]+$/)
})
