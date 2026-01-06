#!/usr/bin/env python3
import ctypes
import ctypes.wintypes as wt
import sys

psapi = ctypes.WinDLL("psapi", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010

LIST_MODULES_ALL = 0x03

kernel32.OpenProcess.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
kernel32.OpenProcess.restype = wt.HANDLE

kernel32.CloseHandle.argtypes = [wt.HANDLE]
kernel32.CloseHandle.restype = wt.BOOL

psapi.EnumProcessModulesEx.argtypes = [
    wt.HANDLE,
    ctypes.POINTER(wt.HMODULE),
    wt.DWORD,
    ctypes.POINTER(wt.DWORD),
    wt.DWORD,
]
psapi.EnumProcessModulesEx.restype = wt.BOOL

psapi.GetModuleFileNameExW.argtypes = [wt.HANDLE, wt.HMODULE, wt.LPWSTR, wt.DWORD]
psapi.GetModuleFileNameExW.restype = wt.DWORD

def winerr(msg: str) -> RuntimeError:
    return RuntimeError(f"{msg} (winerr={ctypes.get_last_error()})")

def list_loaded_modules(pid: int) -> list[str]:
    hproc = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not hproc:
        raise winerr(f"OpenProcess failed for PID {pid}")

    try:
        needed = wt.DWORD(0)
        # start with room for 1024 modules; grow if needed
        size = 1024
        while True:
            arr = (wt.HMODULE * size)()
            cb = ctypes.sizeof(arr)
            ok = psapi.EnumProcessModulesEx(hproc, arr, cb, ctypes.byref(needed), LIST_MODULES_ALL)
            if not ok:
                raise winerr("EnumProcessModulesEx failed")
            if needed.value <= cb:
                count = needed.value // ctypes.sizeof(wt.HMODULE)
                modules = arr[:count]
                break
            size *= 2

        paths = []
        buf = ctypes.create_unicode_buffer(32768)
        for m in modules:
            n = psapi.GetModuleFileNameExW(hproc, m, buf, len(buf))
            if n:
                paths.append(buf.value)
        return paths
    finally:
        kernel32.CloseHandle(hproc)

if __name__ == "__main__":
    if sys.platform != "win32":
        raise SystemExit("Windows only.")
    if len(sys.argv) != 2:
        raise SystemExit(f"Usage: {sys.argv[0]} <pid>")

    pid = int(sys.argv[1])
    for p in list_loaded_modules(pid):
        print(p)
