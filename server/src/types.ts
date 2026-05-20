export interface ChatTurn {
  role: 'user' | 'assistant'
  content: string
}

export interface PageContext {
  route: string
  title: string
  headings: string[]
  apiText: string
  pageText: string
}

export interface ChatRequestBody {
  question: string
  history?: ChatTurn[]
  context?: PageContext
}

export interface KnowledgeChunk {
  id: string
  title: string
  route: string
  filePath: string
  sourceType: 'doc' | 'demo' | 'types'
  component?: string
  text: string
}

export interface RetrievedKnowledge extends KnowledgeChunk {
  score: number
}
