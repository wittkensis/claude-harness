---
triggers: [app icon, tauri icon, update icon, figma icon, app icons]
description: Update Tauri app icons from Figma export or source image
---

# Tauri App Icons

## Overview

Generate all required Tauri app icons from a Figma export or source image. Handles macOS, Windows, iOS, and Android icon requirements.

---

## Available Tools (macOS)

| Tool | Command | Purpose |
|------|---------|---------|
| **sips** | `/usr/bin/sips` | PNG resizing (macOS native) |
| **iconutil** | `/usr/bin/iconutil` | Generate .icns for macOS |
| **ImageMagick** | `/opt/homebrew/bin/magick` | Generate .ico, advanced processing |
| **rsvg-convert** | `/opt/homebrew/bin/rsvg-convert` | SVG to PNG conversion |

---

## Workflow

### Step 1: Get Source Image from Figma

Use Figma MCP to extract the app icon:

```
> Use Figma MCP: get_metadata for [figma URL]
```

Identify the icon node (look for "App Icon", "Icon", or similar naming).

```
> Use Figma MCP: get_screenshot for node [icon_node_id] with scale 4
```

This exports the icon at high resolution. Save to a temp location.

**Requirements for source image:**
- Minimum 1024x1024 pixels (ideally export at 1024px or larger)
- Square aspect ratio
- PNG format with transparency support
- If SVG available, use `rsvg-convert` for best quality

### Step 2: Generate All Icon Sizes

The Tauri icons directory requires these files:

#### Desktop Icons (macOS/Windows/Linux)

| File | Size | Platform |
|------|------|----------|
| `icon.png` | 512x512 | Universal source |
| `icon.icns` | Multi-size | macOS app bundle |
| `icon.ico` | Multi-size | Windows |
| `32x32.png` | 32x32 | Linux/general |
| `64x64.png` | 64x64 | Linux/general |
| `128x128.png` | 128x128 | Linux/general |
| `128x128@2x.png` | 256x256 | Linux HiDPI |

#### Windows Store Icons

| File | Size |
|------|------|
| `Square30x30Logo.png` | 30x30 |
| `Square44x44Logo.png` | 44x44 |
| `Square71x71Logo.png` | 71x71 |
| `Square89x89Logo.png` | 89x89 |
| `Square107x107Logo.png` | 107x107 |
| `Square142x142Logo.png` | 142x142 |
| `Square150x150Logo.png` | 150x150 |
| `Square284x284Logo.png` | 284x284 |
| `Square310x310Logo.png` | 310x310 |
| `StoreLogo.png` | 50x50 |

#### iOS Icons (`ios/` subdirectory)

| File | Actual Size |
|------|-------------|
| `AppIcon-20x20@1x.png` | 20x20 |
| `AppIcon-20x20@2x.png` | 40x40 |
| `AppIcon-20x20@2x-1.png` | 40x40 |
| `AppIcon-20x20@3x.png` | 60x60 |
| `AppIcon-29x29@1x.png` | 29x29 |
| `AppIcon-29x29@2x.png` | 58x58 |
| `AppIcon-29x29@2x-1.png` | 58x58 |
| `AppIcon-29x29@3x.png` | 87x87 |
| `AppIcon-40x40@1x.png` | 40x40 |
| `AppIcon-40x40@2x.png` | 80x80 |
| `AppIcon-40x40@2x-1.png` | 80x80 |
| `AppIcon-40x40@3x.png` | 120x120 |
| `AppIcon-60x60@2x.png` | 120x120 |
| `AppIcon-60x60@3x.png` | 180x180 |
| `AppIcon-76x76@1x.png` | 76x76 |
| `AppIcon-76x76@2x.png` | 152x152 |
| `AppIcon-83.5x83.5@2x.png` | 167x167 |
| `AppIcon-512@2x.png` | 1024x1024 |

#### Android Icons (`android/` subdirectory)

| Directory | Size | Files |
|-----------|------|-------|
| `mipmap-mdpi/` | 48x48 | `ic_launcher.png`, `ic_launcher_foreground.png`, `ic_launcher_round.png` |
| `mipmap-hdpi/` | 72x72 | Same files |
| `mipmap-xhdpi/` | 96x96 | Same files |
| `mipmap-xxhdpi/` | 144x144 | Same files |
| `mipmap-xxxhdpi/` | 192x192 | Same files |

---

## Generation Commands

### Generate PNGs with sips (fastest)

```bash
# From 1024x1024 source to various sizes
SOURCE="source_icon.png"
ICONS_DIR="app/src-tauri/icons"

# Desktop icons
sips -z 512 512 "$SOURCE" --out "$ICONS_DIR/icon.png"
sips -z 256 256 "$SOURCE" --out "$ICONS_DIR/128x128@2x.png"
sips -z 128 128 "$SOURCE" --out "$ICONS_DIR/128x128.png"
sips -z 64 64 "$SOURCE" --out "$ICONS_DIR/64x64.png"
sips -z 32 32 "$SOURCE" --out "$ICONS_DIR/32x32.png"

# Windows Store icons
sips -z 310 310 "$SOURCE" --out "$ICONS_DIR/Square310x310Logo.png"
sips -z 284 284 "$SOURCE" --out "$ICONS_DIR/Square284x284Logo.png"
sips -z 150 150 "$SOURCE" --out "$ICONS_DIR/Square150x150Logo.png"
sips -z 142 142 "$SOURCE" --out "$ICONS_DIR/Square142x142Logo.png"
sips -z 107 107 "$SOURCE" --out "$ICONS_DIR/Square107x107Logo.png"
sips -z 89 89 "$SOURCE" --out "$ICONS_DIR/Square89x89Logo.png"
sips -z 71 71 "$SOURCE" --out "$ICONS_DIR/Square71x71Logo.png"
sips -z 44 44 "$SOURCE" --out "$ICONS_DIR/Square44x44Logo.png"
sips -z 30 30 "$SOURCE" --out "$ICONS_DIR/Square30x30Logo.png"
sips -z 50 50 "$SOURCE" --out "$ICONS_DIR/StoreLogo.png"
```

### Generate .icns with iconutil (macOS)

```bash
# Create iconset directory
ICONSET="AppIcon.iconset"
mkdir -p "$ICONSET"

# Generate required sizes
sips -z 16 16 "$SOURCE" --out "$ICONSET/icon_16x16.png"
sips -z 32 32 "$SOURCE" --out "$ICONSET/icon_16x16@2x.png"
sips -z 32 32 "$SOURCE" --out "$ICONSET/icon_32x32.png"
sips -z 64 64 "$SOURCE" --out "$ICONSET/icon_32x32@2x.png"
sips -z 128 128 "$SOURCE" --out "$ICONSET/icon_128x128.png"
sips -z 256 256 "$SOURCE" --out "$ICONSET/icon_128x128@2x.png"
sips -z 256 256 "$SOURCE" --out "$ICONSET/icon_256x256.png"
sips -z 512 512 "$SOURCE" --out "$ICONSET/icon_256x256@2x.png"
sips -z 512 512 "$SOURCE" --out "$ICONSET/icon_512x512.png"
sips -z 1024 1024 "$SOURCE" --out "$ICONSET/icon_512x512@2x.png"

# Convert to .icns
iconutil -c icns "$ICONSET" -o "$ICONS_DIR/icon.icns"

# Cleanup
rm -rf "$ICONSET"
```

### Generate .ico with ImageMagick

```bash
# Windows ICO with multiple sizes embedded
magick "$SOURCE" \
  -define icon:auto-resize=256,128,96,64,48,32,16 \
  "$ICONS_DIR/icon.ico"
```

### Generate iOS Icons

```bash
IOS_DIR="$ICONS_DIR/ios"
mkdir -p "$IOS_DIR"

# iOS icon sizes (actual pixels)
sips -z 20 20 "$SOURCE" --out "$IOS_DIR/AppIcon-20x20@1x.png"
sips -z 40 40 "$SOURCE" --out "$IOS_DIR/AppIcon-20x20@2x.png"
cp "$IOS_DIR/AppIcon-20x20@2x.png" "$IOS_DIR/AppIcon-20x20@2x-1.png"
sips -z 60 60 "$SOURCE" --out "$IOS_DIR/AppIcon-20x20@3x.png"

sips -z 29 29 "$SOURCE" --out "$IOS_DIR/AppIcon-29x29@1x.png"
sips -z 58 58 "$SOURCE" --out "$IOS_DIR/AppIcon-29x29@2x.png"
cp "$IOS_DIR/AppIcon-29x29@2x.png" "$IOS_DIR/AppIcon-29x29@2x-1.png"
sips -z 87 87 "$SOURCE" --out "$IOS_DIR/AppIcon-29x29@3x.png"

sips -z 40 40 "$SOURCE" --out "$IOS_DIR/AppIcon-40x40@1x.png"
sips -z 80 80 "$SOURCE" --out "$IOS_DIR/AppIcon-40x40@2x.png"
cp "$IOS_DIR/AppIcon-40x40@2x.png" "$IOS_DIR/AppIcon-40x40@2x-1.png"
sips -z 120 120 "$SOURCE" --out "$IOS_DIR/AppIcon-40x40@3x.png"

sips -z 120 120 "$SOURCE" --out "$IOS_DIR/AppIcon-60x60@2x.png"
sips -z 180 180 "$SOURCE" --out "$IOS_DIR/AppIcon-60x60@3x.png"

sips -z 76 76 "$SOURCE" --out "$IOS_DIR/AppIcon-76x76@1x.png"
sips -z 152 152 "$SOURCE" --out "$IOS_DIR/AppIcon-76x76@2x.png"

sips -z 167 167 "$SOURCE" --out "$IOS_DIR/AppIcon-83.5x83.5@2x.png"

sips -z 1024 1024 "$SOURCE" --out "$IOS_DIR/AppIcon-512@2x.png"
```

### Generate Android Icons

```bash
ANDROID_DIR="$ICONS_DIR/android"

# Standard launcher icons
for density in mdpi:48 hdpi:72 xhdpi:96 xxhdpi:144 xxxhdpi:192; do
  name="${density%%:*}"
  size="${density##*:}"
  mkdir -p "$ANDROID_DIR/mipmap-$name"
  sips -z $size $size "$SOURCE" --out "$ANDROID_DIR/mipmap-$name/ic_launcher.png"
  sips -z $size $size "$SOURCE" --out "$ANDROID_DIR/mipmap-$name/ic_launcher_round.png"
  sips -z $size $size "$SOURCE" --out "$ANDROID_DIR/mipmap-$name/ic_launcher_foreground.png"
done

# Adaptive icon XML (if not exists)
mkdir -p "$ANDROID_DIR/mipmap-anydpi-v26"
cat > "$ANDROID_DIR/mipmap-anydpi-v26/ic_launcher.xml" << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/ic_launcher_background"/>
    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
</adaptive-icon>
EOF

mkdir -p "$ANDROID_DIR/values"
cat > "$ANDROID_DIR/values/ic_launcher_background.xml" << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="ic_launcher_background">#1A1816</color>
</resources>
EOF
```

---

## SVG Source Workflow

If extracting SVG from Figma (higher quality):

```bash
# Convert SVG to high-res PNG first
rsvg-convert -w 1024 -h 1024 icon.svg -o source_icon.png

# Then run all generation commands above
```

---

## Complete Generation Script

Save this as `generate-icons.sh` in project root:

```bash
#!/bin/bash
set -e

SOURCE="${1:-source_icon.png}"
ICONS_DIR="${2:-app/src-tauri/icons}"

if [ ! -f "$SOURCE" ]; then
  echo "Error: Source file '$SOURCE' not found"
  exit 1
fi

echo "Generating Tauri icons from $SOURCE..."

# Desktop
echo "  Desktop icons..."
sips -z 512 512 "$SOURCE" --out "$ICONS_DIR/icon.png" >/dev/null
sips -z 256 256 "$SOURCE" --out "$ICONS_DIR/128x128@2x.png" >/dev/null
sips -z 128 128 "$SOURCE" --out "$ICONS_DIR/128x128.png" >/dev/null
sips -z 64 64 "$SOURCE" --out "$ICONS_DIR/64x64.png" >/dev/null
sips -z 32 32 "$SOURCE" --out "$ICONS_DIR/32x32.png" >/dev/null

# Windows Store
echo "  Windows Store icons..."
for size in 310 284 150 142 107 89 71 44 30; do
  sips -z $size $size "$SOURCE" --out "$ICONS_DIR/Square${size}x${size}Logo.png" >/dev/null
done
sips -z 50 50 "$SOURCE" --out "$ICONS_DIR/StoreLogo.png" >/dev/null

# macOS .icns
echo "  macOS .icns..."
ICONSET=$(mktemp -d)/AppIcon.iconset
mkdir -p "$ICONSET"
sips -z 16 16 "$SOURCE" --out "$ICONSET/icon_16x16.png" >/dev/null
sips -z 32 32 "$SOURCE" --out "$ICONSET/icon_16x16@2x.png" >/dev/null
sips -z 32 32 "$SOURCE" --out "$ICONSET/icon_32x32.png" >/dev/null
sips -z 64 64 "$SOURCE" --out "$ICONSET/icon_32x32@2x.png" >/dev/null
sips -z 128 128 "$SOURCE" --out "$ICONSET/icon_128x128.png" >/dev/null
sips -z 256 256 "$SOURCE" --out "$ICONSET/icon_128x128@2x.png" >/dev/null
sips -z 256 256 "$SOURCE" --out "$ICONSET/icon_256x256.png" >/dev/null
sips -z 512 512 "$SOURCE" --out "$ICONSET/icon_256x256@2x.png" >/dev/null
sips -z 512 512 "$SOURCE" --out "$ICONSET/icon_512x512.png" >/dev/null
sips -z 1024 1024 "$SOURCE" --out "$ICONSET/icon_512x512@2x.png" >/dev/null
iconutil -c icns "$ICONSET" -o "$ICONS_DIR/icon.icns"
rm -rf "$(dirname "$ICONSET")"

# Windows .ico
echo "  Windows .ico..."
magick "$SOURCE" -define icon:auto-resize=256,128,96,64,48,32,16 "$ICONS_DIR/icon.ico"

# iOS
echo "  iOS icons..."
IOS_DIR="$ICONS_DIR/ios"
mkdir -p "$IOS_DIR"
sips -z 20 20 "$SOURCE" --out "$IOS_DIR/AppIcon-20x20@1x.png" >/dev/null
sips -z 40 40 "$SOURCE" --out "$IOS_DIR/AppIcon-20x20@2x.png" >/dev/null
cp "$IOS_DIR/AppIcon-20x20@2x.png" "$IOS_DIR/AppIcon-20x20@2x-1.png"
sips -z 60 60 "$SOURCE" --out "$IOS_DIR/AppIcon-20x20@3x.png" >/dev/null
sips -z 29 29 "$SOURCE" --out "$IOS_DIR/AppIcon-29x29@1x.png" >/dev/null
sips -z 58 58 "$SOURCE" --out "$IOS_DIR/AppIcon-29x29@2x.png" >/dev/null
cp "$IOS_DIR/AppIcon-29x29@2x.png" "$IOS_DIR/AppIcon-29x29@2x-1.png"
sips -z 87 87 "$SOURCE" --out "$IOS_DIR/AppIcon-29x29@3x.png" >/dev/null
sips -z 40 40 "$SOURCE" --out "$IOS_DIR/AppIcon-40x40@1x.png" >/dev/null
sips -z 80 80 "$SOURCE" --out "$IOS_DIR/AppIcon-40x40@2x.png" >/dev/null
cp "$IOS_DIR/AppIcon-40x40@2x.png" "$IOS_DIR/AppIcon-40x40@2x-1.png"
sips -z 120 120 "$SOURCE" --out "$IOS_DIR/AppIcon-40x40@3x.png" >/dev/null
sips -z 120 120 "$SOURCE" --out "$IOS_DIR/AppIcon-60x60@2x.png" >/dev/null
sips -z 180 180 "$SOURCE" --out "$IOS_DIR/AppIcon-60x60@3x.png" >/dev/null
sips -z 76 76 "$SOURCE" --out "$IOS_DIR/AppIcon-76x76@1x.png" >/dev/null
sips -z 152 152 "$SOURCE" --out "$IOS_DIR/AppIcon-76x76@2x.png" >/dev/null
sips -z 167 167 "$SOURCE" --out "$IOS_DIR/AppIcon-83.5x83.5@2x.png" >/dev/null
sips -z 1024 1024 "$SOURCE" --out "$IOS_DIR/AppIcon-512@2x.png" >/dev/null

# Android
echo "  Android icons..."
ANDROID_DIR="$ICONS_DIR/android"
for density in mdpi:48 hdpi:72 xhdpi:96 xxhdpi:144 xxxhdpi:192; do
  name="${density%%:*}"
  size="${density##*:}"
  mkdir -p "$ANDROID_DIR/mipmap-$name"
  sips -z $size $size "$SOURCE" --out "$ANDROID_DIR/mipmap-$name/ic_launcher.png" >/dev/null
  sips -z $size $size "$SOURCE" --out "$ANDROID_DIR/mipmap-$name/ic_launcher_round.png" >/dev/null
  sips -z $size $size "$SOURCE" --out "$ANDROID_DIR/mipmap-$name/ic_launcher_foreground.png" >/dev/null
done

echo "Done! All icons generated in $ICONS_DIR"
```

---

## Figma Integration Workflow

### Full Process

1. **Get Figma file structure:**
   ```
   > Use Figma MCP: get_metadata for [figma URL]
   ```

2. **Identify icon node** - Look for app icon frame (usually 1024x1024 or similar)

3. **Export at high resolution:**
   ```
   > Use Figma MCP: get_screenshot for node [icon_id] with scale 4
   ```

4. **Save screenshot** to temp file (e.g., `/tmp/app_icon.png`)

5. **Run generation script:**
   ```bash
   ./generate-icons.sh /tmp/app_icon.png app/src-tauri/icons
   ```

6. **Verify** icons look correct in the icons directory

---

## Troubleshooting

### "sips: image crop edges fall outside image boundaries"
Source image is too small. Ensure source is at least 1024x1024.

### .icns looks blurry
Increase source resolution. Export from Figma at 4x scale minimum.

### .ico shows wrong size in Windows
Regenerate with ImageMagick - some sizes may be missing.

### Android adaptive icons have wrong background
Edit `android/values/ic_launcher_background.xml` to match your app's theme color.

---

## Related Skills

- `figma-design-extraction` - Extracting designs from Figma
- `frontend-design` - your design system design system (color reference)
- `tech-stacks` - Tauri project setup
