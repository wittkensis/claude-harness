# Desktop Stack

**Default: Tauri.** See the `tauri` skill for full implementation details.

## Tauri vs Electron

| Criterion | Tauri | Electron |
|-----------|-------|----------|
| Binary size | ~3-10 MB | 100+ MB |
| Memory usage | Lower (Rust backend) | Higher (Node.js) |
| Startup speed | Faster | Slower |
| Node packages | Not available | Full Node.js ecosystem |
| Security | Better | Standard web model |

**Use Tauri when:** standard web tech sufficient, smaller binary preferred, security matters
**Use Electron when:** need specific Node packages (puppeteer, etc.), building IDE-like tools

## Tauri Stack

```
Tauri 2.x + React 19 + TypeScript 5.8 + Tailwind 3.4
+ SQLite (complex data) + Tauri Store (preferences) + Zustand (state)
```

Full setup, titlebar, and icons → see `tauri` skill.
