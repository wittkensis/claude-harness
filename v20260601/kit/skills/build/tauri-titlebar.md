# Tauri Custom Titlebar

## The Definitive Pattern

macOS overlay titlebar with dragging for Tauri 2.x.

### 1. capabilities/default.json

```json
{
  "permissions": [
    "core:default",
    "core:window:default",
    "core:window:allow-start-dragging"
  ]
}
```

**`core:window:allow-start-dragging` REQUIRED. Without it, dragging will not work.**

### 2. tauri.conf.json

```json
{
  "app": {
    "windows": [{
      "decorations": true,
      "transparent": true,
      "hiddenTitle": true,
      "titleBarStyle": "Overlay"
    }]
  }
}
```

- `decorations: true` — native traffic lights
- `transparent: true` — transparent window
- `hiddenTitle: true` — hides default title text
- `titleBarStyle: "Overlay"` — titlebar overlays content (CRITICAL)

### 3. TitleBar.tsx

```tsx
import { getCurrentWindow } from '@tauri-apps/api/window';

export function TitleBar() {
  return (
    <div
      data-tauri-drag-region
      className="h-8 flex items-center justify-center bg-folk-ink border-b border-folk-stone/10 select-none"
      onMouseDown={(e) => {
        e.preventDefault();
        getCurrentWindow().startDragging();
      }}
    >
      <span className="font-serif text-xs text-folk-cream pointer-events-none">
        App Name
      </span>
    </div>
  );
}
```

**Key elements:**
- `data-tauri-drag-region` — marks region as draggable
- `onMouseDown` calling `getCurrentWindow().startDragging()` — enables dragging (REQUIRED)
- `e.preventDefault()` — prevents text selection
- `pointer-events-none` on children — prevents interference
- `select-none` — prevents text selection while dragging
- `h-8` — standard height

### 4. Layout

```tsx
<div className="flex flex-col h-screen overflow-hidden rounded-[10px] bg-folk-ink">
  <TitleBar />
  <div className="flex flex-1 overflow-hidden">
    <Sidebar />
    <main className="flex-1 overflow-hidden"><Outlet /></main>
  </div>
</div>
```

## What NOT to Do

- Don't forget `core:window:allow-start-dragging` in capabilities
- Don't use `async/await` in the mouseDown handler
- Don't add `-webkit-app-region: drag` (that's Electron)
- Don't use `titleBarStyle: "transparent"` (invalid)
- Don't remove `decorations: true` (needed for traffic lights)
- Don't add padding to compensate — Overlay mode handles it
