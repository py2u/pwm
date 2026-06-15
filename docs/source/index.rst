.. PWM documentation master file

=============================================
PWM — Secure CLI Password Manager |version|
=============================================

**PWM** is a secure, local command-line password manager built with Python.
It encrypts your credentials using **AES-256-GCM** authenticated encryption
and protects them with a master password derived via **PBKDF2-SHA256**.

.. raw:: html

   <div class="pwm-features">
     <div class="pwm-feature-card">
       <h3>🔐 Military-Grade Encryption</h3>
       <p>AES-256-GCM authenticated encryption with PBKDF2-SHA256 key derivation (600,000 iterations). Data is encrypted at rest and never stored in plain text.</p>
     </div>
     <div class="pwm-feature-card">
       <h3>⌨️ Command-Line First</h3>
       <p>Fast, scriptable, and keyboard-driven. No GUI bloat. Manage your passwords directly from the terminal.</p>
     </div>
     <div class="pwm-feature-card">
       <h3>🔑 Smart Password Generator</h3>
       <p>Generate cryptographically random passwords with configurable length, character sets, and easy-read mode.</p>
     </div>
     <div class="pwm-feature-card">
       <h3>🛡️ Brute-Force Protection</h3>
       <p>Configurable rate limiting with automatic lockout after failed attempts. Lockout state persists across process restarts.</p>
     </div>
     <div class="pwm-feature-card">
       <h3>⏱️ Auto-Lock & Clipboard Clear</h3>
       <p>Vault auto-locks after inactivity. Copied passwords are automatically cleared from clipboard after a configurable timeout.</p>
     </div>
     <div class="pwm-feature-card">
       <h3>📦 Encrypted Backups</h3>
       <p>Export and import encrypted vault backups. Backups are never stored in plain text — your data stays protected.</p>
     </div>
   </div>

----

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   cli_reference
   security

.. toctree::
   :maxdepth: 3
   :caption: API Reference

   api/index

.. toctree::
   :maxdepth: 1
   :caption: Development

   changelog
   contributing

----

Quick Install
--------------

.. code-block:: bash

   pip install cryptography
   git clone https://github.com/user/pwm.git
   cd pwm
   pip install -e .

Then initialize your vault:

.. code-block:: bash

   pwm init

----

Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
