# OpenSati Resources

This directory contains app resources:

- `icon.icns` - macOS app icon
- `icon.ico` - Windows app icon  
- `icon.png` - Linux/generic icon

## Creating Icons

Use a square PNG (1024x1024) and convert:

```bash
# macOS
iconutil -c icns icon.iconset

# Windows (requires ImageMagick)
convert icon.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico
```
