# Tauri Project Setup

## Core Config (tauri.conf.json)

```json
{
  "productName": "Your App Name",
  "identifier": "com.example.yourapp",
  "app": {
    "windows": [{
      "title": "Your App Name",
      "width": 1280,
      "height": 800,
      "minWidth": 900,
      "minHeight": 600,
      "resizable": true,
      "decorations": true,
      "transparent": true,
      "hiddenTitle": true,
      "titleBarStyle": "Overlay"
    }]
  },
  "bundle": {
    "icon": ["icons/icon.icns", "icons/icon.ico", "icons/icon.png"]
  }
}
```

## Capabilities (capabilities/default.json)

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "core:window:default",
    "core:window:allow-start-dragging"
  ]
}
```

**`core:window:allow-start-dragging` is REQUIRED for window dragging.**

## SQLite Setup

Personal apps use direct SQLite (no migrations). See tech-stacks for the personal app database workflow.

```rust
// src-tauri/Cargo.toml
[dependencies]
rusqlite = { version = "0.31", features = ["bundled"] }
```

```typescript
// src/lib/db.ts
import Database from '@tauri-apps/plugin-sql'

export async function getDb() {
  return await Database.load('sqlite:app.db')
}
```

## Tauri Store (Preferences)

```typescript
import { Store } from '@tauri-apps/plugin-store'

const store = await Store.load('settings.json')
await store.set('key', value)
await store.save()
```

## App Layout (with rounded corners + overlay titlebar)

```tsx
// App.tsx
<div className="flex flex-col h-screen overflow-hidden rounded-[10px] bg-folk-ink">
  <TitleBar />
  <div className="flex flex-1 overflow-hidden">
    <Sidebar />
    <main className="flex-1 flex flex-col overflow-hidden">
      <Outlet />
    </main>
  </div>
</div>
```

```css
/* index.css — required for rounded corners */
html { background: transparent; }
body { border-radius: 10px; overflow: hidden; }
#root { border-radius: 10px; overflow: hidden; }
```

## Personal App Database Workflow

```bash
# 1. Backup before any schema change
cp database.db database.db.backup-$(date +%Y%m%d-%H%M%S)

# 2. Modify directly
sqlite3 database.db "ALTER TABLE tasks ADD COLUMN priority INTEGER DEFAULT 0"

# 3. Verify
sqlite3 database.db ".schema tasks"
```

**No ORMs with migrations for personal apps. Direct SQLite only.**
