import subprocess
import tempfile
import os
import textwrap
import plistlib
from pathlib import Path

APP_NAME = "CLTDemo"
BUNDLE_ID = "com.example.cltdemo"
APP_PATH = f"/Applications/{APP_NAME}.app"
AGENT_LABEL = BUNDLE_ID
AGENT_PATH = Path.home() / "Library/LaunchAgents" / f"{AGENT_LABEL}.plist"

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

def run(cmd):
    subprocess.run(cmd, check=True)

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

run([
    "codesign",
    "--force",
    "--deep",
    "--options", "runtime",
    "--sign", "-",
    f"dist/{APP_NAME}.app"
])

if os.path.exists(APP_PATH):
    run(["rm", "-rf", APP_PATH])

run(["mv", f"dist/{APP_NAME}.app", "/Applications/"])

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

print("Build complete")
print("App installed at:", APP_PATH)
print("LaunchAgent installed at:", AGENT_PATH)
