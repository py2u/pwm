# Changelog

All notable changes to PWM will be documented in this file.

## [1.0.0] — 2026-06-15

### Added
- AES-256-GCM authenticated encryption for all stored data
- PBKDF2-SHA256 key derivation with 600,000 iterations
- Secure master password management with init/changepw commands
- CRUD operations: add, list, show, edit, delete accounts
- Search accounts by service name and category
- Random password generator with configurable character sets
- Easy-mode password generation (no ambiguous characters)
- Cross-platform clipboard copy with auto-clear timer
- Auto-lock after configurable inactivity timeout
- Rate limiting on failed password attempts with lockout
- Encrypted backup export and import (merge/replace modes)
- Vault configuration management
- Modular package structure: core, cli, utils, config, test
