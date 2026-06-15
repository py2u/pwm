Installation
============

Requirements
------------

PWM requires **Python 3.8** or later. It has a single external dependency:

* `cryptography <https://cryptography.io/>`_ (>= 41.0.0) — provides AES-GCM and PBKDF2 primitives

The ``cryptography`` library is the gold standard for cryptographic operations
in Python and is maintained by the Python Cryptographic Authority.

Install from Source
-------------------

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/user/pwm.git
   cd pwm

   # Install the cryptography dependency
   pip install cryptography

   # Install PWM in development mode
   pip install -e .

After installation, the ``pwm`` command is available in your terminal:

.. code-block:: bash

   pwm --help

Platform-Specific Notes
-----------------------

Windows
^^^^^^^

PWM uses the built-in ``clip.exe`` for clipboard operations — no additional
setup required. ``powershell.exe`` is used for clipboard reading (verification
before auto-clear).

macOS
^^^^^

PWM uses ``pbcopy`` and ``pbpaste`` (built-in) for clipboard operations.

Linux
^^^^^

For clipboard support, install one of:

.. code-block:: bash

   # X11
   sudo apt install xclip

   # Wayland
   sudo apt install wl-clipboard

Without a clipboard tool, PWM will warn but still function — you just won't
get automatic clipboard copy/clear.

Development Install
-------------------

For development, install with extra tools:

.. code-block:: bash

   pip install -e .
   pip install pytest sphinx sphinx-rtd-theme

   # Run tests
   python -m pytest pwm/test/ -v

   # Build docs
   cd docs
   make html

Upgrading
---------

To upgrade to the latest version:

.. code-block:: bash

   git pull
   pip install -e . --force-reinstall --no-deps
