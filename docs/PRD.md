# OpenSati Product Requirements Document

**Version:** 2.0  
**Last Updated:** January 2026  
**Status:** Active Development

---

## Executive Summary

OpenSati is a local-first desktop application that helps knowledge workers maintain sustainable productivity through multi-modal awareness: keyboard patterns, audio analysis, screen context, and optional webcam posture detection.

Unlike website blockers or timers, OpenSati works as an **Intelligent Mirror**—reflecting your digital body language back to you and prompting mindful choices in real-time.

**Core Value Proposition:** Keep users in flow state through gentle, intelligent interventions—without surveillance or cloud dependency.

---

## Success Metrics

### Primary Metric
**Intervention Acceptance Rate**  
`(Interventions Accepted) / (Total Interventions Triggered)` — Target: >40%

### Secondary Metrics
| Metric | Target | Why It Matters |
|--------|--------|----------------|
| Daily Flow Time | +15% vs baseline | Core value delivery |
| Stress Episodes Reduced | -30% vs baseline | Health impact |
| Feature Opt-in Rate | >60% enable webcam/mic | Trust indicator |
| Uninstall Rate (7-day) | <15% | Product-market fit |

---

## User Personas

### Primary: The Overworked IC
- Works 10+ hour days, can't disconnect
- Needs help noticing when they're spiraling, not more blockers

### Secondary: The Anxious Multitasker
- Context-switches 50+ times/hour
- Wants automatic focus protection without micro-managing settings

---

## Feature Overview

### Sensor Modules (All Optional/Toggleable)

| Sensor | Data Captured | Privacy Level |
|--------|---------------|---------------|
| Keyboard | Velocity only (not keystrokes) | Low risk |
| Mouse | Movement patterns, click frequency | Low risk |
| Screen | Periodic screenshots for AI | Medium risk |
| Webcam | Posture & breathing rate | High risk |
| Microphone | Breathing patterns, voice stress | High risk |

> [!IMPORTANT]
> All sensors are **opt-in** and can be disabled individually. All processing happens locally—no data leaves the machine.

---

## Phase 1: Core MVP

### 1.1 Input Stress Detection
**What:** Monitor keyboard/mouse velocity to detect "frantic state."

**Triggers:**
- Typing speed >130% of baseline for 60+ seconds
- Mouse clicking >3x normal rate
- Tab switching >40 times/minute

### 1.2 Grayscale Intervention
**What:** Screen desaturates over 5 seconds when stress detected.

**User Flow:**
1. Stress threshold exceeded
2. Screen fades to grayscale
3. Pill notification: *"Typing fast. Take a breath?"*
4. Accept → Color restores | Dismiss → 2 min grayscale

### 1.3 Meeting Decompression
**What:** 60-second calm screen after video calls end.

**Trigger apps:** Zoom, Teams, Meet, Slack Huddles

---

## Phase 2: Audio Intelligence

### 2.1 Breathing Analysis (Mic)
**What:** Detect shallow/rapid breathing patterns indicating stress.

**How it works:**
1. User enables mic access (opt-in)
2. Audio processed locally for respiratory rate
3. If breathing <8 or >20 breaths/min → intervention

**Privacy:**
- Audio never stored—analyzed in real-time, discarded
- Only respiratory rate logged (not audio content)

### 2.2 Voice Stress Detection
**What:** Detect elevated vocal tension during meetings/calls.

**Triggers:**
- Pitch variance indicating stress
- Speaking rate acceleration
- Post-call: suggest recovery break

---

## Phase 3: Visual Intelligence

### 3.1 Intent-Reality Checker
**What:** User declares work intent; AI verifies screen matches.

**User Flow:**
1. User types intent: *"Writing Q3 report"*
2. Every 30s, screenshot analyzed by local VLM
3. If content doesn't match (e.g., TikTok open):
   - *"Is this part of writing Q3 report?"*
4. User confirms or returns to work

**Technical:**
- Uses Ollama + LLaVA for local vision-language
- Screenshots processed in RAM, never saved

### 3.2 Posture & Breath Detection (Webcam)
**What:** Detect "tech neck" and shallow breathing via camera.

**Interventions:**
- Posture collapse → Screen blurs
- Fix posture → Blur clears immediately
- Creates direct body-digital feedback loop

**Privacy:**
- Video never stored
- Only posture angle logged (not images)

### 3.3 Right Speech Co-Pilot
**What:** Detect aggressive typing and suggest reframes.

**How it works:**
1. Monitors clipboard/text for sentiment (opt-in)
2. Detects aggressive language patterns
3. Offers NVC-style rephrasing

**Example:**
- Typed: *"This is stupid and you missed the deadline."*
- Suggest: *"I'm concerned about the timeline. What blockers came up?"*

---

## Privacy Architecture

### Data Flow
```
Sensors → Local Processing → Insights Only → Local Storage
              ↓
         [RAM only - no disk writes for raw data]
```

### Privacy Dashboard (Always Visible)
```
🔒 Privacy Status
├─ Keyboard: ✓ Velocity only
├─ Mouse: ✓ Patterns only
├─ Screen: ○ Disabled
├─ Webcam: ○ Disabled
├─ Mic: ○ Disabled
├─ Network: 0 bytes sent
└─ AI: Local (Ollama)
```

---

## Technical Requirements

### Supported Platforms
| Platform | Version | Status |
|----------|---------|--------|
| macOS | 12.0+ | Primary |
| Windows | 10/11 | Secondary |
| Linux | Ubuntu 22.04+ | Community |

### Dependencies
- Python 3.10+
- Ollama (for AI features)
- OpenCV (for webcam/vision)
- PyAudio (for mic analysis)
- 8GB RAM recommended

### Performance Targets
| Metric | Target |
|--------|--------|
| CPU (idle) | <2% |
| CPU (active) | <8% |
| RAM | <300MB |

---

## Configuration

```yaml
# config.yaml
sensors:
  keyboard: true      # Always safe
  mouse: true         # Always safe
  screen: false       # Opt-in
  webcam: false       # Opt-in
  microphone: false   # Opt-in

detection:
  stress_threshold: 50
  tab_switch_limit: 40

intervention:
  style: "grayscale"  # grayscale, blur, notification
  intensity: "gentle" # gentle, moderate, firm

ai:
  model: "llama3"
  vision_model: "llava"
```

---

## Monetization

### Pay What You Want Model
| Tier | Price | Includes |
|------|-------|----------|
| Source | Free | Full code, self-setup |
| Installer | $0-$50 | One-click, auto-updates |
| Team | $10/user/mo | Central config, aggregated analytics |

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Users find interventions annoying | Configurable intensity + easy disable |
| Privacy concerns despite local-first | Open source, visible privacy dashboard |
| Webcam/mic feels invasive | Off by default, clear value explanation |
| AI setup too complex | Bundled Ollama in installer |

---

## Out of Scope

- ❌ Cloud sync
- ❌ Mobile app
- ❌ Social/leaderboard features
- ❌ Keystroke content logging (ever)

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Jan 2026 | Initial PRD |
| 2.0 | Jan 2026 | Added audio, webcam, intent features |
