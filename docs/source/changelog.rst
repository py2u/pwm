Changelog
=========

1.0.0 (2026-06-15)
-------------------

**Initial Release**

* AES-256-GCM authenticated encryption for all stored data
* PBKDF2-SHA256 key derivation with 600,000 iterations
* Secure master password management with ``init`` and ``changepw`` commands
* Full CRUD operations: ``add``, ``list``, ``show``, ``edit``, ``delete``
* Search accounts by service name and category
* Random password generator with configurable character sets
* Easy-mode password generation (no ambiguous characters)
* Cross-platform clipboard copy with auto-clear timer
* Auto-lock after configurable inactivity timeout
* Rate limiting on failed password attempts with persistent lockout
* Encrypted backup export and import (merge or replace modes)
* Vault configuration management
* Modular package structure: ``core``, ``cli``, ``utils``, ``config``, ``test``
* Comprehensive test suite (46 tests, 100% pass rate)
* Sphinx documentation with Read the Docs theme
* CI/CD workflow for Linux, macOS, and Windows (Python 3.8–3.12)
