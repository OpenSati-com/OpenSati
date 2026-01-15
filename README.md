<div align="center">

# 🧘 OpenSati
### The Intelligent Mirror for Deep Work.

[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Privacy: Local](https://img.shields.io/badge/Privacy-Local%20First-green.svg)](https://github.com/yourusername/opensati)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

<br>

**A local-AI copilot that watches your digital body language to prevent burnout before it happens.**

[**⬇️ Download Installer for Mac/Windows ($15)**](https://opensati.com)
<br>
*(Supports development & includes auto-updates)*

[**View the Code**](#-installation-for-developers) | [**Read the Manifesto**](https://opensati.com/manifesto) | [**Join Discord**](https://discord.gg/placeholder)

</div>

---

## 🛑 The Problem: "Intent Friction"

You sit down to write a report. Ten minutes later, you are doom-scrolling.
Current tools try to fix this by treating you like a child—blocking sites, locking screens, or using rigid timers.

**But you don't need a blocker. You need a mirror.**

Most burnout happens because we don't notice our own stress signals until it's too late. We hold our breath while typing emails. We switch tabs 40 times a minute when anxious.

## 👁️ The Solution: OpenSati

**OpenSati** is a desktop HUD that runs locally on your machine. It uses Computer Vision and specialized algorithms to monitor your **Digital Body Language**.

When it detects "Frantic State" (high typing velocity, erratic mouse movements, shallow breathing patterns via webcam), it gently intervenes.

> *"I noticed you've switched tabs 45 times in 60 seconds. Let's take one breath before sending that email."*

---

## ✨ Features

### 🔒 1. Zero-Data Privacy (Local First)
**We do not want your data.**
OpenSati uses `Ollama` and local Python libraries to process everything on your CPU/GPU.
* **No Cloud:** Screenshots are processed in RAM and deleted instantly.
* **No Spying:** We log *insights* ("High Stress"), not *content* ("User typed password123").

### 🧠 2. Semantic Awareness
Using local Vision-Language Models (VLM), OpenSati understands context.
* Watching a React tutorial on YouTube? **✅ Allowed.**
* Watching a cat video on YouTube? **⚠️ Intervention Triggered.**

### 🌑 3. The "Grayscale" Nudge
When you lose focus, OpenSati doesn't lock your screen. It slowly fades your monitor to **Black & White**.
* **The Psychology:** The internet is addictive because it is colorful. We remove the dopamine trigger.
* **The Fix:** Take one deep breath (verified by webcam) to restore color.

### 🛑 4. Meeting Decompression
Automatically detects when `Zoom.exe` or `Teams.exe` closes and triggers a **60-second "Palate Cleanser"**—a blank, calming screen to reset your cognitive load before you check email.

---

## 💰 "Pay for Convenience" Model

We believe in **Sustainable Open Source**.

| **The Developer Way (Free)** | **The Human Way ($15)** |
| :--- | :--- |
| ✅ Full Source Code Access | ✅ **One-Click Installer (.exe / .dmg)** |
| ❌ Manual Python Setup | ✅ **Auto-Updates** |
| ❌ No Tech Support | ✅ **Priority Support** |
| ❌ You manage API/Local Models | ✅ **Pre-configured Local AI** |

**[Buy the Installer ($15)](https://opensati.com)** <br>
*Your purchase allows us to keep the code open and audit-able.*

---

## 🛠️ Installation (For Developers)

If you are comfortable with terminals and Python environments, you can run OpenSati for free.

### Prerequisites
* Python 3.10+
* [Ollama](https://ollama.ai/) (for local AI inference)
* `ffmpeg` (for audio processing)

### Quick Start

```bash
# 1. Clone the repo
git clone [https://github.com/yourusername/opensati.git](https://github.com/yourusername/opensati.git)
cd opensati

# 2. Create Virtual Environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Pull the Local AI Model (TinyLlama or Mistral recommended for speed)
ollama pull llama3

# 5. Run Sati
python main.py
