import test from 'node:test'
import assert from 'node:assert/strict'

import { confidencePercent, isTerminalStatus } from '../src/services/detections.js'

test('recognizes only persisted terminal task states', () => {
  assert.equal(isTerminalStatus('queued'), false)
  assert.equal(isTerminalStatus('running'), false)
  assert.equal(isTerminalStatus('succeeded'), true)
  assert.equal(isTerminalStatus('cancelled'), true)
})

test('formats task confidence without presenting it as model accuracy', () => {
  assert.equal(confidencePercent(0.463771), '46.4%')
  assert.equal(confidencePercent(null), '—')
  assert.equal(confidencePercent('not-a-number'), '—')
})
