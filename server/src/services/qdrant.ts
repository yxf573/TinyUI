import { config } from '../config.js'
import type { KnowledgeChunk, SearchResult } from '../types.js'

interface QdrantSearchPoint {
  score: number
  payload?: KnowledgeChunk
}

const qdrantHeaders = () => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json'
  }

  if (config.qdrantApiKey) {
    headers['api-key'] = config.qdrantApiKey
  }

  return headers
}

const qdrantFetch = async <T>(endpoint: string, init?: RequestInit) => {
  const response = await fetch(`${config.qdrantUrl}${endpoint}`, {
    ...init,
    headers: {
      ...qdrantHeaders(),
      ...(init?.headers as Record<string, string> | undefined)
    }
  })

  if (!response.ok) {
    const detail = await response.text()
    throw new Error(`Qdrant request failed: ${response.status} ${detail}`)
  }

  return await response.json() as T
}

export const ensureCollection = async (vectorSize: number) => {
  const endpoint = `/collections/${config.qdrantCollection}`
  const response = await fetch(`${config.qdrantUrl}${endpoint}`, {
    headers: qdrantHeaders()
  })

  if (response.ok) {
    return
  }

  if (response.status !== 404) {
    const detail = await response.text()
    throw new Error(`Unable to inspect collection: ${response.status} ${detail}`)
  }

  await qdrantFetch(endpoint, {
    method: 'PUT',
    body: JSON.stringify({
      vectors: {
        size: vectorSize,
        distance: 'Cosine'
      }
    })
  })
}

export const upsertChunks = async (chunks: KnowledgeChunk[], vectors: number[][]) => {
  const points = chunks.map((chunk, index) => ({
    id: index + 1,
    vector: vectors[index],
    payload: chunk
  }))

  await qdrantFetch(`/collections/${config.qdrantCollection}/points?wait=true`, {
    method: 'PUT',
    body: JSON.stringify({ points })
  })
}

export const searchChunks = async (
  queryVector: number[],
  options?: {
    limit?: number
    component?: string
    route?: string
  }
) => {
  const must: Array<Record<string, unknown>> = []

  if (options?.component) {
    must.push({
      key: 'component',
      match: {
        value: options.component
      }
    })
  }

  const should = options?.route
    ? [{
        key: 'route',
        match: {
          value: options.route
        }
      }]
    : []

  const payload = {
    vector: queryVector,
    limit: options?.limit ?? 6,
    with_payload: true,
    filter: must.length > 0 || should.length > 0
      ? {
          ...(must.length > 0 ? { must } : {}),
          ...(should.length > 0 ? { should } : {})
        }
      : undefined
  }

  const response = await qdrantFetch<{ result: QdrantSearchPoint[] }>(
    `/collections/${config.qdrantCollection}/points/search`,
    {
      method: 'POST',
      body: JSON.stringify(payload)
    }
  )

  return response.result
    .map((item) => item.payload
      ? {
          ...item.payload,
          score: item.score
        } satisfies SearchResult
      : null
    )
    .filter((item): item is SearchResult => item !== null)
}
