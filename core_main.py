"""
SPS_Browser_Core.exe  -  the real browser. Normally started BY SPS_Browser.exe (the sandbox).

   SPS_Browser_Core.exe --selftest     checks that every library was packed correctly
"""
import sys
import os
import multiprocessing

FROZEN = getattr(sys, "frozen", False)
BASE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
EXE_DIR = os.path.dirname(os.path.abspath(sys.executable)) if FROZEN else BASE


def _fatal(msg):
    try:
        log = os.path.join(os.environ.get("TEMP", os.path.expanduser("~")), "SPS_Browser_error.txt")
        with open(log, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass
    try:
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, msg[-1800:], "SPS Browser - startup error", 0x10)
    except Exception:
        pass


def _setup_qt_paths():
    """Tell QtWebEngine where its helper process and resources are inside the bundle."""
    for root in (os.path.join(BASE, "PyQt6", "Qt6"), os.path.join(EXE_DIR, "PyQt6", "Qt6")):
        helper = os.path.join(root, "bin", "QtWebEngineProcess.exe" if sys.platform == "win32" else "QtWebEngineProcess")
        if os.path.exists(helper):
            os.environ["QTWEBENGINEPROCESS_PATH"] = helper
            os.environ["PATH"] = os.path.join(root, "bin") + os.pathsep + os.environ.get("PATH", "")
            res = os.path.join(root, "resources")
            if os.path.isdir(res):
                os.environ.setdefault("QTWEBENGINE_RESOURCES_PATH", res)
            loc = os.path.join(root, "translations", "qtwebengine_locales")
            if os.path.isdir(loc):
                os.environ.setdefault("QTWEBENGINE_LOCALES_PATH", loc)
            break


def _selftest():
    lines, ok = [], True

    def check(name, fn, hard=True):
        nonlocal ok
        try:
            fn()
            lines.append(f"OK    {name}")
        except Exception as e:
            lines.append(f"{'FAIL' if hard else 'WARN'}  {name}: {type(e).__name__}: {e}")
            if hard:
                ok = False

    for mod in ("pickle", "multiprocessing", "json", "sqlite3", "ssl", "socket", "email", "csv",
                "PyQt6.QtCore", "PyQt6.QtGui", "PyQt6.QtWidgets", "PyQt6.QtNetwork",
                "PyQt6.QtWebEngineCore", "PyQt6.QtWebEngineWidgets", "PyQt6.QtPrintSupport",
                "psutil", "requests", "certifi", "http.server", "urllib.request"):
        check("import " + mod, lambda m=mod: __import__(m))
    check("QtWebEngineProcess helper present",
          lambda: (_ for _ in ()).throw(FileNotFoundError(os.environ.get("QTWEBENGINEPROCESS_PATH", "not found")))
          if not os.path.exists(os.environ.get("QTWEBENGINEPROCESS_PATH", "")) else None)
    def _res(name):
        for root in (os.path.join(BASE, "PyQt6", "Qt6"), os.path.join(EXE_DIR, "PyQt6", "Qt6")):
            for sub in ("resources", "bin", "."):
                if os.path.exists(os.path.join(root, sub, name)):
                    return
        raise FileNotFoundError(name + " not packed (web pages would not render)")
    for _n in ("qtwebengine_resources.pak", "icudtl.dat"):
        check("WebEngine file " + _n, lambda n=_n: _res(n))
    check("WebEngine locales", lambda: (_ for _ in ()).throw(FileNotFoundError("qtwebengine_locales"))
          if not any(os.path.isdir(os.path.join(r, "PyQt6", "Qt6", "translations", "qtwebengine_locales")) for r in (BASE, EXE_DIR)) else None)
    check("import llama_cpp (local AI)", lambda: __import__("llama_cpp"), hard=False)
    check("import browser module", lambda: __import__("sps_browser_app"), hard=False)
    lines.append("")
    lines.append("SELFTEST " + ("PASSED" if ok else "FAILED"))
    with open(os.path.join(EXE_DIR, "selftest_result.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    try:
        if BASE not in sys.path:
            sys.path.insert(0, BASE)
        _setup_qt_paths()
        if "--selftest" in sys.argv:
            _selftest()
        import sps_browser_app
        sps_browser_app.sps_main()
    except SystemExit:
        raise
    except Exception:
        import traceback
        _fatal("SPS Browser crashed while starting:\n\n" + traceback.format_exc())
        sys.exit(1)
