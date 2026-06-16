# PWM - Password Manager CLI

A secure local command-line password manager that stores your account credentials with AES-256-GCM encryption.

## Security Features

- **AES-256-GCM authenticated encryption** - protects against tampering
- **PBKDF2-SHA256 key derivation** - 600,000 iterations to resist brute-force attacks
- **Fresh random nonce for every encryption** - prevents nonce reuse
- **Failed-attempt lockout** - defaults to 5 failed attempts, then locks for 10 minutes
- **Automatic vault lock** - defaults to 5 minutes of inactivity
- **Automatic clipboard clearing** - clears copied passwords after 30 seconds by default
- **Encrypted backups** - exported files remain encrypted; plaintext is never written to disk

## Installation

### 1. Install dependencies

```bash
pip install cryptography
```

### 2. Install PWM

```bash
cd pwm
pip install -e .
```

After installation, the `pwm` command is available in your terminal.

## Quick Start

### 1. Initialize a vault

```bash
pwm init
```

Enter and confirm your master password. The vault file is created at `~/.pwm/vault.json`.

### 2. Add an account

```bash
# Interactive mode
pwm add

# Add an account with an auto-generated password
pwm add -s github.com -u myemail@test.com -g

# Add an account with a manually supplied password
pwm add -s google.com -u myemail@test.com -p mypassword123
```

### 3. List accounts

```bash
# List all accounts with masked passwords
pwm list

# Filter by category
pwm list -c Work

# Show plaintext passwords
pwm list --show-passwords
```

### 4. Show account details

```bash
# Show details and copy the password to the clipboard
# The clipboard is cleared after 30 seconds by default.
pwm show github.com
```

### 5. Search accounts

```bash
# Search by service name or category
pwm search github

# Search categories only
pwm search Work --category-only
```

### 6. Edit an account

```bash
# Change the username
pwm edit github.com -u newemail@test.com

# Generate a new password
pwm edit github.com -g

# Change the category
pwm edit github.com -c Development
```

### 7. Delete an account

```bash
pwm delete github.com

# Skip confirmation
pwm delete github.com -f
```

### 8. Generate a random password

```bash
# Default length: 20 characters
pwm gen

# Set a custom length
pwm gen -l 32

# Easy-read mode with ambiguous characters removed
pwm gen -l 16 --easy

# Use only letters and digits
pwm gen --no-symbols

# Generate and copy to clipboard
pwm gen -c
```

### 9. Back up and restore

```bash
# Export an encrypted backup
pwm export backup.pwmbackup

# Import a backup in merge mode, skipping duplicates
pwm import backup.pwmbackup

# Import a backup in replace mode, overwriting all accounts
pwm import backup.pwmbackup --replace
```

**Note:** The current vault and imported backup must use the same master password. PWM will prompt for the master password that belongs to the backup file.

### 10. Security operations

```bash
# Lock the vault manually
pwm lock

# Change the master password
pwm changepw
```

### 11. Configuration

```bash
# Show current configuration
pwm config

# Change the auto-lock timeout in seconds; 0 disables auto-lock
pwm config --set auto_lock_timeout 600

# Change the clipboard clear timeout in seconds; 0 disables auto-clear
pwm config --set clipboard_clear_timeout 15

# Change the maximum failed attempts
pwm config --set max_failed_attempts 3

# Change the lockout duration in seconds
pwm config --set lockout_duration 1800
```

## Configuration Reference

| Key | Default | Description |
| --- | --- | --- |
| `auto_lock_timeout` | 300 | Auto-lock timeout in seconds; `0` disables auto-lock |
| `clipboard_clear_timeout` | 30 | Clipboard clear timeout in seconds; `0` disables auto-clear |
| `max_failed_attempts` | 5 | Maximum failed unlock attempts before lockout |
| `lockout_duration` | 600 | Lockout duration in seconds |

## Data Storage

- **Location:** `~/.pwm/vault.json`
- **Format:** encrypted JSON
- **Encryption:** AES-256-GCM with a fresh random nonce on every write
- **Key:** derived from the master password using PBKDF2-SHA256 with 600,000 iterations

## Security Recommendations

1. Use a strong master password, preferably 12 or more characters with uppercase letters, lowercase letters, digits, and symbols.
2. Export backups regularly and store them in a safe location.
3. Do not share your vault file with anyone.
4. Remember your master password. PWM has no password recovery mechanism.

## Uninstall

```bash
pip uninstall pwm
# The vault file must be removed manually if you no longer need it.
rm ~/.pwm/vault.json
```
