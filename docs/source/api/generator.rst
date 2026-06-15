Generator Module
================

.. automodule:: pwm.utils.generator
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

Functions
---------

.. autofunction:: pwm.utils.generator.generate_password
.. autofunction:: pwm.utils.generator.password_strength
.. autofunction:: pwm.utils.generator.get_character_pool

Usage Example
-------------

.. code-block:: python

   from pwm.utils.generator import generate_password, password_strength

   # Generate a strong password
   pw = generate_password(length=24)
   print(pw)  # e.g., "xK9#mP2@vL5^nQ8!rT3&sW6"

   # Easy-read mode (no ambiguous characters)
   pw = generate_password(length=16, easy_mode=True)

   # Only letters and digits
   pw = generate_password(length=12, symbols=False)

   # Check password strength
   strength = password_strength(pw)
   print(f"Entropy: {strength['entropy_estimate']} bits")
   print(f"Rating: {strength['rating']}")
