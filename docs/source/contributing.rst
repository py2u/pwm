Contributing
============

We welcome contributions! Here's how to get started.

Development Setup
-----------------

.. code-block:: bash

   git clone https://github.com/user/pwm.git
   cd pwm
   pip install -e .
   pip install pytest sphinx sphinx-rtd-theme

Running Tests
-------------

.. code-block:: bash

   # Run all tests
   python -m pytest pwm/test/ -v

   # Run specific test file
   python -m pytest pwm/test/test_crypto.py -v

   # Run with coverage
   pip install pytest-cov
   python -m pytest pwm/test/ --cov=pwm -v

Code Style
----------

- Follow :pep:`8` conventions
- Use type hints where practical
- Keep functions focused and small
- Write docstrings in Google style (processed by Napoleon)

Building Documentation
----------------------

.. code-block:: bash

   cd docs
   pip install sphinx sphinx-rtd-theme
   make html

   # Open in browser (Windows)
   start _build/html/index.html

   # Open in browser (macOS)
   open _build/html/index.html

Project Structure
-----------------

.. code-block:: text

   pwm/
   ├── core/           # Cryptographic primitives, vault, models
   ├── cli/            # CLI argument parsing and handlers
   ├── utils/          # Password generation, clipboard
   ├── config/         # Configuration (reserved for future)
   └── test/           # Test suite

Pull Request Process
--------------------

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

Security Issues
---------------

If you discover a security vulnerability, please do **not** open a public
issue. Instead, email the maintainers directly. We follow responsible
disclosure practices.
