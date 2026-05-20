import fs from 'node:fs/promises'
import path from 'node:path'
import { config } from '../config.js'
import type { KnowledgeChunk, RetrievedKnowledge } from '../types.js'

interface KnowledgeIndex {
  chunks: KnowledgeChunk[]
  loadedAt: number
}

const CACHE_TTL = 10_000
const MAX_CHUNK_LENGTH = 1800
const MAX_SOURCE_TEXT_LENGTH = 9000

let cachedIndex: KnowledgeIndex | null = null

const toPosixPath = (value: string) => value.replace(/\\/g, '/')

const safeReadDir = async (dir: string) => {
  try {
    return await fs.readdir(dir, { withFileTypes: true })
  } catch {
    return []
  }
}

const walkFiles = async (dir: string, shouldInclude: (filePath: string) => boolean) => {
  const entries = await safeReadDir(dir)
  const files: string[] = []

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name)

    if (entry.isDirectory()) {
      if (entry.name === 'node_modules' || entry.name === '.vitepress') {
        continue
      }

      files.push(...(await walkFiles(fullPath, shouldInclude)))
      continue
    }

    if (entry.isFile() && shouldInclude(fullPath)) {
      files.push(fullPath)
    }
  }

  return files
}

const stripFrontmatter = (text: string) => text.replace(/^---[\s\S]*?---\s*/u, '')

const normalizeContent = (text: string) =>
  stripFrontmatter(text)
    .replace(/<!--[\s\S]*?-->/gu, '')
    .replace(/\r\n/g, '\n')
    .replace(/[ \t]+\n/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim()

const splitByLength = (text: string, maxLength = MAX_CHUNK_LENGTH) => {
  const chunks: string[] = []
  let rest = text.trim()

  while (rest.length > maxLength) {
    let cutAt = rest.lastIndexOf('\n\n', maxLength)
    if (cutAt < maxLength * 0.45) {
      cutAt = rest.lastIndexOf('\n', maxLength)
    }
    if (cutAt < maxLength * 0.45) {
      cutAt = maxLength
    }

    chunks.push(rest.slice(0, cutAt).trim())
    rest = rest.slice(cutAt).trim()
  }

  if (rest) {
    chunks.push(rest)
  }

  return chunks
}

const splitMarkdownSections = (text: string) => {
  const normalized = normalizeContent(text)
  const sections = normalized
    .split(/(?=^#{1,3}\s+)/gmu)
    .map((section) => section.trim())
    .filter(Boolean)

  return (sections.length ? sections : [normalized]).flatMap((section) => splitByLength(section))
}

const getTitleFromMarkdown = (text: string, fallback: string) => {
  const match = normalizeContent(text).match(/^#\s+(.+)$/mu)
  return match?.[1]?.trim() || fallback
}

const pascalToKebab = (value: string) =>
  value
    .replace(/([a-z0-9])([A-Z])/g, '$1-$2')
    .replace(/[\s_]+/g, '-')
    .toLowerCase()

const createRoute = (relativePath: string, sourceType: KnowledgeChunk['sourceType']) => {
  const posixPath = toPosixPath(relativePath)

  if (sourceType === 'doc') {
    const withoutExt = posixPath.replace(/\.md$/u, '')
    if (withoutExt === 'docs/index') {
      return '/'
    }

    return `/${withoutExt.replace(/^docs\//u, '')}`
  }

  if (sourceType === 'demo') {
    const match = posixPath.match(/^docs\/demo\/([^/]+)\//u)
    return match ? `/components/${pascalToKebab(match[1])}` : '/'
  }

  const match = posixPath.match(/^src\/components\/([^/]+)\//u)
  return match ? `/components/${pascalToKebab(match[1])}` : '/'
}

const getComponentName = (relativePath: string, sourceType: KnowledgeChunk['sourceType']) => {
  const posixPath = toPosixPath(relativePath)

  if (sourceType === 'doc') {
    const match = posixPath.match(/^docs\/components\/([^/]+)\.md$/u)
    return match ? match[1] : undefined
  }

  if (sourceType === 'demo') {
    return posixPath.match(/^docs\/demo\/([^/]+)\//u)?.[1]
  }

  return posixPath.match(/^src\/components\/([^/]+)\//u)?.[1]
}

const createChunkTitle = (
  relativePath: string,
  sourceType: KnowledgeChunk['sourceType'],
  fileText: string,
  chunkText: string
) => {
  if (sourceType === 'doc') {
    const heading = chunkText.match(/^#{1,3}\s+(.+)$/mu)?.[1]?.trim()
    return heading || getTitleFromMarkdown(fileText, path.basename(relativePath, '.md'))
  }

  if (sourceType === 'demo') {
    const demoName = path.basename(relativePath, path.extname(relativePath))
    const componentName = getComponentName(relativePath, sourceType)
    return `${componentName ?? 'Demo'} ${demoName} demo`
  }

  const componentName = getComponentName(relativePath, sourceType)
  return `${componentName ?? path.basename(relativePath, '.ts')} API types`
}

const createChunksForFile = async (
  filePath: string,
  sourceType: KnowledgeChunk['sourceType']
): Promise<KnowledgeChunk[]> => {
  const relativePath = toPosixPath(path.relative(config.rootDir, filePath))
  const fileText = await fs.readFile(filePath, 'utf-8')
  const sections =
    sourceType === 'doc'
      ? splitMarkdownSections(fileText)
      : splitByLength(normalizeContent(fileText), sourceType === 'demo' ? 2200 : 2600)

  return sections
    .filter(Boolean)
    .map((text, index) => ({
      id: `${relativePath}#${index}`,
      title: createChunkTitle(relativePath, sourceType, fileText, text),
      route: createRoute(relativePath, sourceType),
      filePath: relativePath,
      sourceType,
      component: getComponentName(relativePath, sourceType),
      text
    }))
}

const buildKnowledgeIndex = async (): Promise<KnowledgeIndex> => {
  const docsDir = path.join(config.rootDir, 'docs')
  const componentsDir = path.join(config.rootDir, 'src', 'components')

  const docFiles = await walkFiles(docsDir, (filePath) => filePath.endsWith('.md'))
  const demoFiles = await walkFiles(path.join(docsDir, 'demo'), (filePath) => filePath.endsWith('.vue'))
  const typeFiles = await walkFiles(componentsDir, (filePath) => filePath.endsWith(`${path.sep}types.ts`))

  const chunkGroups = await Promise.all([
    ...docFiles.map((filePath) => createChunksForFile(filePath, 'doc')),
    ...demoFiles.map((filePath) => createChunksForFile(filePath, 'demo')),
    ...typeFiles.map((filePath) => createChunksForFile(filePath, 'types'))
  ])

  return {
    chunks: chunkGroups.flat(),
    loadedAt: Date.now()
  }
}

const getKnowledgeIndex = async () => {
  if (!cachedIndex || Date.now() - cachedIndex.loadedAt > CACHE_TTL) {
    cachedIndex = await buildKnowledgeIndex()
  }

  return cachedIndex
}

const extractTerms = (input: string) => {
  const terms = new Set<string>()
  const lowerInput = input.toLowerCase()

  for (const token of lowerInput.match(/[a-z0-9][a-z0-9-]{1,}/gu) ?? []) {
    terms.add(token)
  }

  for (const segment of lowerInput.match(/[\u4e00-\u9fff]+/gu) ?? []) {
    if (segment.length <= 8) {
      terms.add(segment)
    }

    for (let index = 0; index < segment.length - 1; index += 1) {
      terms.add(segment.slice(index, index + 2))
    }

    for (let index = 0; index < segment.length - 2; index += 1) {
      terms.add(segment.slice(index, index + 3))
    }
  }

  return [...terms].filter((term) => term.length >= 2)
}

const hasAnyTerm = (terms: string[], targets: string[]) =>
  terms.some((term) => targets.some((target) => target.includes(term)))

const getMentionedComponents = (chunks: KnowledgeChunk[], question: string) => {
  const lowerQuestion = question.toLowerCase()
  const componentNames = new Set(chunks.map((chunk) => chunk.component).filter(Boolean) as string[])
  const mentioned = new Set<string>()

  for (const componentName of componentNames) {
    const lowerName = componentName.toLowerCase()
    const kebabName = pascalToKebab(componentName)

    if (lowerQuestion.includes(lowerName) || lowerQuestion.includes(kebabName)) {
      mentioned.add(kebabName)
    }
  }

  return mentioned
}

const scoreChunk = (
  chunk: KnowledgeChunk,
  terms: string[],
  question: string,
  currentRoute?: string,
  mentionedComponents = new Set<string>()
) => {
  const title = chunk.title.toLowerCase()
  const component = chunk.component?.toLowerCase() ?? ''
  const route = chunk.route.toLowerCase()
  const text = chunk.text.toLowerCase()
  let score = 0

  for (const term of terms) {
    if (title.includes(term)) {
      score += 12
    }
    if (component.includes(term)) {
      score += 14
    }
    if (route.includes(term)) {
      score += 8
    }
    if (text.includes(term)) {
      score += term.length >= 4 ? 5 : 2
    }
  }

  if (currentRoute && chunk.route === currentRoute) {
    score += 4
  }

  if (chunk.component && mentionedComponents.size) {
    const normalizedComponent = pascalToKebab(chunk.component)
    score += mentionedComponents.has(normalizedComponent) ? 80 : -12
  }

  if (chunk.sourceType === 'doc') {
    score += 3
  }

  if (chunk.sourceType === 'demo' && hasAnyTerm(extractTerms(question), ['示例', '代码', 'demo', 'example', 'usage'])) {
    score += 10
  }

  if (chunk.sourceType === 'types' && hasAnyTerm(extractTerms(question), ['属性', '事件', '插槽', '类型', 'props', 'events', 'slots', 'api'])) {
    score += 10
  }

  return score
}

const limitSourceText = (items: RetrievedKnowledge[]) => {
  let totalLength = 0
  const limited: RetrievedKnowledge[] = []

  for (const item of items) {
    if (totalLength >= MAX_SOURCE_TEXT_LENGTH) {
      break
    }

    const remaining = MAX_SOURCE_TEXT_LENGTH - totalLength
    const text = item.text.length > remaining ? `${item.text.slice(0, remaining)}\n...` : item.text
    limited.push({ ...item, text })
    totalLength += text.length
  }

  return limited
}

export const getRelevantKnowledge = async (
  question: string,
  currentRoute?: string,
  limit = 8
): Promise<RetrievedKnowledge[]> => {
  const index = await getKnowledgeIndex()
  const terms = extractTerms(question)
  const mentionedComponents = getMentionedComponents(index.chunks, question)

  if (!terms.length) {
    return []
  }

  const scored = index.chunks
    .map((chunk) => ({
      ...chunk,
      score: scoreChunk(chunk, terms, question.toLowerCase(), currentRoute, mentionedComponents)
    }))
    .filter((chunk) => chunk.score > 0)
    .sort((left, right) => right.score - left.score)

  return limitSourceText(scored.slice(0, limit))
}
