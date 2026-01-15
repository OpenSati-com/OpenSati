# Contributing to OpenSati

Thank you for your interest in contributing to OpenSati. This document outlines the guidelines and expectations for contributors.

---

## 🔒 The Golden Rule: No Cloud, Ever

**Any Pull Request that introduces network calls to external servers will be rejected.**

This includes:
- Telemetry or analytics services
- Cloud storage or sync
- External API calls (except Ollama running locally)
- "Optional" tracking with user consent

We are serious about this. OpenSati's entire value proposition is local-first privacy. There are no exceptions.

---

## Getting Started

### 1. Fork and Clone
```bash
git clone https://github.com/YOUR_USERNAME/OpenSati.git
cd OpenSati
```

### 2. Set Up Development Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Testing and linting
```

### 3. Run Tests
```bash
pytest tests/
```

### 4. Run Linting
```bash
ruff check .
mypy src/
```

---

## Pull Request Process

### Before Submitting

1. **Check existing issues** - Someone may already be working on it
2. **Create an issue first** - For significant changes, discuss before coding
3. **Write tests** - All new features need test coverage
4. **Update documentation** - If you change behavior, update the docs

### PR Requirements

- [ ] All tests pass
- [ ] No linting errors
- [ ] Documentation updated (if applicable)
- [ ] Commit messages are clear and descriptive
- [ ] No network calls to external services
- [ ] Privacy-preserving (no content logging)

### Commit Message Format
```
type: short description

Longer explanation if needed.

Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

---

## Code Standards

### Python Style
- Follow PEP 8
- Use type hints for all function signatures
- Maximum line length: 100 characters
- Use `ruff` for formatting

### Naming Conventions
```python
# Classes: PascalCase
class StressDetector:
    pass

# Functions/variables: snake_case
def calculate_typing_velocity():
    baseline_speed = 0

# Constants: UPPER_SNAKE_CASE
MAX_KEYSTROKE_BUFFER = 1000
```

### Privacy-First Patterns

**DO:**
```python
# Log insights, not content
logger.info(f"Stress level: {stress_score}")
logger.info(f"Intervention triggered: grayscale")
```

**DON'T:**
```python
# Never log user content
logger.info(f"User typed: {keystroke_buffer}")  # ❌ REJECTED
logger.info(f"Screenshot saved: {path}")         # ❌ REJECTED
```

---

## Architecture Guidelines

### Module Structure
```
src/
├── core/           # Core detection logic
├── interventions/  # Screen effects, notifications
├── ui/             # System tray, settings window
├── integrations/   # Ollama, Slack (all local/OAuth)
└── utils/          # Shared utilities
```

### Key Principles

1. **Minimal Permissions** - Request only what's needed
2. **Fail Gracefully** - If AI isn't available, fall back to rule-based
3. **User Control** - Every feature must be disableable
4. **No Surprises** - Actions should be predictable

---

## Security Considerations

### Acceptable
- Reading keyboard/mouse velocity (not content)
- Processing screenshots in RAM (deleted immediately)
- Local file storage for settings/logs
- OAuth for optional integrations (Slack status)

### Not Acceptable
- Keystroke logging (actual characters)
- Persistent screenshot storage
- Any form of cloud sync
- Third-party analytics SDKs

---

## Getting Help

- **Questions:** Open a [Discussion](https://github.com/OpenSati-com/OpenSati/discussions)
- **Bugs:** Open an [Issue](https://github.com/OpenSati-com/OpenSati/issues)
- **Security Issues:** Email security@opensati.com (do not open public issues)

---

## License

By contributing, you agree that your contributions will be licensed under the GNU GPLv3 License.
