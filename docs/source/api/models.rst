Models Module
=============

.. automodule:: pwm.core.models
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

Data Classes
------------

.. autoclass:: pwm.core.models.Account
   :members:
   :undoc-members:

.. autoclass:: pwm.core.models.VaultConfig
   :members:
   :undoc-members:

.. autoclass:: pwm.core.models.VaultFile
   :members:
   :undoc-members:

.. autoclass:: pwm.core.models.PlaintextData
   :members:
   :undoc-members:

Usage Example
-------------

.. code-block:: python

   from pwm.core.models import Account, VaultConfig

   # Create an account
   acc = Account(
       service="example.com",
       username="user@example.com",
       password="my_password",
       notes="Optional notes",
       category="personal"
   )

   # Serialize to dict
   data = acc.to_dict()

   # Deserialize from dict
   acc2 = Account.from_dict(data)

   # Configuration
   config = VaultConfig(
       auto_lock_timeout=600,
       clipboard_clear_timeout=15
   )
