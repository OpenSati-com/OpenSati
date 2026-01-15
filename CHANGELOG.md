# Changelog

All notable changes to OpenSati are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-01-15

### Added
- **Core Detection**
  - Keyboard velocity monitoring (privacy-first, no content logging)
  - Mouse movement pattern tracking
  - Multi-modal stress score fusion

- **Audio Analysis** (opt-in)
  - Breathing rate detection via microphone
  - Stress pattern recognition

- **Vision Analysis** (opt-in)
  - Screen capture for intent checking (RAM-only)
  - Webcam posture detection
  - "Tech neck" alert system

- **AI Integration**
  - Local LLM via Ollama (llama3)
  - Vision-Language model for screen understanding (llava)
  - Intent-Reality checker
  - Right Speech sentiment analyzer

- **Interventions**
  - Grayscale screen fade (5-second transition)
  - Blur overlay for posture correction
  - Notification pill with accept/dismiss
  - Meeting decompression (60s calm screen)

- **User Interface**
  - System tray icon with state indicators
  - Settings window with privacy toggles
  - Intent input bar for focus declaration

- **Privacy**
  - All processing local (no cloud)
  - Sensors individually toggleable
  - Privacy dashboard showing data status
  - Zero network requests

### Security
- GPLv3 license to protect open-source nature
- Strict PR review for any network code
- Content never logged, only metrics
