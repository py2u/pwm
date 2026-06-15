API Reference
=============

PWM can be used programmatically as a Python library. All public APIs are
accessible through the ``pwm`` package and its subpackages.

.. toctree::
   :maxdepth: 2

   crypto
   vault
   models
   generator
   exceptions
   constants

Package Overview
----------------

.. code-block:: python

   # Core: cryptographic operations and vault management
   from pwm.core import vault
   from pwm.core.crypto import encrypt, decrypt, derive_key

   # Models: data classes
   from pwm.core.models import Account, VaultConfig, VaultFile

   # Exceptions: error types
   from pwm.core.exceptions import WrongPasswordError, VaultLockedError

   # Utilities: password generation and clipboard
   from pwm.utils import generate_password, password_strength
   from pwm.utils import copy_to_clipboard, schedule_clipboard_clear

Subpackages
-----------

.. list-table::
   :header-rows: 1

   * - Subpackage
     - Description
   * - ``pwm.core``
     - Cryptographic primitives, vault lifecycle, data models, exceptions
   * - ``pwm.cli``
     - Command-line interface (argument parsing and command handlers)
   * - ``pwm.utils``
     - Password generation and clipboard utilities
   * - ``pwm.config``
     - Configuration management (reserved for future expansion)
   * - ``pwm.test``
     - Test suite
