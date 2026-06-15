# Anthropic API Integration

## Current Models (update when new versions release)

```typescript
export type AIModel =
  | 'claude-opus-4-7'           // Most capable
  | 'claude-sonnet-4-6'         // Recommended default
  | 'claude-haiku-4-5-20251001' // Fast, affordable

export const MODEL_DISPLAY_NAMES: Record<AIModel, string> = {
  'claude-opus-4-7': 'Claude Opus 4.7',
  'claude-sonnet-4-6': 'Claude Sonnet 4.6 (Recommended)',
  'claude-haiku-4-5-20251001': 'Claude Haiku 4.5 (Fast)',
}

export const DEPRECATED_MODEL_MIGRATION: Record<string, AIModel> = {
  'claude-3-5-sonnet-20241022': 'claude-sonnet-4-6',
  'claude-3-7-sonnet-20250219': 'claude-sonnet-4-6',
  'claude-sonnet-4-5-20250929': 'claude-sonnet-4-6',
  'claude-haiku-4-5-20250929': 'claude-haiku-4-5-20251001',
}
```

## Project Structure

```
src/lib/ai/
├── index.ts          # Re-exports
├── types.ts          # AIModel, AISettings, AIError types
├── client.ts         # API client with caching
└── prompts/
    └── system.ts     # System prompts

src/stores/
└── debugStore.ts     # Debug inspector state (optional)
```

## API Key Management (Tauri)

```typescript
import { Store } from '@tauri-apps/plugin-store'

export async function getApiKey(): Promise<string | null> {
  const store = await Store.load('settings.json')
  return await store.get<string>('anthropic_api_key') || null
}

export async function setApiKey(apiKey: string): Promise<void> {
  const store = await Store.load('settings.json')
  await store.set('anthropic_api_key', apiKey)
  await store.save()
  client = null // Reset to pick up new key
}
```

## Client Initialization (Tauri)

```typescript
import Anthropic from '@anthropic-ai/sdk'

// dangerouslyAllowBrowser required for Tauri WebView — key is stored locally
client = new Anthropic({ apiKey, dangerouslyAllowBrowser: true })
```

## Prompt Caching

Always cache long system prompts:

```typescript
const response = await anthropic.messages.create({
  model,
  max_tokens: maxTokens,
  system: [{
    type: 'text',
    text: SYSTEM_PROMPT,
    cache_control: { type: 'ephemeral' },
  }],
  messages: [{ role: 'user', content: userPrompt }],
})
```

## Error Handling

```typescript
export type AIErrorType =
  | 'no_api_key' | 'invalid_api_key' | 'rate_limited'
  | 'model_not_found' | 'network_error' | 'unknown'

function parseAnthropicError(error: unknown): AIError {
  if (error instanceof Anthropic.APIError) {
    if (error.status === 401) return createAIError('invalid_api_key')
    if (error.status === 429) return createAIError('rate_limited')
    if (error.status >= 500) return createAIError('network_error')
  }
  return createAIError('unknown')
}
```

## Connection Test

```typescript
export async function testConnection(): Promise<{ success: boolean; error?: string }> {
  try {
    await anthropic.messages.create({
      model: 'claude-haiku-4-5-20251001',
      max_tokens: 10,
      messages: [{ role: 'user', content: 'Hi' }],
    })
    return { success: true }
  } catch (error) {
    if (error instanceof Error) {
      if (error.message.includes('401')) return { success: false, error: 'Invalid API key.' }
      if (error.message.includes('credit balance')) return { success: false, error: 'Insufficient credits.' }
    }
    return { success: false, error: 'Connection failed.' }
  }
}
```

## Model Migration

When Anthropic releases new models:
1. Add new ID to `AIModel` type
2. Add to `MODEL_DISPLAY_NAMES`
3. Add old IDs to `DEPRECATED_MODEL_MIGRATION`
4. Update default if better option exists
5. Check output token limits → update `LIMITED_OUTPUT_MODELS`
