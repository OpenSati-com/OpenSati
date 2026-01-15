# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in OpenSati, please report it privately:

**Email:** security@opensati.com

Please do NOT open a public issue for security vulnerabilities.

## Our Commitment

We take security and privacy seriously. OpenSati is designed with these principles:

### Privacy by Design
- All data processing happens **locally** on your machine
- No network requests to external servers
- Raw data (screenshots, audio, video) is **never stored** to disk
- Only derived metrics are logged (e.g., "stress level: 75")

### What We DON'T Collect
- ❌ Keystroke content (only typing velocity)
- ❌ Screenshots (processed in RAM, deleted immediately)
- ❌ Audio recordings (only breathing rate extracted)
- ❌ Video recordings (only posture metrics extracted)
- ❌ Any data sent to cloud services

### What We DO Log (Locally)
- ✅ Stress level scores (0-100)
- ✅ Intervention triggers and responses
- ✅ Session duration and flow time
- ✅ Settings preferences

## Secure Development

All pull requests are reviewed for:
1. **No unauthorized network calls** - Any attempt to add telemetry or cloud features will be rejected
2. **No content logging** - Actual user input/screen content must never be stored
3. **Minimal permissions** - Only request what's absolutely necessary

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Response Timeline

- **Critical issues:** Patch within 24 hours
- **High severity:** Patch within 7 days
- **Medium/Low:** Addressed in next release
