---
triggers: [favicon, web app icon, pwa icon, apple-touch-icon, home screen icon, ios icon, web icon]
description: Set up favicon, iOS home screen icon, and PWA icons for a web app from a Figma source
---

# Web App Icons

## Brand Icons Figma File (configure your own)

**File:** `Brand – App Icons & Assets`
**URL:** https://www.figma.com/design/ZsnQAWesUcpv1nWOHcPznT/Brand-%E2%80%93-App-Icons---Assets?node-id=701-966
**Page node:** `701:966` (canvas "Your Apps")

---

## Workflow

### Step 1: Export from Figma

Use Figma MCP to pull the icon at 1024×1024:

```
mcp__figma__get_screenshot(fileKey="ZsnQAWesUcpv1nWOHcPznT", nodeId="<node_id>", maxDimension=1024)
```

Then download the PNG:

```bash
curl -o "public/app-icon-1024.png" "<image_url_from_mcp>"
```

Verify it's 1024×1024 RGBA PNG:
```bash
file public/app-icon-1024.png
```

### Step 2: Generate all required sizes

Uses `sips` (macOS built-in, no dependencies) + pure Python stdlib for favicon.ico:

```bash
SRC="public/app-icon-1024.png"

# iOS Safari "Add to Home Screen"
sips -z 180 180 "$SRC" --out public/icons/apple-touch-icon.png

# PWA manifest icons
sips -z 192 192 "$SRC" --out public/icons/icon-192.png
sips -z 512 512 "$SRC" --out public/icons/icon-512.png

# Favicon PNG (browsers that prefer PNG)
sips -z 32 32 "$SRC" --out public/favicon-32.png

# Favicon ICO (16+32 packed, no PIL needed)
sips -z 32 32 "$SRC" --out /tmp/fav-32.png
sips -z 16 16 "$SRC" --out /tmp/fav-16.png

python3 - <<'EOF'
import struct, io

def build_ico(png_paths, out_path):
    images = []
    for p in png_paths:
        with open(p, "rb") as f:
            data = f.read()
        w = struct.unpack(">I", data[16:20])[0]
        h = struct.unpack(">I", data[20:24])[0]
        images.append((w, h, data))
    n = len(images)
    header = struct.pack("<HHH", 0, 1, n)
    offset = 6 + n * 16
    entries = b""
    for w, h, data in images:
        entries += struct.pack("<BBBBHHII",
            w if w < 256 else 0, h if h < 256 else 0,
            0, 0, 1, 32, len(data), offset)
        offset += len(data)
    with open(out_path, "wb") as f:
        f.write(header + entries)
        for _, _, data in images:
            f.write(data)

build_ico(["/tmp/fav-16.png", "/tmp/fav-32.png"], "public/favicon.ico")
print("done")
EOF
```

### Step 3: Wire up index.html

Replace or update the `<head>` icon tags:

```html
<!-- Favicon -->
<link rel="icon" type="image/x-icon" href="/favicon.ico" />
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png" />

<!-- iOS Safari home screen -->
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
<meta name="apple-mobile-web-app-title" content="<App Name>" />

<!-- PWA / theme -->
<link rel="manifest" href="/manifest.json" />
<meta name="theme-color" content="#0e0d0c" />
```

### Step 4: Update manifest.json

```json
{
  "name": "<App Name>",
  "short_name": "<Short>",
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ],
  "theme_color": "#0e0d0c",
  "background_color": "#0e0d0c",
  "display": "standalone"
}
```

---

## File Checklist

| File | Size | Purpose |
|------|------|---------|
| `public/favicon.ico` | 16+32px packed | Browser tab (legacy) |
| `public/favicon-32.png` | 32×32 | Browser tab (modern) |
| `public/icons/apple-touch-icon.png` | 180×180 | iOS "Add to Home Screen" |
| `public/icons/icon-192.png` | 192×192 | PWA / Android |
| `public/icons/icon-512.png` | 512×512 | PWA splash / install |
| `public/app-icon-1024.png` | 1024×1024 | Source (keep for regeneration) |

---

## Notes

- `PIL`/`Pillow` is not available by default on this machine — use the pure stdlib ICO builder above
- `sips` is macOS-only; it's always available without installing anything
- iOS ignores any alpha/rounding on `apple-touch-icon` — iOS rounds it automatically
- After deploy, hard-reload in Safari to bust the cached icon
- For Tauri desktop icons, see `tauri-icons.md`
