import fs from 'node:fs'
import path from 'node:path'

const rootDir = process.cwd()
const envFile = path.join(rootDir, 'server', '.env')

if (fs.existsSync(envFile)) {
  const raw = fs.readFileSync(envFile, 'utf8')
  raw.split(/\r?\n/).forEach((line) => {
    const trimmed = line.trim()
    if (!trimmed || trimmed.startsWith('#')) {
      return
    }

    const separatorIndex = trimmed.indexOf('=')
    if (separatorIndex === -1) {
      return
    }

    const key = trimmed.slice(0, separatorIndex).trim()
    const value = trimmed.slice(separatorIndex + 1).trim().replace(/^["']|["']$/g, '')
    if (!process.env[key]) {
      process.env[key] = value
    }
  })
}

const getEnv = (key: string, fallback = '') => process.env[key]?.trim() || fallback

export const config = {
  port: Number(getEnv('AI_SERVER_PORT', getEnv('RAG_PORT', '3030'))),
  rootDir,
  llmBaseUrl: getEnv('LLM_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1'),
  llmApiKey: getEnv('LLM_API_KEY'),
  llmModel: getEnv('LLM_MODEL', 'qwen-plus')
}

export const ensureConfig = () => {
  if (!config.llmApiKey) {
    throw new Error('Missing LLM_API_KEY environment variable.')
  }
}
