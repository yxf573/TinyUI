interface EmbeddingResponse {
  data: Array<{
    embedding: number[]
  }>
}

interface ChatCompletionResponse {
  choices: Array<{
    message: {
      content: string
    }
  }>
}

const postJson = async <T>(url: string, apiKey: string, body: unknown): Promise<T> => {
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${apiKey}`
    },
    body: JSON.stringify(body)
  })

  if (!response.ok) {
    const detail = await response.text()
    throw new Error(`Request to ${url} failed: ${response.status} ${detail}`)
  }

  return await response.json() as T
}

export class OpenAICompatibleClient {
  constructor(
    private readonly baseUrl: string,
    private readonly apiKey: string
  ) {}

  async embeddings(model: string, input: string[]) {
    const data = await postJson<EmbeddingResponse>(
      `${this.baseUrl}/embeddings`,
      this.apiKey,
      { model, input }
    )

    return data.data.map((item) => item.embedding)
  }

  async chatCompletion(model: string, messages: Array<{ role: string, content: string }>) {
    const data = await postJson<ChatCompletionResponse>(
      `${this.baseUrl}/chat/completions`,
      this.apiKey,
      {
        model,
        temperature: 0.2,
        messages
      }
    )

    return data.choices[0]?.message.content?.trim() || ''
  }
}
