Vault Module
============

The ``vault`` module manages the vault lifecycle: initialization, unlocking,
locking, and all CRUD operations on stored accounts.

.. automodule:: pwm.core.vault
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

Core Functions
--------------

.. autofunction:: pwm.core.vault.init_vault
.. autofunction:: pwm.core.vault.unlock_vault
.. autofunction:: pwm.core.vault.lock_vault
.. autofunction:: pwm.core.vault.ensure_unlocked
.. autofunction:: pwm.core.vault.is_unlocked
.. autofunction:: pwm.core.vault.touch_activity

CRUD Operations
---------------

.. autofunction:: pwm.core.vault.get_accounts
.. autofunction:: pwm.core.vault.find_account
.. autofunction:: pwm.core.vault.add_account
.. autofunction:: pwm.core.vault.update_account
.. autofunction:: pwm.core.vault.delete_account
.. autofunction:: pwm.core.vault.search_accounts

Import / Export
---------------

.. autofunction:: pwm.core.vault.export_vault
.. autofunction:: pwm.core.vault.import_vault

Configuration
-------------

.. autofunction:: pwm.core.vault.get_config
.. autofunction:: pwm.core.vault.set_config

Password Management
-------------------

.. autofunction:: pwm.core.vault.change_master_password

Usage Example
-------------

.. code-block:: python

   from pwm.core import vault
   from pwm.core.models import Account

   # Initialize a new vault
   vault.init_vault("my_master_password")

   # Add accounts
   vault.add_account(Account(
       service="github.com",
       username="me@email.com",
       password="s3cr3t",
       category="dev"
   ))

   # List accounts
   for acc in vault.get_accounts():
       print(f"{acc.service}: {acc.username}")

   # Lock the vault (clears in-memory session)
   vault.lock_vault()

   # Unlock for later use
   vault.unlock_vault("my_master_password")

.. note::

   The vault module maintains **module-level session state**. Only one vault
   can be active at a time per Python process. The session holds the
   decryption key and plaintext data in memory.
