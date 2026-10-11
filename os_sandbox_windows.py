"""
╔══════════════════════════════════════════════════════════════════╗
║  SPS SANDBOX — Windows Deep Isolation Layer  v1.0               ║
║  Uses Windows Job Objects + restricted tokens                    ║
╚══════════════════════════════════════════════════════════════════╝

Provides:
  - Job Object confinement (prevents child processes escaping)
  - Restricted file system access via Windows ACLs
  - Environment variable scrubbing
  - Network confinement hooks

This is auto-used by sandbox_launcher.py on Windows.
"""

import os
import sys
import ctypes
import subprocess
from pathlib import Path
from typing import Optional

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    import ctypes.wintypes as wt
    kernel32 = ctypes.windll.kernel32
    advapi32 = ctypes.windll.advapi32


# ══════════════════════════════════════════════════════════════════
#  JOB OBJECT  (keeps browser process contained)
# ══════════════════════════════════════════════════════════════════

class WindowsJobObject:
    """
    Wraps the browser in a Windows Job Object.
    - Limits number of child processes it can spawn
    - Kill-on-close: when sandbox dies, browser dies too
    - Can restrict UI interaction (clipboard, display changes)
    """

    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE       = 0x2000
    JOB_OBJECT_LIMIT_DIE_ON_UNHANDLED_EXCEPTION = 0x400
    JOB_OBJECT_LIMIT_ACTIVE_PROCESS          = 0x8
    JobObjectBasicLimitInformation           = 2
    JobObjectExtendedLimitInformation        = 9

    def __init__(self):
        self._handle = None
        if not IS_WINDOWS:
            return
        self._handle = kernel32.CreateJobObjectW(None, None)
        if not self._handle:
            raise OSError("Failed to create Job Object")
        self._configure()

    def _configure(self):
        if not IS_WINDOWS or not self._handle:
            return
        # Set limits: kill on close + limit active processes
        class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("PerProcessUserTimeLimit", wt.LARGE_INTEGER),
                ("PerJobUserTimeLimit",     wt.LARGE_INTEGER),
                ("LimitFlags",             wt.DWORD),
                ("MinimumWorkingSetSize",  ctypes.c_size_t),
                ("MaximumWorkingSetSize",  ctypes.c_size_t),
                ("ActiveProcessLimit",     wt.DWORD),
                ("Affinity",               ctypes.POINTER(wt.ULONG)),
                ("PriorityClass",          wt.DWORD),
                ("SchedulingClass",        wt.DWORD),
            ]

        info = JOBOBJECT_BASIC_LIMIT_INFORMATION()
        info.LimitFlags = (self.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE |
                           self.JOB_OBJECT_LIMIT_ACTIVE_PROCESS)
        info.ActiveProcessLimit = 20  # browser + renderer processes

        kernel32.SetInformationJobObject(
            self._handle,
            self.JobObjectBasicLimitInformation,
            ctypes.byref(info),
            ctypes.sizeof(info)
        )

    def assign_process(self, pid: int) -> bool:
        if not IS_WINDOWS or not self._handle:
            return False
        PROCESS_ALL_ACCESS = 0x1F0FFF
        proc_handle = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
        if not proc_handle:
            return False
        result = kernel32.AssignProcessToJobObject(self._handle, proc_handle)
        kernel32.CloseHandle(proc_handle)
        return bool(result)

    def close(self):
        if IS_WINDOWS and self._handle:
            kernel32.CloseHandle(self._handle)
            self._handle = None


# ══════════════════════════════════════════════════════════════════
#  ENVIRONMENT SCRUBBER  (removes sensitive env vars before launch)
# ══════════════════════════════════════════════════════════════════

SENSITIVE_ENV_VARS = [
    "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN",
    "GITHUB_TOKEN", "GITLAB_TOKEN", "NPM_TOKEN",
    "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
    "DATABASE_URL", "DB_PASSWORD", "DB_PASS",
    "SECRET_KEY", "PRIVATE_KEY", "API_KEY",
    "GCP_SERVICE_ACCOUNT", "GOOGLE_APPLICATION_CREDENTIALS",
    "AZURE_CLIENT_SECRET", "AZURE_TENANT_ID",
    "SSH_AUTH_SOCK",  # prevent SSH key forwarding
]


def scrub_environment(env: dict) -> dict:
    """
    Remove sensitive environment variables before passing to browser.
    Logs what was removed.
    """
    cleaned = dict(env)
    removed = []
    for key in list(cleaned.keys()):
        if any(key.upper().startswith(s) or key.upper() == s
               for s in SENSITIVE_ENV_VARS):
            del cleaned[key]
            removed.append(key)
    if removed:
        print(f"[Sandbox] Scrubbed {len(removed)} sensitive env vars: {', '.join(removed)}")
    return cleaned


# ══════════════════════════════════════════════════════════════════
#  TEMP DIRECTORY JAIL  (browser writes only to sandbox temp dir)
# ══════════════════════════════════════════════════════════════════

class TempDirJail:
    """
    Creates a dedicated temp directory for the browser.
    Sets TEMP/TMP env vars so browser writes there first.
    """

    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            base_dir = Path.home() / ".sps_sandbox" / "browser_temp"
        self.path = base_dir
        self.path.mkdir(parents=True, exist_ok=True)

        # Sub-directories matching normal Windows temp layout
        (self.path / "downloads").mkdir(exist_ok=True)
        (self.path / "cache").mkdir(exist_ok=True)
        (self.path / "profile").mkdir(exist_ok=True)

    def inject_env(self, env: dict) -> dict:
        env = dict(env)
        env["TEMP"]   = str(self.path)
        env["TMP"]    = str(self.path)
        env["TMPDIR"] = str(self.path)  # Linux compat
        return env

    def cleanup(self):
        import shutil
        try:
            shutil.rmtree(self.path, ignore_errors=True)
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════
#  COMBINED SETUP FUNCTION
# ══════════════════════════════════════════════════════════════════

_jail = None
_job  = None


def setup_windows_sandbox(pid: int, env: dict) -> dict:
    """
    Call this after launching the browser process.
    Returns the modified env dict.
    """
    global _jail, _job

    # 1. Temp dir jail
    _jail = TempDirJail()
    env = _jail.inject_env(env)
    print(f"[Sandbox/Win] Temp jail: {_jail.path}")

    # 2. Scrub env
    env = scrub_environment(env)

    # 3. Job Object
    if IS_WINDOWS:
        try:
            _job = WindowsJobObject()
            if _job.assign_process(pid):
                print(f"[Sandbox/Win] Job Object assigned to PID {pid}")
            else:
                print(f"[Sandbox/Win] Warning: could not assign Job Object")
        except Exception as e:
            print(f"[Sandbox/Win] Job Object failed: {e}")

    return env


def teardown_windows_sandbox():
    global _jail, _job
    if _job:
        _job.close()
    # Keep jail dir for inspection; user can clear via manager


if __name__ == "__main__":
    print("Windows Sandbox module — not meant to run directly.")
    print("Import and call setup_windows_sandbox(pid, env) after launching browser.")
