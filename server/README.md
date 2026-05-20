# AI Chat Server

This server is a lightweight API-key-safe proxy for the VitePress AI assistant.
It uses the current documentation page as context and streams Qwen responses back to the browser with SSE.

## Environment

Copy `server/.env.example` to `server/.env` and fill in:

- `LLM_API_KEY`
- `LLM_MODEL` if you want a model other than `qwen-plus`

## Commands

- `npm run server:build`
- `npm run server:start`
- `npm run docs:dev`

## Flow

1. VitePress collects the current page title, headings, tables, code blocks, and visible text.
2. The browser posts the question and page context to `/api/chat`.
3. The Node server adds the private Qwen API key and streams the model response to the browser.
4. The browser renders the streamed Markdown with code highlighting.
