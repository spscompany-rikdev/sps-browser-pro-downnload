"""
SPS Sandbox - what is worth asking the user about?   (pure Python, no Qt, unit-tested)

The old rules asked about C:\\Users, C:\\Program Files and C:\\Windows\\System32 - but the browser reads
its own DLLs and caches there thousands of times, so the sandbox drowned in dialogs and froze.
Now the user is asked ONLY about:
  * personal content folders  (Documents, Desktop, Pictures, Videos, Music, OneDrive)
  * dangerous file types (.exe .bat .ps1 .dll ...) written outside the browser's own folders
Everything the browser needs for itself (its install folder, C:\\SPS_Browser, caches, temp, Windows) is silently safe.
"""
import os
import sys
from pathlib import Path
from typing import List, Optional

DANGEROUS_EXT = {
    ".exe", ".bat", ".cmd", ".ps1", ".vbs", ".wsf", ".hta", ".scr", ".reg", ".lnk",
    ".dll", ".msi", ".jar", ".sh", ".dmg", ".pkg", ".deb", ".rpm",
}


def _norm(p: str) -> str:
    try:
        return os.path.normcase(os.path.abspath(p)).rstrip("\\/")
    except Exception:
        return (p or "").lower()


def _under(path: str, prefix: str) -> bool:
    if not prefix:
        return False
    pre = _norm(prefix)
    return path == pre or path.startswith(pre + os.sep)


def user_content_dirs() -> List[str]:
    h = Path.home()
    dirs = [str(h / n) for n in ("Documents", "Desktop", "Pictures", "Videos", "Music")]
    for var in ("OneDrive", "OneDriveConsumer", "OneDriveCommercial"):
        v = os.environ.get(var)
        if v:
            dirs.append(v)
    return dirs


def safe_prefixes(browser_dir: str = "") -> List[str]:
    h = Path.home()
    out = [browser_dir, str(h / ".sps_sandbox"), str(h / ".cache"), str(h / ".config"),
           getattr(sys, "prefix", ""), getattr(sys, "base_prefix", ""), getattr(sys, "_MEIPASS", "")]
    if sys.platform == "win32":
        for var in ("APPDATA", "LOCALAPPDATA", "TEMP", "TMP", "PROGRAMDATA", "SYSTEMROOT", "WINDIR",
                    "PROGRAMFILES", "PROGRAMFILES(X86)"):
            out.append(os.environ.get(var, ""))
        out += ["C:\\SPS_Browser", "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)", "C:\\ProgramData"]
    else:
        out += ["/proc", "/sys", "/dev", "/usr", "/lib", "/lib64", "/etc", "/tmp", "/var", "/opt", "/run"]
    return [p for p in out if p]


def classify(path: str, browser_dir: str = "", write: Optional[bool] = None) -> Optional[str]:
    """-> 'file_read' | 'file_write' when the user must be asked, None when it is fine.
    write=None means 'unknown' (psutil on Windows does not tell): only dangerous types count as writes."""
    if not path:
        return None
    p = _norm(path)
    ext = os.path.splitext(p)[1].lower()
    if any(_under(p, s) for s in safe_prefixes(browser_dir)):
        return None
    if ext in DANGEROUS_EXT and write is not False:
        return "file_write"
    if any(_under(p, d) for d in user_content_dirs()):
        return "file_write" if write else "file_read"
    return None
