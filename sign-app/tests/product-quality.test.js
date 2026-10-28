import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import test from 'node:test'
import { fileURLToPath } from 'node:url'

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const pages = JSON.parse(
  fs.readFileSync(path.join(projectRoot, 'src', 'pages.json'), 'utf8'),
)
const pngSignature = Buffer.from('89504e470d0a1a0a', 'hex')

function readPng(relativePath) {
  const bytes = fs.readFileSync(path.join(projectRoot, 'src', relativePath))
  assert.deepEqual(bytes.subarray(0, 8), pngSignature, `${relativePath} must be a binary PNG`)
  return {
    width: bytes.readUInt32BE(16),
    height: bytes.readUInt32BE(20),
  }
}

test('all four tab bar states use consistent 200px binary PNG assets', () => {
  const dimensions = pages.tabBar.list.flatMap((item) => [
    readPng(item.iconPath),
    readPng(item.selectedIconPath),
  ])

  assert.equal(dimensions.length, 8)
  assert.deepEqual([...new Set(dimensions.map(({ width, height }) => `${width}x${height}`))], [
    '200x200',
  ])
})
