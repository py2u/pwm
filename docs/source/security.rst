Security
========

This document describes the security architecture of PWM, its threat model,
and cryptographic guarantees.

Encryption Architecture
-----------------------

PWM uses a **defense-in-depth** approach with multiple layers of protection:

.. code-block:: text

   Master Password
        │
        ▼
   ┌─────────────────────────────────┐
   │  PBKDF2-SHA256                  │
   │  600,000 iterations             │
   │  Random 32-byte salt            │
   └─────────────────────────────────┘
        │
        ▼  256-bit key
   ┌─────────────────────────────────┐
   │  AES-256-GCM                    │
   │  Fresh random 12-byte nonce     │
   │  per encryption operation       │
   └─────────────────────────────────┘
        │
        ▼
   Encrypted Vault File (JSON)
   - salt (base64)
   - encrypted_data (base64)

Key Derivation
~~~~~~~~~~~~~~

- **Algorithm**: PBKDF2-SHA256
- **Iterations**: 600,000 (OWASP 2023 recommendation)
- **Salt**: 32 cryptographically random bytes (``secrets.token_bytes``)
- **Output**: 256-bit AES key

The salt is generated once at vault creation and stored in the vault file.
It prevents precomputation attacks (rainbow tables).

Encryption
~~~~~~~~~~

- **Algorithm**: AES-256-GCM (Galois/Counter Mode)
- **Nonce**: 12 random bytes per encryption (``os.urandom``)
- **Authentication tag**: 16 bytes (automatically verified on decryption)

AES-GCM is **authenticated encryption** — any modification to the ciphertext
causes decryption to fail with an ``InvalidTag`` error. This means:

* Tampered vault files are detected and rejected
* An attacker cannot modify encrypted data without knowing the key
* There are no padding oracle attacks (GCM is not vulnerable)

Nonce Safety
~~~~~~~~~~~~

Every time the vault is saved (after any mutation), a **fresh random nonce**
is generated. With a 96-bit nonce, the probability of collision across
millions of encryption operations is negligible.

.. note::

   PWM never reuses a nonce with the same key. The nonce is prepended to
   the ciphertext and stored in the vault file.

Threat Model
------------

What PWM protects against
~~~~~~~~~~~~~~~~~~~~~~~~~

* **Passive disk access**: An attacker with read access to your vault file
  cannot decrypt it without the master password.
* **Vault tampering**: Any modification to the encrypted vault file is
  detected and rejected (GCM authentication).
* **Online brute force**: Rate limiting and lockout prevent rapid password
  guessing. Lockout state persists in the vault file across process restarts.
* **Clipboard sniffing**: Passwords are automatically cleared from clipboard
  after a configurable timeout.
* **Memory inspection** (partial): Key material is zeroed on vault lock.
  Plaintext passwords are held in memory only as long as needed.

What PWM does NOT protect against
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Keyloggers**: If your system is compromised with a keylogger, the master
  password can be captured.
* **Memory dumps**: While the vault is unlocked, the decryption key and
  plaintext data reside in process memory.
* **Untrusted systems**: Do not use PWM on a system you don't trust.
* **Forgotten master password**: There is no recovery mechanism — the
  encryption is designed to be irreversible without the key.

Brute-Force Protection
----------------------

Configurable rate limiting with persistent lockout:

.. code-block:: text

   Attempt 1: Wrong password → 4 attempts remaining
   Attempt 2: Wrong password → 3 attempts remaining
   ...
   Attempt 5: Wrong password → VAULT LOCKED for 10 minutes

The failed attempt counter and lockout timestamp are stored **in the vault
file itself**, so they survive:

- Process restarts
- Terminal close/reopen
- System reboot

An attacker with file write access could reset the counter by editing the
vault JSON, but this would corrupt the encrypted data (detected by GCM).

Auto-Lock
---------

After a configurable period of inactivity (default: 5 minutes), the vault
automatically locks:

1. Plaintext data is re-encrypted and written to disk
2. The AES key is zeroed in memory
3. The plaintext account list is cleared

The next command prompts for the master password again.

Backup Security
---------------

.. important::

   **Exported backups are encrypted.** The ``pwm export`` command copies the
   already-encrypted vault file — no decryption occurs. Your data never
   touches disk in plain text form.

Importing a backup requires the **same master password** as the exported
vault. The import process:

1. Decrypts the imported vault with your current session key
2. If decryption fails → the backup was created with a different password
3. If decryption succeeds → merges or replaces accounts

Best Practices
--------------

1. **Master password**: Use 12+ characters with mixed types. Consider a
   passphrase (e.g., "correct-horse-battery-staple").
2. **Backups**: Export backups regularly and store them in a separate
   location (encrypted USB drive, secure cloud storage).
3. **System security**: Keep your OS and Python packages updated.
4. **Lock when away**: Run ``pwm lock`` (or use auto-lock) before leaving
   your computer.
5. **Don't share**: Never share your vault file or master password.
6. **Unique passwords**: Use the built-in password generator to create
   unique, strong passwords for every service.
