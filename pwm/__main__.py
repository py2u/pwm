"""Entry point for the PWM password manager CLI."""

import sys

from pwm.core.exceptions import PwmError


def main() -> None:
    """Main entry point — parse args and dispatch to the appropriate command handler."""

    # Check for essential dependency
    try:
        import cryptography  # noqa: F401
    except ImportError:
        print("ERROR: The 'cryptography' package is required.")
        print("Install it with: pip install cryptography")
        sys.exit(1)

    from pwm.cli.commands import build_parser

    parser = build_parser()
    args = parser.parse_args()

    if hasattr(args, "func"):
        try:
            args.func(args)
        except PwmError as e:
            print(f"Error: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nCancelled.")
            sys.exit(0)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
