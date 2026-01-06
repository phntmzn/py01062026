#!/usr/bin/env python3

import subprocess
import tempfile
import os
import textwrap
import plistlib
import sys
from pathlib import Path

# -----------------------------
# App / LaunchAgent config
# -----------------------------
APP_NAME = "CLTDemo"
BUNDLE_ID = "com.example.cltdemo"
APP_PATH = f"/Applications/{APP_NAME}.app"
AGENT_LABEL = BUNDLE_ID
AGENT_PATH = Path.home() / "Library/LaunchAgents" / f"{AGENT_LABEL}.plist"

# -----------------------------
# Kext config
# -----------------------------
KEXT_PATH = Path("/Library/Extensions/MyDriver.kext")

# -----------------------------
# App source code
# -----------------------------
CODE = textwrap.dedent("""
    import numpy as np
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt

    print("hello world")

    samples = [np.mean(np.random.uniform(0, 1, 30)) for _ in range(1000)]
    plt.hist(samples, bins=30)
    plt.title("Central Limit Theorem Demo")
    plt.show()
""")

# -----------------------------
# Helpers
# -----------------------------
def run(cmd):
    subprocess.run(cmd, check=True)

def require_root():
    if os.geteuid() != 0:
        print("This script must be run as root (use sudo).")
        sys.exit(1)

def validate_kext():
    if not KEXT_PATH.exists():
        print(f"Kext not found: {KEXT_PATH}")
        sys.exit(1)

def load_kext():
    validate_kext()
    run([
        "kmutil",
        "load",
        "-p", str(KEXT_PATH)
    ])
    print("Kext loaded")

def unload_kext():
    validate_kext()
    run([
        "kmutil",
        "unload",
        "-p", str(KEXT_PATH)
    ])
    print("Kext unloaded")

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    require_root()

    # 1. Build the app
    with tempfile.TemporaryDirectory() as d:
        script_path = os.path.join(d, "clt_demo.py")

        with open(script_path, "w") as f:
            f.write(CODE)

        run([
            "pyinstaller",
            "--windowed",
            "--onefile",
            "--name", APP_NAME,
            "--hidden-import", "numpy",
            "--hidden-import", "matplotlib",
            script_path,
        ])

    # 2. Code sign the app (ad-hoc)
    run([
        "codesign",
        "--force",
        "--deep",
        "--options", "runtime",
        "--sign", "-",
        f"dist/{APP_NAME}.app"
    ])

    # 3. Install app
    if os.path.exists(APP_PATH):
        run(["rm", "-rf", APP_PATH])

    run(["mv", f"dist/{APP_NAME}.app", "/Applications/"])

    # 4. Create LaunchAgent
    AGENT_PATH.parent.mkdir(parents=True, exist_ok=True)

    plist = {
        "Label": AGENT_LABEL,
        "ProgramArguments": [
            f"{APP_PATH}/Contents/MacOS/{APP_NAME}"
        ],
        "RunAtLoad": True,
        "KeepAlive": False
    }

    with open(AGENT_PATH, "wb") as f:
        plistlib.dump(plist, f)

    run(["launchctl", "unload", str(AGENT_PATH)])
    run(["launchctl", "load", str(AGENT_PATH)])

    # 5. Load kernel extension
    load_kext()

    print("Build complete")
    print("App installed at:", APP_PATH)
    print("LaunchAgent installed at:", AGENT_PATH)
    print("Kext path:", KEXT_PATH)
