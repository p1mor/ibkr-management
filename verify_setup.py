#!/usr/bin/env python3
"""Backward-compatible entrypoint for setup verification."""

from scripts.verify_setup import main


if __name__ == "__main__":
    raise SystemExit(main())
