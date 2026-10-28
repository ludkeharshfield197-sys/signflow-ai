import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const platform = process.argv[2]
const supportedPlatforms = new Set(['h5', 'mp-weixin'])

if (!supportedPlatforms.has(platform)) {
  throw new Error(`Unsupported build platform: ${platform ?? '(missing)'}`)
}

const sourceDir = path.join(projectRoot, 'src', 'static', 'tabbar')
const outputDir = path.join(projectRoot, 'dist', 'build', platform, 'static', 'tabbar')
const expectedFiles = [
  'home.png',
  'home-active.png',
  'recognize.png',
  'recognize-active.png',
  'history.png',
  'history-active.png',
  'my.png',
  'my-active.png',
]
const pngSignature = Buffer.from('89504e470d0a1a0a', 'hex')

fs.mkdirSync(outputDir, { recursive: true })

for (const filename of expectedFiles) {
  const sourcePath = path.join(sourceDir, filename)
  const outputPath = path.join(outputDir, filename)
  const sourceBytes = fs.readFileSync(sourcePath)

  assert.deepEqual(
    sourceBytes.subarray(0, 8),
    pngSignature,
    `${filename} must be a binary PNG`,
  )
  assert.equal(sourceBytes.readUInt32BE(16), 200, `${filename} width must be 200px`)
  assert.equal(sourceBytes.readUInt32BE(20), 200, `${filename} height must be 200px`)

  fs.copyFileSync(sourcePath, outputPath)
  assert.deepEqual(fs.readFileSync(outputPath), sourceBytes, `${filename} copy mismatch`)
}

console.log(`Synced and verified ${expectedFiles.length} tab bar assets for ${platform}.`)
