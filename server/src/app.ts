import express from 'express'
import { ensureConfig, config } from './config.js'
import { getRelevantKnowledge } from './services/siteKnowledge.js'
import type { ChatRequestBody, RetrievedKnowledge } from './types.js'

interface QwenStreamChunk {
  choices?: Array<{
    delta?: {
      content?: string
    }
    message?: {
      content?: string
    }
  }>
}

const app = express()

app.use(express.json({ limit: '1mb' }))
app.use((_, response, next) => {
  response.setHeader('Access-Control-Allow-Origin', '*')
  response.setHeader('Access-Control-Allow-Headers', 'Content-Type')
  response.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
  next()
})

app.options('*', (_, response) => {
  response.sendStatus(204)
})

const trimContext = (value = '', maxLength = 6000) => {
  if (value.length <= maxLength) {
    return value
  }

  return `${value.slice(0, maxLength)}\n...`
}

const formatRetrievedKnowledge = (items: RetrievedKnowledge[]) => {
  if (!items.length) {
    return '(No relevant site-wide documentation was retrieved.)'
  }

  return items
    .map(
      (item, index) => [
        `[Source ${index + 1}]`,
        `title: ${item.title}`,
        `route: ${item.route}`,
        `file: ${item.filePath}`,
        `type: ${item.sourceType}`,
        item.component ? `component: ${item.component}` : '',
        'content:',
        trimContext(item.text, 1800)
      ]
        .filter(Boolean)
        .join('\n')
    )
    .join('\n\n')
}

const buildSystemPrompt = (body: ChatRequestBody, retrievedKnowledge: RetrievedKnowledge[]) => {
  const context = body.context
  const headings = context?.headings?.length ? context.headings.join(' / ') : 'Unknown'
  const apiText = trimContext(context?.apiText ?? '', 3500)
  const pageText = trimContext(context?.pageText ?? '', 3000)

  return [
    'You are the AI documentation assistant for the TinyElement Vue component library.',
    'Answer in Chinese by default.',
    'You can answer questions about the entire VitePress documentation site, no matter which page the user is currently viewing.',
    'Use the retrieved site-wide documentation as the primary source of truth.',
    'The current-page context is only secondary context for location and wording.',
    'Do not invent props, events, slots, component names, or APIs that are not present in the retrieved documentation.',
    'If the retrieved documentation is insufficient, say so clearly and suggest which docs/source file should be checked.',
    'When generating Vue examples, use Vue 3 Composition API and follow the component usage style implied by the docs.',
    'When helpful, mention the matched document route or component name.',
    'Return Markdown. Use fenced code blocks for code.',
    '',
    'Retrieved site-wide documentation:',
    formatRetrievedKnowledge(retrievedKnowledge),
    '',
    'Current page metadata:',
    `- route: ${context?.route ?? 'unknown'}`,
    `- title: ${context?.title ?? 'unknown'}`,
    `- headings: ${headings}`,
    '',
    'Current page API/spec context:',
    apiText || '(No explicit API table or spec text found on the current page.)',
    '',
    'Current page visible text:',
    pageText || '(No page text captured.)'
  ].join('\n')
}

const sendSse = (response: express.Response, event: string, data: unknown) => {
  response.write(`event: ${event}\n`)
  response.write(`data: ${JSON.stringify(data)}\n\n`)
}

const streamQwen = async (body: ChatRequestBody, response: express.Response) => {
  const retrievedKnowledge = await getRelevantKnowledge(body.question, body.context?.route)

  sendSse(response, 'sources', {
    sources: retrievedKnowledge.map(({ title, route, filePath, sourceType, score }) => ({
      title,
      route,
      filePath,
      sourceType,
      score
    }))
  })

  const upstreamResponse = await fetch(`${config.llmBaseUrl}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${config.llmApiKey}`
    },
    body: JSON.stringify({
      model: config.llmModel,
      stream: true,
      temperature: 0.2,
      messages: [
        {
          role: 'system',
          content: buildSystemPrompt(body, retrievedKnowledge)
        },
        ...(body.history ?? []).slice(-6),
        {
          role: 'user',
          content: body.question
        }
      ]
    })
  })

  if (!upstreamResponse.ok || !upstreamResponse.body) {
    const detail = await upstreamResponse.text()
    throw new Error(`Qwen request failed: ${upstreamResponse.status} ${detail}`)
  }

  const reader = upstreamResponse.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) {
      break
    }

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''

    for (const line of lines) {
      const trimmed = line.trim()
      if (!trimmed || !trimmed.startsWith('data:')) {
        continue
      }

      const data = trimmed.slice(5).trim()
      if (data === '[DONE]') {
        sendSse(response, 'done', {})
        return
      }

      try {
        const parsed = JSON.parse(data) as QwenStreamChunk
        const content = parsed.choices?.[0]?.delta?.content ?? parsed.choices?.[0]?.message?.content ?? ''
        if (content) {
          sendSse(response, 'delta', { content })
        }
      } catch {
        // Ignore malformed keep-alive chunks from the upstream stream.
      }
    }
  }

  sendSse(response, 'done', {})
}

app.get('/api/chat/health', (_, response) => {
  response.json({
    ok: true,
    model: config.llmModel,
    rag: 'site-wide-file-retrieval'
  })
})

app.post('/api/chat', async (request, response) => {
  const body = request.body as ChatRequestBody
  const question = body.question?.trim()

  if (!question) {
    response.status(400).json({ message: 'question is required' })
    return
  }

  response.setHeader('Content-Type', 'text/event-stream; charset=utf-8')
  response.setHeader('Cache-Control', 'no-cache, no-transform')
  response.setHeader('Connection', 'keep-alive')
  response.flushHeaders?.()

  try {
    await streamQwen({ ...body, question }, response)
  } catch (error) {
    sendSse(response, 'error', {
      message: error instanceof Error ? error.message : 'Unknown server error'
    })
  } finally {
    response.end()
  }
})

ensureConfig()

app.listen(config.port, () => {
  console.log(`AI chat server listening on http://127.0.0.1:${config.port}`)
})
