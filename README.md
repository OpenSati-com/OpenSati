<div align="center">

# 🧘 OpenSati
### The Intelligent Mirror for Deep Work

[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Privacy: Local](https://img.shields.io/badge/Privacy-Local%20First-green.svg)](https://github.com/OpenSati-com/OpenSati)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

<br>

**A local-AI copilot that reads your digital body language to keep you in flow state.**

[**⬇️ Download Installer (Pay What You Want)**](https://opensati.com)
<br>
*(Support open source development & get auto-updates)*

[**View the Code**](#-installation-for-developers) | [**Read the Manifesto**](https://opensati.com/manifesto) | [**Join Discord**](https://discord.gg/opensati)

</div>

---

## 🛑 The Problem

You sit down to write a report. Ten minutes later, you're doom-scrolling.

Current tools treat you like a child—blocking sites, locking screens, using rigid timers.

**But you don't need a blocker. You need a mirror.**

Most burnout happens because we don't notice our own stress signals. We hold our breath while typing emails. We switch tabs 40 times a minute when anxious. We hunch forward when stressed.

## 👁️ The Solution: OpenSati

**OpenSati** is a desktop HUD that monitors your **Digital Body Language** using local AI:

- **Typing patterns** → Detects frantic state
- **Breathing rhythm** → Catches stress before you notice
- **Screen content** → Knows if you're on-task (via local AI)
- **Posture** → Sees when you're hunching

When something's off, it intervenes gently—fading your screen to grayscale, suggesting a breath, or asking if TikTok is really part of your Q3 report.

> *"I noticed you've switched tabs 45 times in 60 seconds. Let's take one breath."*

---

## ✨ Features

### 🔒 Zero-Data Privacy (Local First)
**We do not want your data.**

Everything runs on your CPU/GPU via Ollama. Screenshots analyzed in RAM and deleted instantly. We log *insights* ("High Stress"), never *content*.

```
🔒 Privacy Dashboard
├─ Keyboard: Velocity only ✓
├─ Screen: RAM only, deleted ✓
├─ Webcam: Posture only ✓
├─ Network: 0 bytes sent ✓
└─ AI: 100% Local ✓
```

### 🎯 Intent-Reality Checker
Tell OpenSati what you're working on:
> *"Writing the Q3 financial report"*

If you open YouTube for a finance tutorial → **Allowed**  
If you open TikTok → *"Is this part of your Q3 report?"*

No blocking. Just a mirror.

### 🌑 The Grayscale Nudge
When stress is detected, your screen slowly fades to **Black & White**.

- **The Psychology:** Color is addictive. We remove the dopamine trigger.
- **The Fix:** Take one breath to restore color.

### 🧘 Posture & Breath Awareness (Optional)
Enable webcam to detect:
- **Tech Neck** → Screen blurs until you sit up
- **Shallow breathing** → Gentle reminder to breathe

Enable microphone to detect:
- **Breathing rate** → Intervention if too fast/shallow
- **Voice stress** → Post-call recovery suggestion

### 💬 Right Speech Co-Pilot (Optional)
Detects aggressive typing patterns and offers reframes:

| You type | Suggestion |
|----------|------------|
| *"This is stupid and you missed the deadline."* | *"I'm concerned about the timeline. What blockers came up?"* |

### 🛑 Meeting Decompression
Detects when Zoom/Teams/Meet closes and triggers a **60-second calm screen** before you check email.

---

## 🎛️ Privacy Controls

Every sensor is **opt-in** and **individually toggleable**:

```yaml
# config.yaml
sensors:
  keyboard: true      # Low risk - velocity only
  mouse: true         # Low risk - patterns only
  screen: false       # Enable for intent checking
  webcam: false       # Enable for posture detection
  microphone: false   # Enable for breath analysis
```

---

## 💰 Pay What You Want

We believe in **Sustainable Open Source**.

| **Developer (Free)** | **Installer (Pay What You Want)** |
| :--- | :--- |
| ✅ Full Source Code | ✅ One-Click Install |
| ❌ Manual Python Setup | ✅ Auto-Updates |
| ❌ Configure Ollama | ✅ Pre-configured AI |
| ❌ No Support | ✅ Priority Support |

**[Get the Installer](https://opensati.com)** <br>
*Your contribution keeps the code open and auditable.*

---

## 🛠️ Installation (For Developers)

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.ai/) (for AI features)
- `ffmpeg` (for audio processing)

### Quick Start

```bash
# 1. Clone
git clone https://github.com/OpenSati-com/OpenSati.git
cd OpenSati

# 2. Install
pip install -e .

# 3. Pull AI models
ollama pull llama3
ollama pull llava  # For vision features

# 4. Run
opensati
```

### Configuration

```yaml
# config.yaml
detection:
  stress_threshold: 50      # Keystrokes per 10s
  tab_switch_limit: 40      # Per minute

intervention:
  style: "grayscale"        # grayscale, blur, notification
  recovery_method: "breath" # breath, timeout, manual

ai:
  model: "llama3"
  vision_model: "llava"
```

---

## 🗺️ Roadmap

- [x] **v0.1:** Typing stress detection & grayscale fade
- [x] **v0.2:** Meeting decompression
- [ ] **v0.3:** Intent-Reality checker (VLM)
- [ ] **v0.4:** Webcam posture detection
- [ ] **v0.5:** Mic breathing analysis
- [ ] **v0.6:** Right Speech co-pilot
- [ ] **v1.0:** Signed installers (macOS/Windows)

---

## 🤝 Contributing

We welcome Pull Requests! See [CONTRIBUTING.md](CONTRIBUTING.md).

**Security Note:** PRs adding network calls to external servers will be **rejected** to maintain our privacy promise.

---

## 📜 License

**GNU GPLv3** — Use, modify, distribute freely. Modified versions must remain open source.

---

<div align="center">
<b>OpenSati</b> is built with 🖤 and mindfulness.

<br><br>

<i>"The mind is a wonderful servant, but a terrible master."</i>
</div>
