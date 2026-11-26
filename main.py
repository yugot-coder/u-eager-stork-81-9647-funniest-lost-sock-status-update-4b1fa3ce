#!/usr/bin/env python3
"""Funniest Lost Sock Status Update.

Writes one status update, in the voice of a lost sock, to
``$MAKEFUN_OUTPUT_DIR/entry.txt`` (default ``/output``).

Standard library only. Fully deterministic: the entry is a constant, and
``--check`` re-reads the written file and verifies its sha256, its length
(1..120 characters), that it is a single line, and that it is not only
whitespace.
"""

import hashlib
import os
import sys

LINE = "The cat dragged me under the bed in March. We are married now. Please tell my partner I have moved on."
EXPECTED_SHA256 = "b244d2846aba28a6a3c9ca1640bfb9cb76717b89a35727a4594be4e2b1624581"


def output_path():
    """Path of entry.txt, honouring $MAKEFUN_OUTPUT_DIR (default /output)."""
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    return os.path.join(out_dir, "entry.txt")


def check(path):
    """Verify an existing entry.txt. Returns (errors, text or None)."""
    errors = []
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError as exc:
        return ["cannot read %s: %s" % (path, exc)], None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return ["entry.txt is not valid UTF-8: %s" % exc], None
    if hashlib.sha256(raw).hexdigest() != EXPECTED_SHA256:
        errors.append("sha256 mismatch")
    if not 1 <= len(text) <= 120:
        errors.append("length %d out of range 1..120" % len(text))
    if "\n" in text or "\r" in text:
        errors.append("entry is not a single line")
    if text != text.rstrip("\n"):
        errors.append("entry has a trailing newline")
    if not text.strip():
        errors.append("entry is only whitespace")
    return errors, text


def main(argv):
    if "--check" in argv:
        path = output_path()
        errors, text = check(path)
        if errors:
            for err in errors:
                print("FAIL: %s" % err, file=sys.stderr)
            return 1
        # Report the length of the file actually read, not the constant.
        print("OK: %s (%d chars, sha256 %s)" % (path, len(text), EXPECTED_SHA256))
        return 0

    path = output_path()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    # No trailing newline: the entry is exactly one line.
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(LINE)
    print(LINE)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
