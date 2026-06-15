Crypto Module
=============

.. automodule:: pwm.core.crypto
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

Overview
--------

The ``crypto`` module provides all cryptographic primitives used by PWM.
It wraps the `cryptography <https://cryptography.io/>`_ library's low-level
hazmat primitives.

Functions
---------

.. autofunction:: pwm.core.crypto.generate_salt
.. autofunction:: pwm.core.crypto.derive_key
.. autofunction:: pwm.core.crypto.encrypt
.. autofunction:: pwm.core.crypto.decrypt
.. autofunction:: pwm.core.crypto.verify_key
.. autofunction:: pwm.core.crypto.encode_blob
.. autofunction:: pwm.core.crypto.decode_blob
.. autofunction:: pwm.core.crypto.secure_erase

Usage Example
-------------

.. code-block:: python

   from pwm.core.crypto import generate_salt, derive_key, encrypt, decrypt

   # Generate a salt and derive a key
   salt = generate_salt()
   key = derive_key("my_master_password", salt)

   # Encrypt data
   plaintext = b"Sensitive data here"
   encrypted = encrypt(key, plaintext)

   # Decrypt data
   decrypted = decrypt(key, encrypted)
   assert decrypted == plaintext

   # Wrong password raises WrongPasswordError
   wrong_key = derive_key("wrong_password", salt)
   try:
       decrypt(wrong_key, encrypted)
   except WrongPasswordError:
       print("Authentication failed — wrong password or tampered data")
