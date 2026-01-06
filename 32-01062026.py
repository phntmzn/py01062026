#!/usr/bin/env python3
import argparse
import ctypes
import ctypes.wintypes as wt
import sys
import time

advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

# Hives
HIVES = {
    "HKLM": 0x80000002,
    "HKEY_LOCAL_MACHINE": 0x80000002,
    "HKCU": 0x80000001,
    "HKEY_CURRENT_USER": 0x80000001,
    "HKCR": 0x80000000,
    "HKEY_CLASSES_ROOT": 0x80000000,
    "HKU": 0x80000003,
    "HKEY_USERS": 0x80000003,
    "HKCC": 0x80000005,
    "HKEY_CURRENT_CONFIG": 0x80000005,
}

# Notify filters
REG_NOTIFY_CHANGE_NAME = 0x00000001
REG_NOTIFY_CHANGE_ATTRIBUTES = 0x00000002
REG_NOTIFY_CHANGE_LAST_SET = 0x00000004
REG_NOTIFY_CHANGE_SECURITY = 0x00000008

KEY_READ = 0x20019

advapi32.RegOpenKeyExW.argtypes = [wt.HANDLE, wt.LPCWSTR, wt.DWORD, wt.REGSAM, ctypes.POINTER(wt.HANDLE)]
advapi32.RegOpenKeyExW.restype = wt.LONG

advapi32.RegNotifyChangeKeyValue.argtypes = [
    wt.HANDLE, wt.BOOL, wt.DWORD, wt.HANDLE, wt.BOOL
]
advapi32.RegNotifyChangeKeyValue.restype = wt.LONG

advapi32.RegCloseKey.argtypes = [wt.HANDLE]
advapi32.RegCloseKey.restype = wt.LONG

kernel32.CreateEventW.argtypes = [ctypes.c_void_p, wt.BOOL, wt.BOOL, wt.LPCWSTR]
kernel32.CreateEventW.restype = wt.HANDLE

kernel32.WaitForSingleObject.argtypes = [wt.HANDLE, wt.DWORD]
kernel32.WaitForSingleObject.restype = wt.DWORD

kernel32.ResetEvent.argtypes = [wt.HANDLE]
kernel32.ResetEvent.restype = wt.BOOL

kernel32.CloseHandle.argtypes = [wt.HANDLE]
kernel32.CloseHandle.restype = wt.BOOL

WAIT_OBJECT_0 = 0x00000000
INFINITE = 0xFFFFFFFF

def die_win(msg: str) -> None:
    err = ctypes.get_last_error()
    raise SystemExit(f"{msg} (winerr={err})")

def parse_path(path: str):
    if "\\" not in path:
        raise SystemExit("Use format like: HKLM\\Software\\Microsoft")
    hive_str, subkey = path.split("\\", 1)
    hive = HIVES.get(hive_str.upper())
    if hive is None:
        raise SystemExit(f"Unknown hive '{hive_str}'. Use HKLM/HKCU/etc.")
    return hive, subkey

def watch_registry(path: str, subtree: bool) -> None:
    hive, subkey = parse_path(path)

    hkey = wt.HANDLE()
    rc = advapi32.RegOpenKeyExW(wt.HANDLE(hive), subkey, 0, KEY_READ, ctypes.byref(hkey))
    if rc != 0:
        raise SystemExit(f"RegOpenKeyExW failed rc={rc} for {path}")

    event = kernel32.CreateEventW(None, True, False, None)
    if not event:
        advapi32.RegCloseKey(hkey)
        die_win("CreateEventW failed")

    notify_filter = (REG_NOTIFY_CHANGE_NAME |
                     REG_NOTIFY_CHANGE_ATTRIBUTES |
                     REG_NOTIFY_CHANGE_LAST_SET |
                     REG_NOTIFY_CHANGE_SECURITY)

    print(f"[+] Watching registry changes: {path} (subtree={subtree})")
    print("[+] Press Ctrl+C to stop.")

    try:
        while True:
            # Arm notification
            rc = advapi32.RegNotifyChangeKeyValue(hkey, bool(subtree), notify_filter, event, True)
            if rc != 0:
                raise SystemExit(f"RegNotifyChangeKeyValue failed rc={rc}")

            # Wait for event
            w = kernel32.WaitForSingleObject(event, INFINITE)
            if w != WAIT_OBJECT_0:
                die_win("WaitForSingleObject failed")

            # Reset and report
            kernel32.ResetEvent(event)
            print(f"[!] Change detected at {time.strftime('%Y-%m-%d %H:%M:%S')} in {path}")

    except KeyboardInterrupt:
        print("\n[+] Stopped.")
    finally:
        kernel32.CloseHandle(event)
        advapi32.RegCloseKey(hkey)

def main():
    ap = argparse.ArgumentParser(description="User-mode registry change watcher (defensive).")
    ap.add_argument("key", help=r"Registry key, e.g. HKLM\Software\Microsoft")
    ap.add_argument("--subtree", action="store_true", help="Watch entire subtree under the key")
    args = ap.parse_args()
    watch_registry(args.key, args.subtree)

if __name__ == "__main__":
    if sys.platform != "win32":
        raise SystemExit("This script must be run on Windows.")
    main()
