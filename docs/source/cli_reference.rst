CLI Reference
=============

Global Options
--------------

.. option:: --vault, -V PATH

   Path to the vault file. Overrides the default ``~/.pwm/vault.json``.
   Can be used with any subcommand.

.. option:: --help, -h

   Show help message and exit.

Commands
--------

pwm init
~~~~~~~~

Initialize a new password vault.

.. code-block:: bash

   pwm init [--vault PATH]

Prompts you to create a master password (with confirmation). The vault file
is created at the specified path (default: ``~/.pwm/vault.json``).

---

pwm add
~~~~~~~

Add a new account to the vault.

.. code-block:: bash

   pwm add [options]

Options:
   * ``--service, -s SERVICE`` — Service/website name (required)
   * ``--username, -u USERNAME`` — Username or email (required)
   * ``--password, -p PASSWORD`` — Password (omit for interactive prompt)
   * ``--generate, -g`` — Auto-generate a random password
   * ``--easy, -e`` — Use easy-read mode for generated password
   * ``--notes, -n NOTES`` — Optional notes
   * ``--category, -c CATEGORY`` — Optional category/tag

If no options are provided, PWM enters **interactive mode** and prompts for each field.

**Examples:**

.. code-block:: bash

   # Interactive
   pwm add

   # With auto-generated password
   pwm add -s github.com -u me@email.com -g

   # With explicit password and category
   pwm add -s aws.amazon.com -u admin -p "s3cr3t!" -c "Work"

---

pwm list
~~~~~~~~

List all accounts in a formatted table.

.. code-block:: bash

   pwm list [--category CATEGORY] [--show-passwords]

Options:
   * ``--category, -c CATEGORY`` — Filter by category (exact match)
   * ``--show-passwords, -P`` — Show passwords in plain text (default: ``********``)

**Example output:**

.. code-block:: text

     Service          Username            Password         Category   Updated
   --------------------------------------------------------------------------------
     github.com       me@email.com        ********         dev        2026-06-15
     google.com       you@email.com       ********         work       2026-06-14

---

pwm show
~~~~~~~~

Show full details for a single account and copy its password to the clipboard.

.. code-block:: bash

   pwm show SERVICE [--no-copy]

Options:
   * ``--no-copy, -C`` — Do not copy password to clipboard

The password is automatically copied to clipboard and cleared after
the configured timeout (default: 30 seconds).

---

pwm edit
~~~~~~~~

Edit fields on an existing account.

.. code-block:: bash

   pwm edit SERVICE [options]

Options:
   * ``--service, -s NEW_NAME`` — Rename the service
   * ``--username, -u USERNAME`` — New username
   * ``--password, -p PASSWORD`` — New password
   * ``--generate, -g`` — Generate a new random password
   * ``--easy, -e`` — Easy-read mode for generated password
   * ``--notes, -n NOTES`` — New notes (use ``""`` to clear)
   * ``--category, -c CATEGORY`` — New category

**Examples:**

.. code-block:: bash

   pwm edit github.com -u newemail@test.com
   pwm edit github.com -g -c "dev"

---

pwm delete
~~~~~~~~~~

Delete an account.

.. code-block:: bash

   pwm delete SERVICE [--force]

Options:
   * ``--force, -f`` — Skip confirmation prompt

---

pwm search
~~~~~~~~~~

Search accounts by service name or category.

.. code-block:: bash

   pwm search QUERY [--category-only] [--show-passwords]

Options:
   * ``--category-only`` — Only search in category field
   * ``--show-passwords, -P`` — Show passwords in plain text

Search is **case-insensitive** and matches **substrings**.

---

pwm gen
~~~~~~~

Generate a random password.

.. code-block:: bash

   pwm gen [options]

Options:
   * ``--length, -l LENGTH`` — Password length (default: 20)
   * ``--no-upper`` — Exclude uppercase letters
   * ``--no-lower`` — Exclude lowercase letters
   * ``--no-digits`` — Exclude digits
   * ``--no-symbols`` — Exclude symbols
   * ``--easy, -e`` — Exclude ambiguous characters (O/0, l/1, B/8, S/5)
   * ``--copy, -c`` — Copy generated password to clipboard

Passwords use ``secrets.SystemRandom()`` for cryptographically secure
random generation.

---

pwm export
~~~~~~~~~~

Export an encrypted backup of the vault.

.. code-block:: bash

   pwm export PATH

The export is a copy of the **already-encrypted** vault file. No decryption
is performed — your data never touches disk in plain text.

---

pwm import
~~~~~~~~~~

Import accounts from an encrypted backup.

.. code-block:: bash

   pwm import PATH [--replace]

Options:
   * ``--replace, -r`` — Replace all current accounts (default: merge, skip duplicates)

.. warning::

   Both vaults must use the **same master password**. The import decrypts
   the backup with your current session key to validate compatibility.

---

pwm lock
~~~~~~~~

Manually lock the vault, clearing the in-memory session.

.. code-block:: bash

   pwm lock

The next command that requires vault access will prompt for the master password.

---

pwm config
~~~~~~~~~~

View or change vault configuration.

.. code-block:: bash

   pwm config                    # View all settings
   pwm config --set KEY VALUE    # Change a setting

Configurable settings:

.. list-table::
   :header-rows: 1

   * - Key
     - Default
     - Description
   * - ``auto_lock_timeout``
     - 300
     - Seconds of inactivity before auto-lock (0 = disabled)
   * - ``clipboard_clear_timeout``
     - 30
     - Seconds before clipboard is cleared (0 = disabled)
   * - ``max_failed_attempts``
     - 5
     - Wrong password attempts before lockout
   * - ``lockout_duration``
     - 600
     - Seconds of lockout after too many failures

---

pwm changepw
~~~~~~~~~~~~

Change the master password.

.. code-block:: bash

   pwm changepw

Prompts for a new master password (with confirmation). All data is
re-encrypted with a new key derived from the new password.
