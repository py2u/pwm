Quick Start
===========

This guide walks you through the essential PWM workflow.

1. Initialize Your Vault
------------------------

Start by creating a new encrypted vault:

.. code-block:: bash

   pwm init

You'll be prompted to create a **master password**. This is the only password
you need to remember — it protects all your stored credentials.

.. tip::

   Choose a strong master password (12+ characters, mix of upper/lower/digits/symbols).
   There is **no password recovery** — if you forget it, your data is unrecoverable.

Your vault is stored at ``~/.pwm/vault.json``. The file is encrypted and safe
to back up.

2. Add Your First Account
-------------------------

.. code-block:: bash

   # Interactive mode (prompts for each field)
   pwm add

   # Command-line mode with auto-generated password
   pwm add -s github.com -u you@email.com -g

   # With a specific password and category
   pwm add -s google.com -u you@email.com -p "your-password" -c "Work"

3. View Your Accounts
---------------------

.. code-block:: bash

   # List all accounts (passwords masked)
   pwm list

   # Show passwords in plain text
   pwm list --show-passwords

   # Filter by category
   pwm list -c Work

4. View Account Details
-----------------------

.. code-block:: bash

   pwm show github.com

This displays the full account details and **automatically copies the password
to your clipboard**. The clipboard is cleared after 30 seconds (configurable).

5. Search for Accounts
----------------------

.. code-block:: bash

   # Search by service name or category
   pwm search github

   # Search only in categories
   pwm search Work --category-only

6. Edit or Delete Accounts
--------------------------

.. code-block:: bash

   # Update username
   pwm edit github.com -u newemail@test.com

   # Generate a new password
   pwm edit github.com -g

   # Delete an account
   pwm delete github.com

7. Generate Passwords
---------------------

.. code-block:: bash

   # Default 20-character password
   pwm gen

   # 32-character password, easy-read mode (no ambiguous chars)
   pwm gen -l 32 --easy

   # Generate and copy to clipboard
   pwm gen -c

8. Back Up Your Vault
---------------------

.. code-block:: bash

   # Export encrypted backup
   pwm export backup.pwmbackup

   # Import (merge with existing accounts)
   pwm import backup.pwmbackup

   # Import (replace all accounts)
   pwm import backup.pwmbackup --replace

.. warning::

   Import only works between vaults with the **same master password**.
   The backup is encrypted — you must know the original master password to restore.

9. Security Operations
----------------------

.. code-block:: bash

   # Manually lock the vault
   pwm lock

   # Change your master password
   pwm changepw

   # Configure auto-lock timeout (10 minutes)
   pwm config --set auto_lock_timeout 600

   # Configure clipboard clear timeout (15 seconds)
   pwm config --set clipboard_clear_timeout 15

Next Steps
----------

- Read the :doc:`cli_reference` for a complete list of commands
- Read the :doc:`security` documentation for details on encryption and threat model
- Browse the :doc:`api/index` for programmatic usage
