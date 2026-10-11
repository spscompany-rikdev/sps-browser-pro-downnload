"""
╔══════════════════════════════════════════════════════════════════╗
║  AUTO-UPDATE SYSTEM  v1.0  (for SPS Browser)                     ║
║                                                                  ║
║  This file does TWO things:                                      ║
║  1. Explains exactly how Chrome/Brave/Firefox auto-update works  ║
║  2. Implements a REAL auto-update system for SPS Browser         ║
╚══════════════════════════════════════════════════════════════════╝

HOW REAL BROWSER AUTO-UPDATES WORK (Chrome/Brave explained):
═════════════════════════════════════════════════════════════

CHROME (Google's Update Service):
  Step 1 — Background service:
    Chrome installs "GoogleUpdate.exe" (Windows) or a LaunchAgent (Mac)
    or a cron job (Linux). This runs OUTSIDE Chrome, 24/7, even when
    Chrome is closed. It wakes up every few hours.

  Step 2 — Version check:
    GoogleUpdate sends an HTTP request to Google's update server:
      POST https://update.googleapis.com/service/update2/json
    The request includes:
      - Current Chrome version (e.g., 120.0.6099.109)
      - OS version, architecture
      - An "app ID" GUID that identifies Chrome
      - Cohort info (which update channel: Stable/Beta/Dev/Canary)

  Step 3 — Server responds:
    Server replies with JSON:
      - "noupdate" if already latest
      - OR: download URL + SHA256 hash of the new installer

  Step 4 — Download:
    GoogleUpdate downloads the update package (.crx3 bundle or mini-installer)
    to a temp folder. Downloads in chunks (resumable).

  Step 5 — Verification:
    Verifies the SHA256 hash matches exactly.
    Verifies the digital signature (code-signed by Google).
    If either fails → update is DISCARDED.

  Step 6 — Silent install:
    Runs the installer silently in the background.
    Chrome's files are replaced while Chrome is closed
    (or next time it's closed).
    On Windows: uses a separate "elevation service" to write to Program Files.

  Step 7 — Rollback info:
    Old version is kept in a side folder for 7 days.
    If the new version crashes on startup, it auto-reverts.

BRAVE (Sparkle / Omaha / their own):
  - Same architecture as Chrome (Brave forked Chromium including Omaha)
  - Uses "BraveUpdate" service instead of GoogleUpdate
  - Update server: https://updates.bravesoftware.com/
  - Same hash+signature verification

FIREFOX:
  - Uses Mozilla's "Balrog" update server
  - No separate background service — Firefox itself checks on launch
  - Uses MAR (Mozilla ARchive) format for incremental updates
  - Partial updates: only downloads what changed (saves bandwidth)
  - Full updates as fallback if partial fails

KEY SECURITY CONCEPTS all real browsers use:
  ✓ HTTPS only for update checks
  ✓ SHA256 (or SHA512) hash verification
  ✓ Code signing (digital signature from the vendor)
  ✓ Incremental/delta updates to save bandwidth
  ✓ Rollback capability
  ✓ Background service separate from browser
  ✓ Cohort/channel system (stable vs beta vs dev)
  ✓ Staged rollouts (1% → 10% → 50% → 100% of users)
"""

import os
import sys
import json
import time
import hashlib
import zipfile
import shutil
import threading
import tempfile
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Callable


# ══════════════════════════════════════════════════════════════════
#  VERSION INFO
# ══════════════════════════════════════════════════════════════════

CURRENT_VERSION = "34.0.0"   # Your SPS Browser version
UPDATE_CHANNEL  = "stable"    # stable | beta | dev

# Where your update server would be (you'll host this)
UPDATE_SERVER_URL = "https://updates.spsbrowser.example.com/check"

# Public key for verifying update signatures (you generate this)
# For now uses SHA256 hash comparison only.
UPDATE_PUBLIC_KEY = None  # fill in when you have a signing key


# ══════════════════════════════════════════════════════════════════
#  UPDATE MANIFEST FORMAT  (what your server returns)
# ══════════════════════════════════════════════════════════════════

# Your server should return JSON like this:
EXAMPLE_SERVER_RESPONSE = {
    "status": "update_available",  # or "no_update"
    "version": "34.1.0",
    "channel": "stable",
    "release_notes": "Bug fixes and security improvements",
    "download_url": "https://updates.spsbrowser.example.com/releases/SPS_Browser_V34.1.zip",
    "sha256": "abc123...64hexchars...",
    "signature": "base64_signature_here",  # optional, for code signing
    "size_bytes": 1234567,
    "released_at": "2026-10-10T00:00:00Z",
    "min_rollout_percent": 100,  # staged rollout percentage
}


# ══════════════════════════════════════════════════════════════════
#  UPDATE CHECKER
# ══════════════════════════════════════════════════════════════════

class UpdateChecker:
    """
    Checks for updates from the update server.
    Mimics how Chrome/Brave do it — background, silent, verifiable.
    """

    CHECK_INTERVAL_HOURS = 6   # check every 6 hours (like Chrome)
    STATE_FILE = Path.home() / ".sps_sandbox" / "update_state.json"

    def __init__(
        self,
        current_version: str = CURRENT_VERSION,
        channel: str = UPDATE_CHANNEL,
        on_update_available: Optional[Callable] = None,
    ):
        self.current_version    = current_version
        self.channel            = channel
        self.on_update_available = on_update_available
        self._state             = self._load_state()

    def _load_state(self) -> dict:
        try:
            if self.STATE_FILE.exists():
                return json.loads(self.STATE_FILE.read_text())
        except Exception:
            pass
        return {"last_check": None, "pending_update": None}

    def _save_state(self):
        try:
            self.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            self.STATE_FILE.write_text(json.dumps(self._state, indent=2))
        except Exception:
            pass

    def should_check_now(self) -> bool:
        last = self._state.get("last_check")
        if not last:
            return True
        last_dt = datetime.fromisoformat(last)
        return datetime.now() - last_dt > timedelta(hours=self.CHECK_INTERVAL_HOURS)

    def check(self) -> Optional[dict]:
        """
        Check for updates. Returns update info dict, or None if up to date.
        This is what Chrome's GoogleUpdate does every few hours.
        """
        self._state["last_check"] = datetime.now().isoformat()
        self._save_state()

        # Build request (mirrors Chrome's Omaha protocol structure)
        payload = {
            "app_id":  "SPS_BROWSER",
            "version": self.current_version,
            "channel": self.channel,
            "os":      sys.platform,
            "arch":    "x64" if sys.maxsize > 2**32 else "x86",
        }

        try:
            req = urllib.request.Request(
                UPDATE_SERVER_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent":   f"SPS_Browser/{self.current_version}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as e:
            print(f"[Updater] Network error: {e}")
            return None
        except Exception as e:
            print(f"[Updater] Check failed: {e}")
            return None

        if data.get("status") == "no_update":
            print(f"[Updater] Already up to date (v{self.current_version})")
            return None

        if data.get("status") == "update_available":
            update = data
            self._state["pending_update"] = update
            self._save_state()
            print(f"[Updater] Update available: v{data.get('version')}")
            if self.on_update_available:
                self.on_update_available(update)
            return update

        return None

    def start_background_checking(self):
        """
        Start a background thread that checks for updates periodically.
        This mirrors what Chrome's separate update service does.
        """
        def _loop():
            # Wait a bit after startup before first check
            time.sleep(30)
            while True:
                if self.should_check_now():
                    try:
                        self.check()
                    except Exception as e:
                        print(f"[Updater] Background check error: {e}")
                time.sleep(3600)  # sleep 1 hour between polls

        t = threading.Thread(target=_loop, daemon=True, name="SPS-Updater")
        t.start()
        print("[Updater] Background update checker started")


# ══════════════════════════════════════════════════════════════════
#  UPDATE DOWNLOADER  (with hash verification)
# ══════════════════════════════════════════════════════════════════

class UpdateDownloader:
    """
    Downloads and verifies an update package.
    Uses the same approach as real browsers:
      1. Download to temp
      2. Verify SHA256 hash
      3. Verify digital signature (if available)
      4. Only then apply
    """

    def __init__(self, update_info: dict, progress_callback: Optional[Callable] = None):
        self.update_info       = update_info
        self.progress_callback = progress_callback  # fn(bytes_done, total_bytes)
        self._cancel           = False

    def cancel(self):
        self._cancel = True

    def download_and_verify(self) -> Optional[Path]:
        """
        Downloads the update and verifies its integrity.
        Returns path to verified download, or None on failure.
        """
        url       = self.update_info["download_url"]
        expected_hash = self.update_info["sha256"]
        size      = self.update_info.get("size_bytes", 0)

        # Download to temp file
        tmp_dir  = Path(tempfile.mkdtemp(prefix="sps_update_"))
        tmp_file = tmp_dir / "update.zip"

        print(f"[Updater] Downloading: {url}")
        print(f"[Updater] Expected SHA256: {expected_hash}")

        try:
            with urllib.request.urlopen(url, timeout=60) as resp:
                total = int(resp.getheader("Content-Length", size) or size)
                done  = 0
                sha   = hashlib.sha256()

                with open(tmp_file, "wb") as f:
                    while not self._cancel:
                        chunk = resp.read(65536)  # 64 KB chunks
                        if not chunk:
                            break
                        f.write(chunk)
                        sha.update(chunk)
                        done += len(chunk)
                        if self.progress_callback and total:
                            self.progress_callback(done, total)

        except Exception as e:
            print(f"[Updater] Download failed: {e}")
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return None

        if self._cancel:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return None

        # Step: Verify SHA256
        actual_hash = sha.hexdigest()
        if actual_hash.lower() != expected_hash.lower():
            print(f"[Updater] ❌ HASH MISMATCH!")
            print(f"[Updater]   Expected: {expected_hash}")
            print(f"[Updater]   Got:      {actual_hash}")
            print(f"[Updater] Update DISCARDED (could be tampered or corrupted)")
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return None

        print(f"[Updater] ✅ SHA256 verified")

        # Step: Verify digital signature (if you have a key set up)
        if UPDATE_PUBLIC_KEY and self.update_info.get("signature"):
            if not self._verify_signature(tmp_file):
                print("[Updater] ❌ SIGNATURE INVALID — update rejected")
                shutil.rmtree(tmp_dir, ignore_errors=True)
                return None
            print("[Updater] ✅ Digital signature verified")

        return tmp_file

    def _verify_signature(self, file_path: Path) -> bool:
        """
        Verify a digital signature using RSA (like Chrome/Brave do).
        Requires cryptography library.
        """
        try:
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import padding
            import base64

            pub_key_bytes = UPDATE_PUBLIC_KEY.encode("utf-8")
            from cryptography.hazmat.primitives.serialization import load_pem_public_key
            public_key = load_pem_public_key(pub_key_bytes)

            sig_b64 = self.update_info["signature"]
            signature = base64.b64decode(sig_b64)

            file_data = file_path.read_bytes()
            public_key.verify(
                signature,
                file_data,
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return True
        except Exception as e:
            print(f"[Updater] Signature verification error: {e}")
            return False


# ══════════════════════════════════════════════════════════════════
#  UPDATE APPLIER
# ══════════════════════════════════════════════════════════════════

class UpdateApplier:
    """
    Applies the downloaded update package.
    - Backs up the current version
    - Extracts new files
    - Keeps rollback copy for 7 days (like Chrome)
    """

    def __init__(self, browser_dir: str):
        self.browser_dir = Path(browser_dir)
        self.backup_dir  = Path.home() / ".sps_sandbox" / "rollback"

    def apply(self, update_zip: Path, new_version: str) -> bool:
        """
        Apply the update.
        Browser must be closed before calling this.
        """
        print(f"[Updater] Applying update to v{new_version}...")

        # 1. Backup current version
        backup_path = self.backup_dir / f"v{self._current_version()}"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        if backup_path.exists():
            shutil.rmtree(backup_path)
        try:
            shutil.copytree(self.browser_dir, backup_path)
            print(f"[Updater] Backed up current version to: {backup_path}")
        except Exception as e:
            print(f"[Updater] Backup failed: {e}")
            return False

        # 2. Extract new files
        try:
            with zipfile.ZipFile(update_zip, "r") as zf:
                # Extract to a staging dir first
                staging = Path(tempfile.mkdtemp(prefix="sps_staging_"))
                zf.extractall(staging)

                # Find the top-level folder in the zip
                contents = list(staging.iterdir())
                if len(contents) == 1 and contents[0].is_dir():
                    source = contents[0]
                else:
                    source = staging

                # Copy new files over
                for item in source.rglob("*"):
                    rel = item.relative_to(source)
                    dest = self.browser_dir / rel
                    if item.is_dir():
                        dest.mkdir(parents=True, exist_ok=True)
                    else:
                        shutil.copy2(str(item), str(dest))

                shutil.rmtree(staging)
        except Exception as e:
            print(f"[Updater] Extract failed: {e} — rolling back")
            self._rollback(backup_path)
            return False

        # 3. Clean up old backups (keep 7 days like Chrome)
        self._cleanup_old_backups(days=7)

        # 4. Clean up downloaded zip
        try:
            shutil.rmtree(update_zip.parent, ignore_errors=True)
        except Exception:
            pass

        print(f"[Updater] ✅ Update applied successfully: v{new_version}")
        return True

    def _current_version(self) -> str:
        # Read version from browser's own file
        ver_file = self.browser_dir / "version.txt"
        if ver_file.exists():
            return ver_file.read_text().strip()
        return CURRENT_VERSION

    def _rollback(self, backup_path: Path):
        print(f"[Updater] Rolling back to: {backup_path}")
        try:
            if backup_path.exists():
                for item in backup_path.rglob("*"):
                    rel  = item.relative_to(backup_path)
                    dest = self.browser_dir / rel
                    if item.is_dir():
                        dest.mkdir(parents=True, exist_ok=True)
                    else:
                        shutil.copy2(str(item), str(dest))
            print("[Updater] Rollback complete")
        except Exception as e:
            print(f"[Updater] Rollback failed: {e}")

    def _cleanup_old_backups(self, days: int = 7):
        if not self.backup_dir.exists():
            return
        cutoff = datetime.now() - timedelta(days=days)
        for d in self.backup_dir.iterdir():
            if d.is_dir():
                mtime = datetime.fromtimestamp(d.stat().st_mtime)
                if mtime < cutoff:
                    shutil.rmtree(d, ignore_errors=True)
                    print(f"[Updater] Removed old backup: {d.name}")


# ══════════════════════════════════════════════════════════════════
#  FULL UPDATE MANAGER  (combines everything)
# ══════════════════════════════════════════════════════════════════

class AutoUpdateManager:
    """
    The complete auto-update system for SPS Browser.
    Use this in your browser or launcher.

    Usage:
        updater = AutoUpdateManager(browser_dir="/path/to/browser")
        updater.start()   # begins background checking
        # ... browser runs ...
        updater.stop()
    """

    def __init__(
        self,
        browser_dir: str,
        on_update_ready: Optional[Callable] = None,
    ):
        self.browser_dir   = browser_dir
        self.on_update_ready = on_update_ready
        self._checker      = UpdateChecker(
            on_update_available=self._handle_update_available
        )
        self._pending_update: Optional[dict] = None
        self._download_thread: Optional[threading.Thread] = None

    def start(self):
        """Call this when browser starts — begins background update checking."""
        self._checker.start_background_checking()

    def check_now(self):
        """Force an immediate check."""
        return self._checker.check()

    def _handle_update_available(self, update_info: dict):
        """Called when update server says there's a new version."""
        self._pending_update = update_info
        print(f"[AutoUpdate] New version available: {update_info['version']}")
        print(f"[AutoUpdate] Release notes: {update_info.get('release_notes', 'N/A')}")

        # Start downloading in background (like Chrome does)
        self._download_thread = threading.Thread(
            target=self._background_download,
            args=(update_info,),
            daemon=True,
        )
        self._download_thread.start()

    def _background_download(self, update_info: dict):
        """Downloads the update silently in the background."""
        def progress(done, total):
            pct = int(done / total * 100) if total else 0
            print(f"\r[AutoUpdate] Downloading: {pct}% ({done//1024}KB/{total//1024}KB)", end="")

        downloader = UpdateDownloader(update_info, progress_callback=progress)
        zip_path   = downloader.download_and_verify()

        if zip_path:
            print(f"\n[AutoUpdate] ✅ Update downloaded and verified")
            print(f"[AutoUpdate] Update will be applied next time browser restarts")
            if self.on_update_ready:
                self.on_update_ready(update_info, zip_path)
        else:
            print(f"\n[AutoUpdate] ❌ Download or verification failed")

    def apply_pending_update(self) -> bool:
        """
        Apply any downloaded update. Call this when the browser is about to close.
        Like Chrome — updates install after you close the browser.
        """
        if not self._pending_update:
            return False
        applier = UpdateApplier(self.browser_dir)
        result  = applier.apply(
            Path(self._pending_update.get("_local_zip", "")),
            self._pending_update["version"]
        )
        if result:
            self._pending_update = None
        return result

    def stop(self):
        pass  # background threads are daemons, they stop with the process


# ══════════════════════════════════════════════════════════════════
#  HOW TO SET UP YOUR OWN UPDATE SERVER
# ══════════════════════════════════════════════════════════════════

UPDATE_SERVER_GUIDE = """
HOW TO SET UP YOUR OWN UPDATE SERVER FOR SPS BROWSER:
═══════════════════════════════════════════════════════

Option 1: Simple Python HTTP Server (for testing):
  
  # server.py
  from http.server import HTTPServer, BaseHTTPRequestHandler
  import json

  class Handler(BaseHTTPRequestHandler):
      def do_POST(self):
          body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
          current = body.get('version', '0.0.0')
          
          # Compare versions — if update available, return it
          if current < '35.0.0':  # your new version
              resp = {
                  'status': 'update_available',
                  'version': '35.0.0',
                  'channel': 'stable',
                  'download_url': 'http://yourserver.com/SPS_Browser_V35.zip',
                  'sha256': 'your_sha256_hash_here',
                  'size_bytes': 5000000,
                  'release_notes': 'Security fixes',
              }
          else:
              resp = {'status': 'no_update'}
          
          self.send_response(200)
          self.send_header('Content-Type', 'application/json')
          self.end_headers()
          self.wfile.write(json.dumps(resp).encode())
  
  HTTPServer(('0.0.0.0', 8080), Handler).serve_forever()

Option 2: GitHub Releases (free hosting):
  - Upload your .zip release to GitHub Releases
  - Run a tiny server or serverless function that checks the GitHub API
  - GitHub API: https://api.github.com/repos/YOU/SPS_Browser/releases/latest
  - Compare version tags and return the download URL

Option 3: Cloudflare Workers (free, fast, global CDN):
  - Deploy a Worker that reads from a JSON config file
  - Workers are free up to 100,000 requests/day
  - Files go in R2 (object storage)

Generating SHA256 for your release:
  Python: python -c "import hashlib; print(hashlib.sha256(open('SPS_Browser_V35.zip','rb').read()).hexdigest())"
  Windows: certutil -hashfile SPS_Browser_V35.zip SHA256
  Linux:   sha256sum SPS_Browser_V35.zip

Setting up code signing (recommended for production):
  1. Generate RSA key pair:
       openssl genrsa -out private_key.pem 2048
       openssl rsa -in private_key.pem -pubout -out public_key.pem
  2. Sign your release:
       openssl dgst -sha256 -sign private_key.pem -out signature.bin SPS_Browser_V35.zip
       python -c "import base64; print(base64.b64encode(open('signature.bin','rb').read()).decode())"
  3. Put the base64 signature in your server response as 'signature'
  4. Put the public key content in UPDATE_PUBLIC_KEY in this file
"""

if __name__ == "__main__":
    print("Auto-Update System — Documentation Mode")
    print("=" * 60)
    print(UPDATE_SERVER_GUIDE)
    print()
    print("To test the updater (will fail because no server is set up):")
    checker = UpdateChecker()
    print(f"Current version: {checker.current_version}")
    print(f"Should check now: {checker.should_check_now()}")
