"""OpenSati entry point."""

from opensati.app import OpenSatiApp


def main() -> None:
    """Run OpenSati application."""
    app = OpenSatiApp()
    app.run()


if __name__ == "__main__":
    main()
