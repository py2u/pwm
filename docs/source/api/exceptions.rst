Exceptions Module
=================

.. automodule:: pwm.core.exceptions
   :members:
   :show-inheritance:

Exception Hierarchy
-------------------

.. code-block:: text

   PwmError (base)
   ├── VaultNotFoundError        # Vault file doesn't exist
   ├── VaultAlreadyExistsError   # init when vault already exists
   ├── WrongPasswordError        # Master password incorrect
   ├── VaultLockedError          # Vault is locked (auto-lock/manual)
   ├── LockoutError              # Too many failed attempts
   ├── AccountNotFoundError      # Lookup by service name failed
   ├── AccountDuplicateError     # Add with existing service name
   ├── CryptoError               # Wraps cryptography exceptions
   ├── ClipboardError            # Clipboard tool unavailable
   └── ConfigError               # Invalid config key or value

Usage Example
-------------

.. code-block:: python

   from pwm.core.exceptions import (
       WrongPasswordError,
       VaultLockedError,
       AccountNotFoundError,
   )

   try:
       vault.unlock_vault("password")
   except WrongPasswordError as e:
       print(f"Wrong password: {e}")
   except VaultLockedError:
       print("Vault is locked")
