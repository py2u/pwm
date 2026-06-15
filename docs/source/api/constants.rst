Constants Module
================

.. automodule:: pwm.core.constants
   :members:
   :undoc-members:

Usage Example
-------------

.. code-block:: python

   from pwm.core.constants import (
       VAULT_DIR,
       VAULT_FILE,
       PBKDF2_ITERATIONS,
       SALT_LENGTH,
       KEY_LENGTH,
       DEFAULT_PASSWORD_LENGTH,
   )

   print(f"Vault directory: {VAULT_DIR}")
   print(f"PBKDF2 iterations: {PBKDF2_ITERATIONS}")
   print(f"AES key size: {KEY_LENGTH * 8} bits")
