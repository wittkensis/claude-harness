---
triggers: [ios web app, mobile web, pwa, safari url bar, safe area, home screen app, overscroll, mobile layout, spa shell, viewport, add to home screen, ios safari, mobile-first]
description: Patterns for building iOS-first SPAs that feel native — SPA shell, safe area, URL bar, and mobile panel architecture
---

# iOS Web App Patterns

These patterns apply to any Vite/React SPA deployed as a web app and accessed via iOS Safari or added to the home screen.

---

## SPA Shell — Root CSS

Use `position: fixed; inset: 0` on `#root`, NOT `height: 100dvh`. Fixed is more reliable on iOS — it prevents the Safari URL bar from affecting layout measurements.

```css
html {
  overscroll-behavior: none; /* prevents bounce scroll → URL bar trigger */
  height: 100%;
}

body {
  overflow: hidden;
  overscroll-behavior: none;
  touch-action: manipulation;         /* prevents double-tap zoom */
  -webkit-tap-highlight-color: transparent;
}

#root {
  position: fixed;
  inset: 0;
  overflow: hidden;
}
```

The root App div: `<div className="flex flex-col h-full min-h-0 bg-[ink]">` — **no `overflow-hidden`**. `#root` already clips; adding a second `overflow: hidden` on the App div causes subpixel rounding to clip `env(safe-area-inset-bottom)` padding on the bottom nav, creating a visible seam under the home indicator. See §"Footer doesn't reach bottom" below.

---

## Safe Area — Pick ONE Layer

**The rule:** apply `env(safe-area-inset-top/bottom)` at exactly ONE level. Double-application creates a large gap.

**Use Pattern B — each component handles its own safe area. Pattern A is broken.**

Pattern A (root `main` handles safe area) seems clean but causes a visible background color gap: the `paddingTop` on `main` creates space filled by the root element's background color, not the view's header background. The header appears to "float" below the status bar with the wrong color behind it.

Pattern B is correct:

```tsx
// App.tsx — main has NO paddingTop
<main className="flex-1 flex flex-col overflow-hidden" style={{ paddingTop: 0 }}>
```

Every view's topmost visible element carries its own safe area:
```tsx
// The background of this element extends to the top of the screen.
// Only the text/icon content is offset below the notch.
<div style={{ paddingTop: 'calc(env(safe-area-inset-top) + 12px)' }}>
```

This makes the header color "bleed" through the safe area zone — matching native iOS behavior.

**Fixed/overlay elements always handle their own safe area** since they're outside the main flow:
```tsx
<div className="fixed inset-0 flex flex-col">
  <header style={{ paddingTop: 'calc(env(safe-area-inset-top) + 12px)' }}>
```

**Gotcha:** Every "first visible element" of a view needs the calc. If a conditional header might be hidden (e.g. an alignments shortcut only shown when data exists), the list below it becomes the first element and also needs safe area. Track which element is topmost per state.

---

## Bottom Safe Area

Bottom nav must account for the home indicator:
```css
.pb-nav {
  padding-bottom: calc(64px + env(safe-area-inset-bottom));
}
```

Nav bar itself:
```tsx
<nav style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}>
  <div className="flex items-stretch h-16">
```

---

## Safari URL Bar Prevention

`overscroll-behavior: none` is the main fix — prevents the bounce scroll gesture that causes Safari to show the URL bar. Combined with `position: fixed` on `#root`, navigation between routes (react-router `navigate()`) won't trigger the URL bar.

Note: in Safari browser (not home screen), the URL bar can still appear on first load. It permanently disappears once the user adds the app to the Home Screen.

Required meta tags (in `<head>`):
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
<link rel="manifest" href="/manifest.json" />
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
<meta name="apple-mobile-web-app-title" content="<App Name>" />
<meta name="theme-color" content="#0e0d0c" />
```

---

## Detail Panel Architecture on Mobile

Desktop sidebar panels (`position: fixed; right: 0; width: 480px`) appear correctly on desktop but clip on mobile phones (e.g. a 375px screen only shows the rightmost 375px of a 480px panel).

**Two fixes to apply together:**

**1. Make the panel full-width on mobile:**
```tsx
// Before (desktop only)
'fixed top-0 right-0 h-full w-[480px]'

// After (responsive)
'fixed top-0 right-0 h-full w-full sm:w-[480px] sm:border-l'
```

**2. Suppress the overlay on routes that have their own inline detail:**

On a route like `/sessions`, if both an inline master-detail AND an overlay panel respond to the same store state, they double-render. Suppress the overlay on that route:

```tsx
// App.tsx
const { pathname } = useLocation()
{isSessionDetailPanelOpen && pathname !== '/sessions' && <SessionDetailPanel />}
```

The route's own inline component (e.g. `SessionsMasterDetail`) reads `selectedSessionId` from the store and handles the detail natively.

**3. Clean up panel state on route changes:**

Use a `ViewSync` component or route-change effect to close stale panels when navigating away:

```tsx
function ViewSync() {
  const { pathname } = useLocation()
  const prevPathRef = useRef(pathname)

  useEffect(() => {
    const prev = prevPathRef.current
    prevPathRef.current = pathname
    // Close session panel when leaving /sessions so it doesn't reappear on other routes
    if (prev === '/sessions' && pathname !== '/sessions') {
      useAppStore.getState().closeSessionDetailPanel()
    }
  }, [pathname])

  return null
}
```

---

## Scrollable Areas

Use `-webkit-overflow-scrolling` is deprecated; use `overflow-y: auto` + `overscroll-behavior: contain` on individual scroll containers:

```tsx
<div className="flex-1 overflow-y-auto scrollbar-hidden">
```

Add `overscroll-behavior: contain` (CSS) or `overscroll-behavior-y: contain` on inner scroll areas to prevent scroll chaining to the document body.

---

## Nested Flexbox Correctness

Nested flex columns are the single most common source of layout bugs in KW apps. One rule governs everything: **height flows DOWN from a bounded root. It never flows up from content.**

### The correct shell

```
#root          position: fixed; inset: 0; overflow: hidden;   ← the ONE size boundary
  App div      display: flex; flex-direction: column;
               height: 100%; min-h-0;                         ← NO overflow: hidden
    header     flex-shrink: 0;                                ← fixed height, never compresses
    main       flex: 1; min-height: 0; overflow: hidden;      ← takes remaining space
      scroller height: 100%; overflow-y: auto;                ← scrolls within main
    nav        flex-shrink: 0;                                ← fixed height
               padding-bottom: env(safe-area-inset-bottom);
```

### The three rules

**1. Exactly one `overflow: hidden` between root and any scroll container.**  
`#root` is that boundary. Every intermediate container (App div, layout shells) must NOT add a second one. Extra `overflow: hidden` copies create subpixel clip boundaries that eat 1–2px from the bottom of the nav's safe-area padding — the footer-doesn't-reach-bottom bug.

**2. `min-h-0` on every flex child that must shrink below its content.**  
Flex children default to `min-height: auto`, which prevents them from shrinking below their content height. This means a `flex: 1` child containing a 2000px list will expand past the parent bounds instead of scrolling. Always add `min-h-0` (Tailwind) / `min-height: 0` (CSS) to:
- The `<main>` area
- Any flex child that wraps a scrollable element
- Any flex child you expect to stay within the parent bounds

**3. `h-full` only works when every ancestor has a bounded height.**  
Trace the height chain from `#root` to the element using `h-full`. If any link is unbounded, `h-full` resolves to 0 or the content height, breaking the layout. Never use `h-full` on an element whose parent doesn't explicitly size itself.

```tsx
// Correct — main can shrink; scroll container fills it reliably
<main className="flex-1 min-h-0 overflow-hidden">
  <div className="h-full overflow-y-auto">content</div>
</main>

// Wrong — main can grow past parent bounds; h-full on scroller is undefined
<main className="flex-1 overflow-hidden">
  <div className="h-full overflow-y-auto">content</div>
</main>
```

### Validation checklist for any flex column layout

- [ ] Trace height chain: `#root` → every ancestor → every `h-full` element — all links bounded
- [ ] Exactly ONE `overflow: hidden` between `#root` and any scroll container
- [ ] Every flex child that scrolls has `min-h-0`
- [ ] `header` and `nav` have `flex-shrink: 0`
- [ ] Test with both very short AND very long content
- [ ] On device: bottom nav reaches the screen bottom with no seam

---

## Footer Doesn't Reach Screen Bottom

**Symptom.** The bottom nav stops 1–34px short of the physical screen bottom. A seam of the body background shows under the home indicator.

**Canonical fix: `position: fixed; bottom: 0` on the nav.** This is the only reliable approach — a fixed element's `bottom: 0` anchors to the physical viewport edge, not a flex container boundary. The `padding-bottom: env(safe-area-inset-bottom)` then fills the home indicator area without any container that could clip it.

```tsx
<nav
  className="fixed bottom-0 left-0 right-0 z-30 bg-[color] border-t ..."
  style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}
>
  <div className="flex items-stretch h-16">...</div>
</nav>
```

With a fixed nav, all page content areas need `pb-nav` (`padding-bottom: calc(64px + env(safe-area-inset-bottom))`) on their scroll containers so content doesn't disappear behind the nav. Any `absolute bottom-0` buttons in a view need bottom offset `calc(env(safe-area-inset-bottom) + 64px + gap)`.

**Why the flex item approach fails.** A flex column's computed height resolves to the *safe area boundary*, not the physical screen bottom — even when `#root` is `position: fixed; inset: 0` and `viewport-fit=cover` is set. The nav's `padding-bottom: env(safe-area-inset-bottom)` extends the nav *below* the flex container boundary, where `#root`'s `overflow: hidden` clips it. This creates a gap exactly `env(safe-area-inset-bottom)` (~34px) tall. This cannot be fixed by removing `overflow: hidden` from intermediate containers — the clipping happens at `#root`, which must have overflow containment.

**Confirmed in a production SPA (2026-05).** The flex item approach failed even after removing double overflow. Switching to `position: fixed` on the nav resolved it completely.

**Other causes worth checking first:**

| Cause | Diagnostic | Fix |
|-------|-----------|-----|
| Missing `viewport-fit=cover` | `env(safe-area-inset-bottom)` is 0 on device | Add to `<meta name="viewport">` |
| Nav compressed by parent flex | `flex-shrink` is not 0 | Add `flex-shrink: 0` |
| Translucent nav + mismatched body color | 1px seam, not full safe-area gap | Use opaque nav or match body bg |

---

## Cache Headers + Service Worker (PWA Update Flow)

Without correct cache headers and a service worker, iOS PWAs show stale content after deploys — the user has to manually kill and reopen the app. This was confirmed as the mechanism behind the persistent nav-gap bug appearing in multiple sessions even after fixes were deployed.

### Express cache headers

```typescript
// backend/src/index.ts
app.use(express.static(DIST, {
  setHeaders(res, filePath) {
    if (filePath.includes('/assets/')) {
      // Hashed filenames — safe to cache forever
      res.setHeader('Cache-Control', 'public, max-age=31536000, immutable')
    } else {
      // index.html, manifest, icons, sw.js — must revalidate
      res.setHeader('Cache-Control', 'no-cache')
    }
  },
}))

app.get('*', (_req, res) => {
  res.setHeader('Cache-Control', 'no-cache')  // fallback also no-cache
  res.sendFile(path.join(DIST, 'index.html'))
})
```

### Service worker (public/sw.js)

Write a manual SW — do NOT use `vite-plugin-pwa`. The plugin's internal Vite build conflicts with ESM `postcss.config.js` in `type: module` packages.

The SW must do:
1. `self.skipWaiting()` in `install` — activate immediately without waiting for tabs to close
2. `clients.claim()` in `activate` — claim all open tabs so they get the new version
3. Purge old caches in `activate`
4. Network-first for navigation (HTML), cache-first for hashed assets
5. Never cache `/api`, `/voice`, `/health` endpoints

Register in `main.tsx` (web platform only):
```tsx
if ('serviceWorker' in navigator && import.meta.env.VITE_PLATFORM === 'web') {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {})
  })
}
```

The SW lives in `public/sw.js` so Vite copies it as-is into `dist/sw.js`.

### Verifying the full chain

```bash
# SW served with correct content-type and no-cache
curl -sI https://{app}.{your-domain}/sw.js | grep "content-type\|cache-control"
# → content-type: application/javascript
# → cache-control: no-cache

# Hashed asset served immutable
curl -sI https://{app}.{your-domain}/assets/index-HASH.js | grep "cache-control"
# → cache-control: public, max-age=31536000, immutable
```

---

## Reference implementation

This app (`app.{your-domain}`) is a canonical implementation of these patterns. See `app/src/index.css`, `app/src/App.tsx`, and `app/src/components/sessions/SessionsMasterDetail.tsx` for working examples.
