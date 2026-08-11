"""Diagnostic: log every directory the official secrets scan walks.

Used only to investigate the CI-only behaviour where check-package-secrets
reports paths under .scripts even though -d points at the unpacked plugin.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".scripts").resolve()))
from toolkit.checks import secrets

orig_walk = os.walk


def logged_walk(top, *args, **kwargs):
    for entry in orig_walk(top, *args, **kwargs):
        print("WALK>", entry[0], flush=True)
        yield entry


os.walk = logged_walk
target = Path(os.environ["PLUGIN_PATH"])
print("TARGET>", target, "is_dir:", target.is_dir(), flush=True)
errors, warnings = secrets.scan_package(target)
print("ERRORS>", len(errors), flush=True)
for error in errors[:8]:
    print("E>", error, flush=True)
