# OpenSati Design System

**Version:** 1.0  
**Design Philosophy:** Calm Computing  
**Target Era:** 2025-2030

---

## Design Philosophy

OpenSati exists to reduce digital anxiety, not add to it. Every design decision must pass this test:

> **"Does this calm the user, or demand their attention?"**

We draw inspiration from:
- **Dieter Rams** — Less, but better
- **Naoto Fukasawa** — Design that dissolves into the background
- **Apple Human Interface Guidelines** — Clarity, depth, deference
- **Linear** — Precision without coldness
- **Vercel** — Technical elegance

---

## Core Principles

### 1. Invisible Until Needed
The best interface is no interface. OpenSati should feel like part of the OS, not an app fighting for attention.

### 2. Respectful Interventions
When we do interrupt, we ask—never demand. The user is always in control.

### 3. Dark by Default
Knowledge workers spend hours staring at screens. We default to dark mode to reduce eye strain.

### 4. Motion with Purpose
Animation exists to communicate state, not to delight. Every transition should be fast and functional.

---

## Color System

### Philosophy
Our palette is inspired by natural dawn and dusk—transitions that feel inevitable, not jarring.

### Dark Mode (Default)

| Token | Hex | RGB | Usage |
|-------|-----|-----|-------|
| `--bg-primary` | `#0A0A0B` | 10, 10, 11 | Main background |
| `--bg-secondary` | `#141415` | 20, 20, 21 | Cards, panels |
| `--bg-elevated` | `#1C1C1E` | 28, 28, 30 | Modals, dropdowns |
| `--border-subtle` | `#2C2C2E` | 44, 44, 46 | Dividers |
| `--border-default` | `#3A3A3C` | 58, 58, 60 | Input borders |
| `--text-primary` | `#F5F5F7` | 245, 245, 247 | Headings |
| `--text-secondary` | `#A1A1A6` | 161, 161, 166 | Body text |
| `--text-tertiary` | `#6E6E73` | 110, 110, 115 | Placeholders |

### Accent Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--accent-calm` | `#4ADE80` | Success, flow state, positive |
| `--accent-alert` | `#F97316` | Warning, stress detected |
| `--accent-focus` | `#818CF8` | Interactive elements, links |
| `--accent-danger` | `#EF4444` | Errors, critical alerts |

### Semantic Colors

```css
/* States */
--state-flow: #4ADE80;      /* User in deep work */
--state-stress: #F97316;    /* Elevated stress detected */
--state-neutral: #6E6E73;   /* Baseline, no intervention */
--state-recovery: #818CF8;  /* Post-intervention cooldown */
```

### Light Mode (Optional)

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-primary` | `#FFFFFF` | Main background |
| `--bg-secondary` | `#F5F5F7` | Cards, panels |
| `--text-primary` | `#1D1D1F` | Headings |
| `--text-secondary` | `#6E6E73` | Body text |

---

## Typography

### Font Stack

```css
--font-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
--font-mono: "JetBrains Mono", "SF Mono", Consolas, monospace;
```

**Why Inter:** Designed for screens, excellent at small sizes, free and open source.

### Type Scale

| Token | Size | Weight | Line Height | Usage |
|-------|------|--------|-------------|-------|
| `--text-xs` | 11px | 400 | 1.4 | Labels, metadata |
| `--text-sm` | 13px | 400 | 1.5 | Secondary text |
| `--text-base` | 15px | 400 | 1.6 | Body copy |
| `--text-lg` | 17px | 500 | 1.5 | Subheadings |
| `--text-xl` | 20px | 600 | 1.4 | Section titles |
| `--text-2xl` | 24px | 600 | 1.3 | Page titles |
| `--text-3xl` | 32px | 700 | 1.2 | Hero text |

### Usage Guidelines

- **Headlines:** Semi-bold (600), tight tracking (-0.02em)
- **Body:** Regular (400), comfortable line height (1.6)
- **UI Labels:** Medium (500), uppercase sparingly
- **Code/Data:** Monospace, tabular numerals

---

## Spacing System

Based on 4px grid with 8px as the primary unit.

| Token | Value | Usage |
|-------|-------|-------|
| `--space-1` | 4px | Tight grouping |
| `--space-2` | 8px | Related elements |
| `--space-3` | 12px | Standard gap |
| `--space-4` | 16px | Section padding |
| `--space-5` | 24px | Card padding |
| `--space-6` | 32px | Section separation |
| `--space-8` | 48px | Major sections |
| `--space-10` | 64px | Page margins |

---

## Components

### Intervention Pill

The primary UI element during stress detection.

```
┌─────────────────────────────────────────┐
│  ○  You're typing fast. Breathe?  [Yes] │
└─────────────────────────────────────────┘
```

**Specifications:**
- Position: Bottom-center, 24px from edge
- Background: `--bg-elevated` with 0.95 opacity
- Border: 1px `--border-subtle`
- Border-radius: 12px
- Shadow: `0 4px 24px rgba(0,0,0,0.4)`
- Animation: Fade up + scale (200ms ease-out)

**States:**
- Idle: Full opacity
- Hover (button): Subtle highlight
- Dismissing: Fade down (150ms)

### System Tray Icon

Minimal indicator of current state.

| State | Icon | Color |
|-------|------|-------|
| Neutral | ○ (circle outline) | `--text-tertiary` |
| Monitoring | ◐ (half-filled) | `--text-secondary` |
| Flow Detected | ● (filled) | `--state-flow` |
| Stress Detected | ● (pulsing) | `--state-stress` |

### Settings Panel

Native-feeling preferences window.

```
┌─────────────────────────────────────────────────┐
│  ⚙️  Settings                              ─ □ × │
├─────────────────────────────────────────────────┤
│                                                 │
│  Detection                                      │
│  ┌───────────────────────────────────────────┐ │
│  │  Stress Threshold          ────●────  50  │ │
│  │  Intervention Style        [Grayscale ▼]  │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  Privacy                                        │
│  ┌───────────────────────────────────────────┐ │
│  │  🔒 All data stays on this device         │ │
│  │  Network requests: 0                      │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Motion Design

### Timing Functions

| Token | Curve | Usage |
|-------|-------|-------|
| `--ease-default` | `cubic-bezier(0.4, 0, 0.2, 1)` | General purpose |
| `--ease-in` | `cubic-bezier(0.4, 0, 1, 1)` | Elements leaving |
| `--ease-out` | `cubic-bezier(0, 0, 0.2, 1)` | Elements entering |
| `--ease-spring` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Playful bounce |

### Durations

| Token | Duration | Usage |
|-------|----------|-------|
| `--duration-fast` | 100ms | Micro-interactions |
| `--duration-base` | 200ms | Standard transitions |
| `--duration-slow` | 300ms | Complex animations |
| `--duration-grayscale` | 5000ms | Screen desaturation |

### The Grayscale Transition

The signature intervention effect.

```css
@keyframes desaturate {
  0%   { filter: saturate(1); }
  100% { filter: saturate(0); }
}

.intervention-active {
  animation: desaturate 5s ease-out forwards;
}
```

**Design Intent:**
- 5 seconds is long enough to notice, short enough not to frustrate
- Ease-out curve: Fast start, slow finish (feels inevitable)
- No jarring cuts—the world fades naturally

---

## Iconography

### Style
- Line icons, 1.5px stroke
- 24x24 base size
- Rounded caps and joins
- Consistent optical sizing

### Core Icons

| Icon | Usage | Glyph |
|------|-------|-------|
| Breathe | Intervention prompt | ◎ |
| Settings | Preferences | ⚙ |
| Shield | Privacy indicator | 🛡 |
| Flow | Deep work state | ● |
| Alert | Stress detected | ⚠ |
| Check | Confirmation | ✓ |
| Close | Dismiss | × |

**Icon Source:** [Lucide](https://lucide.dev) (MIT licensed, consistent style)

---

## Accessibility

### Color Contrast
All text meets WCAG 2.1 AA standards:
- Primary text on primary bg: 15.8:1
- Secondary text on primary bg: 7.2:1
- Accent on primary bg: 4.6:1

### Motion Sensitivity
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Screen Reader Support
- All interactive elements have aria-labels
- Intervention notifications announced via aria-live
- Keyboard navigation for all UI

---

## Platform-Specific Adaptations

### macOS
- Use SF Pro for system UI where appropriate
- Respect system accent color for highlights
- Vibrancy/blur effects for elevated surfaces (NSVisualEffectView)
- Menu bar integration with native styling

### Windows
- Use Segoe UI for system UI
- Acrylic material for panels (Windows 11)
- System tray follows Windows conventions
- Toast notifications use native Windows style

---

## Future Directions (2027-2030)

### Ambient Interfaces
As AR/spatial computing matures, OpenSati could extend to:
- Peripheral vision indicators (not screen overlays)
- Environmental lighting changes via smart bulbs
- Subtle haptic feedback via wearables

### Adaptive Aesthetics
- Time-of-day color temperature shifts
- Seasonal palette variations
- User-learned preferences (ML-driven)

### Voice-First Interventions
- Whispered audio prompts instead of visual
- "Hey, you've been at this for 2 hours. Stretch?"

---

## Resources

- [Inter Font](https://rsms.me/inter/)
- [Lucide Icons](https://lucide.dev)
- [Radix Colors](https://www.radix-ui.com/colors)
- [Apple HIG](https://developer.apple.com/design/human-interface-guidelines/)
- [Material Design 3](https://m3.material.io/)

---

*"Good design is as little design as possible."* — Dieter Rams
