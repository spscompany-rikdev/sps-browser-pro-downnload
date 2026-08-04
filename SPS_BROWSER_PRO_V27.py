import sys
import json
import os
import datetime
import html
import re
import shutil
import math
import base64
import hashlib
import secrets
import string
import subprocess
import threading
import time
import tempfile
import platform
from functools import partial
from urllib.parse import urlparse, quote_plus, unquote_plus, urljoin

try:
    import requests
except ImportError:
    requests = None

from PyQt6.QtCore import (
    QUrl, Qt, QSize, QTimer, pyqtSignal, QPoint, QRect,
    QBuffer, QIODevice, QThread, QPropertyAnimation, QEasingCurve,
    QByteArray, QDateTime, QObject, QRunnable, QThreadPool
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QLineEdit, QPushButton,
    QVBoxLayout, QWidget, QTabWidget, QMenu, QDialog, QFormLayout,
    QCheckBox, QComboBox, QLabel, QFileDialog, QMessageBox,
    QListWidget, QHBoxLayout, QStatusBar, QProgressBar,
    QFrame, QSizePolicy, QToolButton, QScrollArea, QPlainTextEdit,
    QSplitter, QListWidgetItem, QInputDialog, QGridLayout,
    QSlider, QSpinBox, QTabBar, QGroupBox, QTreeWidget,
    QTreeWidgetItem, QTextEdit, QColorDialog, QFontDialog,
    QSystemTrayIcon, QTableWidget, QTableWidgetItem, QHeaderView,
    QStackedWidget, QButtonGroup, QRadioButton, QDockWidget,
    QCalendarWidget
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import (
    QWebEngineProfile, QWebEnginePage, QWebEngineSettings,
    QWebEngineDownloadRequest, QWebEngineScript,
    QWebEngineUrlRequestInterceptor, QWebEngineCertificateError,
    QWebEngineNewWindowRequest
)
from PyQt6.QtGui import (
    QAction, QIcon, QActionGroup, QColor, QPalette, QFont,
    QShortcut, QKeySequence, QPixmap, QPainter, QBrush, QPen,
    QLinearGradient, QRadialGradient, QCursor, QDesktopServices,
    QFontMetrics
)
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog

# ═══════════════════════════════════════════════════════════════
#  CONSTANTS & PATHS
# ═══════════════════════════════════════════════════════════════
APP_NAME         = "SPS Web Browser Pro"
VERSION          = "27.0.0"
UPDATE_CHECK_URL = "https://sites.google.com/view/spsbrowserpro/updates"
EXTENSION_STORE_URL ="https://spscompany-rikdev.github.io/SPS_BROWSER_EXTENTIONS"   # ← PUT YOUR EXTENSION WEBSITE URL HERE (e.g. "https://yoursite.com/extensions")
BASE_DATA_DIR    = os.path.expanduser("~/.sps_browser_v21")
PROFILES_DIR     = os.path.join(BASE_DATA_DIR, "profiles")
EXTENSIONS_DIR   = os.path.join(BASE_DATA_DIR, "extensions")
NOTES_DIR        = os.path.join(BASE_DATA_DIR, "notes")
EXT_INSTALLED_DIR = os.path.join(BASE_DATA_DIR, "installed_extensions")
UPDATE_HISTORY_PATH = os.path.join(BASE_DATA_DIR, "update_history.json")
CURRENT_PROFILE_NAME = "Default"

for _d in [BASE_DATA_DIR, PROFILES_DIR, os.path.join(PROFILES_DIR,"Default"),
           EXTENSIONS_DIR, NOTES_DIR, EXT_INSTALLED_DIR]:
    os.makedirs(_d, exist_ok=True)

SEARCH_ENGINES = {
    "SPS Search":  "https://spscompany-rikdev.github.io/sps-search-engine?q=",
    "Google":      "https://www.google.com/search?q=",
    "DuckDuckGo":  "https://duckduckgo.com/?q=",
    "Bing":        "https://www.bing.com/search?q=",
    "Brave":       "https://search.brave.com/search?q=",
    "Ecosia":      "https://www.ecosia.org/search?q=",
    "Yahoo":       "https://search.yahoo.com/search?p=",
    "Startpage":   "https://www.startpage.com/search?q=",
    "Yandex":      "https://yandex.com/search/?text=",
    "Qwant":       "https://www.qwant.com/?q=",
}

USER_AGENTS = {
    "Default":       "",
    "Chrome (Win)":  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Firefox (Win)": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Safari (Mac)":  "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Edge":          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    "Mobile Chrome": "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36",
    "Googlebot":     "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
}

DEFAULT_THEME = {
    "bg_primary":    "#ffffff", "bg_secondary":  "#f5f5f5",
    "bg_tertiary":   "#ebebeb", "accent":        "#1a73e8",
    "accent_light":  "#e8f0fe", "text_primary":  "#202124",
    "text_secondary":"#5f6368", "border":        "#dadce0",
    "tab_active":    "#ffffff", "tab_inactive":  "#f1f3f4",
    "sidebar_bg":    "#f8f9fa", "toolbar_bg":    "#ffffff",
    "hover":         "#e8eaed", "danger":        "#d93025",
    "success":       "#188038", "warning":       "#f9ab00",
}

DEFAULT_SETTINGS = {
    # ── Security & Privacy ──
    "js_enabled":              True,
    "plugins_enabled":         True,
    "storage_enabled":         True,
    "load_images":             True,
    "js_popups":               False,
    "fullscreen":              True,
    "insecure_content":        False,
    "dns_prefetch":            True,
    "smooth_scroll":           True,
    "error_pages":             True,
    "local_remote_access":     False,
    "xss_auditing":            True,
    "ad_blocker":              True,
    "tracking_protection":     True,
    "total_cookie_protection": True,
    "do_not_track":            True,
    "block_popups":            True,
    "safe_browsing":           True,
    "https_only":              False,
    "clear_on_exit":           False,
    "block_fingerprinting":    True,
    "block_third_cookies":     True,
    "block_cryptomining":      True,
    "block_social_trackers":   True,
    "certificate_errors":      False,
    # ── General ──
    "search_engine":           "SPS Search",
    "download_path":           os.path.expanduser("~/Downloads"),
    "dark_mode":               False,
    "zoom_factor":             1.0,
    "auto_update":             True,
    "user_agent":              "Default",
    "sidebar_visible":         True,
    "hardware_accel":          True,
    "instant_answers":         True,
    "voice_search":            True,
    "spell_check":             True,
    "auto_fill":               True,
    "save_passwords":          True,
    "reading_mode":            False,
    "custom_css":              "",
    "startup_page":            "home",
    "restore_tabs":            True,
    "font_size":               16,
    "tab_position":            "top",
    "show_bookmarks_bar":      True,
    "show_status_bar":         True,
    "compact_mode":            False,
    "auto_play_media":         True,
    "reader_mode_font":        "Georgia",
    "new_tab_page":            "speed_dial",
    "language":                "en",
    "timezone":                "auto",
    "theme":                   DEFAULT_THEME,
    "accent_color":            "#1a73e8",
    # ── NEW SETTINGS (10 new) ──
    "pip_mode":                False,   # Picture-in-picture mode auto-detect
    "tab_preview_hover":       True,    # Show thumbnail preview on tab hover
    "mouse_gesture":           True,    # Mouse gesture navigation (right-drag)
    "focus_mode":              False,   # Hide all UI chrome for distraction-free
    "proxy_enabled":           False,   # Custom proxy
    "proxy_host":              "",
    "proxy_port":              8080,
    "wake_lock":               False,   # Prevent screen from sleeping while browsing
    "notify_blocked":          True,    # Show notification when something is blocked
    "session_auto_save":       True,    # Auto-save session every 5 minutes
    "tab_memory_limit":        50,      # Suspend tabs after N minutes of inactivity
    "custom_homepage_url":     "",      # Custom homepage URL (overrides speed dial)
    "sidebar_width":           230,
    "max_concurrent_downloads":5,
    "preload_hover_links":     False,   # Prefetch pages on link hover
    "show_tab_count":          True,    # Show number of open tabs in title bar
    "new_tab_show_stats":      True,    # Show stats row on the new tab page
    "new_tab_show_tools":      True,    # Show quick tools on the new tab page
    "new_tab_show_recent_tabs":True,    # Show recent tabs on the new tab page
    "new_tab_show_bookmarks":  True,    # Show bookmarks on the new tab page
    "new_tab_show_search":     True,    # Show search box on the new tab page
    "new_tab_show_shortcuts":  True,    # Show shortcut chips on the new tab page
    "new_tab_show_recent_history": True, # Show recent history on the new tab page
    "auto_refresh_enabled":    False,   # Auto-refresh the active tab
    "auto_refresh_interval":   60,      # Auto-refresh interval in seconds
    "page_dark_filter":        False,   # Apply a dark filter to the active page
    "page_text_only_mode":     False,   # Hide media on the active page
    "open_links_in_background": False,   # Open links in background tabs
    "confirm_before_close":     True,    # Ask before closing browser window
    "block_insecure_downloads": False,   # Block http downloads on https pages
    "scan_downloads_before_saving": True, # Download to temp, scan, then ask user
    "fast_download_scanning": True,        # Only deep-scan risky downloads
    "scan_archives_before_saving": False,  # Deep-scan zip/rar/7z downloads
    "skip_safe_file_deep_scan": True,      # Let normal images/media/docs download fast
    "max_download_scan_mb": 150,           # Large files skip deep temp scanning
    "download_scan_sample_kb": 512,        # Heuristic sample size for risky files
    "ask_before_large_downloads": False,   # Confirm very large downloads
    "large_download_warning_mb": 500,
    "trusted_download_domains": "",        # comma-separated domains that skip deep scan
    "allow_trusted_download_domains": True,
    "auto_open_download_folder_after_save": False,
    "keep_download_scan_log": True,
    "block_unknown_executable_sources": False,
    "warn_executable_downloads": True,    # Confirm EXE/MSI/script downloads
    "block_double_extension_downloads": True, # Block invoice.pdf.exe-style names
    "quarantine_blocked_downloads": True, # Keep blocked downloads in quarantine
    "verify_update_hash": True,           # Verify sha256= metadata when available
    "silent_update_install": True,        # Use Inno Setup silent install switches
    "create_desktop_shortcut_on_update": True, # Ask installer to create desktop icon
    "update_check_url": UPDATE_CHECK_URL, # Plain text/web page containing latest installer link
    "update_page_plain_text": True,       # Treat update page as simple text first
    "auto_download_updates": False,       # Automatically begin update after confirmation window opens
    "update_check_interval_hours": 12,    # Minimum time between startup update checks
    "update_run_as_admin_hint": True,     # Explain elevation if the installer asks for admin rights
    "update_close_before_install": True,  # Close this browser after launching installer
    "update_keep_installer_copy": False,  # Keep downloaded installer after starting setup
    "update_download_subfolder": "SPS Browser Updates",
    "save_last_workspace":      True,    # Auto-save workspace snapshot on exit
    "restore_last_workspace":   False,   # Restore workspace snapshot on startup
    "enable_tab_groups":        True,    # Enable saved tab groups
    "new_tab_show_workspaces":   True,    # Show workspaces panel on the new tab page
    "history_retention_days":    30,      # Keep history for N days
    "page_zoom_step":           10,      # Zoom step percentage
    "open_bookmarks_in_background": False, # Open bookmarks without stealing focus
    # V27 feature pack switches
    "feature_pack_menu_enabled": True,
    "confirm_bulk_tab_actions": True,
    "auto_bookmark_folder_prefix": "Session",
    "clipboard_multi_url_open_limit": 30,
    "markdown_export_include_titles": True,
    "tab_sort_ignores_prefix_icons": True,
    "copy_tabs_include_incognito": False,
    "bulk_reload_skips_about_pages": True,
    "close_duplicate_keep_active": True,
    "default_qr_service": "https://api.qrserver.com/v1/create-qr-code/?size=320x320&data=",
    # ── V26 NEW FEATURES ──
    "block_fingerprinting_canvas":  True,   # Block canvas fingerprinting
    "block_fingerprinting_webgl":   True,   # Block WebGL fingerprinting
    "block_fingerprinting_audio":   True,   # Block AudioContext fingerprinting
    "block_fingerprinting_fonts":   True,   # Block font enumeration fingerprinting
    "block_battery_api":            True,   # Block Battery Status API (privacy leak)
    "block_geolocation":            False,  # Block geolocation access
    "randomize_canvas_noise":       True,   # Add noise to canvas reads
    "randomize_webgl_vendor":       True,   # Spoof WebGL vendor/renderer strings
    "block_etag_tracking":          True,   # Strip ETag/If-None-Match headers
    "block_referrer_header":        True,   # Strip Referer header on cross-origin
    "spoof_timezone":               False,  # Spoof timezone to UTC
    "spoof_language":               False,  # Spoof Accept-Language header
    "csp_header_injection":         False,  # Inject CSP header for extra XSS protection
    "hsts_preload_check":           True,   # Warn on sites not on HSTS preload list
    "dns_over_https":               False,  # Use DoH resolver
    "dns_over_https_url":           "https://cloudflare-dns.com/dns-query",
    "extension_sandbox":            True,   # Run extensions in sandboxed context
    "content_security_audit":       True,   # Log and audit CSP violations
    "block_mixed_audio_video":      True,   # Block mixed HTTP audio/video on HTTPS pages
    # ── V26 NEW GENERAL FEATURES ──
    "vertical_tabs":                False,  # Show tabs as vertical sidebar
    "tab_emoji_favicon":            True,   # Show emoji fallback for missing favicons
    "url_bar_show_etld":            True,   # Highlight eTLD+1 in URL bar
    "smooth_tab_switch":            True,   # Animate tab switching
    "enable_pip":                   True,   # Enable picture-in-picture on video right-click
    "download_progress_in_title":   True,   # Show download % in window title
    "confirm_on_form_close":        True,   # Warn before closing tab with unsaved form
    "smart_paste_url":              True,   # Auto-navigate on paste in address bar
    "tab_tooltip_full_url":         True,   # Show full URL in tab tooltip
    "double_click_tab_close":       False,  # Close tab on double-click
    "middle_click_new_tab":         True,   # Middle-click link opens new tab
    "scroll_tabs_with_wheel":       True,   # Scroll through tabs with mouse wheel
    "reader_mode_auto":             False,  # Auto-enable reader mode on article pages
    "new_tab_wallpaper":            "",     # Path to custom new tab background image
    "extensions_toolbar_visible":   True,   # Show enabled-extension buttons in toolbar
}

TRACKER_DOMAINS = [
    "doubleclick.net","adservice.google","ads.yahoo.com","analytics.google.com",
    "facebook.net","track.js","scorecardresearch.com","quantserve.com",
    "hotjar.com","mixpanel.com","segment.io","amplitude.com","heap.io",
    "mouseflow.com","fullstory.com","logrocket.com","datadog.com",
    "newrelic.com","pingdom.com","chartbeat.com","parsely.com",
    "comscore.com","nielsen.com","moatads.com","criteo.com",
    "adsrvr.org","pubmatic.com","rubiconproject.com","openx.net",
    "advertising.com","taboola.com","outbrain.com","bat.bing.com",
    "connect.facebook.net","analytics.twitter.com","snap.licdn.com",
]

CRYPTO_MINING_DOMAINS = [
    "coinhive.com","cryptoloot.pro","miner.pr0gramm.com","minero.pw",
    "coin-hive.com","jsecoin.com","coinblind.com","webmine.pro",
    "crypto-loot.com","ppoi.org","monerominer.rocks","hashforcash.us",
]

SOCIAL_TRACKER_DOMAINS = [
    "connect.facebook.net","platform.twitter.com","platform.linkedin.com",
    "widgets.pinterest.com","apis.google.com","static.addtoany.com",
    "s7.addthis.com","sharethis.com",
]

MALWARE_SHA256_SIGNATURES = {
    "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f": "EICAR-Test-File",
    "ed01ebfbc9eb5bbea545af4d01bf5f1071661840480439c6e5babe8e080e41aa": "Ransom.WannaCry",
    "24d004a104d4d54034dbcffc2a4b19a11f39008a575aa614ea04703480b1022c": "Ransom.WannaCry.B",
    "b9c5d4339809e0ad9a00d4d3dd26fdf44a32819a54abf846bb9b560d81391c25": "Ransom.WannaCry.C",
    "027cc450ef5f8c5f653329641ec1fed91f694e0d229928963b30f6b0d7d3a745": "Ransom.NotPetya",
    "64b0b58a2c030c77fdb2b537b2fcc4af432bc55ffb36599a31d418c7c69e94b1": "Ransom.Petya.A",
}

MALWARE_MD5_SIGNATURES = {
    "44d88612fea8a8f36de82e1278abb02f": "EICAR-Test-File",
    "aa15c8248d7e57aade5a6e7bbdb0d7cb": "Ransom.WannaCry",
    "7bf2b57f2a205768755c07f238fb32cc": "Trojan.Emotet",
    "a93ee7ea13238bd038bcbec635f500fb": "Backdoor.NjRAT",
}

DANGEROUS_DOWNLOAD_EXTENSIONS = {
    ".bat", ".cmd", ".ps1", ".vbs", ".jse", ".wsf",
    ".scr", ".pif", ".hta", ".reg",
}

# Extensions that show a soft warning but download immediately (not blocked)
WARN_ONLY_EXTENSIONS = {
    ".exe", ".msi", ".js", ".jar", ".dll", ".lnk", ".com",
}

DOCUMENT_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt",
    ".jpg", ".jpeg", ".png", ".gif", ".zip", ".rar", ".7z",
}

SAFE_FAST_DOWNLOAD_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg", ".ico",
    ".mp3", ".wav", ".ogg", ".mp4", ".webm", ".mkv", ".avi", ".mov",
    ".pdf", ".txt", ".csv", ".json", ".xml", ".md",
}

ARCHIVE_DOWNLOAD_EXTENSIONS = {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"}

SUSPICIOUS_DOWNLOAD_PATTERNS = [
    (rb"X5O!P%@AP\[4\\PZX54\(P\^\)7CC\)7\}", "EICAR antivirus test string"),
    (rb"powershell(?:\.exe)?.{0,80}-(?:enc|encodedcommand)\s+[A-Za-z0-9+/]{40,}={0,2}", "Encoded PowerShell command"),
    (rb"vssadmin\s+delete\s+shadows|wmic\s+shadowcopy\s+delete|bcdedit\s+/set", "Ransomware recovery-disabling command"),
    (rb"mimikatz|sekurlsa|lsadump|kerberos::golden", "Credential dumping signature"),
    (rb"certutil\s+(?:-decode|-urlcache|-split)|bitsadmin\s+/(?:transfer|download)", "Living-off-the-land downloader"),
    (rb"CreateRemoteThread|WriteProcessMemory|VirtualAllocEx|ReflectiveLoader", "Process injection behavior"),
]

# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════
def get_profile_path(name):
    p = os.path.join(PROFILES_DIR, name)
    os.makedirs(p, exist_ok=True)
    return p

def load_settings(profile_name):
    path = os.path.join(get_profile_path(profile_name), "settings.json")
    try:
        if os.path.exists(path):
            with open(path) as f:
                saved = json.load(f)
            merged = dict(DEFAULT_SETTINGS)
            merged.update(saved)
            if "theme" not in merged or not isinstance(merged["theme"], dict):
                merged["theme"] = dict(DEFAULT_THEME)
            else:
                t = dict(DEFAULT_THEME); t.update(merged["theme"])
                merged["theme"] = t
            return merged
    except:
        pass
    return dict(DEFAULT_SETTINGS)

def save_settings_to_disk(profile_name, data):
    path = os.path.join(get_profile_path(profile_name), "settings.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def hash_password(pw):
    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt+pw).encode()).hexdigest()
    return f"{salt}:{h}"

def verify_password(pw, stored):
    try:
        salt, h = stored.split(":",1)
        return hashlib.sha256((salt+pw).encode()).hexdigest() == h
    except:
        return False

def generate_password(length=16, symbols=True):
    chars = string.ascii_letters + string.digits
    if symbols: chars += "!@#$%^&*()-_=+[]{}|;:,.<>?"
    return "".join(secrets.choice(chars) for _ in range(length))

def _clamp(v): return max(0, min(255, v))
def _lighten(hex_color, amt):
    h = hex_color.lstrip("#")
    r,g,b = int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
    return f"#{_clamp(r+amt):02x}{_clamp(g+amt):02x}{_clamp(b+amt):02x}"
def _darken(hex_color, amt): return _lighten(hex_color, -amt)

def version_gt(a, b):
    try:
        pa = [int(x) for x in re.findall(r"\d+", str(a))[:4]]
        pb = [int(x) for x in re.findall(r"\d+", str(b))[:4]]
        ln = max(len(pa), len(pb), 1)
        return tuple(pa + [0] * (ln - len(pa))) > tuple(pb + [0] * (ln - len(pb)))
    except Exception:
        return False

def extract_version(text):
    nums = re.findall(r"\d+(?:\.\d+){1,3}", str(text or ""))
    return nums[0] if nums else ""

def safe_filename_from_url(url, fallback="download.bin"):
    name = os.path.basename(urlparse(url).path) or fallback
    name = unquote_plus(name).strip().replace("\\", "_").replace("/", "_")
    return re.sub(r"[^A-Za-z0-9._() -]", "_", name)[:160] or fallback

def file_hash(path, algorithm="sha256"):
    h = hashlib.new(algorithm)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def analyze_download(path, url="", filename="", sample_kb=512, hash_large_files=True):
    reasons = []
    filename = filename or os.path.basename(path)
    lower_name = filename.lower()
    suffixes = [s.lower() for s in os.path.splitext(lower_name)]
    ext = os.path.splitext(lower_name)[1]
    parts = lower_name.split(".")
    if len(parts) >= 3 and f".{parts[-2]}" in DOCUMENT_EXTENSIONS and ext in DANGEROUS_DOWNLOAD_EXTENSIONS:
        reasons.append(f"Double extension hides an executable: .{parts[-2]}{ext}")
    if ext in DANGEROUS_DOWNLOAD_EXTENSIONS:
        reasons.append(f"Potentially dangerous script download: {ext}")
    # Note: .exe/.msi are handled separately as warn-only, not auto-blocked
    if url.lower().startswith("http://"):
        reasons.append("Download uses insecure HTTP")
    try:
        size = os.path.getsize(path)
        if hash_large_files or size <= 50 * 1024 * 1024:
            sha = file_hash(path, "sha256")
            md5 = file_hash(path, "md5")
            if sha in MALWARE_SHA256_SIGNATURES:
                reasons.append(f"Known malware SHA-256 match: {MALWARE_SHA256_SIGNATURES[sha]}")
            if md5 in MALWARE_MD5_SIGNATURES:
                reasons.append(f"Known malware MD5 match: {MALWARE_MD5_SIGNATURES[md5]}")
        with open(path, "rb") as f:
            sample = f.read(max(64, int(sample_kb)) * 1024)
        for pattern, label in SUSPICIOUS_DOWNLOAD_PATTERNS:
            if re.search(pattern, sample, re.IGNORECASE | re.DOTALL):
                reasons.append(label)
        if ext not in DANGEROUS_DOWNLOAD_EXTENSIONS and sample[:2] == b"MZ":
            reasons.append("File content is a Windows executable but the name does not look like one")
    except Exception as exc:
        reasons.append(f"Could not fully scan file: {exc}")
    return reasons

def find_update_info(page_url, text):
    decoded = html.unescape(text)
    version_patterns = [
        r"(?:LATEST_VERSION|VERSION|APP_VERSION|NEW_VERSION|LATEST|RELEASE)\s*[=:]\s*v?([0-9]+(?:\.[0-9]+){1,3})",
        r"\bv([0-9]+(?:\.[0-9]+){1,3})\b",
    ]
    latest = ""
    for pattern in version_patterns:
        m = re.search(pattern, decoded, re.IGNORECASE)
        if m:
            latest = m.group(1).strip()
            break

    candidates = []
    for m in re.finditer(r"https?://[^\s<>'\"]+?\.exe(?:\?[^\s<>'\"]*)?", decoded, re.IGNORECASE):
        candidates.append(m.group(0).rstrip(").,;"))
    for raw_line in decoded.splitlines():
        line = raw_line.strip()
        if ".exe" in line.lower() and not re.search(r"https?://", line, re.IGNORECASE):
            candidates.append(urljoin(page_url, line.split()[0].strip(" '\"")))
    for m in re.finditer(r"(?:href|src|data-[\w-]+)\s*=\s*['\"]([^'\"]+\.exe(?:\?[^'\"]*)?)['\"]", decoded, re.IGNORECASE):
        candidates.append(urljoin(page_url, html.unescape(m.group(1))))
    for m in re.finditer(r"(?:DOWNLOAD_URL|INSTALLER_URL|SETUP_URL|URL|LINK)\s*[=:]\s*([^\s<>'\"]+\.exe(?:\?[^\s<>'\"]*)?)", decoded, re.IGNORECASE):
        candidates.append(urljoin(page_url, m.group(1).strip()))

    seen = set()
    links = []
    for url in candidates:
        clean = url.strip().replace("&amp;", "&")
        key = clean.lower()
        if key not in seen:
            seen.add(key)
            links.append(clean)

    def link_score(url):
        name = safe_filename_from_url(url, "")
        link_version = extract_version(name)
        return (
            1 if "setup" in name.lower() or "installer" in name.lower() else 0,
            [int(x) for x in re.findall(r"\d+", link_version)[:4]] if link_version else [0],
            len(url),
        )

    if links:
        links.sort(key=link_score, reverse=True)

    sha = ""
    m = re.search(r"(?:SHA256|SHA-256|HASH|CHECKSUM)\s*[=:]\s*([a-fA-F0-9]{64})", decoded)
    if m:
        sha = m.group(1).lower()
    return latest, (links[0] if links else ""), sha

def load_update_history():
    try:
        if os.path.exists(UPDATE_HISTORY_PATH):
            with open(UPDATE_HISTORY_PATH, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_update_history(data):
    try:
        with open(UPDATE_HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

# ═══════════════════════════════════════════════════════════════
#  AUTO-UPDATER  (checks UPDATE_CHECK_URL for a download link)
# ═══════════════════════════════════════════════════════════════
class UpdateWorker(QThread):
    """
    Fetches the update page, looks for a line like:
        LATEST_VERSION=26.0.0
        DOWNLOAD_URL=https://example.com/SPS_Browser_Setup.exe
    If version > current, downloads the installer to Downloads folder,
    runs it silently, then deletes itself (the .py script).
    Emits update_available(version, url) or no_update() or error(msg).
    """
    update_available = pyqtSignal(str, str, str)   # (version, url, sha256)
    no_update        = pyqtSignal()
    error            = pyqtSignal(str)
    download_progress= pyqtSignal(int)        # 0-100
    install_ready    = pyqtSignal(str)        # installer path

    def __init__(self, current_version, update_url=None, settings=None, parent=None):
        super().__init__(parent)
        self.current_version = current_version
        self.update_url = update_url or UPDATE_CHECK_URL
        self.settings = settings or {}
        self._download_url   = ""
        self._new_version    = ""
        self._sha256         = ""

    def run(self):
        if hasattr(self, "_direct_download_url"):
            self.download_and_install(self._direct_download_url, getattr(self, "_direct_expected_sha256", ""))
            return
        if requests is None:
            self.error.emit("requests library not installed."); return
        try:
            resp = requests.get(self.update_url, timeout=20, headers={"User-Agent": f"{APP_NAME}/{VERSION}"})
            resp.raise_for_status()
            text = resp.text

            latest, dl_url, sha = find_update_info(self.update_url, text)

            if not dl_url:
                self.no_update.emit(); return

            has_explicit_version = bool(latest)
            if not latest:
                latest = extract_version(safe_filename_from_url(dl_url)) or "unknown"
            self._new_version = latest
            self._download_url = dl_url
            self._sha256 = sha

            if (not has_explicit_version and latest == "unknown") or version_gt(latest, self.current_version):
                self.update_available.emit(latest, dl_url, sha)
            else:
                self.no_update.emit()
        except Exception as e:
            self.error.emit(str(e))

    def _version_gt(self, a, b):
        return version_gt(a, b)

    def download_and_install(self, url, expected_sha256=""):
        """Download installer then launch it and remove this script."""
        if requests is None:
            self.error.emit("requests not installed"); return
        try:
            base_dir = self.settings.get("download_path") or tempfile.gettempdir()
            update_sub = self.settings.get("update_download_subfolder", "SPS Browser Updates")
            dl_dir = os.path.join(base_dir, safe_filename_from_url(update_sub, "SPS Browser Updates"))
            os.makedirs(dl_dir, exist_ok=True)
            dl_path = os.path.join(dl_dir, safe_filename_from_url(url, "SPS_Browser_Setup.exe"))
            resp = requests.get(url, stream=True, timeout=120, headers={"User-Agent": f"{APP_NAME}/{VERSION}"})
            resp.raise_for_status()
            total = int(resp.headers.get("content-length", 0))
            done  = 0
            with open(dl_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
                        done += len(chunk)
                        if total:
                            self.download_progress.emit(int(done/total*100))
            if expected_sha256:
                actual = file_hash(dl_path, "sha256")
                if actual.lower() != expected_sha256.lower():
                    try: os.remove(dl_path)
                    except Exception: pass
                    self.error.emit("Update hash check failed. Installer was deleted.")
                    return
            hist = load_update_history()
            hist.update({
                "last_downloaded_version": self._new_version,
                "last_installer": dl_path,
                "last_url": url,
                "last_sha256": expected_sha256,
                "last_download_time": str(datetime.datetime.now()),
            })
            save_update_history(hist)
            self.install_ready.emit(dl_path)
        except Exception as e:
            self.error.emit(str(e))

class UpdateInstallerThread(QThread):
    """Runs the Inno Setup installer silently."""
    finished = pyqtSignal()
    def __init__(self, installer_path, settings=None, parent=None):
        super().__init__(parent)
        self.installer_path = installer_path
        self.settings = settings or {}

    def run(self):
        try:
            if platform.system() == "Windows":
                args = [self.installer_path]
                if self.settings.get("silent_update_install", True):
                    args += ["/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/SP-", "/CLOSEAPPLICATIONS", "/RESTARTAPPLICATIONS"]
                if self.settings.get("create_desktop_shortcut_on_update", True):
                    args.append("/MERGETASKS=desktopicon")
                proc = subprocess.Popen(args, shell=False)
                proc.wait()
                if not self.settings.get("update_keep_installer_copy", False):
                    try:
                        os.remove(self.installer_path)
                    except Exception:
                        pass
            elif platform.system() == "Linux":
                subprocess.Popen(["bash", self.installer_path])
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", self.installer_path])
            time.sleep(3)
        except Exception:
            pass
        self.finished.emit()

class UpdateDialog(QDialog):
    def __init__(self, version, url, sha256, theme, parent=None):
        super().__init__(parent)
        self.url   = url
        self.sha256 = sha256
        self.theme = theme
        self.settings = parent.settings_data if parent and hasattr(parent, "settings_data") else DEFAULT_SETTINGS
        self._worker = parent._update_worker if parent and hasattr(parent,"_update_worker") else None
        t = theme
        self.setWindowTitle("🆕 Update Available")
        self.resize(460, 300)
        self.setStyleSheet(f"background:{t['bg_primary']}; color:{t['text_primary']};")
        lay = QVBoxLayout(self)
        ico = QLabel("🆕"); ico.setStyleSheet("font-size:48px;"); ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(ico)
        title = QLabel(f"SPS Browser Pro {version} is available!")
        title.setStyleSheet(f"font-size:18px; font-weight:700; color:{t['accent']}; padding:8px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)
        verify = "SHA-256 verification available." if sha256 else "No SHA-256 hash found on the update page."
        sub = QLabel("A new version is ready. SPS will download the installer, verify it when possible,\n"
                     "then run your Inno Setup installer silently in the background.\n\n"
                     f"{verify}\n{url}")
        sub.setWordWrap(True)
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color:{t['text_secondary']}; font-size:13px; padding:6px;")
        lay.addWidget(sub)
        self.progress = QProgressBar()
        self.progress.setRange(0,100); self.progress.hide()
        self.progress.setStyleSheet(f"""
            QProgressBar {{ border:1px solid {t['border']}; border-radius:6px; height:14px; text-align:center; }}
            QProgressBar::chunk {{ background:{t['accent']}; border-radius:5px; }}
        """)
        lay.addWidget(self.progress)
        self.status_lbl = QLabel("")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet(f"color:{t['text_secondary']}; font-size:11px;")
        lay.addWidget(self.status_lbl)
        btn_row = QHBoxLayout()
        self.install_btn = QPushButton("⬇️ Download & Install Now")
        self.install_btn.setStyleSheet(f"background:{t['accent']}; color:white; border-radius:8px; padding:10px 22px; font-weight:700;")
        self.install_btn.clicked.connect(self._start_download)
        later_btn = QPushButton("Later")
        later_btn.setStyleSheet(f"background:{t['bg_tertiary']}; color:{t['text_primary']}; border-radius:8px; padding:10px 22px;")
        later_btn.clicked.connect(self.reject)
        btn_row.addWidget(self.install_btn); btn_row.addWidget(later_btn)
        lay.addLayout(btn_row)

    def _start_download(self):
        self.install_btn.setEnabled(False)
        self.progress.show()
        self.status_lbl.setText("Downloading update…")
        self._worker2 = UpdateWorker(VERSION, self.url, self.settings)
        self._worker2._direct_download_url = self.url
        self._worker2._direct_expected_sha256 = self.sha256 if self.settings.get("verify_update_hash", True) else ""
        self._worker2.download_progress.connect(self.progress.setValue)
        self._worker2.install_ready.connect(self._on_ready)
        self._worker2.error.connect(lambda e: (self.status_lbl.setText(f"Error: {e}"),
                                                self.install_btn.setEnabled(True)))
        self._worker2.start()

    def _on_ready(self, path):
        self.status_lbl.setText("Installing… browser will close.")
        self._installer_thread = UpdateInstallerThread(path, self.settings, self)
        self._installer_thread.finished.connect(lambda: QApplication.instance().quit())
        self._installer_thread.start()

class SafeDownloadWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str, str, list)
    error = pyqtSignal(str)

    def __init__(self, url, filename, sample_kb=512, hash_large_files=True, parent=None):
        super().__init__(parent)
        self.url = url
        self.filename = filename or safe_filename_from_url(url)
        self.sample_kb = sample_kb
        self.hash_large_files = hash_large_files

    def run(self):
        if requests is None:
            self.error.emit("requests library is not installed.")
            return
        try:
            temp_name = f"sps_scan_{int(time.time())}_{safe_filename_from_url(self.url, self.filename)}"
            temp_path = os.path.join(tempfile.gettempdir(), temp_name)
            with requests.get(self.url, stream=True, timeout=120, headers={"User-Agent": f"{APP_NAME}/{VERSION}"}) as resp:
                resp.raise_for_status()
                total = int(resp.headers.get("content-length", 0))
                done = 0
                with open(temp_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=131072):
                        if chunk:
                            f.write(chunk)
                            done += len(chunk)
                            if total:
                                self.progress.emit(int(done / total * 100))
            reasons = analyze_download(temp_path, self.url, self.filename, self.sample_kb, self.hash_large_files)
            self.finished.emit(temp_path, self.filename, reasons)
        except Exception as exc:
            self.error.emit(str(exc))

# ═══════════════════════════════════════════════════════════════
#  TOGGLE SWITCH WIDGET
# ═══════════════════════════════════════════════════════════════
class ToggleSwitch(QWidget):
    toggled = pyqtSignal(bool)
    def __init__(self, checked=False, accent="#1a73e8", parent=None):
        super().__init__(parent)
        self._checked = checked; self._accent = accent
        self.setFixedSize(48,26); self.setCursor(Qt.CursorShape.PointingHandCursor)
    def isChecked(self): return self._checked
    def setChecked(self, val): self._checked=val; self.update()
    def mousePressEvent(self, e):
        self._checked = not self._checked; self.update(); self.toggled.emit(self._checked)
    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor(self._accent) if self._checked else QColor("#ccc")))
        p.setPen(Qt.PenStyle.NoPen); p.drawRoundedRect(0,3,48,20,10,10)
        p.setBrush(QBrush(QColor("white"))); p.drawEllipse(26 if self._checked else 4,3,20,20)
        p.end()

# ═══════════════════════════════════════════════════════════════
#  PRIVACY INTERCEPTOR
# ═══════════════════════════════════════════════════════════════
class PrivacyInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, settings_ref, parent=None):
        super().__init__(parent)
        self.s = settings_ref
        self.blocked_trackers = 0; self.blocked_ads = 0
        self.blocked_crypto   = 0; self.total_blocked = 0
        self.blocked_social   = 0

    def interceptRequest(self, info):
        url = info.requestUrl().toString().lower()
        blocked = False
        if self.s.get("tracking_protection") and any(d in url for d in TRACKER_DOMAINS):
            blocked=True; self.blocked_trackers+=1
        if self.s.get("block_social_trackers") and any(d in url for d in SOCIAL_TRACKER_DOMAINS):
            blocked=True; self.blocked_social+=1
        if self.s.get("block_cryptomining") and any(d in url for d in CRYPTO_MINING_DOMAINS):
            blocked=True; self.blocked_crypto+=1
        if self.s.get("ad_blocker"):
            ad_patterns=["/ads/","/ad/","/advert/","banner","/popup/","doubleclick",
                         "adnxs.com","googlesyndication","adsystem","adtech","adserver",
                         "pagead","sponsor","promo","banner_ad"]
            if any(p in url for p in ad_patterns):
                blocked=True; self.blocked_ads+=1
        if self.s.get("do_not_track"):
            info.setHttpHeader(b"DNT", b"1")
        ua = self.s.get("user_agent","Default")
        if ua != "Default" and ua in USER_AGENTS:
            info.setHttpHeader(b"User-Agent", USER_AGENTS[ua].encode())
        # V26: ETag tracking prevention
        if self.s.get("block_etag_tracking", True):
            info.setHttpHeader(b"If-None-Match", b"")
            info.setHttpHeader(b"If-Modified-Since", b"")
        # V26: Referrer stripping on cross-origin
        if self.s.get("block_referrer_header", True):
            ref_url = info.requestUrl().toString()
            init_url = ""
            try: init_url = info.initiator().toString() if hasattr(info,"initiator") else ""
            except Exception: pass
            if init_url and urlparse(init_url).netloc != urlparse(ref_url).netloc:
                info.setHttpHeader(b"Referer", b"")
        # V26: Language spoofing
        if self.s.get("spoof_language", False):
            info.setHttpHeader(b"Accept-Language", b"en-US,en;q=0.9")
        if blocked:
            self.total_blocked+=1; info.block(True)

# ═══════════════════════════════════════════════════════════════
#  WEB PAGE
# ═══════════════════════════════════════════════════════════════
class WebPage(QWebEnginePage):
    def __init__(self, profile, main_window, parent=None):
        super().__init__(profile, main_window)
        self.main_window = main_window
    def createWindow(self, _type):
        tab = self.main_window.add_new_tab()
        return tab.page()
    def acceptNavigationRequest(self, url, nav_type, isMainFrame):
        if url.scheme() == "sps":
            self.main_window.handle_sps_action(url)
            return False
        return super().acceptNavigationRequest(url, nav_type, isMainFrame)
    def javaScriptConsoleMessage(self, level, msg, line, src):
        pass

# ═══════════════════════════════════════════════════════════════
#  BROWSER TAB
# ═══════════════════════════════════════════════════════════════
class BrowserTab(QWebEngineView):
    def __init__(self, profile, main_window, parent=None):
        super().__init__(parent)
        self.main_window   = main_window
        self._last_active  = time.time()
        page = WebPage(profile, main_window, self)
        self.setPage(page)
        self._apply_settings()

    def _apply_settings(self):
        s = load_settings(CURRENT_PROFILE_NAME)
        st = self.settings()
        st.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled,              s["js_enabled"])
        st.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled,                 s["plugins_enabled"])
        st.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled,            s["storage_enabled"])
        st.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages,                 s["load_images"])
        st.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows,       s["js_popups"])
        st.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled,       s["fullscreen"])
        st.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent,    s["insecure_content"])
        st.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled,             s["dns_prefetch"])
        st.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled,          s["smooth_scroll"])
        st.setAttribute(QWebEngineSettings.WebAttribute.ErrorPageEnabled,               s["error_pages"])
        st.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls,s["local_remote_access"])
        st.setAttribute(QWebEngineSettings.WebAttribute.XSSAuditingEnabled,             s["xss_auditing"])
        self.setZoomFactor(s["zoom_factor"])

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        menu.addSeparator()
        menu.addAction("Open in New Tab",    lambda: self.main_window.add_new_tab(self.url(),"New Tab",False,not self.main_window.settings_data.get("open_links_in_background",False)))
        menu.addAction("Open in New Window", self._open_new_window)
        menu.addAction("Save Page As…",      self._save_page)
        menu.addAction("Inspect Element",    self.main_window.open_dev_tools)
        menu.addAction("Add to Reading List",self._add_reading_list)
        menu.exec(event.globalPos())

    def _open_new_window(self):
        w = MainWindow(CURRENT_PROFILE_NAME); w.show()
        w.add_new_tab(self.url())

    def _save_page(self):
        path, _ = QFileDialog.getSaveFileName(self,"Save Page","","HTML (*.html);;All (*.*)")
        if path: self.page().save(path)

    def _add_reading_list(self):
        self.main_window.add_to_reading_list(
            self.url().toString(), self.page().title())

# ═══════════════════════════════════════════════════════════════
#  DOWNLOAD ITEM WIDGET
# ═══════════════════════════════════════════════════════════════
class DownloadItemWidget(QFrame):
    def __init__(self, download, theme, parent=None):
        super().__init__(parent)
        self.download = download; self.theme = theme
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self._build_ui()
        download.receivedBytesChanged.connect(self._update)
        download.stateChanged.connect(self._state_changed)

    def _build_ui(self):
        t = self.theme
        self.setStyleSheet(f"""
            QFrame{{background:{t['bg_secondary']};border:1px solid {t['border']};
                    border-radius:10px;margin:4px;padding:10px;}}
            QPushButton{{background:{t['bg_tertiary']};color:{t['text_primary']};
                         border:none;border-radius:6px;padding:5px 12px;}}
            QPushButton:hover{{background:{t['hover']};}}
        """)
        lay = QVBoxLayout(self)
        top = QHBoxLayout()
        self.name_lbl   = QLabel(self.download.downloadFileName())
        self.name_lbl.setStyleSheet(f"font-weight:600;font-size:13px;color:{t['text_primary']};")
        top.addWidget(self.name_lbl,1)
        self.status_lbl = QLabel("Starting…")
        self.status_lbl.setStyleSheet(f"color:{t['text_secondary']};font-size:11px;")
        top.addWidget(self.status_lbl)
        lay.addLayout(top)
        self.bar = QProgressBar(); self.bar.setRange(0,100)
        self.bar.setStyleSheet(f"""
            QProgressBar{{border:1px solid {t['border']};border-radius:5px;height:8px;text-align:center;}}
            QProgressBar::chunk{{background:{t['accent']};border-radius:4px;}}
        """)
        lay.addWidget(self.bar)
        btn_row = QHBoxLayout()
        self.pause_btn = QPushButton("⏸ Pause"); self.pause_btn.clicked.connect(self._toggle_pause)
        self.cancel_btn = QPushButton("✕ Cancel")
        self.cancel_btn.setStyleSheet(f"background:{t['danger']};color:white;")
        self.cancel_btn.clicked.connect(self._cancel)
        self.open_btn = QPushButton("📂 Open"); self.open_btn.clicked.connect(self._open_file)
        self.open_btn.hide()
        self.folder_btn = QPushButton("🗂 Folder"); self.folder_btn.clicked.connect(self._open_folder)
        self.folder_btn.hide()
        for b in [self.pause_btn,self.cancel_btn,self.open_btn,self.folder_btn]:
            btn_row.addWidget(b)
        btn_row.addStretch()
        lay.addLayout(btn_row)

    def _update(self):
        pos=self.download.receivedBytes(); total=self.download.totalBytes()
        if total>0:
            pct=int(pos/total*100); self.bar.setValue(pct)
            speed = pos/(time.time()+0.001)
            self.status_lbl.setText(f"{pct}%  •  {pos//1024}/{total//1024} KB")

    def _toggle_pause(self):
        if self.download.isPaused():
            self.download.resume(); self.pause_btn.setText("⏸ Pause")
        else:
            self.download.pause();  self.pause_btn.setText("▶ Resume")

    def _cancel(self):
        self.download.cancel(); self.status_lbl.setText("Cancelled")
        self.pause_btn.setEnabled(False); self.cancel_btn.setEnabled(False)

    def _open_file(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(
            os.path.join(self.download.downloadDirectory(), self.download.downloadFileName())))

    def _open_folder(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.download.downloadDirectory()))

    def _state_changed(self, state):
        S = QWebEngineDownloadRequest.DownloadState
        if state == S.DownloadCompleted:
            self.status_lbl.setText("✅ Completed")
            self.status_lbl.setStyleSheet(f"color:{self.theme['success']};")
            self.pause_btn.setEnabled(False); self.cancel_btn.setEnabled(False)
            self.open_btn.show(); self.folder_btn.show()
        elif state == S.DownloadCancelled:
            self.status_lbl.setText("❌ Cancelled")
            self.status_lbl.setStyleSheet(f"color:{self.theme['danger']};")
        elif state == S.DownloadInterrupted:
            self.status_lbl.setText("⚠️ Interrupted")
            self.status_lbl.setStyleSheet(f"color:{self.theme['warning']};")

# ═══════════════════════════════════════════════════════════════
#  DOWNLOAD MANAGER DIALOG
# ═══════════════════════════════════════════════════════════════
class DownloadManagerDialog(QDialog):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.setWindowTitle("SPS Download Manager")
        self.resize(650, 520)
        t = theme
        self.setStyleSheet(f"background:{t['bg_primary']}; color:{t['text_primary']};")
        lay = QVBoxLayout(self)
        hdr = QLabel("📥 Downloads")
        hdr.setStyleSheet(f"font-size:20px; font-weight:700; color:{t['text_primary']}; padding:10px;")
        lay.addWidget(hdr)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.c_lay = QVBoxLayout(self.container)
        self.c_lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.container)
        lay.addWidget(self.scroll)
        clr = QPushButton("Clear All")
        clr.setStyleSheet(f"background:{t['danger']}; color:white; border-radius:6px; padding:8px 18px;")
        clr.clicked.connect(self._clear_all)
        lay.addWidget(clr, alignment=Qt.AlignmentFlag.AlignRight)

    def add_download(self, download):
        w = DownloadItemWidget(download, self.theme, self)
        self.c_lay.addWidget(w)
        self.show(); self.raise_()

    def _clear_all(self):
        while self.c_lay.count():
            item = self.c_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

# ═══════════════════════════════════════════════════════════════
#  PASSWORD MANAGER
# ═══════════════════════════════════════════════════════════════
class PasswordManager:
    def __init__(self, profile_name):
        self.path=os.path.join(get_profile_path(profile_name),"passwords.json")
        self._data=self._load()
    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path) as f: return json.load(f)
            except: pass
        return []
    def _save(self):
        with open(self.path,"w") as f: json.dump(self._data,f,indent=2)
    def add(self,site,username,password):
        entry={"id":secrets.token_hex(8),"site":site,"username":username,
               "password":password,"added":str(datetime.datetime.now())}
        self._data.append(entry); self._save(); return entry
    def get_all(self): return list(self._data)
    def delete(self,eid):
        self._data=[e for e in self._data if e.get("id")!=eid]; self._save()
    def search(self,query):
        q=query.lower()
        return [e for e in self._data if q in e.get("site","").lower() or q in e.get("username","").lower()]
    def update(self,eid,**kw):
        for e in self._data:
            if e.get("id")==eid: e.update(kw)
        self._save()
    def check_strength(self, pw):
        score=0
        if len(pw)>=8:  score+=1
        if len(pw)>=16: score+=1
        if re.search(r'[A-Z]',pw): score+=1
        if re.search(r'[a-z]',pw): score+=1
        if re.search(r'\d',pw):    score+=1
        if re.search(r'[^A-Za-z0-9]',pw): score+=1
        if score<=2: return "Weak","#d93025"
        if score<=4: return "Medium","#f9ab00"
        return "Strong","#188038"

class PasswordManagerDialog(QDialog):
    def __init__(self, pm, theme, parent=None):
        super().__init__(parent)
        self.pm=pm; self.theme=theme
        self.setWindowTitle("🔐 SPS Password Manager"); self.resize(850,620)
        t=theme
        self.setStyleSheet(f"""
            QDialog{{background:{t['bg_primary']};}}
            QLabel{{color:{t['text_primary']};}}
            QLineEdit{{background:{t['bg_secondary']};color:{t['text_primary']};
                       border:1px solid {t['border']};border-radius:8px;padding:8px 12px;}}
            QPushButton{{background:{t['accent']};color:white;border:none;
                         border-radius:8px;padding:8px 18px;font-weight:600;}}
            QPushButton:hover{{background:{t['accent']}dd;}}
            QTableWidget{{background:{t['bg_secondary']};color:{t['text_primary']};
                          gridline-color:{t['border']};border:1px solid {t['border']};border-radius:8px;}}
            QHeaderView::section{{background:{t['bg_tertiary']};color:{t['text_primary']};
                                  padding:8px;border:none;font-weight:600;}}
        """)
        self._build_ui(); self._refresh()

    def _build_ui(self):
        t=self.theme; lay=QVBoxLayout(self); lay.setSpacing(12)
        hdr=QLabel("🔐 Password Manager")
        hdr.setStyleSheet(f"font-size:22px;font-weight:700;color:{t['text_primary']};padding:10px 0;")
        lay.addWidget(hdr)
        sr=QHBoxLayout()
        self.search_bar=QLineEdit(); self.search_bar.setPlaceholderText("🔍 Search passwords…")
        self.search_bar.textChanged.connect(self._refresh); sr.addWidget(self.search_bar,1)
        gen_btn=QPushButton("⚡ Generate")
        gen_btn.setStyleSheet(f"background:{t['bg_tertiary']};color:{t['text_primary']};border:1px solid {t['border']};")
        gen_btn.clicked.connect(self._generate_pw); sr.addWidget(gen_btn)
        exp_btn=QPushButton("📤 Export")
        exp_btn.setStyleSheet(f"background:{t['bg_tertiary']};color:{t['text_primary']};border:1px solid {t['border']};")
        exp_btn.clicked.connect(self._export); sr.addWidget(exp_btn)
        lay.addLayout(sr)
        self.table=QTableWidget(0,5)
        self.table.setHorizontalHeaderLabels(["Site","Username","Password","Strength","Actions"])
        for i,m in enumerate([QHeaderView.ResizeMode.Stretch,QHeaderView.ResizeMode.Stretch,
                               QHeaderView.ResizeMode.ResizeToContents,
                               QHeaderView.ResizeMode.ResizeToContents,
                               QHeaderView.ResizeMode.ResizeToContents]):
            self.table.horizontalHeader().setSectionResizeMode(i,m)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        lay.addWidget(self.table,1)
        fb=QGroupBox("Add New Entry")
        fb.setStyleSheet(f"QGroupBox{{color:{t['text_primary']};border:1px solid {t['border']};"
                         f"border-radius:10px;margin-top:12px;padding:12px;}}"
                         f"QGroupBox::title{{subcontrol-origin:margin;padding:0 6px;}}")
        form=QHBoxLayout(fb)
        self.f_site=QLineEdit(); self.f_site.setPlaceholderText("Site / URL")
        self.f_user=QLineEdit(); self.f_user.setPlaceholderText("Username")
        self.f_pass=QLineEdit(); self.f_pass.setPlaceholderText("Password")
        self.f_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.f_pass.textChanged.connect(self._show_strength)
        self.strength_lbl=QLabel(""); self.strength_lbl.setFixedWidth(60)
        add_btn=QPushButton("➕ Add"); add_btn.clicked.connect(self._add_entry)
        for w in [self.f_site,self.f_user,self.f_pass,self.strength_lbl]: form.addWidget(w,1 if w!=self.strength_lbl else 0)
        form.addWidget(add_btn); lay.addWidget(fb)

    def _show_strength(self, pw):
        label,color=self.pm.check_strength(pw)
        self.strength_lbl.setText(label)
        self.strength_lbl.setStyleSheet(f"color:{color};font-weight:600;font-size:11px;")

    def _refresh(self):
        query=self.search_bar.text()
        entries=self.pm.search(query) if query else self.pm.get_all()
        t=self.theme; self.table.setRowCount(0)
        for e in entries:
            row=self.table.rowCount(); self.table.insertRow(row)
            self.table.setItem(row,0,QTableWidgetItem(e.get("site","")))
            self.table.setItem(row,1,QTableWidgetItem(e.get("username","")))
            pw_item=QTableWidgetItem("••••••••")
            pw_item.setData(Qt.ItemDataRole.UserRole,e.get("password",""))
            self.table.setItem(row,2,pw_item)
            strength,color=self.pm.check_strength(e.get("password",""))
            s_item=QTableWidgetItem(strength); s_item.setForeground(QColor(color))
            self.table.setItem(row,3,s_item)
            cell_w=QWidget(); cell_l=QHBoxLayout(cell_w)
            cell_l.setContentsMargins(4,2,4,2); cell_l.setSpacing(4)
            for icon,tip,fn in [
                ("👁","Show/hide",partial(self._toggle_reveal,row,pw_item,e)),
                ("📋","Copy",partial(self._copy_password,e.get("password",""))),
                ("🗑","Delete",partial(self._delete_entry,e.get("id"))),
            ]:
                b=QPushButton(icon); b.setFixedSize(30,26)
                b.setStyleSheet(f"background:{t['bg_tertiary']};color:{t['text_primary']};border-radius:4px;padding:0;")
                b.setToolTip(tip); b.clicked.connect(fn); cell_l.addWidget(b)
            self.table.setCellWidget(row,4,cell_w)

    def _toggle_reveal(self,row,pw_item,entry,*_):
        pw_item.setText(entry.get("password","") if pw_item.text()=="••••••••" else "••••••••")

    def _copy_password(self,pw,*_):
        QApplication.clipboard().setText(pw)

    def _delete_entry(self,eid,*_):
        if QMessageBox.question(self,"Delete","Delete this password entry?")==QMessageBox.StandardButton.Yes:
            self.pm.delete(eid); self._refresh()

    def _add_entry(self):
        site=self.f_site.text().strip(); user=self.f_user.text().strip(); pw=self.f_pass.text()
        if not site or not user or not pw:
            QMessageBox.warning(self,"Missing Fields","Please fill in all fields."); return
        self.pm.add(site,user,pw)
        self.f_site.clear(); self.f_user.clear(); self.f_pass.clear(); self._refresh()

    def _generate_pw(self):
        t=self.theme; dlg=QDialog(self); dlg.setWindowTitle("Generate Password")
        dlg.setStyleSheet(f"background:{t['bg_primary']};color:{t['text_primary']};")
        lay=QVBoxLayout(dlg)
        lr=QHBoxLayout(); lr.addWidget(QLabel("Length:"))
        spin=QSpinBox(); spin.setRange(8,64); spin.setValue(16); lr.addWidget(spin)
        lay.addLayout(lr)
        sym_cb=QCheckBox("Include symbols"); sym_cb.setChecked(True); lay.addWidget(sym_cb)
        num_cb=QCheckBox("Include numbers"); num_cb.setChecked(True); lay.addWidget(num_cb)
        result=QLineEdit(); result.setReadOnly(True); lay.addWidget(result)
        self._pw_strength_lbl=QLabel(""); lay.addWidget(self._pw_strength_lbl)
        def regen():
            pw=generate_password(spin.value(),sym_cb.isChecked())
            result.setText(pw)
            lbl,col=self.pm.check_strength(pw)
            self._pw_strength_lbl.setText(f"Strength: {lbl}")
            self._pw_strength_lbl.setStyleSheet(f"color:{col};font-weight:700;")
        br=QHBoxLayout()
        for txt,fn in [("🔄 Generate",regen),
                       ("📋 Copy",lambda: QApplication.clipboard().setText(result.text())),
                       ("✓ Use",lambda: (self.f_pass.setText(result.text()),dlg.accept()))]:
            b=QPushButton(txt); b.clicked.connect(fn); br.addWidget(b)
        lay.addLayout(br); regen(); dlg.exec()

    def _export(self):
        path,_=QFileDialog.getSaveFileName(self,"Export Passwords","passwords.csv","CSV (*.csv)")
        if path:
            with open(path,"w") as f:
                f.write("site,username,password\n")
                for e in self.pm.get_all():
                    f.write(f"{e.get('site','')},{e.get('username','')},{e.get('password','')}\n")
            QMessageBox.information(self,"Exported",f"Passwords exported to {path}")

# ═══════════════════════════════════════════════════════════════
#  NOTES / SCRATCHPAD
# ═══════════════════════════════════════════════════════════════
class NotesDialog(QDialog):
    def __init__(self, profile_name, theme, parent=None):
        super().__init__(parent)
        self.profile_name=profile_name; self.theme=theme
        self.path=os.path.join(NOTES_DIR,f"{profile_name}_notes.json")
        self._notes=self._load()
        t=theme
        self.setWindowTitle("📝 SPS Notes"); self.resize(800,580)
        self.setStyleSheet(f"background:{t['bg_primary']};color:{t['text_primary']};")
        self._build_ui()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path) as f: return json.load(f)
            except: pass
        return []

    def _save(self):
        with open(self.path,"w") as f: json.dump(self._notes,f,indent=2)

    def _build_ui(self):
        t=self.theme; lay=QHBoxLayout(self)
        # Sidebar note list
        left=QWidget(); left.setFixedWidth(220)
        left.setStyleSheet(f"background:{t['sidebar_bg']};border-right:1px solid {t['border']};")
        ll=QVBoxLayout(left); ll.setContentsMargins(8,8,8,8)
        lbl=QLabel("📝 My Notes")
        lbl.setStyleSheet(f"font-size:16px;font-weight:700;color:{t['text_primary']};padding:8px 0;")
        ll.addWidget(lbl)
        new_btn=QPushButton("＋ New Note")
        new_btn.setStyleSheet(f"background:{t['accent']};color:white;border-radius:8px;padding:8px;")
        new_btn.clicked.connect(self._new_note); ll.addWidget(new_btn)
        self.note_list=QListWidget()
        self.note_list.setStyleSheet(f"background:transparent;border:none;color:{t['text_primary']};")
        self.note_list.itemClicked.connect(self._select_note)
        ll.addWidget(self.note_list,1)
        del_btn=QPushButton("🗑 Delete Note")
        del_btn.setStyleSheet(f"background:{t['danger']};color:white;border-radius:8px;padding:8px;")
        del_btn.clicked.connect(self._delete_note); ll.addWidget(del_btn)
        lay.addWidget(left)
        # Editor
        right=QWidget(); rl=QVBoxLayout(right); rl.setContentsMargins(12,12,12,12)
        self.title_edit=QLineEdit(); self.title_edit.setPlaceholderText("Note title…")
        self.title_edit.setStyleSheet(f"font-size:16px;font-weight:600;background:{t['bg_secondary']};"
                                      f"color:{t['text_primary']};border:none;border-radius:8px;padding:8px 12px;")
        self.title_edit.textChanged.connect(self._auto_save)
        rl.addWidget(self.title_edit)
        self.editor=QTextEdit()
        self.editor.setPlaceholderText("Start writing your note…")
        self.editor.setStyleSheet(f"background:{t['bg_secondary']};color:{t['text_primary']};"
                                  f"border:none;border-radius:8px;padding:12px;font-size:14px;")
        self.editor.textChanged.connect(self._auto_save)
        rl.addWidget(self.editor,1)
        # Format toolbar
        fmt=QHBoxLayout()
        for txt,fn in [("B",lambda: self.editor.setFontWeight(700)),
                       ("I",lambda: self.editor.setFontItalic(True)),
                       ("U",lambda: self.editor.setFontUnderline(True)),
                       ("📋 Copy All",lambda: QApplication.clipboard().setText(self.editor.toPlainText())),
                       ("💾 Export TXT",self._export_txt)]:
            b=QPushButton(txt); b.setStyleSheet(f"background:{t['bg_tertiary']};color:{t['text_primary']};border-radius:6px;padding:6px 12px;")
            b.clicked.connect(fn); fmt.addWidget(b)
        fmt.addStretch(); rl.addLayout(fmt)
        lay.addWidget(right,1)
        self._refresh_list()
        if self._notes: self._select_note_by_idx(0)

    def _refresh_list(self):
        self.note_list.clear()
        for n in self._notes:
            self.note_list.addItem(n.get("title","Untitled"))

    def _new_note(self):
        self._notes.append({"id":secrets.token_hex(6),"title":"New Note","content":"",
                             "created":str(datetime.datetime.now())})
        self._save(); self._refresh_list(); self._select_note_by_idx(len(self._notes)-1)

    def _select_note(self,item):
        self._select_note_by_idx(self.note_list.row(item))

    def _select_note_by_idx(self,idx):
        if 0<=idx<len(self._notes):
            self._current_idx=idx; n=self._notes[idx]
            self.title_edit.blockSignals(True); self.editor.blockSignals(True)
            self.title_edit.setText(n.get("title","")); self.editor.setPlainText(n.get("content",""))
            self.title_edit.blockSignals(False); self.editor.blockSignals(False)
            self.note_list.setCurrentRow(idx)

    def _auto_save(self):
        if not hasattr(self,"_current_idx"): return
        n=self._notes[self._current_idx]
        n["title"]=self.title_edit.text() or "Untitled"
        n["content"]=self.editor.toPlainText()
        self._save(); self._refresh_list(); self.note_list.setCurrentRow(self._current_idx)

    def _delete_note(self):
        if not hasattr(self,"_current_idx"): return
        if QMessageBox.question(self,"Delete","Delete this note?")==QMessageBox.StandardButton.Yes:
            self._notes.pop(self._current_idx)
            self._save(); self._refresh_list()
            if self._notes: self._select_note_by_idx(0)
            else:
                self.title_edit.clear(); self.editor.clear()
                del self._current_idx

    def _export_txt(self):
        path,_=QFileDialog.getSaveFileName(self,"Export Note","note.txt","Text (*.txt)")
        if path:
            with open(path,"w") as f:
                f.write(self.title_edit.text()+"\n\n"+self.editor.toPlainText())

# ═══════════════════════════════════════════════════════════════
#  READING LIST
# ═══════════════════════════════════════════════════════════════
class ReadingListDialog(QDialog):
    open_url = pyqtSignal(str,str)
    def __init__(self, profile_name, theme, parent=None):
        super().__init__(parent)
        self.path=os.path.join(get_profile_path(profile_name),"reading_list.json")
        self.theme=theme
        t=theme; self.setWindowTitle("📚 Reading List"); self.resize(620,480)
        self.setStyleSheet(f"background:{t['bg_primary']};color:{t['text_primary']};")
        self._items=self._load()
        self._build_ui()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path) as f: return json.load(f)
            except: pass
        return []

    def _save(self):
        with open(self.path,"w") as f: json.dump(self._items,f,indent=2)

    def add_item(self,url,title):
        if any(i["url"]==url for i in self._items): return
        self._items.append({"url":url,"title":title or url,
                             "added":str(datetime.datetime.now()),"read":False})
        self._save()

    def _build_ui(self):
        t=self.theme; lay=QVBoxLayout(self)
        hdr=QLabel("📚 Reading List")
        hdr.setStyleSheet(f"font-size:20px;font-weight:700;color:{t['text_primary']};padding:10px 0;")
        lay.addWidget(hdr)
        self.lst=QListWidget()
        self.lst.setStyleSheet(f"background:{t['bg_secondary']};color:{t['text_primary']};"
                               f"border:1px solid {t['border']};border-radius:8px;")
        self._refresh()
        self.lst.itemDoubleClicked.connect(self._open_item)
        lay.addWidget(self.lst,1)
        br=QHBoxLayout()
        for txt,fn in [("🔖 Mark Read",self._mark_read),
                       ("🗑 Remove",self._remove),
                       ("Close",self.accept)]:
            b=QPushButton(txt)
            b.setStyleSheet(f"background:{t['accent']};color:white;border-radius:8px;padding:8px 16px;")
            b.clicked.connect(fn); br.addWidget(b)
        br.addStretch(); lay.addLayout(br)

    def _refresh(self):
        self.lst.clear()
        for i in self._items:
            read_mark="✅ " if i.get("read") else "📖 "
            item=QListWidgetItem(read_mark+i.get("title",""))
            item.setData(Qt.ItemDataRole.UserRole,i["url"]); self.lst.addItem(item)

    def _open_item(self,item):
        self.open_url.emit(item.data(Qt.ItemDataRole.UserRole),item.text())
        self.accept()

    def _mark_read(self):
        item=self.lst.currentItem()
        if item:
            url=item.data(Qt.ItemDataRole.UserRole)
            for i in self._items:
                if i["url"]==url: i["read"]=True
            self._save(); self._refresh()

    def _remove(self):
        item=self.lst.currentItem()
        if item:
            url=item.data(Qt.ItemDataRole.UserRole)
            self._items=[i for i in self._items if i["url"]!=url]
            self._save(); self._refresh()

# ═══════════════════════════════════════════════════════════════
#  COOKIE MANAGER
# ═══════════════════════════════════════════════════════════════
class CookieManagerDialog(QDialog):
    def __init__(self, profile, theme, parent=None):
        super().__init__(parent)
        self.browser_profile=profile; self.theme=theme
        t=theme; self.setWindowTitle("🍪 Cookie Manager"); self.resize(650,500)
        self.setStyleSheet(f"background:{t['bg_primary']};color:{t['text_primary']};")
        lay=QVBoxLayout(self)
        hdr=QLabel("🍪 Cookie Manager")
        hdr.setStyleSheet(f"font-size:20px;font-weight:700;color:{t['text_primary']};padding:10px 0;")
        lay.addWidget(hdr)
        info=QLabel("Cookies are managed by the browser engine. Use the buttons below to control them.")
        info.setWordWrap(True)
        info.setStyleSheet(f"color:{t['text_secondary']};font-size:12px;padding:6px;")
        lay.addWidget(info)
        # Cookie store stats
        self.stats_lbl=QLabel("Loading…")
        self.stats_lbl.setStyleSheet(f"background:{t['bg_secondary']};border-radius:8px;padding:12px;"
                                     f"color:{t['text_primary']};font-size:14px;")
        lay.addWidget(self.stats_lbl)
        lay.addStretch()
        br=QHBoxLayout()
        clr_btn=QPushButton("🗑 Clear All Cookies")
        clr_btn.setStyleSheet(f"background:{t['danger']};color:white;border-radius:8px;padding:10px 18px;")
        clr_btn.clicked.connect(self._clear_all)
        ses_btn=QPushButton("🗑 Clear Session Cookies")
        ses_btn.setStyleSheet(f"background:{t['warning']};color:white;border-radius:8px;padding:10px 18px;")
        ses_btn.clicked.connect(self._clear_session)
        br.addWidget(ses_btn); br.addWidget(clr_btn)
        lay.addLayout(br)
        self._load_stats()

    def _load_stats(self):
        store=self.browser_profile.cookieStore()
        self.stats_lbl.setText("✅ Cookie store is active.\nUse clear buttons to manage cookies.")

    def _clear_all(self):
        if QMessageBox.question(self,"Clear Cookies","Delete ALL cookies? This will log you out of all sites.")==QMessageBox.StandardButton.Yes:
            self.browser_profile.cookieStore().deleteAllCookies()
            self.stats_lbl.setText("✅ All cookies cleared.")

    def _clear_session(self):
        self.browser_profile.cookieStore().deleteSessionCookies()
        self.stats_lbl.setText("✅ Session cookies cleared.")

# ═══════════════════════════════════════════════════════════════
#  SITE INFORMATION DIALOG
# ═══════════════════════════════════════════════════════════════
class SiteInfoDialog(QDialog):
    def __init__(self, url, title, theme, parent=None):
        super().__init__(parent)
        t=theme; self.setWindowTitle("🔍 Site Information"); self.resize(420,320)
        self.setStyleSheet(f"background:{t['bg_primary']};color:{t['text_primary']};")
        lay=QVBoxLayout(self)
        parsed=urlparse(url)
        rows=[("🔗 Full URL:", url),("🌐 Domain:", parsed.netloc or "—"),
              ("📂 Path:", parsed.path or "/"),("🔒 Protocol:", parsed.scheme.upper()),
              ("📄 Page Title:", title or "—")]
        is_https=url.startswith("https://")
        sec_lbl=QLabel("🔒 Connection is secure (HTTPS)" if is_https else "⚠️ Connection is NOT secure (HTTP)")
        sec_lbl.setStyleSheet(f"background:{'#e6f4ea' if is_https else '#fce8e6'};"
                              f"color:{'#188038' if is_https else '#d93025'};"
                              f"border-radius:8px;padding:10px;font-weight:600;")
        lay.addWidget(sec_lbl)
        for label,val in rows:
            row=QWidget()
            row.setStyleSheet(f"background:{t['bg_secondary']};border-radius:6px;margin:2px 0;")
            rh=QHBoxLayout(row); rh.setContentsMargins(10,8,10,8)
            l=QLabel(label); l.setStyleSheet(f"font-weight:600;color:{t['text_primary']};min-width:110px;")
            v=QLabel(str(val)[:60]); v.setStyleSheet(f"color:{t['text_secondary']};")
            v.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            rh.addWidget(l); rh.addWidget(v,1); lay.addWidget(row)
        cp=QPushButton("📋 Copy URL")
        cp.setStyleSheet(f"background:{t['accent']};color:white;border-radius:8px;padding:8px 16px;")
        cp.clicked.connect(lambda: QApplication.clipboard().setText(url))
        lay.addWidget(cp,alignment=Qt.AlignmentFlag.AlignRight)

# ═══════════════════════════════════════════════════════════════
#  EXTENSIONS MANAGER
# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════
#  V26 EXTENSION MANAGER (full install/manage/store/toolbar system)
# ═══════════════════════════════════════════════════════════════
class ExtensionManager:
    """Manages installed extensions (.json packages) plus legacy userscripts."""
    def __init__(self, profile_name):
        self.profile_name = profile_name
        self.scripts_path = os.path.join(get_profile_path(profile_name), "userscripts.json")
        self.ext_index_path = os.path.join(EXT_INSTALLED_DIR, "installed.json")
        self._scripts = self._load_scripts()
        self._extensions = self._load_extensions()

    def _load_scripts(self):
        if os.path.exists(self.scripts_path):
            try:
                with open(self.scripts_path) as f: return json.load(f)
            except: pass
        return []

    def _save_scripts(self):
        with open(self.scripts_path,"w") as f: json.dump(self._scripts, f, indent=2)

    def _load_extensions(self):
        if os.path.exists(self.ext_index_path):
            try:
                with open(self.ext_index_path) as f: return json.load(f)
            except: pass
        return []

    def _save_extensions(self):
        with open(self.ext_index_path,"w") as f: json.dump(self._extensions, f, indent=2)

    def get_all_scripts(self): return list(self._scripts)
    def get_all_extensions(self): return list(self._extensions)

    def add_script(self, name, match, type_, code, show_in_toolbar=False, toolbar_icon="🧩"):
        entry = {"id": secrets.token_hex(6), "name": name or "Unnamed",
                 "match": match or "*", "type": type_, "code": code,
                 "enabled": True, "show_in_toolbar": show_in_toolbar,
                 "toolbar_icon": toolbar_icon,
                 "added": str(datetime.datetime.now())}
        self._scripts.append(entry); self._save_scripts(); return entry

    def update_script(self, idx, **kw):
        if 0 <= idx < len(self._scripts):
            self._scripts[idx].update(kw); self._save_scripts()

    def remove_script(self, idx):
        if 0 <= idx < len(self._scripts):
            self._scripts.pop(idx); self._save_scripts()

    def toggle_script(self, idx):
        if 0 <= idx < len(self._scripts):
            self._scripts[idx]["enabled"] = not self._scripts[idx].get("enabled", True)
            self._save_scripts()

    def install_extension_from_file(self, path):
        """Install a .json extension package."""
        try:
            with open(path) as f: data = json.load(f)
            required = ["name", "code"]
            if not all(k in data for k in required):
                return None, "Extension package must have 'name' and 'code' fields."
            ext = {
                "id": secrets.token_hex(8),
                "name": data.get("name","Unknown"),
                "description": data.get("description",""),
                "version": data.get("version","1.0"),
                "author": data.get("author","Unknown"),
                "match": data.get("match","*"),
                "type": data.get("type","JavaScript"),
                "code": data.get("code",""),
                "icon": data.get("icon","🧩"),
                "show_in_toolbar": data.get("show_in_toolbar", False),
                "toolbar_action": data.get("toolbar_action",""),
                "enabled": True,
                "source": "file",
                "installed_at": str(datetime.datetime.now()),
            }
            # Save to installed extensions dir
            ext_path = os.path.join(EXT_INSTALLED_DIR, f"{ext['id']}.json")
            with open(ext_path,"w") as f: json.dump(ext, f, indent=2)
            self._extensions.append(ext); self._save_extensions()
            # Also add as userscript so it runs on pages
            self.add_script(ext["name"], ext["match"], ext["type"], ext["code"],
                            ext.get("show_in_toolbar", False), ext.get("icon","🧩"))
            return ext, None
        except Exception as e:
            return None, str(e)

    def install_extension_from_url(self, url, on_done, on_error):
        """Download and install a .json extension from a URL (async)."""
        if requests is None:
            on_error("requests library not installed."); return
        def _worker():
            try:
                resp = requests.get(url, timeout=30, headers={"User-Agent": f"{APP_NAME}/{VERSION}"})
                resp.raise_for_status()
                data = resp.json()
                ext, err = self._install_from_dict(data, source_url=url)
                if err: on_error(err)
                else: on_done(ext)
            except Exception as e:
                on_error(str(e))
        t = threading.Thread(target=_worker, daemon=True); t.start()

    def _install_from_dict(self, data, source_url=""):
        try:
            ext = {
                "id": secrets.token_hex(8),
                "name": data.get("name","Unknown"),
                "description": data.get("description",""),
                "version": data.get("version","1.0"),
                "author": data.get("author","Unknown"),
                "match": data.get("match","*"),
                "type": data.get("type","JavaScript"),
                "code": data.get("code",""),
                "icon": data.get("icon","🧩"),
                "show_in_toolbar": data.get("show_in_toolbar", False),
                "toolbar_action": data.get("toolbar_action",""),
                "enabled": True,
                "source": source_url or "store",
                "installed_at": str(datetime.datetime.now()),
            }
            ext_path = os.path.join(EXT_INSTALLED_DIR, f"{ext['id']}.json")
            with open(ext_path,"w") as f: json.dump(ext, f, indent=2)
            self._extensions.append(ext); self._save_extensions()
            self.add_script(ext["name"], ext["match"], ext["type"], ext["code"],
                            ext.get("show_in_toolbar", False), ext.get("icon","🧩"))
            return ext, None
        except Exception as e:
            return None, str(e)

    def uninstall_extension(self, ext_id):
        self._extensions = [e for e in self._extensions if e.get("id") != ext_id]
        self._save_extensions()
        # Remove matching userscript by name
        self._scripts = [s for s in self._scripts if s.get("id") != ext_id]
        self._save_scripts()
        # Delete file
        ext_path = os.path.join(EXT_INSTALLED_DIR, f"{ext_id}.json")
        try:
            if os.path.exists(ext_path): os.remove(ext_path)
        except: pass

    def toggle_extension(self, ext_id):
        for ext in self._extensions:
            if ext.get("id") == ext_id:
                ext["enabled"] = not ext.get("enabled", True)
        self._save_extensions()
        # Sync to userscripts
        for s in self._scripts:
            if s.get("name") == next((e["name"] for e in self._extensions if e["id"]==ext_id), None):
                s["enabled"] = next(e["enabled"] for e in self._extensions if e["id"]==ext_id)
        self._save_scripts()

    def get_toolbar_extensions(self):
        """Return installed extensions that should show a toolbar button (enabled only)."""
        result = []
        for ext in self._extensions:
            if ext.get("enabled", True) and ext.get("show_in_toolbar", False):
                result.append(ext)
        for s in self._scripts:
            if s.get("enabled", True) and s.get("show_in_toolbar", False):
                # Avoid duplicates with installed extensions
                if not any(e["name"]==s["name"] for e in result):
                    result.append(s)
        return result

    def get_scripts_for_url(self, url):
        result = []
        all_scripts = list(self._scripts)
        for s in all_scripts:
            if not s.get("enabled", True): continue
            pattern = s.get("match","*").replace(".", r"\.").replace("*",".*")
            try:
                if re.search(pattern, url): result.append(s)
            except: pass
        return result


class ExtensionsDialog(QDialog):
    """V26 full Extension Manager: manage, add custom, download from store."""
    extensions_changed = pyqtSignal()

    def __init__(self, profile_name, theme, ext_manager, parent=None):
        super().__init__(parent)
        self.profile_name = profile_name
        self.theme = theme
        self.ext_manager = ext_manager
        t = theme
        self.setWindowTitle("🧩 Extensions Manager")
        self.resize(920, 660)
        self.setStyleSheet(f"background:{t['bg_primary']};color:{t['text_primary']};")
        self._build_ui()

    def _build_ui(self):
        t = self.theme
        lay = QVBoxLayout(self)
        hdr = QLabel("🧩 Extensions & Userscripts")
        hdr.setStyleSheet(f"font-size:20px;font-weight:700;color:{t['text_primary']};padding:8px 0;")
        lay.addWidget(hdr)

        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane{{border:1px solid {t['border']};border-radius:8px;background:{t['bg_secondary']};}}
            QTabBar::tab{{background:{t['bg_tertiary']};color:{t['text_primary']};padding:10px 18px;border-radius:6px 6px 0 0;margin-right:4px;}}
            QTabBar::tab:selected{{background:{t['accent']};color:white;font-weight:700;}}
        """)
        tabs.addTab(self._build_manage_tab(), "📋 Manage Extensions")
        tabs.addTab(self._build_add_custom_tab(), "✏️ Add Custom Script")
        tabs.addTab(self._build_store_tab(), "🌐 Extension Store")
        lay.addWidget(tabs, 1)

        close_btn = QPushButton("✓ Close")
        close_btn.setStyleSheet(f"background:{t['accent']};color:white;border-radius:8px;padding:10px 24px;font-weight:700;")
        close_btn.clicked.connect(self.accept)
        lay.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

    # ── Manage tab ────────────────────────────────────────────
    def _build_manage_tab(self):
        t = self.theme
        w = QWidget(); lay = QVBoxLayout(w); lay.setContentsMargins(12,12,12,12)

        info = QLabel("Toggle extensions on/off. Enabled extensions with 'Show in toolbar' will appear in the top bar.")
        info.setWordWrap(True)
        info.setStyleSheet(f"color:{t['text_secondary']};font-size:12px;margin-bottom:8px;")
        lay.addWidget(info)

        # Installed extensions section
        inst_lbl = QLabel("📦 Installed Extensions")
        inst_lbl.setStyleSheet(f"font-size:14px;font-weight:700;color:{t['text_primary']};padding:6px 0;")
        lay.addWidget(inst_lbl)

        self.ext_list = QListWidget()
        self.ext_list.setStyleSheet(f"background:{t['bg_primary']};color:{t['text_primary']};"
                                    f"border:1px solid {t['border']};border-radius:8px;")
        self.ext_list.setFixedHeight(180)
        lay.addWidget(self.ext_list)

        ext_btns = QHBoxLayout()
        for lbl, fn in [("🔄 Toggle On/Off", self._toggle_extension),
                         ("🗑 Uninstall", self._uninstall_extension)]:
            b = QPushButton(lbl)
            col = t['accent'] if "Toggle" in lbl else t['danger']
            b.setStyleSheet(f"background:{col};color:white;border-radius:8px;padding:8px 14px;")
            b.clicked.connect(fn); ext_btns.addWidget(b)
        ext_btns.addStretch()
        lay.addLayout(ext_btns)

        # Userscripts section
        script_lbl = QLabel("📜 Custom Userscripts")
        script_lbl.setStyleSheet(f"font-size:14px;font-weight:700;color:{t['text_primary']};padding:10px 0 4px;")
        lay.addWidget(script_lbl)

        self.script_list = QListWidget()
        self.script_list.setStyleSheet(f"background:{t['bg_primary']};color:{t['text_primary']};"
                                       f"border:1px solid {t['border']};border-radius:8px;")
        self.script_list.setFixedHeight(160)
        self.script_list.itemClicked.connect(self._select_script)
        lay.addWidget(self.script_list)

        script_btns = QHBoxLayout()
        for lbl, fn in [("🔄 Toggle", self._toggle_script),
                         ("🗑 Remove", self._remove_script),
                         ("⬆ Show in Toolbar", self._toggle_script_toolbar)]:
            b = QPushButton(lbl)
            col = t['accent'] if "Toggle" in lbl or "Toolbar" in lbl else t['danger']
            b.setStyleSheet(f"background:{col};color:white;border-radius:8px;padding:8px 14px;")
            b.clicked.connect(fn); script_btns.addWidget(b)
        script_btns.addStretch()
        lay.addLayout(script_btns)
        lay.addStretch()

        self._refresh_ext_lists()
        return w

    def _refresh_ext_lists(self):
        self.ext_list.clear()
        for ext in self.ext_manager.get_all_extensions():
            en = "✅" if ext.get("enabled", True) else "⬜"
            toolbar = " 📌" if ext.get("show_in_toolbar") else ""
            item = QListWidgetItem(f"{en} {ext.get('icon','🧩')} {ext.get('name','?')}  v{ext.get('version','?')}  by {ext.get('author','?')}{toolbar}")
            item.setData(Qt.ItemDataRole.UserRole, ext.get("id"))
            self.ext_list.addItem(item)

        self.script_list.clear()
        for i, s in enumerate(self.ext_manager.get_all_scripts()):
            en = "✅" if s.get("enabled", True) else "⬜"
            toolbar = " 📌" if s.get("show_in_toolbar") else ""
            item = QListWidgetItem(f"{en} [{s.get('type','JS')}] {s.get('name','Unnamed')} — {s.get('match','*')}{toolbar}")
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.script_list.addItem(item)

    def _toggle_extension(self):
        item = self.ext_list.currentItem()
        if item:
            self.ext_manager.toggle_extension(item.data(Qt.ItemDataRole.UserRole))
            self._refresh_ext_lists(); self.extensions_changed.emit()

    def _uninstall_extension(self):
        item = self.ext_list.currentItem()
        if item:
            if QMessageBox.question(self, "Uninstall", f"Uninstall '{item.text().strip()}'?") == QMessageBox.StandardButton.Yes:
                self.ext_manager.uninstall_extension(item.data(Qt.ItemDataRole.UserRole))
                self._refresh_ext_lists(); self.extensions_changed.emit()

    def _select_script(self, item):
        self._script_edit_idx = item.data(Qt.ItemDataRole.UserRole)

    def _toggle_script(self):
        idx = self.script_list.currentRow()
        if idx >= 0:
            self.ext_manager.toggle_script(idx); self._refresh_ext_lists(); self.extensions_changed.emit()

    def _remove_script(self):
        idx = self.script_list.currentRow()
        if idx >= 0:
            self.ext_manager.remove_script(idx); self._refresh_ext_lists(); self.extensions_changed.emit()

    def _toggle_script_toolbar(self):
        idx = self.script_list.currentRow()
        scripts = self.ext_manager.get_all_scripts()
        if 0 <= idx < len(scripts):
            s = scripts[idx]
            self.ext_manager.update_script(idx, show_in_toolbar=not s.get("show_in_toolbar", False))
            self._refresh_ext_lists(); self.extensions_changed.emit()

    # ── Add custom script tab ────────────────────────────────
    def _build_add_custom_tab(self):
        t = self.theme
        w = QWidget(); lay = QVBoxLayout(w); lay.setContentsMargins(12,12,12,12)
        lay.addWidget(QLabel("Add a custom JavaScript or CSS script that runs on matching pages."))

        form = QFormLayout()
        self.f_name = QLineEdit(); self.f_name.setPlaceholderText("My Script")
        self.f_match = QLineEdit(); self.f_match.setPlaceholderText("* (all pages) or *.google.com")
        self.f_type = QComboBox(); self.f_type.addItems(["JavaScript","CSS"])
        self.f_toolbar_icon = QLineEdit(); self.f_toolbar_icon.setPlaceholderText("🧩")
        self.f_toolbar_cb = QCheckBox("Show button in top toolbar when enabled")
        for field in [self.f_name, self.f_match, self.f_toolbar_icon]:
            field.setStyleSheet(f"background:{t['bg_secondary']};color:{t['text_primary']};"
                                f"border:1px solid {t['border']};border-radius:8px;padding:7px 12px;")
        form.addRow("Name:", self.f_name)
        form.addRow("URL Pattern:", self.f_match)
        form.addRow("Type:", self.f_type)
        form.addRow("Toolbar Icon:", self.f_toolbar_icon)
        form.addRow("", self.f_toolbar_cb)
        lay.addLayout(form)

        self.f_code = QPlainTextEdit()
        self.f_code.setPlaceholderText("// Your JavaScript or CSS code here…\n// Example JS: document.body.style.background='red';\n// Example CSS: body { font-size: 18px !important; }")
        self.f_code.setStyleSheet(f"background:{t['bg_secondary']};color:{t['text_primary']};"
                                  f"border:1px solid {t['border']};border-radius:8px;font-family:monospace;font-size:13px;padding:8px;")
        self.f_code.setMinimumHeight(160)
        lay.addWidget(QLabel("Code:"))
        lay.addWidget(self.f_code, 1)

        add_btn = QPushButton("➕ Add Script")
        add_btn.setStyleSheet(f"background:{t['accent']};color:white;border-radius:8px;padding:10px 24px;font-weight:700;")
        add_btn.clicked.connect(self._add_custom_script)
        lay.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        tip = QLabel("💡 Tip: Use * as URL pattern to run on all pages. Toolbar button lets users click your extension icon at the top bar to trigger an action.")
        tip.setWordWrap(True)
        tip.setStyleSheet(f"color:{t['text_secondary']};font-size:11px;margin-top:10px;")
        lay.addWidget(tip)
        lay.addStretch()
        return w

    def _add_custom_script(self):
        name = self.f_name.text().strip() or "Unnamed"
        match = self.f_match.text().strip() or "*"
        type_ = self.f_type.currentText()
        code = self.f_code.toPlainText().strip()
        icon = self.f_toolbar_icon.text().strip() or "🧩"
        toolbar = self.f_toolbar_cb.isChecked()
        if not code:
            QMessageBox.warning(self,"Empty Code","Please enter some code for the script."); return
        self.ext_manager.add_script(name, match, type_, code, toolbar, icon)
        QMessageBox.information(self, "Added", f"Script '{name}' added successfully!")
        self.f_name.clear(); self.f_match.clear(); self.f_code.clear()
        self._refresh_ext_lists(); self.extensions_changed.emit()

    # ── Extension Store tab ──────────────────────────────────
    def _build_store_tab(self):
        t = self.theme
        w = QWidget(); lay = QVBoxLayout(w); lay.setContentsMargins(12,12,12,12)

        title = QLabel("🌐 Extension Store")
        title.setStyleSheet(f"font-size:16px;font-weight:700;color:{t['text_primary']};")
        lay.addWidget(title)

        # Download from URL
        url_box = QGroupBox("Download Extension from URL")
        url_box.setStyleSheet(f"QGroupBox{{color:{t['text_primary']};border:1px solid {t['border']};"
                              f"border-radius:10px;margin-top:10px;padding:12px;}}"
                              f"QGroupBox::title{{subcontrol-origin:margin;padding:0 6px;}}")
        ul = QVBoxLayout(url_box)
        ul.addWidget(QLabel("Enter the URL of a .json extension file to download and install:"))
        url_row = QHBoxLayout()
        self.ext_url_field = QLineEdit()
        self.ext_url_field.setPlaceholderText("https://example.com/my-extension.json")
        self.ext_url_field.setStyleSheet(f"background:{t['bg_secondary']};color:{t['text_primary']};"
                                         f"border:1px solid {t['border']};border-radius:8px;padding:7px 12px;")
        url_row.addWidget(self.ext_url_field, 1)
        dl_btn = QPushButton("⬇ Download & Install")
        dl_btn.setStyleSheet(f"background:{t['accent']};color:white;border-radius:8px;padding:8px 16px;font-weight:700;")
        dl_btn.clicked.connect(self._download_extension)
        url_row.addWidget(dl_btn)
        ul.addLayout(url_row)

        self.ext_dl_status = QLabel("")
        self.ext_dl_status.setStyleSheet(f"color:{t['text_secondary']};font-size:12px;")
        self.ext_dl_status.setWordWrap(True)
        ul.addWidget(self.ext_dl_status)
        lay.addWidget(url_box)

        # Install from file
        file_box = QGroupBox("Install Extension from Local File")
        file_box.setStyleSheet(f"QGroupBox{{color:{t['text_primary']};border:1px solid {t['border']};"
                               f"border-radius:10px;margin-top:10px;padding:12px;}}"
                               f"QGroupBox::title{{subcontrol-origin:margin;padding:0 6px;}}")
        fl = QVBoxLayout(file_box)
        fl.addWidget(QLabel("Select a .json extension package file from your computer:"))
        file_btn = QPushButton("📂 Browse & Install .json Extension")
        file_btn.setStyleSheet(f"background:{t['bg_tertiary']};color:{t['text_primary']};"
                               f"border:1px solid {t['border']};border-radius:8px;padding:8px 16px;")
        file_btn.clicked.connect(self._install_from_file)
        fl.addWidget(file_btn)
        self.ext_file_status = QLabel("")
        self.ext_file_status.setStyleSheet(f"color:{t['text_secondary']};font-size:12px;")
        fl.addWidget(self.ext_file_status)
        lay.addWidget(file_box)

        # Store link
        if EXTENSION_STORE_URL:
            store_btn = QPushButton(f"🛒 Open Extension Store: {EXTENSION_STORE_URL}")
            store_btn.setStyleSheet(f"background:{t['accent']};color:white;border-radius:8px;padding:10px 20px;margin-top:10px;")
            store_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(EXTENSION_STORE_URL)))
            lay.addWidget(store_btn)

        # Extension format guide
        fmt_lbl = QLabel(
            "📄 Extension .json format:\n"
            '{"name":"My Ext","description":"...","version":"1.0","author":"You",\n'
            ' "match":"*","type":"JavaScript","code":"alert(\'hello\');",\n'
            ' "icon":"🧩","show_in_toolbar":true,"toolbar_action":"run_code"}'
        )
        fmt_lbl.setStyleSheet(f"color:{t['text_secondary']};font-size:11px;font-family:monospace;"
                              f"background:{t['bg_secondary']};border-radius:8px;padding:10px;margin-top:10px;")
        fmt_lbl.setWordWrap(True)
        lay.addWidget(fmt_lbl)
        lay.addStretch()
        return w

    def _download_extension(self):
        url = self.ext_url_field.text().strip()
        if not url:
            self.ext_dl_status.setText("⚠️ Please enter a URL."); return
        self.ext_dl_status.setText("⏳ Downloading extension…")
        def on_done(ext):
            self.ext_dl_status.setText(f"✅ Installed: {ext['name']} v{ext['version']}")
            self._refresh_ext_lists(); self.extensions_changed.emit()
        def on_error(msg):
            self.ext_dl_status.setText(f"❌ Failed: {msg}")
        self.ext_manager.install_extension_from_url(url, on_done, on_error)

    def _install_from_file(self):
        path, _ = QFileDialog.getOpenFileName(self,"Install Extension","","Extension Package (*.json);;All Files (*.*)")
        if not path: return
        ext, err = self.ext_manager.install_extension_from_file(path)
        if err:
            self.ext_file_status.setText(f"❌ Error: {err}")
        else:
            self.ext_file_status.setText(f"✅ Installed: {ext['name']} v{ext.get('version','?')}")
            self._refresh_ext_lists(); self.extensions_changed.emit()

    # Legacy compat
    def get_scripts_for_url(self, url):
        return self.ext_manager.get_scripts_for_url(url)

# ═══════════════════════════════════════════════════════════════
#  SESSION MANAGER
# ═══════════════════════════════════════════════════════════════
class SessionManager:
    def __init__(self, profile_name):
        self.path=os.path.join(get_profile_path(profile_name),"session.json")
    def save(self, tabs_info):
        with open(self.path,"w") as f: json.dump({"tabs":tabs_info,"saved":str(datetime.datetime.now())},f)
    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path) as f: data=json.load(f)
                return data.get("tabs",[])
            except: pass
        return []

# ═══════════════════════════════════════════════════════════════
#  FIND BAR
# ═══════════════════════════════════════════════════════════════
class FindBar(QWidget):
    def __init__(self, browser_getter, theme, parent=None):
        super().__init__(parent)
        self.browser_getter=browser_getter; t=theme
        self.setStyleSheet(f"background:{t['bg_secondary']};border-top:1px solid {t['border']};")
        lay=QHBoxLayout(self); lay.setContentsMargins(8,6,8,6); lay.setSpacing(6)
        self.field=QLineEdit(); self.field.setPlaceholderText("Find in page…")
        self.field.setStyleSheet(f"background:{t['bg_primary']};color:{t['text_primary']};"
                                 f"border:1px solid {t['border']};border-radius:6px;padding:5px 10px;")
        self.field.textChanged.connect(self._find); self.field.returnPressed.connect(self._find_next)
        lay.addWidget(self.field)
        for txt,slot in [("▲",self._find_prev),("▼",self._find_next)]:
            b=QPushButton(txt); b.setFixedSize(28,28)
            b.setStyleSheet(f"background:{t['bg_tertiary']};color:{t['text_primary']};border-radius:5px;border:none;")
            b.clicked.connect(slot); lay.addWidget(b)
        self.case_cb=QCheckBox("Case"); self.case_cb.setStyleSheet(f"color:{t['text_primary']};")
        lay.addWidget(self.case_cb)
        self.count_lbl=QLabel("")
        self.count_lbl.setStyleSheet(f"color:{t['text_secondary']};font-size:11px;")
        lay.addWidget(self.count_lbl)
        close=QPushButton("✕"); close.setFixedSize(24,24)
        close.setStyleSheet(f"background:transparent;color:{t['text_secondary']};border:none;")
        close.clicked.connect(self.hide); lay.addWidget(close)

    def _find(self, text=""):
        b=self.browser_getter()
        if b:
            flags=QWebEnginePage.FindFlag(0)
            if self.case_cb.isChecked(): flags|=QWebEnginePage.FindFlag.FindCaseSensitively
            b.findText(text or self.field.text(),flags)

    def _find_next(self): self._find()
    def _find_prev(self):
        b=self.browser_getter()
        if b:
            flags=QWebEnginePage.FindFlag.FindBackward
            if self.case_cb.isChecked(): flags|=QWebEnginePage.FindFlag.FindCaseSensitively
            b.findText(self.field.text(),flags)

    def show_and_focus(self):
        self.show(); self.field.setFocus(); self.field.selectAll()

# ═══════════════════════════════════════════════════════════════
#  SPEED DIAL
# ═══════════════════════════════════════════════════════════════
class CommandPaletteDialog(QDialog):
    def __init__(self, main_window, commands, theme, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.commands = commands
        self.theme = theme
        self.filtered = []

        t = theme
        self.setWindowTitle("Command Palette")
        self.setModal(True)
        self.resize(820, 560)
        self.setStyleSheet(f"background:{t['bg_primary']};color:{t['text_primary']};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)

        title = QLabel("Command Palette")
        title.setStyleSheet(f"font-size:22px;font-weight:700;color:{t['accent']};")
        subtitle = QLabel("Search tabs, browser tools, bookmarks, and history from one place.")
        subtitle.setStyleSheet(f"color:{t['text_secondary']};font-size:12px;")
        lay.addWidget(title)
        lay.addWidget(subtitle)

        self.query = QLineEdit()
        self.query.setPlaceholderText("Type a command, tab title, bookmark, or URL...")
        self.query.setStyleSheet(
            f"background:{t['bg_secondary']};color:{t['text_primary']};"
            f"border:1px solid {t['border']};border-radius:10px;padding:10px 14px;font-size:14px;"
        )
        self.query.textChanged.connect(self._refresh)
        self.query.returnPressed.connect(self._activate_current)
        lay.addWidget(self.query)

        self.list_w = QListWidget()
        self.list_w.setStyleSheet(
            f"background:{t['bg_secondary']};color:{t['text_primary']};"
            f"border:1px solid {t['border']};border-radius:10px;"
        )
        self.list_w.itemDoubleClicked.connect(lambda _: self._activate_current())
        self.list_w.currentItemChanged.connect(lambda *_: self._update_footer())
        lay.addWidget(self.list_w, 1)

        footer = QHBoxLayout()
        self.footer_lbl = QLabel("")
        self.footer_lbl.setStyleSheet(f"color:{t['text_secondary']};font-size:11px;")
        footer.addWidget(self.footer_lbl, 1)
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(
            f"background:{t['bg_secondary']};color:{t['text_primary']};"
            f"border:1px solid {t['border']};border-radius:8px;padding:8px 14px;"
        )
        close_btn.clicked.connect(self.reject)
        footer.addWidget(close_btn)
        lay.addLayout(footer)

        self._refresh()

    def showEvent(self, event):
        super().showEvent(event)
        self.query.setFocus()
        self.query.selectAll()

    def _normalize(self, text):
        return re.sub(r"\s+", " ", (text or "").strip().lower())

    def _score(self, query, item):
        if not query:
            return 0
        hay = self._normalize(" ".join([
            item.get("label", ""),
            item.get("detail", ""),
            item.get("category", ""),
            item.get("keywords", ""),
        ]))
        if hay.startswith(query):
            return 1000 - len(hay)
        if query in hay:
            return 700 - hay.index(query)
        q_parts = [p for p in re.split(r"\s+", query) if p]
        if q_parts and all(p in hay for p in q_parts):
            return 500 - len(hay)
        return -1

    def _refresh(self):
        query = self._normalize(self.query.text())
        scored = []
        for item in self.commands:
            score = self._score(query, item)
            if score >= 0:
                scored.append((score, item))
        if not query:
            scored = [(0, item) for item in self.commands]
        scored.sort(key=lambda pair: (-pair[0], pair[1].get("category", ""), pair[1].get("label", "")))
        self.filtered = [item for _, item in scored[:200]]

        self.list_w.blockSignals(True)
        self.list_w.clear()
        for item in self.filtered:
            label = item["label"]
            detail = item.get("detail", "")
            category = item.get("category", "")
            text = label if not detail else f"{label}\n{detail}"
            lw_item = QListWidgetItem(text)
            lw_item.setData(Qt.ItemDataRole.UserRole, item)
            if category:
                lw_item.setToolTip(f"{category} • {detail}")
            else:
                lw_item.setToolTip(detail)
            self.list_w.addItem(lw_item)
        self.list_w.blockSignals(False)
        if self.list_w.count():
            self.list_w.setCurrentRow(0)
        self._update_footer()

    def _update_footer(self):
        item = self.list_w.currentItem()
        if not item:
            self.footer_lbl.setText("No command selected.")
            return
        cmd = item.data(Qt.ItemDataRole.UserRole) or {}
        cat = cmd.get("category", "Command")
        detail = cmd.get("detail", "")
        self.footer_lbl.setText(f"{cat} • {detail}")

    def _activate_current(self):
        item = self.list_w.currentItem()
        if not item:
            text = self.query.text().strip()
            if text:
                self.main_window.url_bar.setText(text)
                self.main_window.navigate_to_url()
                self.accept()
            return
        cmd = item.data(Qt.ItemDataRole.UserRole) or {}
        callback = cmd.get("callback")
        if callable(callback):
            callback()
        self.accept()

SPEED_DIAL_DEFAULTS=[
    ("Google",     "https://www.google.com",     "🔍"),
    ("YouTube",    "https://www.youtube.com",    "📺"),
    ("GitHub",     "https://www.github.com",     "🐙"),
    ("Wikipedia",  "https://www.wikipedia.org",  "📖"),
    ("Reddit",     "https://www.reddit.com",     "🤖"),
    ("ChatGPT",    "https://chat.openai.com",    "🧠"),
    ("SPS Search", "https://spscompany-rikdev.github.io/sps-search-engine","⭐"),
    ("Gmail",      "https://mail.google.com",    "📧"),
    ("Twitter/X",  "https://x.com",              "🐦"),
    ("LinkedIn",   "https://www.linkedin.com",   "💼"),
    ("Amazon",     "https://www.amazon.com",     "🛒"),
    ("Netflix",    "https://www.netflix.com",    "🎬"),
]

def build_speed_dial_html(theme, recent_tabs=None, bookmarks=None, history=None, workspaces=None, settings=None):
    settings = settings or {}
    recent_tabs = recent_tabs or []
    bookmarks = bookmarks or []
    history = history or []
    workspaces = workspaces or []
    t = theme
    action_cards = [
        ("New Tab", "sps:new-tab", "＋"),
        ("Incognito", "sps:new-incognito", "🕵"),
        ("Palette", "sps:command-palette", "⌘"),
        ("Organizer", "sps:tab-organizer", "🗂"),
        ("Bookmarks", "sps:bookmarks", "⭐"),
        ("History", "sps:history", "🕘"),
        ("Downloads", "sps:downloads", "⬇"),
        ("Notes", "sps:notes", "📝"),
        ("Privacy", "sps:privacy", "🛡"),
        ("Settings", "sps:settings", "⚙"),
        ("Stats", "sps:stats", "📊"),
        ("Cache", "sps:clear-cache", "🧹"),
        ("Session", "sps:session-snapshot", "💾"),
        ("Restore", "sps:restore-snapshot", "↺"),
        ("External", "sps:external-browser", "↗"),
        ("Save Text", "sps:save-page-text", "📝"),
        ("Cookies", "sps:clear-site-data", "🍪"),
        ("Images", "sps:toggle-images", "🖼"),
        ("Dark Filter", "sps:toggle-dark-filter", "🌑"),
        ("Text Only", "sps:toggle-text-only", "📄"),
        ("Auto Refresh", "sps:toggle-auto-refresh", "⟳"),
        ("Workspaces", "sps:workspaces", "🧩"),
        ("History Export", "sps:export-history", "📤"),
        ("Import BMs", "sps:import-bookmarks", "📥"),
        ("Clipboard URL", "sps:open-clipboard", "📋"),
        ("Copy URLs", "sps:copy-all-urls", "🔗"),
        ("Blank Tabs", "sps:close-blank-tabs", "✕"),
    ]
    quick_tiles = "".join(
        f'<a class="card action" href="{html.escape(url)}"><div class="icon">{html.escape(icon)}</div>'
        f'<div class="label">{html.escape(name)}</div></a>'
        for name, url, icon in action_cards
    )
    site_tiles = "".join(
        f'<a class="card site" href="{html.escape(url)}"><div class="icon">🔗</div>'
        f'<div class="label">{html.escape(name)}</div></a>'
        for name, url, _icon in SPEED_DIAL_DEFAULTS
    )
    recent_html = ""
    if settings.get("new_tab_show_recent_tabs", True) and recent_tabs:
        recent_items = "".join(
            f'<a class="recent-item" href="{html.escape(item["url"])}">'
            f'<span class="recent-title">{html.escape(item["title"][:56])}</span>'
            f'<span class="recent-url">{html.escape(item["url"][:72])}</span></a>'
            for item in recent_tabs[:8]
        )
        recent_html = f"""
        <section class="panel">
          <div class="section-head"><h2>Recent tabs</h2><span>Continue where you left off</span></div>
          <div class="recent-grid">{recent_items}</div>
        </section>
        """
    bookmark_html = ""
    if settings.get("new_tab_show_bookmarks", True) and bookmarks:
        bookmark_items = "".join(
            f'<a class="recent-item" href="{html.escape(item["url"])}">'
            f'<span class="recent-title">{html.escape(item["title"][:56])}</span>'
            f'<span class="recent-url">{html.escape(item["url"][:72])}</span></a>'
            for item in bookmarks[:8]
        )
        bookmark_html = f"""
        <section class="panel">
          <div class="section-head"><h2>Top bookmarks</h2><span>One click back to your favorite sites</span></div>
          <div class="recent-grid">{bookmark_items}</div>
        </section>
        """
    workspace_html = ""
    if settings.get("new_tab_show_workspaces", True) and workspaces:
        workspace_items = "".join(
            f'<a class="recent-item" href="sps:workspace-open-{quote_plus(item)}">'
            f'<span class="recent-title">{html.escape(item)}</span>'
            f'<span class="recent-url">Saved workspace</span></a>'
            for item in workspaces[:8]
        )
        workspace_html = f"""
        <section class="panel">
          <div class="section-head"><h2>Workspaces</h2><span>Open saved browsing sets</span></div>
          <div class="recent-grid">{workspace_items}</div>
        </section>
        """
    history_html = ""
    if settings.get("new_tab_show_recent_history", True) and history:
        history_items = "".join(
            f'<a class="recent-item" href="{html.escape(item["url"])}">'
            f'<span class="recent-title">{html.escape(item["title"][:56])}</span>'
            f'<span class="recent-url">{html.escape(item["url"][:72])}</span></a>'
            for item in history[:8]
        )
        history_html = f"""
        <section class="panel">
          <div class="section-head"><h2>Recent history</h2><span>Recently visited pages</span></div>
          <div class="recent-grid">{history_items}</div>
        </section>
        """
    stats_html = ""
    if settings.get("new_tab_show_stats", True):
        stats_html = f"""
        <section class="stats">
          <div class="stat"><b>{len(recent_tabs)}</b><span>Recent tabs</span></div>
          <div class="stat"><b>{len(bookmarks)}</b><span>Bookmarks</span></div>
          <div class="stat"><b>{settings.get('search_engine', 'SPS Search')}</b><span>Search engine</span></div>
          <div class="stat"><b>SPS</b><span>Browser pro mode</span></div>
        </section>
        """
    search_html = ""
    if settings.get("new_tab_show_search", True):
        search_html = """
        <div class="search-box">
          <span style="font-size:18px;margin-right:10px;">🔍</span>
          <input id="q" placeholder="Search or enter URL…" onkeydown="if(event.key==='Enter'){window.location='https://www.google.com/search?q='+encodeURIComponent(this.value);}"/>
        </div>
        """
    tools_html = ""
    if settings.get("new_tab_show_tools", True):
        tools_html = f"""
        <div class="section-head"><h2>Quick tools</h2><span>Open browser features instantly</span></div>
        <div class="grid">{quick_tiles}</div>
        """
    shortcuts_html = ""
    if settings.get("new_tab_show_shortcuts", True):
        shortcuts_html = """
        <div class="shortcut-row">
          <a class="shortcut-chip" href="sps:command-palette">Command Palette</a>
          <a class="shortcut-chip" href="sps:tab-organizer">Tab Organizer</a>
          <a class="shortcut-chip" href="sps:history">History</a>
          <a class="shortcut-chip" href="sps:bookmarks">Bookmarks</a>
          <a class="shortcut-chip" href="sps:settings">Settings</a>
          <a class="shortcut-chip" href="sps:privacy">Privacy</a>
        </div>
        """
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:radial-gradient(circle at top,{t['accent']}22,transparent 34%),{t['bg_primary']};
     color:{t['text_primary']};font-family:'Segoe UI',Arial,sans-serif;min-height:100vh;padding:36px 22px;}}
.shell{{max-width:1280px;margin:0 auto;}}
.hero{{display:flex;justify-content:space-between;align-items:flex-start;gap:18px;flex-wrap:wrap;margin-bottom:24px;}}
.time{{font-size:58px;font-weight:200;letter-spacing:-2px;line-height:1;color:{t['text_primary']};}}
.date{{font-size:15px;color:{t['text_secondary']};margin-top:6px;}}
.hero-card{{background:{t['bg_secondary']};border:1px solid {t['border']};border-radius:18px;padding:16px 18px;min-width:280px;}}
.hero-title{{font-size:18px;font-weight:700;margin-bottom:4px;}}
.hero-sub{{font-size:12px;color:{t['text_secondary']};}}
.search-box{{display:flex;align-items:center;background:{t['bg_secondary']};border:1px solid {t['border']};
             border-radius:30px;padding:12px 20px;width:min(760px,100%);margin-bottom:22px;
             box-shadow:0 10px 28px rgba(0,0,0,.08);}}
.search-box input{{flex:1;border:none;background:transparent;font-size:16px;color:{t['text_primary']};outline:none;}}
.shortcut-row{{display:flex;flex-wrap:wrap;gap:10px;margin:-2px 0 18px;}}
.shortcut-chip{{display:inline-flex;align-items:center;gap:6px;background:{t['bg_secondary']};color:{t['text_primary']};
                border:1px solid {t['border']};border-radius:999px;padding:8px 12px;font-size:12px;text-decoration:none;}}
.shortcut-chip:hover{{background:{t['hover']};}}
.stats{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:20px 0 26px;}}
.stat{{background:{t['bg_secondary']};border:1px solid {t['border']};border-radius:16px;padding:16px 18px;}}
.stat b{{display:block;font-size:20px;margin-bottom:4px;color:{t['accent']};}}
.stat span{{font-size:12px;color:{t['text_secondary']};}}
.section-head{{display:flex;justify-content:space-between;align-items:baseline;gap:12px;margin-bottom:12px;}}
.section-head h2{{font-size:16px;}}
.section-head span{{font-size:12px;color:{t['text_secondary']};}}
.grid{{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:14px;}}
.card{{background:{t['bg_secondary']};border:1px solid {t['border']};border-radius:18px;
       padding:20px 12px;text-align:center;text-decoration:none;color:{t['text_primary']};
       transition:transform .18s ease,background .18s ease,box-shadow .18s ease;cursor:pointer;min-height:98px;}}
.card:hover{{background:{t['hover']};transform:translateY(-4px);box-shadow:0 14px 30px rgba(0,0,0,.12);}}
.icon{{font-size:28px;margin-bottom:8px;}}
.label{{font-size:12px;font-weight:700;color:{t['text_secondary']};}}
.panel{{margin-top:22px;}}
.recent-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;}}
.recent-item{{display:flex;flex-direction:column;gap:4px;text-decoration:none;background:{t['bg_secondary']};
             border:1px solid {t['border']};border-radius:14px;padding:14px 16px;color:{t['text_primary']};}}
.recent-item:hover{{background:{t['hover']};}}
.recent-title{{font-size:13px;font-weight:700;}}
.recent-url{{font-size:11px;color:{t['text_secondary']};word-break:break-all;}}
.footer{{margin-top:26px;color:{t['text_secondary']};font-size:11px;}}
@media (max-width:1100px){{.grid{{grid-template-columns:repeat(4,minmax(0,1fr));}}.stats{{grid-template-columns:repeat(2,minmax(0,1fr));}}}}
@media (max-width:720px){{.grid{{grid-template-columns:repeat(2,minmax(0,1fr));}}.recent-grid{{grid-template-columns:1fr;}}.time{{font-size:42px;}}}}
</style></head><body>
<div class="shell">
  <div class="hero">
    <div>
      <div class="time" id="clock">00:00</div>
      <div class="date" id="date"></div>
    </div>
    <div class="hero-card">
      <div class="hero-title">SPS Browser Pro</div>
      <div class="hero-sub">Built for speed, privacy, and one-click control</div>
    </div>
  </div>
  {search_html}
  {shortcuts_html}
  {stats_html}
  {tools_html}
  <div class="panel">
    <div class="section-head"><h2>Speed dial</h2><span>Favorite sites</span></div>
    <div class="grid">{site_tiles}</div>
  </div>
  {recent_html}
  {bookmark_html}
  {workspace_html}
  {history_html}
  <div class="footer">SPS Browser Pro v{VERSION} &nbsp;•&nbsp; about:newtab dashboard</div>
</div>
<script>
function update(){{
  var n=new Date();
  document.getElementById('clock').textContent=
    n.getHours().toString().padStart(2,'0')+':'+n.getMinutes().toString().padStart(2,'0')+':'+n.getSeconds().toString().padStart(2,'0');
  document.getElementById('date').textContent=
    n.toLocaleDateString('en-US',{{weekday:'long',year:'numeric',month:'long',day:'numeric'}});
  setTimeout(update,1000);
}} update();
var q=document.getElementById('q'); if(q) q.focus();
</script></body></html>"""

# ═══════════════════════════════════════════════════════════════
#  PROFILE SELECTOR
# ═══════════════════════════════════════════════════════════════
class ProfileSelector(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SPS Browser — Select Profile")
        self.setMinimumSize(520,420); self.selected_profile="Default"
        self.setStyleSheet("""
            QDialog{background:#ffffff;}QLabel{color:#202124;}
            QListWidget{background:#f8f9fa;color:#202124;border:1px solid #dadce0;
                        border-radius:10px;padding:8px;font-size:14px;}
            QListWidget::item{padding:12px;border-radius:8px;margin:2px 6px;}
            QListWidget::item:hover{background:#e8eaed;}
            QListWidget::item:selected{background:#1a73e8;color:white;}
            QPushButton{border-radius:8px;padding:10px 18px;font-weight:600;border:none;}
        """)
        lay=QVBoxLayout(self); lay.setSpacing(16)
        title=QLabel("Who's using SPS Browser?")
        title.setStyleSheet("font-size:26px;font-weight:700;margin-bottom:8px;color:#202124;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter); lay.addWidget(title)
        self.list_w=QListWidget(); self._load(); lay.addWidget(self.list_w)
        br=QHBoxLayout()
        add=QPushButton("＋ Add Profile"); add.setStyleSheet("background:#f1f3f4;color:#1a73e8;")
        add.clicked.connect(self._create)
        rem=QPushButton("🗑 Remove"); rem.setStyleSheet("background:#f1f3f4;color:#d93025;")
        rem.clicked.connect(self._delete)
        go=QPushButton("▶ Continue"); go.setStyleSheet("background:#1a73e8;color:white;font-size:15px;")
        go.clicked.connect(self._accept)
        for b in [add,rem,go]: br.addWidget(b)
        lay.addLayout(br)

    def _load(self):
        self.list_w.clear()
        for p in os.listdir(PROFILES_DIR): self.list_w.addItem(p)
        if self.list_w.count(): self.list_w.setCurrentRow(0)

    def _create(self):
        name,ok=QInputDialog.getText(self,"New Profile","Profile name:")
        if ok and name: get_profile_path(name); self._load()

    def _delete(self):
        item=self.list_w.currentItem()
        if not item: return
        if item.text()=="Default":
            QMessageBox.warning(self,"Error","Cannot delete the Default profile."); return
        if QMessageBox.question(self,"Delete Profile",f"Delete '{item.text()}' and all its data?")==QMessageBox.StandardButton.Yes:
            shutil.rmtree(os.path.join(PROFILES_DIR,item.text()),ignore_errors=True); self._load()

    def _accept(self):
        if self.list_w.currentItem():
            self.selected_profile=self.list_w.currentItem().text(); self.accept()

# ═══════════════════════════════════════════════════════════════
#  SETTINGS DIALOG
# ═══════════════════════════════════════════════════════════════
class SettingsDialog(QDialog):
    def __init__(self, settings_data, profile_name, accent, parent=None):
        super().__init__(parent)
        self.s=settings_data; self.profile_name=profile_name; self.accent=accent
        self.toggles={}
        self.setWindowTitle("⚙️ Settings"); self.resize(960,700)
        self._apply_style(); self._build_ui()

    def _apply_style(self):
        t=self.s["theme"]
        self.setStyleSheet(f"""
            QDialog{{background:{t['bg_primary']};}}
            QLabel{{color:{t['text_primary']};}}
            QListWidget{{background:{t['sidebar_bg']};border:none;color:{t['text_primary']};
                         font-size:14px;outline:none;border-right:1px solid {t['border']};}}
            QListWidget::item{{padding:12px 16px;border-radius:8px;margin:2px 8px;}}
            QListWidget::item:hover{{background:{t['hover']};}}
            QListWidget::item:selected{{background:{t['accent_light']};color:{t['accent']};font-weight:700;}}
            QGroupBox{{color:{t['text_primary']};border:1px solid {t['border']};
                       border-radius:10px;margin-top:14px;padding:12px 16px;}}
            QGroupBox::title{{subcontrol-origin:margin;padding:0 8px;font-weight:600;}}
            QLineEdit{{background:{t['bg_secondary']};color:{t['text_primary']};
                       border:1px solid {t['border']};border-radius:8px;padding:7px 12px;}}
            QPushButton{{background:{t['accent']};color:white;border:none;
                         border-radius:8px;padding:8px 18px;font-weight:600;}}
            QPushButton:hover{{background:{t['accent']}dd;}}
            QScrollArea{{border:none;}}
            QComboBox{{background:{t['bg_secondary']};color:{t['text_primary']};
                       border:1px solid {t['border']};border-radius:8px;padding:6px 10px;}}
            QSlider::groove:horizontal{{height:4px;background:{t['border']};border-radius:2px;}}
            QSlider::handle:horizontal{{background:{t['accent']};width:16px;height:16px;
                                        margin:-6px 0;border-radius:8px;}}
            QSpinBox{{background:{t['bg_secondary']};color:{t['text_primary']};
                      border:1px solid {t['border']};border-radius:6px;padding:5px;}}
        """)

    def _build_ui(self):
        t=self.s["theme"]; outer=QHBoxLayout(self)
        outer.setContentsMargins(0,0,0,0); outer.setSpacing(0)
        self.nav=QListWidget(); self.nav.setFixedWidth(210)
        sections=["🏠 General","🔒 Privacy & Security","🛡️ Ad & Tracker Blocking",
                  "🎨 Appearance","🔍 Search","📥 Downloads","🔐 Passwords",
                  "🌐 Network & Proxy","🧩 Extensions","⌨️ Shortcuts",
                  "🔔 Notifications","⚡ Performance","🌐 Languages","🔧 Advanced"]
        self.nav.addItems(sections); self.nav.setCurrentRow(0); outer.addWidget(self.nav)
        right=QWidget(); right_lay=QVBoxLayout(right)
        right_lay.setContentsMargins(24,20,24,20)
        self.stack=QStackedWidget()
        pages=[self._page_general(),self._page_privacy(),self._page_adblock(),
               self._page_appearance(),self._page_search(),self._page_downloads(),
               self._page_passwords(),self._page_network(),self._page_extensions(),
               self._page_shortcuts(),self._page_notifications(),self._page_performance(),
               self._page_languages(),self._page_advanced()]
        for p in pages:
            scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(p)
            self.stack.addWidget(scroll)
        right_lay.addWidget(self.stack,1)
        save_btn=QPushButton("💾 Save Settings"); save_btn.clicked.connect(self._save)
        right_lay.addWidget(save_btn,alignment=Qt.AlignmentFlag.AlignRight)
        outer.addWidget(right,1)
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)

    def _make_w(self):
        w=QWidget(); w.setLayout(QVBoxLayout())
        w.layout().setSpacing(14); w.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        return w

    def _add_toggle(self, lay, key, label, desc=""):
        t=self.s["theme"]
        row=QWidget(); row.setStyleSheet(f"background:{t['bg_secondary']};border-radius:10px;")
        h=QHBoxLayout(row); h.setContentsMargins(14,12,14,12)
        tc=QVBoxLayout()
        l=QLabel(label); l.setStyleSheet(f"font-size:14px;font-weight:600;color:{t['text_primary']};background:transparent;")
        tc.addWidget(l)
        if desc:
            d=QLabel(desc); d.setStyleSheet(f"font-size:11px;color:{t['text_secondary']};background:transparent;")
            d.setWordWrap(True); tc.addWidget(d)
        h.addLayout(tc,1)
        tog=ToggleSwitch(self.s.get(key,False),self.accent)
        h.addWidget(tog); lay.addWidget(row); self.toggles[key]=tog
        return tog

    def _add_group(self, lay, title):
        box=QGroupBox(title); inner=QVBoxLayout(box); inner.setSpacing(8)
        lay.addWidget(box); return inner

    def _page_general(self):
        w=self._make_w(); lay=w.layout()
        g=self._add_group(lay,"Startup & Tabs")
        self._add_toggle(g,"restore_tabs","Restore previous tabs","Reopen last session tabs on startup")
        self._add_toggle(g,"show_bookmarks_bar","Bookmarks bar","Show bookmarks below the toolbar")
        self._add_toggle(g,"show_status_bar","Status bar","Show URL and security info at bottom")
        self._add_toggle(g,"show_tab_count","Show tab count in title bar","Display open tab number in window title")
        self._add_toggle(g,"tab_preview_hover","Tab preview on hover","Show page thumbnail when hovering over tabs")
        self._add_toggle(g,"confirm_before_close","Confirm before closing","Ask before the browser exits")
        self._add_toggle(g,"enable_tab_groups","Enable tab groups","Allow workspaces and tab groups to be saved")
        self._add_toggle(g,"new_tab_show_search","New tab search box","Show the search bar on the about:newtab dashboard")
        self._add_toggle(g,"new_tab_show_tools","New tab quick tools","Show browser tool shortcuts on the new tab page")
        self._add_toggle(g,"new_tab_show_recent_tabs","New tab recent tabs","Show recently opened tabs on the start page")
        self._add_toggle(g,"new_tab_show_bookmarks","New tab bookmarks","Show favorite sites on the start page")
        self._add_toggle(g,"new_tab_show_stats","New tab stats","Show browser stats on the dashboard")
        self._add_toggle(g,"new_tab_show_shortcuts","New tab shortcuts","Show shortcut chips on the start page")
        self._add_toggle(g,"new_tab_show_recent_history","New tab history","Show recent browsing history on the start page")
        self._add_toggle(g,"new_tab_show_workspaces","New tab workspaces","Show saved workspaces on the start page")
        g2=self._add_group(lay,"Scrolling & Animation")
        self._add_toggle(g2,"smooth_scroll","Smooth scrolling","Animated page scrolling")
        self._add_toggle(g2,"compact_mode","Compact mode","Reduce UI padding for more content")
        g3=self._add_group(lay,"Zoom")
        zr=QWidget(); zh=QHBoxLayout(zr); zh.setContentsMargins(0,0,0,0)
        lbl=QLabel("Default zoom:"); lbl.setStyleSheet(f"color:{self.s['theme']['text_primary']};")
        self.zoom_slider=QSlider(Qt.Orientation.Horizontal); self.zoom_slider.setRange(25,300)
        self.zoom_slider.setValue(int(self.s.get("zoom_factor",1.0)*100))
        self.zoom_val_lbl=QLabel(f"{self.zoom_slider.value()}%")
        self.zoom_slider.valueChanged.connect(lambda v: self.zoom_val_lbl.setText(f"{v}%"))
        zh.addWidget(lbl); zh.addWidget(self.zoom_slider,1); zh.addWidget(self.zoom_val_lbl)
        g3.addWidget(zr)
        g4=self._add_group(lay,"Homepage")
        hp_row=QWidget(); hpl=QHBoxLayout(hp_row); hpl.setContentsMargins(0,0,0,0)
        hpl.addWidget(QLabel("Custom homepage URL (leave empty for speed dial):"))
        self.homepage_edit=QLineEdit(self.s.get("custom_homepage_url",""))
        self.homepage_edit.setPlaceholderText("https://example.com")
        hpl.addWidget(self.homepage_edit,1); g4.addWidget(hp_row)
        return w

    def _page_privacy(self):
        w=self._make_w(); lay=w.layout()
        g=self._add_group(lay,"Browsing Privacy")
        self._add_toggle(g,"do_not_track","Send 'Do Not Track'","Sends DNT:1 header to every website")
        self._add_toggle(g,"tracking_protection","Enhanced Tracking Protection","Block known trackers and spy pixels")
        self._add_toggle(g,"block_fingerprinting","Fingerprint Protection","Reduce browser fingerprint exposure to sites")
        # V26 granular fingerprint controls
        gfp=self._add_group(lay,"🔑 Fingerprint Safety (V26)")
        self._add_toggle(gfp,"randomize_canvas_noise","Canvas Noise","Add random noise to canvas reads to defeat canvas fingerprinting")
        self._add_toggle(gfp,"randomize_webgl_vendor","WebGL Spoof","Report generic GPU info to prevent WebGL fingerprinting")
        self._add_toggle(gfp,"block_fingerprinting_audio","Audio API Protection","Block AudioContext-based fingerprinting")
        self._add_toggle(gfp,"block_fingerprinting_fonts","Font Enumeration Block","Prevent sites from enumerating your installed fonts")
        self._add_toggle(gfp,"block_battery_api","Block Battery API","Return dummy battery info (1.0 always charging)")
        self._add_toggle(gfp,"block_geolocation","Block Geolocation","Deny location access to all sites")
        self._add_toggle(gfp,"spoof_timezone","Spoof Timezone as UTC","Report UTC as the browser timezone to all sites")
        self._add_toggle(gfp,"spoof_language","Spoof Language","Report en-US as Accept-Language to all sites")
        self._add_toggle(gfp,"block_etag_tracking","Block ETag tracking","Strip ETag and If-None-Match headers to prevent cache-based tracking")
        self._add_toggle(gfp,"block_referrer_header","Strip Referrer Header","Don't send Referer on cross-origin requests")
        self._add_toggle(g,"block_third_cookies","Block third-party cookies","Prevent cross-site cookie tracking")
        self._add_toggle(g,"total_cookie_protection","Total Cookie Protection","Isolate cookies to each individual website")
        self._add_toggle(g,"block_social_trackers","Block social trackers","Block Facebook, Twitter, LinkedIn tracking pixels")
        self._add_toggle(g,"block_insecure_downloads","Block insecure downloads","Prevent downloads from insecure HTTP sources on secure pages")
        self._add_toggle(g,"scan_downloads_before_saving","Scan downloads before saving","Download to a temporary area, scan the file, then ask before risky downloads are kept")
        self._add_toggle(g,"warn_executable_downloads","Warn for executable downloads","Ask before saving EXE, MSI, script, shortcut, and registry files")
        self._add_toggle(g,"block_double_extension_downloads","Block double-extension tricks","Warn on names such as invoice.pdf.exe")
        self._add_toggle(g,"quarantine_blocked_downloads","Quarantine blocked downloads","Keep blocked risky downloads in a private SPS quarantine folder")
        g2=self._add_group(lay,"Security")
        self._add_toggle(g2,"safe_browsing","Safe Browsing","Warn before visiting potentially dangerous sites")
        self._add_toggle(g2,"https_only","HTTPS-Only Mode","Automatically upgrade all connections to HTTPS")
        self._add_toggle(g2,"js_enabled","JavaScript","Enable JavaScript on web pages")
        self._add_toggle(g2,"js_popups","Allow JavaScript popups","Let sites open new windows via JavaScript")
        self._add_toggle(g2,"block_popups","Block popups","Prevent unsolicited popup windows from opening")
        self._add_toggle(g2,"xss_auditing","XSS Protection","Block reflected cross-site scripting attacks")
        self._add_toggle(g2,"insecure_content","Allow insecure content","Load HTTP resources on HTTPS pages (not recommended)")
        self._add_toggle(g2,"open_links_in_background","Open links in background","Open clicked links without switching tabs")
        self._add_toggle(g2,"open_bookmarks_in_background","Open bookmarks in background","Keep focus on the current tab when opening bookmarks")
        g3=self._add_group(lay,"Data & Storage")
        self._add_toggle(g3,"storage_enabled","Local Storage","Allow websites to use local browser storage")
        self._add_toggle(g3,"local_remote_access","Local → Remote access","Allow local files to access remote URLs")
        self._add_toggle(g3,"clear_on_exit","Clear data on exit","Delete cookies and cache when browser closes")
        self._add_toggle(g3,"session_auto_save","Auto-save session","Save open tabs every 5 minutes for crash recovery")
        return w

    def _page_adblock(self):
        w=self._make_w(); lay=w.layout()
        g=self._add_group(lay,"Blocking Engines")
        self._add_toggle(g,"ad_blocker","Ad Blocker","Block advertisements across all websites")
        self._add_toggle(g,"block_cryptomining","Block Cryptomining","Prevent hidden cryptocurrency mining scripts")
        self._add_toggle(g,"plugins_enabled","Allow browser plugins","Enable plugins such as the built-in PDF viewer")
        g2=self._add_group(lay,"Notifications")
        self._add_toggle(g2,"notify_blocked","Notify when content is blocked","Show status bar message when ads/trackers are blocked")
        info=QLabel("SPS Browser's built-in blocker runs before any request leaves your device. "
                    "Blocked counts are shown live in the Privacy Dashboard and status bar.")
        info.setWordWrap(True)
        info.setStyleSheet(f"color:{self.s['theme']['text_secondary']};font-size:12px;padding:10px;")
        lay.addWidget(info); return w

    def _page_appearance(self):
        w=self._make_w(); lay=w.layout(); t=self.s["theme"]
        g=self._add_group(lay,"Theme Colors")
        # Accent
        ar=QWidget(); ah=QHBoxLayout(ar); ah.setContentsMargins(0,0,0,0)
        lbl=QLabel("Accent color:"); lbl.setStyleSheet(f"color:{t['text_primary']};")
        self.accent_prev=QLabel(); self.accent_prev.setFixedSize(30,30)
        self.accent_prev.setStyleSheet(f"background:{self.s.get('accent_color','#1a73e8')};border-radius:15px;")
        pb=QPushButton("Choose…"); pb.setStyleSheet(f"background:{t['bg_tertiary']};color:{t['text_primary']};border:1px solid {t['border']};")
        pb.clicked.connect(self._pick_accent)
        ah.addWidget(lbl); ah.addWidget(self.accent_prev); ah.addWidget(pb); ah.addStretch(); g.addWidget(ar)
        # BG
        br=QWidget(); bh=QHBoxLayout(br); bh.setContentsMargins(0,0,0,0)
        lbl2=QLabel("Background color:"); lbl2.setStyleSheet(f"color:{t['text_primary']};")
        self.bg_prev=QLabel(); self.bg_prev.setFixedSize(30,30)
        self.bg_prev.setStyleSheet(f"background:{t['bg_primary']};border-radius:15px;border:1px solid {t['border']};")
        pbg=QPushButton("Choose…"); pbg.setStyleSheet(f"background:{t['bg_tertiary']};color:{t['text_primary']};border:1px solid {t['border']};")
        pbg.clicked.connect(self._pick_bg)
        bh.addWidget(lbl2); bh.addWidget(self.bg_prev); bh.addWidget(pbg); bh.addStretch(); g.addWidget(br)
        # Presets
        pr=QHBoxLayout()
        presets=[("☀️ Light","#ffffff","#1a73e8"),("🌙 Dark","#1a1a1a","#8ab4f8"),
                 ("🌊 Ocean","#0d1b2a","#00b4d8"),("🌲 Forest","#1a2e1a","#4caf50"),
                 ("🌸 Pink","#fff0f5","#e91e63"),("🖤 Midnight","#0a0a0a","#bb86fc"),
                 ("🍊 Orange","#fff8f0","#e65100"),("🟣 Purple","#f5f0ff","#7c3aed")]
        for name,bg,acc in presets:
            b=QPushButton(name); b.setFixedHeight(36)
            b.setStyleSheet(f"background:{bg};color:{'#fff' if bg<'#888888' else '#000'};"
                            f"border:2px solid {acc};border-radius:8px;font-size:11px;")
            b.clicked.connect(partial(self._apply_preset,bg,acc)); pr.addWidget(b)
        g.addLayout(pr)
        g2=self._add_group(lay,"Display")
        fsr=QWidget(); fl=QHBoxLayout(fsr); fl.setContentsMargins(0,0,0,0)
        lbl3=QLabel("Font size:"); lbl3.setStyleSheet(f"color:{t['text_primary']};")
        self.font_spin=QSpinBox(); self.font_spin.setRange(10,32); self.font_spin.setValue(self.s.get("font_size",16))
        fl.addWidget(lbl3); fl.addWidget(self.font_spin); fl.addStretch(); g2.addWidget(fsr)
        self._add_toggle(g2,"spell_check","Spell check","Highlight misspelled words in text fields")
        self._add_toggle(g2,"focus_mode","Focus mode","Hide all UI chrome for distraction-free browsing")
        return w

    def _pick_accent(self):
        c=QColorDialog.getColor(QColor(self.s.get("accent_color","#1a73e8")),self,"Pick Accent Color")
        if c.isValid():
            self.s["accent_color"]=c.name(); self.s["theme"]["accent"]=c.name()
            self.accent_prev.setStyleSheet(f"background:{c.name()};border-radius:15px;")

    def _pick_bg(self):
        c=QColorDialog.getColor(QColor(self.s["theme"]["bg_primary"]),self,"Pick Background Color")
        if c.isValid():
            self.s["theme"]["bg_primary"]=c.name()
            self.bg_prev.setStyleSheet(f"background:{c.name()};border-radius:15px;border:1px solid {self.s['theme']['border']};")

    def _apply_preset(self,bg,acc,*_):
        dark=bg<"#888888"
        text="#ffffff" if dark else "#202124"; text2="#aaaaaa" if dark else "#5f6368"
        sec=_lighten(bg,20) if dark else _darken(bg,5)
        ter=_lighten(bg,40) if dark else _darken(bg,10)
        border=_lighten(bg,60) if dark else _darken(bg,15)
        hover=_lighten(bg,35) if dark else _darken(bg,8)
        self.s["theme"].update({"bg_primary":bg,"bg_secondary":sec,"bg_tertiary":ter,
                                "accent":acc,"accent_light":acc+"33","text_primary":text,
                                "text_secondary":text2,"border":border,"hover":hover,
                                "sidebar_bg":sec,"toolbar_bg":bg,"tab_active":bg,"tab_inactive":sec})
        self.s["accent_color"]=acc
        self.accent_prev.setStyleSheet(f"background:{acc};border-radius:15px;")
        self.bg_prev.setStyleSheet(f"background:{bg};border-radius:15px;border:1px solid {border};")

    def _page_search(self):
        w=self._make_w(); lay=w.layout(); t=self.s["theme"]
        g=self._add_group(lay,"Default Search Engine")
        er=QWidget(); eh=QHBoxLayout(er); eh.setContentsMargins(0,0,0,0)
        eh.addWidget(QLabel("Search engine:"))
        self.engine_combo=QComboBox(); self.engine_combo.addItems(list(SEARCH_ENGINES.keys()))
        self.engine_combo.setCurrentText(self.s.get("search_engine","SPS Search"))
        eh.addWidget(self.engine_combo); eh.addStretch(); g.addWidget(er)
        self._add_toggle(g,"instant_answers","Instant answers","Show quick results in URL bar (calculator, conversions, time)")
        self._add_toggle(g,"voice_search","Voice search","Enable microphone/voice search button in toolbar")
        self._add_toggle(g,"dns_prefetch","DNS prefetching","Pre-resolve DNS for links to speed up navigation")
        self._add_toggle(g,"preload_hover_links","Preload hovered links","Prefetch pages when you hover over links (uses more data)")
        return w

    def _page_downloads(self):
        w=self._make_w(); lay=w.layout(); t=self.s["theme"]
        g=self._add_group(lay,"Download Location")
        pr=QWidget(); ph=QHBoxLayout(pr); ph.setContentsMargins(0,0,0,0)
        ph.addWidget(QLabel("Save to:"))
        self.dl_path_edit=QLineEdit(self.s.get("download_path",os.path.expanduser("~/Downloads")))
        browse=QPushButton("Browse…"); browse.setStyleSheet(f"background:{t['bg_tertiary']};color:{t['text_primary']};border:1px solid {t['border']};")
        browse.clicked.connect(self._browse_dl)
        ph.addWidget(self.dl_path_edit,1); ph.addWidget(browse); g.addWidget(pr)
        g2=self._add_group(lay,"Download Settings")
        self._add_toggle(g2,"scan_downloads_before_saving","Scan downloads before saving","SPS downloads to temp first, checks hashes and suspicious content, then saves clean files")
        self._add_toggle(g2,"warn_executable_downloads","Warn before executable files","Ask before keeping EXE, MSI, BAT, CMD, PS1, JS, VBS, SCR, JAR, DLL, REG, and LNK files")
        self._add_toggle(g2,"block_double_extension_downloads","Block hidden executable names","Warn on document-looking executable names like photo.jpg.exe")
        self._add_toggle(g2,"quarantine_blocked_downloads","Quarantine blocked files","Move blocked downloads to the SPS quarantine folder instead of deleting them immediately")
        mr=QWidget(); mh=QHBoxLayout(mr); mh.setContentsMargins(0,0,0,0)
        mh.addWidget(QLabel("Max concurrent downloads:"))
        self.max_dl_spin=QSpinBox(); self.max_dl_spin.setRange(1,20)
        self.max_dl_spin.setValue(self.s.get("max_concurrent_downloads",5))
        mh.addWidget(self.max_dl_spin); mh.addStretch(); g2.addWidget(mr)
        return w

    def _browse_dl(self):
        d=QFileDialog.getExistingDirectory(self,"Select Download Folder")
        if d: self.dl_path_edit.setText(d)

    def _page_passwords(self):
        w=self._make_w(); lay=w.layout()
        g=self._add_group(lay,"Password Management")
        self._add_toggle(g,"save_passwords","Save passwords","Offer to save passwords when you log in")
        self._add_toggle(g,"auto_fill","Auto-fill forms","Automatically fill saved login credentials in forms")
        info=QLabel("Manage saved passwords via sidebar 🔐 or the Password Manager in the main menu.")
        info.setWordWrap(True)
        info.setStyleSheet(f"color:{self.s['theme']['text_secondary']};font-size:12px;padding:10px;")
        lay.addWidget(info); return w

    def _page_network(self):
        w=self._make_w(); lay=w.layout(); t=self.s["theme"]
        g=self._add_group(lay,"HTTP Proxy")
        self._add_toggle(g,"proxy_enabled","Use custom proxy","Route browser traffic through a proxy server")
        hr=QWidget(); hh=QHBoxLayout(hr); hh.setContentsMargins(0,0,0,0)
        hh.addWidget(QLabel("Host:"))
        self.proxy_host_edit=QLineEdit(self.s.get("proxy_host","")); self.proxy_host_edit.setPlaceholderText("e.g. 127.0.0.1")
        hh.addWidget(self.proxy_host_edit,1)
        hh.addWidget(QLabel("Port:"))
        self.proxy_port_spin=QSpinBox(); self.proxy_port_spin.setRange(1,65535)
        self.proxy_port_spin.setValue(self.s.get("proxy_port",8080))
        hh.addWidget(self.proxy_port_spin); g.addWidget(hr)
        g2=self._add_group(lay,"Connection")
        self._add_toggle(g2,"wake_lock","Prevent screen sleep","Keep screen awake while the browser is running")
        g3=self._add_group(lay,"User Agent Spoofing")
        uir=QWidget(); uh=QHBoxLayout(uir); uh.setContentsMargins(0,0,0,0)
        uh.addWidget(QLabel("User Agent:"))
        self.ua_combo=QComboBox(); self.ua_combo.addItems(list(USER_AGENTS.keys()))
        self.ua_combo.setCurrentText(self.s.get("user_agent","Default"))
        uh.addWidget(self.ua_combo); uh.addStretch(); g3.addWidget(uir)
        return w

    def _page_extensions(self):
        w=self._make_w(); lay=w.layout()
        info=QLabel("V26: Extensions can now be installed from a URL or .json file. "
                    "Enable 'Show in toolbar' on any extension to get a one-click toolbar button. "
                    "JavaScript and CSS are injected after page load on matching URL patterns.")
        info.setWordWrap(True)
        info.setStyleSheet(f"color:{self.s['theme']['text_secondary']};font-size:13px;padding:10px;")
        lay.addWidget(info)
        g=self._add_group(lay,"Extension Toolbar")
        self._add_toggle(g,"extensions_toolbar_visible","Show extension buttons in toolbar","Display a button for each enabled extension that has 'Show in toolbar' checked")
        btn=QPushButton("🧩 Open Extensions Manager")
        btn.setStyleSheet(f"background:{self.s['theme']['accent']};color:white;border-radius:8px;padding:10px 20px;font-weight:700;")
        mw = self.parent()
        if mw and hasattr(mw,"extension_manager"):
            btn.clicked.connect(lambda: ExtensionsDialog(self.profile_name, self.s["theme"], mw.extension_manager, self).exec())
        else:
            btn.clicked.connect(lambda: QMessageBox.information(self,"Note","Open from the main window menubar for full functionality."))
        lay.addWidget(btn)
        guide=QLabel(
            "How to make an extension .json file:\n"
            '{"name":"My Extension","description":"Does something cool","version":"1.0",\n'
            ' "author":"YourName","match":"*.example.com","type":"JavaScript",\n'
            ' "code":"document.body.style.background=\'red\';","icon":"🎨",\n'
            ' "show_in_toolbar":true}\n\n'
            "Host this .json file anywhere (GitHub, your server, etc.)\n"
            "Users paste the URL in Extensions > Extension Store > Download from URL."
        )
        guide.setStyleSheet(f"color:{self.s['theme']['text_secondary']};font-size:11px;font-family:monospace;"
                            f"background:{self.s['theme']['bg_secondary']};border-radius:8px;padding:12px;margin-top:12px;")
        guide.setWordWrap(True)
        lay.addWidget(guide)
        return w

    def _page_shortcuts(self):
        w=self._make_w(); lay=w.layout(); t=self.s["theme"]
        shortcuts=[("Ctrl+T","New tab"),("Ctrl+W","Close tab"),("Ctrl+Shift+T","Reopen closed tab"),
                   ("Ctrl+L","Focus URL bar"),("Ctrl+R / F5","Reload page"),
                   ("Ctrl+Shift+R","Hard reload (bypass cache)"),("Ctrl+B","Toggle sidebar"),
                   ("Ctrl+D","Add bookmark"),("Ctrl+H","History"),("Ctrl+J","Downloads"),
                   ("Ctrl++","Zoom in"),("Ctrl+-","Zoom out"),("Ctrl+0","Reset zoom"),
                   ("F12","Developer tools"),("Ctrl+U","View page source"),("Ctrl+P","Print"),
                   ("Ctrl+S","Save page"),("Ctrl+F","Find in page"),("Alt+←","Back"),
                   ("Alt+→","Forward"),("Ctrl+Tab","Next tab"),("Ctrl+Shift+Tab","Previous tab"),
                   ("Ctrl+M","Mute/unmute tab"),("Ctrl+Shift+N","New incognito tab")]
        g=self._add_group(lay,"Keyboard Shortcuts")
        table=QTableWidget(len(shortcuts),2)
        table.setHorizontalHeaderLabels(["Shortcut","Action"])
        table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setStyleSheet(f"background:{t['bg_secondary']};color:{t['text_primary']};gridline-color:{t['border']};")
        for i,(k,v) in enumerate(shortcuts):
            table.setItem(i,0,QTableWidgetItem(k)); table.setItem(i,1,QTableWidgetItem(v))
        g.addWidget(table); return w

    def _page_notifications(self):
        w=self._make_w(); lay=w.layout()
        g=self._add_group(lay,"Notification Settings")
        self._add_toggle(g,"notify_blocked","Blocked content notifications","Show message when ads or trackers are blocked")
        self._add_toggle(g,"auto_update","Auto-update check","Automatically check for new SPS Browser versions on startup")
        info=QLabel("SPS Browser checks for updates at https://sites.google.com/view/spsbrowserpro/updates\n"
                    "When a new setup.exe is available it will automatically download and install it, then remove the old version.")
        info.setWordWrap(True)
        info.setStyleSheet(f"color:{self.s['theme']['text_secondary']};font-size:12px;padding:10px;")
        lay.addWidget(info); return w

    def _page_performance(self):
        w=self._make_w(); lay=w.layout()
        g=self._add_group(lay,"Performance")
        self._add_toggle(g,"hardware_accel","Hardware acceleration","Use GPU for rendering (faster; disable if glitchy)")
        self._add_toggle(g,"auto_play_media","Auto-play media","Allow pages to auto-play audio and video")
        self._add_toggle(g,"load_images","Load images","Display images on pages (disable to save data and speed up)")
        g2=self._add_group(lay,"Memory & Tabs")
        mr=QWidget(); mh=QHBoxLayout(mr); mh.setContentsMargins(0,0,0,0)
        mh.addWidget(QLabel("Suspend inactive tabs after (minutes):"))
        self.tab_mem_spin=QSpinBox(); self.tab_mem_spin.setRange(1,120)
        self.tab_mem_spin.setValue(self.s.get("tab_memory_limit",50))
        mh.addWidget(self.tab_mem_spin); mh.addStretch(); g2.addWidget(mr)
        self._add_toggle(g2,"session_auto_save","Session auto-save","Save session every 5 min for crash recovery")
        self._add_toggle(g2,"auto_refresh_enabled","Auto-refresh active tab","Keep the current tab refreshed on a timer")
        ar=QWidget(); ah=QHBoxLayout(ar); ah.setContentsMargins(0,0,0,0)
        ah.addWidget(QLabel("Auto-refresh interval (seconds):"))
        self.refresh_spin=QSpinBox(); self.refresh_spin.setRange(5,3600)
        self.refresh_spin.setValue(self.s.get("auto_refresh_interval",60))
        ah.addWidget(self.refresh_spin); ah.addStretch(); g2.addWidget(ar)
        ar2=QWidget(); ah2=QHBoxLayout(ar2); ah2.setContentsMargins(0,0,0,0)
        ah2.addWidget(QLabel("History retention days:"))
        self.history_retention_spin=QSpinBox(); self.history_retention_spin.setRange(1,3650)
        self.history_retention_spin.setValue(self.s.get("history_retention_days",30))
        ah2.addWidget(self.history_retention_spin); ah2.addStretch(); g2.addWidget(ar2)
        ar3=QWidget(); ah3=QHBoxLayout(ar3); ah3.setContentsMargins(0,0,0,0)
        ah3.addWidget(QLabel("Zoom step (%):"))
        self.zoom_step_spin=QSpinBox(); self.zoom_step_spin.setRange(1,50)
        self.zoom_step_spin.setValue(self.s.get("page_zoom_step",10))
        ah3.addWidget(self.zoom_step_spin); ah3.addStretch(); g2.addWidget(ar3)
        return w

    def _page_languages(self):
        w=self._make_w(); lay=w.layout(); t=self.s["theme"]
        g=self._add_group(lay,"Language & Region")
        lr=QWidget(); lh=QHBoxLayout(lr); lh.setContentsMargins(0,0,0,0)
        lh.addWidget(QLabel("Browser language:"))
        self.lang_combo=QComboBox()
        langs=["English (en)","Hindi (hi)","Spanish (es)","French (fr)","German (de)",
               "Portuguese (pt)","Russian (ru)","Chinese (zh)","Japanese (ja)","Arabic (ar)",
               "Bengali (bn)","Turkish (tr)","Korean (ko)","Italian (it)"]
        self.lang_combo.addItems(langs); lh.addWidget(self.lang_combo); lh.addStretch(); g.addWidget(lr)
        self._add_toggle(g,"spell_check","Spell check","Underline misspelled words while typing"); return w

    def _page_advanced(self):
        w=self._make_w(); lay=w.layout()
        g=self._add_group(lay,"Developer & Debug")
        self._add_toggle(g,"error_pages","Custom error pages","Show friendly error pages instead of browser default")
        self._add_toggle(g,"fullscreen","Allow fullscreen","Let websites request fullscreen mode")
        self._add_toggle(g,"local_remote_access","Local → Remote access","Allow local HTML to access remote URLs")
        g1=self._add_group(lay,"Page View")
        self._add_toggle(g1,"page_dark_filter","Dark filter on pages","Invert and shift colors for easier night reading")
        self._add_toggle(g1,"page_text_only_mode","Text-only mode on pages","Hide media for faster, distraction-free reading")
        g2=self._add_group(lay,"Experimental")
        self._add_toggle(g2,"pip_mode","Picture-in-Picture auto-detect","Auto-activate PiP when switching tabs with video")
        self._add_toggle(g2,"mouse_gesture","Mouse gesture navigation","Right-click drag to go back/forward")
        self._add_toggle(g2,"preload_hover_links","Preload on hover","Prefetch pages when hovering links")
        g3=self._add_group(lay,"Updater")
        ur=QWidget(); uh=QHBoxLayout(ur); uh.setContentsMargins(0,0,0,0)
        uh.addWidget(QLabel("Update page URL:"))
        self.update_url_edit=QLineEdit(self.s.get("update_check_url", UPDATE_CHECK_URL))
        self.update_url_edit.setPlaceholderText("https://your-site.example.com/updates.txt")
        uh.addWidget(self.update_url_edit,1); g3.addWidget(ur)
        ir=QWidget(); ih=QHBoxLayout(ir); ih.setContentsMargins(0,0,0,0)
        ih.addWidget(QLabel("Startup check interval (hours):"))
        self.update_interval_spin=QSpinBox(); self.update_interval_spin.setRange(1,168)
        self.update_interval_spin.setValue(int(self.s.get("update_check_interval_hours",12)))
        ih.addWidget(self.update_interval_spin); ih.addStretch(); g3.addWidget(ir)
        self._add_toggle(g3,"verify_update_hash","Verify update SHA-256","If your update webpage includes sha256=..., verify the installer before running")
        self._add_toggle(g3,"silent_update_install","Silent update install","Run Inno Setup with /VERYSILENT /SUPPRESSMSGBOXES /NORESTART")
        self._add_toggle(g3,"create_desktop_shortcut_on_update","Desktop shortcut after update","Ask Inno Setup to create or refresh the desktop shortcut")
        self._add_toggle(g3,"auto_download_updates","Auto-start update download","When the update window opens, begin downloading immediately")
        self._add_toggle(g3,"update_keep_installer_copy","Keep update installer copy","Do not delete the downloaded setup file after launching it")
        self._add_toggle(g3,"feature_pack_menu_enabled","Show V27 Tools Pack","Show the 20+ extra browser tools in the main menu")
        info=QLabel("⚠️ Experimental features may cause instability. Use with caution.")
        info.setStyleSheet(f"color:{self.s['theme']['warning']};font-size:12px;padding:10px;")
        info.setWordWrap(True); lay.addWidget(info); return w

    def _save(self):
        for key,toggle in self.toggles.items(): self.s[key]=toggle.isChecked()
        if hasattr(self,"zoom_slider"): self.s["zoom_factor"]=self.zoom_slider.value()/100
        if hasattr(self,"font_spin"):   self.s["font_size"]=self.font_spin.value()
        if hasattr(self,"engine_combo"):self.s["search_engine"]=self.engine_combo.currentText()
        if hasattr(self,"dl_path_edit"):self.s["download_path"]=self.dl_path_edit.text()
        if hasattr(self,"ua_combo"):    self.s["user_agent"]=self.ua_combo.currentText()
        if hasattr(self,"proxy_host_edit"): self.s["proxy_host"]=self.proxy_host_edit.text()
        if hasattr(self,"proxy_port_spin"): self.s["proxy_port"]=self.proxy_port_spin.value()
        if hasattr(self,"tab_mem_spin"): self.s["tab_memory_limit"]=self.tab_mem_spin.value()
        if hasattr(self,"refresh_spin"): self.s["auto_refresh_interval"]=self.refresh_spin.value()
        if hasattr(self,"history_retention_spin"): self.s["history_retention_days"]=self.history_retention_spin.value()
        if hasattr(self,"zoom_step_spin"): self.s["page_zoom_step"]=self.zoom_step_spin.value()
        if hasattr(self,"max_dl_spin"):  self.s["max_concurrent_downloads"]=self.max_dl_spin.value()
        if hasattr(self,"homepage_edit"): self.s["custom_homepage_url"]=self.homepage_edit.text()
        if hasattr(self,"update_url_edit"): self.s["update_check_url"]=self.update_url_edit.text().strip() or UPDATE_CHECK_URL
        if hasattr(self,"update_interval_spin"): self.s["update_check_interval_hours"]=self.update_interval_spin.value()
        save_settings_to_disk(self.profile_name,self.s)
        self.accept()

# ═══════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ═══════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self, profile_name="Default"):
        super().__init__()
        global CURRENT_PROFILE_NAME
        CURRENT_PROFILE_NAME = profile_name
        self.profile_name    = profile_name
        self.settings_data   = load_settings(profile_name)
        self.profile_path    = get_profile_path(profile_name)
        self._closed_tabs    = []
        self._reading_mode   = False
        self._focus_mode     = False
        self._update_worker  = None

        # Web engine profiles
        self.browser_profile = QWebEngineProfile(profile_name, self)
        self.browser_profile.setPersistentStoragePath(os.path.join(self.profile_path,"storage"))
        self.browser_profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)
        self.incognito_profile = QWebEngineProfile("Incognito",self)

        # Privacy interceptor
        self.interceptor = PrivacyInterceptor(self.settings_data)
        self.browser_profile.setUrlRequestInterceptor(self.interceptor)
        self.incognito_profile.setUrlRequestInterceptor(self.interceptor)

        self._theme = self.settings_data["theme"]

        # Sub-managers
        self.download_manager  = DownloadManagerDialog(self._theme, self)
        self.browser_profile.downloadRequested.connect(self._handle_download)
        self.incognito_profile.downloadRequested.connect(self._handle_download)
        self.password_manager  = PasswordManager(profile_name)
        self.session_manager   = SessionManager(profile_name)
        self._reading_list_dlg = None
        self._reading_list_data= self._load_reading_list()
        # V26: new ExtensionManager (replaces old ExtensionsDialog as data manager)
        self.extension_manager = ExtensionManager(profile_name)
        self._extensions_mgr   = None  # created lazily in show_extensions

        self._init_ui()
        self._setup_shortcuts()
        # V26: build extension toolbar buttons after UI is ready
        QTimer.singleShot(200, self._rebuild_extension_toolbar_buttons)

        # Session auto-save timer
        if self.settings_data.get("session_auto_save"):
            self._session_timer = QTimer(self)
            self._session_timer.timeout.connect(self._auto_save_session)
            self._session_timer.start(300000)  # 5 min

        # Auto-update
        if self.settings_data.get("auto_update"):
            QTimer.singleShot(5000, self._startup_update_check)

        # Tab memory check timer
        self._tab_check_timer = QTimer(self)
        self._tab_check_timer.timeout.connect(self._check_tab_memory)
        self._tab_check_timer.start(60000)

        # Restore previous session
        if self.settings_data.get("restore_tabs"):
            QTimer.singleShot(800, self._restore_session)
        if self.settings_data.get("restore_last_workspace"):
            QTimer.singleShot(1200, lambda: self.load_workspace("Last Session"))

    def _load_reading_list(self):
        path=os.path.join(self.profile_path,"reading_list.json")
        if os.path.exists(path):
            try:
                with open(path) as f: return json.load(f)
            except: pass
        return []

    def _workspace_dir(self):
        path=os.path.join(self.profile_path,"workspaces")
        os.makedirs(path, exist_ok=True)
        return path

    def _workspace_path(self, name):
        safe=re.sub(r"[^A-Za-z0-9_.-]+","_",name.strip()) or "workspace"
        return os.path.join(self._workspace_dir(),f"{safe}.json")

    def _list_workspaces(self):
        items=[]
        if os.path.exists(self._workspace_dir()):
            for fn in os.listdir(self._workspace_dir()):
                if fn.lower().endswith(".json"):
                    items.append(os.path.splitext(fn)[0])
        return sorted(items, key=str.lower)

    def _capture_tabs(self):
        tabs=[]
        for i in range(self.tabs.count()):
            browser=self.tabs.widget(i)
            if not browser:
                continue
            url=browser.url().toString()
            if not url or url.startswith("about:"):
                continue
            tabs.append({
                "url":url,
                "title":self.tabs.tabText(i) or browser.page().title() or "Tab",
                "pinned": len(self.tabs.tabText(i) or "") <= 2,
                "incognito": browser.page().profile().isOffTheRecord(),
            })
        return tabs

    def save_workspace(self, name=None, silent=False):
        if not name:
            name, ok = QInputDialog.getText(self,"Save Workspace","Workspace name:")
            if not ok or not name.strip():
                return
        data={
            "name":name,
            "saved":str(datetime.datetime.now()),
            "tabs":self._capture_tabs(),
            "active_index":self.tabs.currentIndex(),
        }
        path=self._workspace_path(name)
        with open(path,"w",encoding="utf-8") as f:
            json.dump(data,f,indent=2)
        if not silent:
            self.status.showMessage(f"Workspace saved: {name}",2500)

    def load_workspace(self, name=None):
        if not name:
            name, ok = QInputDialog.getItem(self,"Load Workspace","Workspace:",self._list_workspaces(),0,False)
            if not ok or not name:
                return
        path=self._workspace_path(name)
        if not os.path.exists(path):
            self.status.showMessage("Workspace not found.",2500)
            return
        try:
            with open(path,encoding="utf-8") as f:
                data=json.load(f)
            tabs=data.get("tabs",[])
            if not tabs:
                self.status.showMessage("Workspace is empty.",2500)
                return
            while self.tabs.count():
                self.tabs.removeTab(0)
            for item in tabs:
                self.add_new_tab(QUrl(item.get("url","")), item.get("title","Tab"), focus=False)
            self.tabs.setCurrentIndex(min(data.get("active_index",0), self.tabs.count()-1))
            self.status.showMessage(f"Workspace loaded: {name}",2500)
        except Exception as e:
            self.status.showMessage(f"Workspace load failed: {e}",3000)

    def delete_workspace(self, name=None):
        if not name:
            name, ok = QInputDialog.getItem(self,"Delete Workspace","Workspace:",self._list_workspaces(),0,False)
            if not ok or not name:
                return
        path=self._workspace_path(name)
        if os.path.exists(path):
            os.remove(path)
            self.status.showMessage(f"Workspace deleted: {name}",2500)

    def show_workspaces(self):
        t=self._theme
        dlg=QDialog(self); dlg.setWindowTitle("Workspaces & Tab Groups"); dlg.resize(760,520)
        dlg.setStyleSheet(f"background:{t['bg_primary']};color:{t['text_primary']};")
        lay=QVBoxLayout(dlg)
        title=QLabel("Workspaces & Tab Groups")
        title.setStyleSheet(f"font-size:22px;font-weight:700;color:{t['accent']};")
        lay.addWidget(title)
        lst=QListWidget()
        lst.setStyleSheet(f"background:{t['bg_secondary']};color:{t['text_primary']};border:1px solid {t['border']};border-radius:8px;")
        for name in self._list_workspaces():
            lst.addItem(name)
        lay.addWidget(lst,1)
        row=QHBoxLayout()
        for label,fn in [
            ("Save Workspace",lambda:(self.save_workspace(),lst.clear(),[lst.addItem(n) for n in self._list_workspaces()])),
            ("Load Workspace",lambda:self.load_workspace(lst.currentItem().text() if lst.currentItem() else None)),
            ("Delete Workspace",lambda:(self.delete_workspace(lst.currentItem().text() if lst.currentItem() else None),lst.clear(),[lst.addItem(n) for n in self._list_workspaces()])),
            ("Save Tab Group",lambda:self.save_workspace(f"Group_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")),
        ]:
            b=QPushButton(label); b.clicked.connect(fn); row.addWidget(b)
        row.addStretch()
        close=QPushButton("Close"); close.clicked.connect(dlg.accept); row.addWidget(close)
        lay.addLayout(row)
        dlg.exec()

    def export_history(self):
        path,_=QFileDialog.getSaveFileName(self,"Export History","history.json","JSON (*.json);;HTML (*.html)")
        if not path:
            return
        hist_path=self._hist_path()
        if not os.path.exists(hist_path):
            self.status.showMessage("No history to export.",2500); return
        with open(hist_path,encoding="utf-8") as f:
            hist=json.load(f)
        if path.lower().endswith(".html"):
            with open(path,"w",encoding="utf-8") as f:
                f.write("<html><body><h1>History</h1><ul>")
                for item in hist:
                    f.write(f'<li><a href="{html.escape(item.get("url",""))}">{html.escape(item.get("title",item.get("url","")))}</a></li>')
                f.write("</ul></body></html>")
        else:
            with open(path,"w",encoding="utf-8") as f:
                json.dump(hist,f,indent=2)
        self.status.showMessage(f"History exported to {path}",2500)

    def import_bookmarks(self):
        path,_=QFileDialog.getOpenFileName(self,"Import Bookmarks","","Bookmarks (*.html *.json);;All Files (*.*)")
        if not path:
            return
        bookmarks=self._load_bookmarks()
        imported=0
        try:
            if path.lower().endswith(".json"):
                with open(path,encoding="utf-8") as f:
                    data=json.load(f)
                for item in data:
                    if item.get("url") and not any(b["url"]==item["url"] for b in bookmarks):
                        bookmarks.append({"title":item.get("title",item["url"]), "url":item["url"], "folder":item.get("folder","Imported"), "added":str(datetime.datetime.now())})
                        imported+=1
            else:
                text=open(path,encoding="utf-8",errors="ignore").read()
                for url,title in re.findall(r'<A[^>]*HREF="([^"]+)"[^>]*>([^<]+)</A>', text, re.IGNORECASE):
                    if not any(b["url"]==url for b in bookmarks):
                        bookmarks.append({"title":title, "url":url, "folder":"Imported", "added":str(datetime.datetime.now())})
                        imported+=1
            self._save_bookmarks(bookmarks)
            self.status.showMessage(f"Imported {imported} bookmarks.",2500)
        except Exception as e:
            self.status.showMessage(f"Bookmark import failed: {e}",3000)

    def copy_all_tab_urls(self):
        urls=[]
        for i in range(self.tabs.count()):
            browser=self.tabs.widget(i)
            if browser and browser.url().toString() and not browser.url().toString().startswith("about:"):
                urls.append(browser.url().toString())
        QApplication.clipboard().setText("\n".join(urls))
        self.status.showMessage("All tab URLs copied.",2500)

    def open_clipboard_url(self):
        text=QApplication.clipboard().text().strip()
        if not text:
            self.status.showMessage("Clipboard is empty.",2000); return
        if not text.startswith(("http://","https://","ftp://")) and "." in text and " " not in text:
            text="https://"+text
        self.add_new_tab(QUrl(text), "Clipboard")

    def close_blank_tabs(self):
        closed=0
        for i in reversed(range(self.tabs.count())):
            browser=self.tabs.widget(i)
            if browser and browser.url().toString().startswith("about:"):
                self._close_tab(i); closed+=1
        self.status.showMessage(f"Closed {closed} blank tabs.",2500)

    # ── UI Init ──────────────────────────────
    def _newtab_context(self):
        recent_tabs = []
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            if not browser:
                continue
            url = browser.url().toString()
            if not url or url.startswith("about:"):
                continue
            recent_tabs.append({
                "title": self.tabs.tabText(i) or browser.page().title() or "Tab",
                "url": url,
            })
        history = []
        hist_path = self._hist_path()
        if os.path.exists(hist_path):
            try:
                with open(hist_path) as f:
                    items = json.load(f)
                for item in reversed(items[-8:]):
                    history.append({
                        "title": item.get("title") or item.get("url") or "Page",
                        "url": item.get("url", ""),
                    })
            except Exception:
                pass
        workspaces=self._list_workspaces()[:8]
        return recent_tabs[:8], self._load_bookmarks()[:8], history[:8], workspaces

    def handle_sps_action(self, url):
        action = (url.path() or url.host() or url.toString()).split(":", 1)[-1].lstrip("/")
        if action.startswith("workspace-open-"):
            name = action[len("workspace-open-"):]
            self.load_workspace(unquote_plus(name))
            return
        actions = {
            "new-tab": lambda: self.add_new_tab(),
            "new-incognito": lambda: self.add_new_tab(incognito=True),
            "command-palette": self.show_command_palette,
            "tab-organizer": self.show_tab_organizer,
            "workspaces": self.show_workspaces,
            "bookmarks": self.show_bookmarks,
            "history": self.show_history,
            "downloads": lambda: self.download_manager.show(),
            "notes": self.show_notes,
            "privacy": self.show_privacy_dashboard,
            "settings": self.show_settings,
            "stats": self.show_browser_stats,
            "clear-cache": self.clear_browser_cache,
            "session-snapshot": self.save_session_snapshot,
            "restore-snapshot": self.restore_session_snapshot,
            "external-browser": self.open_current_page_externally,
            "save-page-text": self.save_page_as_text,
            "clear-site-data": self.clear_current_site_data,
            "toggle-images": self.toggle_current_tab_images,
            "toggle-dark-filter": self.toggle_current_tab_dark_filter,
            "toggle-text-only": self.toggle_current_tab_text_only,
            "toggle-auto-refresh": self.toggle_auto_refresh,
            "export-history": self.export_history,
            "import-bookmarks": self.import_bookmarks,
            "copy-all-urls": self.copy_all_tab_urls,
            "open-clipboard": self.open_clipboard_url,
            "close-blank-tabs": self.close_blank_tabs,
        }
        fn = actions.get(action)
        if fn:
            fn()
        else:
            self.status.showMessage(f"Unknown dashboard action: {action}", 2500)

    def _init_ui(self):
        t=self._theme
        self.setWindowTitle(f"{APP_NAME} v{VERSION}  —  {self.profile_name}")
        self.setMinimumSize(1200,800)
        self._apply_global_style()

        central=QWidget(); self.setCentralWidget(central)
        root=QVBoxLayout(central); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # Toolbar
        self.toolbar=QToolBar(); self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(18,18))
        self.toolbar.setStyleSheet(f"QToolBar{{background:{t['toolbar_bg']};border-bottom:1px solid {t['border']};padding:4px 8px;spacing:4px;}}")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea,self.toolbar)
        self._build_toolbar()

        # Bookmarks bar
        self.bookmarks_bar=QWidget()
        self.bookmarks_bar.setStyleSheet(f"background:{t['bg_secondary']};border-bottom:1px solid {t['border']};")
        self.bookmarks_bar.setFixedHeight(34)
        bbl=QHBoxLayout(self.bookmarks_bar); bbl.setContentsMargins(8,2,8,2); bbl.setSpacing(4)
        self.bm_bar_layout=bbl
        self.bookmarks_bar.setVisible(self.settings_data.get("show_bookmarks_bar",True))
        root.addWidget(self.bookmarks_bar)
        self._refresh_bookmarks_bar()

        # Splitter
        self.splitter=QSplitter(Qt.Orientation.Horizontal); self.splitter.setHandleWidth(1)
        self.sidebar=self._build_sidebar()
        self.sidebar.setVisible(self.settings_data.get("sidebar_visible",True))
        self.splitter.addWidget(self.sidebar)

        right=QWidget(); right_lay=QVBoxLayout(right)
        right_lay.setContentsMargins(0,0,0,0); right_lay.setSpacing(0)

        # Tabs
        self.tabs=QTabWidget()
        self.tabs.setDocumentMode(True); self.tabs.setTabsClosable(True); self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.tabs.currentChanged.connect(self._tab_changed)
        self.tabs.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabs.customContextMenuRequested.connect(self._tab_context_menu)
        self.tabs.setStyleSheet(self._tab_style())
        add_tab_btn=QToolButton(); add_tab_btn.setText("＋"); add_tab_btn.setFixedSize(30,28)
        add_tab_btn.setStyleSheet(f"background:transparent;color:{t['text_secondary']};border:none;font-size:18px;")
        add_tab_btn.clicked.connect(lambda: self.add_new_tab())
        self.tabs.setCornerWidget(add_tab_btn,Qt.Corner.TopRightCorner)
        right_lay.addWidget(self.tabs,1)

        # Find bar
        self.find_bar=FindBar(lambda: self.tabs.currentWidget(),self._theme)
        self.find_bar.hide(); right_lay.addWidget(self.find_bar)

        # Instant answer
        self.instant_label=QLabel()
        self.instant_label.setStyleSheet(f"background:{t['accent_light']};color:{t['accent']};"
                                         f"padding:8px 16px;font-weight:600;border-top:1px solid {t['border']};")
        self.instant_label.hide(); right_lay.addWidget(self.instant_label)

        self.splitter.addWidget(right); self.splitter.setSizes([230,980])
        root.addWidget(self.splitter,1)

        # Status bar
        self.status=QStatusBar()
        self.status.setStyleSheet(f"background:{t['bg_secondary']};color:{t['text_secondary']};font-size:11px;")
        self.setStatusBar(self.status)
        self.status.setVisible(self.settings_data.get("show_status_bar",True))
        self._security_lbl=QLabel("🔒"); self.status.addPermanentWidget(self._security_lbl)
        self._blocked_lbl=QLabel(); self.status.addPermanentWidget(self._blocked_lbl)
        self._zoom_status=QLabel("100%"); self.status.addPermanentWidget(self._zoom_status)
        QTimer.singleShot(2000,self._update_blocked_count)

        # System tray
        self._setup_tray()

        self.add_new_tab(label="New Tab")

    def _apply_global_style(self):
        t=self._theme; accent=self.settings_data.get("accent_color",t["accent"])
        self.setStyleSheet(f"""
            QMainWindow{{background:{t['bg_primary']};}}
            QLineEdit{{background:{t['bg_secondary']};color:{t['text_primary']};
                       border:1px solid {t['border']};border-radius:20px;padding:7px 18px;font-size:14px;}}
            QLineEdit:focus{{border:2px solid {accent};}}
            QPushButton{{background:transparent;color:{t['text_primary']};border:none;
                         padding:7px 14px;border-radius:8px;font-weight:600;}}
            QPushButton:hover{{background:{t['hover']};}}
            QMenu{{background:{t['bg_primary']};color:{t['text_primary']};
                   border:1px solid {t['border']};border-radius:10px;padding:6px;}}
            QMenu::item{{padding:9px 24px;border-radius:6px;}}
            QMenu::item:selected{{background:{t['hover']};}}
            QDialog{{background:{t['bg_primary']};}}
            QLabel{{color:{t['text_primary']};}}
            QListWidget{{background:{t['bg_secondary']};color:{t['text_primary']};
                         border:1px solid {t['border']};border-radius:8px;outline:none;}}
            QListWidget::item{{padding:10px;border-radius:6px;margin:2px;}}
            QListWidget::item:hover{{background:{t['hover']};}}
            QListWidget::item:selected{{background:{accent};color:white;}}
            QScrollBar:vertical{{background:{t['bg_secondary']};width:8px;border-radius:4px;}}
            QScrollBar::handle:vertical{{background:{t['border']};border-radius:4px;min-height:20px;}}
            QGroupBox{{color:{t['text_primary']};border:1px solid {t['border']};
                       border-radius:10px;margin-top:12px;padding:10px;}}
            QGroupBox::title{{subcontrol-origin:margin;padding:0 6px;}}
        """)

    def _tab_style(self):
        t=self._theme; accent=self.settings_data.get("accent_color",t["accent"])
        return f"""
            QTabBar::tab{{background:{t['tab_inactive']};color:{t['text_secondary']};
                          padding:10px 24px 10px 16px;border-top-left-radius:10px;
                          border-top-right-radius:10px;margin-right:3px;
                          border:1px solid {t['border']};font-size:13px;max-width:200px;}}
            QTabBar::tab:selected{{background:{t['tab_active']};color:{t['text_primary']};
                                   font-weight:600;border-top:2.5px solid {accent};border-bottom:none;}}
            QTabBar::tab:hover{{background:{t['hover']};}}
            QTabWidget::pane{{border:none;}}QTabWidget::tab-bar{{left:8px;}}
        """

    def _build_toolbar(self):
        t=self._theme; accent=self.settings_data.get("accent_color",t["accent"])
        def nav_btn(text,tip,slot,w=38,h=36):
            b=QPushButton(text); b.setFixedSize(w,h); b.setToolTip(tip)
            b.setStyleSheet(
                f"QPushButton{{font-size:16px;color:{t['text_primary']};border-radius:8px;"
                f"background:transparent;padding:0px;min-width:{w}px;max-width:{w}px;}}"
                f"QPushButton:hover{{background:{t['hover']};}}"
            )
            b.clicked.connect(slot); self.toolbar.addWidget(b); return b

        nav_btn("☰","Toggle sidebar (Ctrl+B)",self._toggle_sidebar,38)
        self.back_btn   =nav_btn("←","Back (Alt+←)",    self.go_back,38)
        self.fwd_btn    =nav_btn("→","Forward (Alt+→)",  self.go_forward,38)
        self.reload_btn =nav_btn("↻","Reload (Ctrl+R)",  self.reload_page,38)
        nav_btn("🏠","Home",self.navigate_home,38)

        self.engine_btn=QPushButton(self.settings_data.get("search_engine","SPS Search"))
        self.engine_btn.setFixedSize(130,34)
        self.engine_btn.setStyleSheet(
            f"QPushButton{{background:{t['bg_secondary']};color:{accent};"
            f"border:1px solid {t['border']};border-radius:17px;font-weight:700;font-size:11px;"
            f"min-width:130px;max-width:130px;padding:0 8px;}}"
        )
        self.engine_btn.clicked.connect(self._cycle_engine); self.toolbar.addWidget(self.engine_btn)

        self.url_bar=QLineEdit()
        self.url_bar.setPlaceholderText("🔍 Search or enter URL…")
        self.url_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.url_bar.setFixedHeight(36)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.textChanged.connect(self._instant_answers)
        self.url_bar.focusInEvent=self._url_focus_in
        self.toolbar.addWidget(self.url_bar)

        self.lock_btn=QPushButton("🔒"); self.lock_btn.setFixedSize(34,34)
        self.lock_btn.setStyleSheet(
            f"QPushButton{{color:{t['success']};font-size:15px;background:transparent;border:none;padding:0;}}"
            f"QPushButton:hover{{background:{t['hover']};border-radius:8px;}}"
        )
        self.lock_btn.setToolTip("Click for site info"); self.lock_btn.clicked.connect(self.show_site_info)
        self.toolbar.addWidget(self.lock_btn)

        nav_btn("⭐","Add bookmark (Ctrl+D)",self.add_bookmark_current,38)

        nav_btn("−","Zoom out (Ctrl+-)",self.zoom_out,32)
        self.zoom_lbl=QLabel("100%"); self.zoom_lbl.setFixedSize(44,36)
        self.zoom_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_lbl.setStyleSheet(f"color:{t['text_secondary']};font-size:12px;")
        self.toolbar.addWidget(self.zoom_lbl)
        nav_btn("＋","Zoom in (Ctrl++)",self.zoom_in,32)

        ai_btn=QPushButton("🤖 AI"); ai_btn.setFixedSize(68,34)
        ai_btn.setStyleSheet(
            f"QPushButton{{background:{accent};color:white;border-radius:17px;font-weight:700;"
            f"font-size:13px;padding:0 10px;min-width:68px;max-width:68px;}}"
        )
        ai_btn.clicked.connect(self._show_ai_hub); self.toolbar.addWidget(ai_btn)

        self.menu_btn=QPushButton("⋮"); self.menu_btn.setFixedSize(36,36)
        self.menu_btn.setStyleSheet(
            f"QPushButton{{font-size:20px;color:{t['text_primary']};border-radius:8px;background:transparent;padding:0;}}"
            f"QPushButton:hover{{background:{t['hover']};}}"
        )
        self.menu_btn.clicked.connect(self._show_main_menu); self.toolbar.addWidget(self.menu_btn)

    def _build_sidebar(self):
        t=self._theme; accent=self.settings_data.get("accent_color",t["accent"])
        sb=QWidget(); sb.setFixedWidth(self.settings_data.get("sidebar_width",230))
        sb.setStyleSheet(f"background:{t['sidebar_bg']};border-right:1px solid {t['border']};")
        lay=QVBoxLayout(sb); lay.setContentsMargins(8,16,8,16); lay.setSpacing(4)
        logo=QLabel(f"<b>SPS</b> Browser")
        logo.setStyleSheet(f"font-size:18px;color:{accent};padding:8px 10px 16px;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter); lay.addWidget(logo)
        self.sidebar_list=QListWidget()
        self.sidebar_list.setStyleSheet(f"""
            QListWidget{{background:transparent;border:none;color:{t['text_primary']};font-size:13px;outline:none;}}
            QListWidget::item{{padding:11px 14px;border-radius:10px;margin:2px 4px;}}
            QListWidget::item:hover{{background:{t['hover']};}}
            QListWidget::item:selected{{background:{accent}22;color:{accent};font-weight:700;}}
        """)
        items=[
            ("🏠 Home","home"),("⭐ Bookmarks","bookmarks"),("🕒 History","history"),
            ("📥 Downloads","downloads"),("🔐 Passwords","passwords"),
            ("📚 Reading List","reading_list"),("📝 Notes","notes"),
            ("🧩 Extensions","extensions"),("🍪 Cookies","cookies"),
            ("🛡️ Privacy Shield","privacy"),("📸 Screenshot","screenshot"),
            ("📄 Export PDF","pdf"),("🔍 SPS Lens","lens"),
            ("🌐 Translate","translate"),("📖 Reader Mode","reader"),
            ("💻 Dev Tools","devtools"),("👤 Profiles","profiles"),
            ("⚙️ Settings","settings"),
        ]
        for label,tag in items:
            item=QListWidgetItem(label); item.setData(Qt.ItemDataRole.UserRole,tag)
            self.sidebar_list.addItem(item)
        self.sidebar_list.itemClicked.connect(self._sidebar_click); lay.addWidget(self.sidebar_list,1)
        self.shield_badge=QLabel("🛡️ 0 blocked")
        self.shield_badge.setStyleSheet(f"color:{t['text_secondary']};font-size:11px;padding:4px 10px;")
        self.shield_badge.setAlignment(Qt.AlignmentFlag.AlignCenter); lay.addWidget(self.shield_badge)
        return sb

    # ── System Tray ───────────────────────────
    def _setup_tray(self):
        self.tray=QSystemTrayIcon(self)
        self.tray.setToolTip("SPS Browser Pro")
        tray_menu=QMenu()
        tray_menu.addAction("Show Browser",self.show)
        tray_menu.addAction("New Tab",lambda: (self.show(),self.add_new_tab()))
        tray_menu.addAction("New Incognito Tab",lambda: (self.show(),self.add_new_tab(incognito=True)))
        tray_menu.addSeparator()
        tray_menu.addAction("Quit",QApplication.instance().quit)
        self.tray.setContextMenu(tray_menu)
        self.tray.activated.connect(lambda r: self.show() if r==QSystemTrayIcon.ActivationReason.Trigger else None)
        self.tray.show()

    # ── Shortcuts ─────────────────────────────
    def _setup_shortcuts(self):
        def s(key,fn): QShortcut(QKeySequence(key),self).activated.connect(fn)
        s("Ctrl+T",       lambda: self.add_new_tab())
        s("Ctrl+W",       lambda: self._close_tab(self.tabs.currentIndex()))
        s("Ctrl+Shift+T", self._reopen_closed_tab)
        s("Ctrl+L",       lambda: (self.url_bar.setFocus(),self.url_bar.selectAll()))
        s("Ctrl+R",       self.reload_page)
        s("Ctrl+Shift+R", self.hard_reload)
        s("F5",           self.reload_page)
        s("Ctrl+B",       self._toggle_sidebar)
        s("Ctrl+D",       self.add_bookmark_current)
        s("Ctrl+H",       self.show_history)
        s("Ctrl+J",       lambda: self.download_manager.show())
        s("Ctrl++",       self.zoom_in)
        s("Ctrl+=",       self.zoom_in)
        s("Ctrl+-",       self.zoom_out)
        s("Ctrl+0",       self.reset_zoom)
        s("F12",          self.open_dev_tools)
        s("Ctrl+U",       self.view_source)
        s("Ctrl+P",       self.print_page)
        s("Ctrl+S",       self.save_page)
        s("Ctrl+F",       self.find_bar.show_and_focus)
        s("Escape",       self.find_bar.hide)
        s("Alt+Left",     self.go_back)
        s("Alt+Right",    self.go_forward)
        s("Ctrl+Tab",     self._next_tab)
        s("Ctrl+Shift+Tab",self._prev_tab)
        s("Ctrl+M",       self._mute_current_tab)
        s("Ctrl+Shift+N", lambda: self.add_new_tab(incognito=True))
        s("Ctrl+I",       self.show_site_info)
        s("Ctrl+K",       self.show_command_palette)
        s("Ctrl+Shift+A", self.show_tab_organizer)
        s("Ctrl+Shift+P", self.show_command_palette)
        s("F11",          self._toggle_focus_mode)

    # ── Tab management ────────────────────────
    def add_new_tab(self, qurl=None, label="New Tab", incognito=False, focus=True):
        profile=self.incognito_profile if incognito else self.browser_profile
        browser=BrowserTab(profile,self)
        if qurl is None:
            recent_tabs, bookmarks, history, workspaces = self._newtab_context()
            html=build_speed_dial_html(self._theme,recent_tabs,bookmarks,history,workspaces,self.settings_data)
            browser.setHtml(html,QUrl("about:newtab"))
        else:
            u=qurl if isinstance(qurl,QUrl) else QUrl(qurl)
            browser.setUrl(u)
        label_txt=("🕵️ "+label) if incognito else label
        i=self.tabs.addTab(browser,label_txt)
        if focus:
            self.tabs.setCurrentIndex(i)
        browser.urlChanged.connect(lambda u,b=browser: self._url_changed(u,b))
        browser.titleChanged.connect(lambda ttl,b=browser: self.tabs.setTabText(
            self.tabs.indexOf(b),(("🕵️ " if incognito else "")+(ttl or "New Tab"))[:28]))
        browser.loadStarted.connect(lambda: self.reload_btn.setText("✕"))
        browser.loadFinished.connect(self._load_finished)
        browser.loadFinished.connect(lambda ok,b=browser: self._apply_tab_runtime_settings(b))
        browser.page().linkHovered.connect(lambda u: self.status.showMessage(u,3000))
        self._update_title()
        # Inject userscripts on load finish
        browser.loadFinished.connect(lambda ok,b=browser: self._inject_userscripts(b))
        self._apply_tab_runtime_settings(browser)
        return browser

    def _inject_userscripts(self, browser):
        url = browser.url().toString()
        scripts = self.extension_manager.get_scripts_for_url(url)
        for s in scripts:
            if s.get("type","JavaScript") == "JavaScript":
                browser.page().runJavaScript(s.get("code",""))
            else:  # CSS
                css = s.get("code","").replace("`","\\`")
                js = f"var s=document.createElement('style');s.textContent=`{css}`;document.head.appendChild(s);"
                browser.page().runJavaScript(js)
        # V26: Fingerprint protection injection
        self._inject_fingerprint_protection(browser)

    def _inject_fingerprint_protection(self, browser):
        """Inject JS to mitigate canvas/WebGL/audio/font fingerprinting."""
        sd = self.settings_data
        parts = []
        if sd.get("randomize_canvas_noise", True):
            parts.append("""
(function(){
  var orig=HTMLCanvasElement.prototype.toDataURL;
  HTMLCanvasElement.prototype.toDataURL=function(type){
    var ctx=this.getContext('2d');
    if(ctx){var img=ctx.getImageData(0,0,this.width,this.height);
    for(var i=0;i<img.data.length;i+=4){img.data[i]+=Math.floor(Math.random()*2-1);}
    ctx.putImageData(img,0,0);}
    return orig.apply(this,arguments);};
  var orig2=HTMLCanvasElement.prototype.toBlob;
  HTMLCanvasElement.prototype.toBlob=function(){
    this.toDataURL();return orig2.apply(this,arguments);};
})();""")
        if sd.get("randomize_webgl_vendor", True):
            parts.append("""
(function(){
  var getParam=WebGLRenderingContext.prototype.getParameter;
  WebGLRenderingContext.prototype.getParameter=function(p){
    if(p===37445)return 'Intel Open Source Technology Center';
    if(p===37446)return 'Mesa DRI Intel(R) HD Graphics';
    return getParam.call(this,p);};
  if(window.WebGL2RenderingContext){
    var gp2=WebGL2RenderingContext.prototype.getParameter;
    WebGL2RenderingContext.prototype.getParameter=function(p){
      if(p===37445)return 'Intel Open Source Technology Center';
      if(p===37446)return 'Mesa DRI Intel(R) HD Graphics';
      return gp2.call(this,p);};}
})();""")
        if sd.get("block_fingerprinting_audio", True):
            parts.append("""
(function(){
  if(!window.AudioContext&&!window.webkitAudioContext)return;
  var AC=window.AudioContext||window.webkitAudioContext;
  var origGetChan=AC.prototype.createOscillator;
  var origAnalyser=AC.prototype.createAnalyser;
  var _noise=function(arr){for(var i=0;i<arr.length;i++)arr[i]+=Math.random()*0.0001-0.00005;};
  AC.prototype.createAnalyser=function(){
    var node=origAnalyser.apply(this,arguments);
    var orig=node.getFloatFrequencyData.bind(node);
    node.getFloatFrequencyData=function(a){orig(a);_noise(a);};
    return node;};
})();""")
        if sd.get("block_battery_api", True):
            parts.append("""
(function(){
  if(navigator.getBattery){
    navigator.getBattery=function(){
      return Promise.resolve({charging:true,chargingTime:0,dischargingTime:Infinity,level:1.0,
        addEventListener:function(){},removeEventListener:function(){}});};
  }
})();""")
        if sd.get("spoof_timezone", False):
            parts.append("""
(function(){
  var _orig=Date.prototype.getTimezoneOffset;
  Date.prototype.getTimezoneOffset=function(){return 0;};
  var _origToStr=Date.prototype.toString;
  Date.prototype.toString=function(){return _origToStr.call(this).replace(/\\(.*\\)/,'(UTC)');};
})();""")
        if parts:
            browser.page().runJavaScript("(function(){\n" + "\n".join(parts) + "\n})();")

    def _apply_tab_runtime_settings(self, browser):
        if not browser:
            return
        s = self.settings_data
        images_enabled = getattr(browser, "_sps_images_enabled_override", None)
        if images_enabled is None:
            images_enabled = s.get("load_images", True)
            browser._sps_images_enabled_override = images_enabled
        browser.settings().setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, images_enabled)
        browser.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, s.get("js_enabled", True))
        dark_on = s.get("page_dark_filter", False)
        dark_state = getattr(browser, "_sps_dark_filter_enabled", None)
        if dark_state is None:
            dark_state = dark_on
            browser._sps_dark_filter_enabled = dark_state
        if dark_state:
            browser.page().runJavaScript(
                "(function(){var style=document.getElementById('sps-dark-filter');"
                "if(!style){style=document.createElement('style');style.id='sps-dark-filter';"
                "style.textContent='html{filter:invert(1) hue-rotate(180deg) !important;background:#111 !important;} "
                "img,video,iframe,canvas,svg{filter:invert(1) hue-rotate(180deg) !important;}';"
                "document.head.appendChild(style);}})();"
            )
        else:
            browser.page().runJavaScript("(function(){var s=document.getElementById('sps-dark-filter'); if(s) s.remove();})();")

        text_on = s.get("page_text_only_mode", False)
        text_state = getattr(browser, "_sps_text_only_enabled", None)
        if text_state is None:
            text_state = text_on
            browser._sps_text_only_enabled = text_state
        if text_state:
            browser.page().runJavaScript(
                "(function(){var style=document.getElementById('sps-text-only');"
                "if(!style){style=document.createElement('style');style.id='sps-text-only';"
                "style.textContent='img,video,iframe,canvas,svg,object,embed{display:none !important;}';"
                "document.head.appendChild(style);}})();"
            )
        else:
            browser.page().runJavaScript("(function(){var s=document.getElementById('sps-text-only'); if(s) s.remove();})();")

        refresh_state = getattr(browser, "_sps_auto_refresh_enabled", None)
        if refresh_state is None:
            refresh_state = s.get("auto_refresh_enabled", False)
            browser._sps_auto_refresh_enabled = refresh_state
        if refresh_state:
            interval = max(5, int(s.get("auto_refresh_interval", 60)))
            if not hasattr(browser, "_sps_auto_refresh_timer"):
                browser._sps_auto_refresh_timer = QTimer(browser)
                browser._sps_auto_refresh_timer.timeout.connect(browser.reload)
            browser._sps_auto_refresh_timer.start(interval * 1000)
        elif hasattr(browser, "_sps_auto_refresh_timer"):
            browser._sps_auto_refresh_timer.stop()

    def _close_tab(self, i):
        browser=self.tabs.widget(i)
        if browser:
            self._closed_tabs.append((browser.url(),self.tabs.tabText(i)))
            if len(self._closed_tabs)>30: self._closed_tabs.pop(0)
        if self.tabs.count()>1: self.tabs.removeTab(i)
        else:
            recent_tabs, bookmarks, history, workspaces = self._newtab_context()
            html=build_speed_dial_html(self._theme,recent_tabs,bookmarks,history,workspaces,self.settings_data)
            self.tabs.currentWidget().setHtml(html,QUrl("about:newtab"))
        self._update_title()

    def _reopen_closed_tab(self):
        if self._closed_tabs:
            url,title=self._closed_tabs.pop(); self.add_new_tab(url,title)

    def _tab_changed(self,i):
        if i<0 or not self.tabs.widget(i): return
        self._url_changed(self.tabs.widget(i).url(),self.tabs.widget(i))

    def _next_tab(self): self.tabs.setCurrentIndex((self.tabs.currentIndex()+1)%self.tabs.count())
    def _prev_tab(self): self.tabs.setCurrentIndex((self.tabs.currentIndex()-1)%self.tabs.count())
    def _mute_current_tab(self):
        p=self.tabs.currentWidget().page(); p.setAudioMuted(not p.isAudioMuted())
        self.status.showMessage("🔇 Tab muted" if p.isAudioMuted() else "🔊 Tab unmuted",2000)

    def _tab_context_menu(self,pos):
        idx=self.tabs.tabBar().tabAt(pos)
        if idx<0: return
        m=QMenu(self)
        m.addAction("Duplicate Tab",    lambda: self.add_new_tab(self.tabs.widget(idx).url()))
        m.addAction("Pin Tab",          lambda: self._pin_tab(idx))
        m.addAction("Mute/Unmute Tab",  lambda: self._mute_tab(idx))
        m.addAction("Move to New Window",lambda: self._move_to_window(idx))
        m.addAction("Add to Reading List",lambda: self.add_to_reading_list(
            self.tabs.widget(idx).url().toString(),self.tabs.tabText(idx)))
        m.addSeparator()
        m.addAction("Close Tab",        lambda: self._close_tab(idx))
        m.addAction("Close Other Tabs", lambda: self._close_others(idx))
        m.addAction("Close Tabs to Right",lambda: [self._close_tab(i) for i in reversed(range(idx+1,self.tabs.count()))])
        m.exec(self.tabs.mapToGlobal(pos))

    def _build_command_palette_commands(self):
        commands = []

        def add(label, callback, detail="", category="Browser", keywords=""):
            commands.append({
                "label": label,
                "detail": detail,
                "category": category,
                "keywords": keywords,
                "callback": callback,
            })

        add("New Tab", lambda: self.add_new_tab(), "Open a fresh tab", "Browser", "tab new open")
        add("New Incognito Tab", lambda: self.add_new_tab(incognito=True), "Open a private tab", "Browser", "private incognito")
        add("Reopen Closed Tab", self._reopen_closed_tab, "Restore the last closed tab", "Browser", "undo close restore")
        add("Tab Organizer", self.show_tab_organizer, "Search and manage all open tabs", "Browser", "tabs organizer search")
        add("Workspaces", self.show_workspaces, "Save, load, and delete workspaces", "Browser", "workspace groups tabs")
        add("V27 Tools Pack", self.show_tools_pack, "Open 20+ extra tab, clipboard, bookmark, and session tools", "Tools", "feature pack bulk tabs")
        add("Bookmarks", self.show_bookmarks, "Browse saved sites", "Browser", "saved links")
        add("History", self.show_history, "Review recent visits", "Browser", "recent pages")
        add("Downloads", lambda: self.download_manager.show(), "Open the download manager", "Browser", "download files")
        add("Password Manager", self.show_password_manager, "Manage saved passwords", "Browser", "password vault")
        add("Reading List", self.show_reading_list, "Open your reading list", "Browser", "reading later")
        add("Notes", self.show_notes, "Open browser notes", "Browser", "notes memo")
        add("Extensions", self.show_extensions, "Manage userscripts and extensions", "Browser", "extensions userscripts")
        add("Cookies", self.show_cookie_manager, "Inspect and delete cookies", "Privacy", "cookies site data")
        add("Privacy Dashboard", self.show_privacy_dashboard, "View blocked trackers and ads", "Privacy", "shield blockers")
        add("Settings", self.show_settings, "Open browser settings", "Browser", "preferences")
        add("Manage Profiles", self.manage_profiles, "Switch browser profile", "Browser", "profile user")
        add("Check for Updates", self._check_updates, "Look for a newer build", "Browser", "update version")
        add("About", self._show_about, "Show app information", "Browser", "info version")
        add("Focus Mode", self._toggle_focus_mode, "Hide browser chrome for distraction-free reading", "View", "zen fullscreen")
        add("Toggle Sidebar", self._toggle_sidebar, "Show or hide the sidebar", "View", "sidebar")
        add("Find in Page", self.find_bar.show_and_focus, "Search within the current page", "Page", "find search")
        add("Toggle Reader Mode", self.toggle_reader_mode, "Open a simplified reading view", "Page", "reader readability")
        add("Translate Page", self.translate_page, "Open the current page in Google Translate", "Page", "translate language")
        add("Site Information", self.show_site_info, "View security and page details", "Page", "lock info")
        add("Developer Tools", self.open_dev_tools, "Inspect the current page", "Page", "devtools inspect")
        add("View Source", self.view_source, "Open the page source", "Page", "source html")
        add("Print Page", self.print_page, "Print the current page", "Page", "print")
        add("Save Page", self.save_page, "Save the current page to disk", "Page", "save")
        add("Screenshot", self.take_screenshot, "Capture the current tab", "Page", "screenshot capture")
        add("Export PDF", self.export_pdf, "Export the current page as PDF", "Page", "pdf")
        add("SPS Lens", self.open_sps_lens, "Send the page URL to visual search", "Page", "lens image")
        add("Copy Page URL", self.copy_current_url, "Copy the current page URL", "Page", "copy url")
        add("Copy Page Title", self.copy_current_title, "Copy the current page title", "Page", "copy title")
        add("Open in External Browser", self.open_current_page_externally, "Open the current page in your system browser", "Page", "external browser")
        add("Save Page as Text", self.save_page_as_text, "Export the readable text of the current page", "Page", "plain text")
        add("Clear Site Data", self.clear_current_site_data, "Delete cookies and cache for this browser profile", "Privacy", "cookies cache data")
        add("Toggle Images", self.toggle_current_tab_images, "Enable or disable images for the current tab", "Page", "images media")
        add("Dark Filter", self.toggle_current_tab_dark_filter, "Invert the current page for a dark reading mode", "Page", "dark filter night")
        add("Text-Only Mode", self.toggle_current_tab_text_only, "Hide media on the current page", "Page", "text only")
        add("Auto Refresh Tab", self.toggle_auto_refresh, "Toggle tab auto-refresh using the configured interval", "Page", "refresh reload")
        add("Duplicate Current Tab", self.duplicate_current_tab, "Open the current tab in a duplicate tab", "Tabs", "duplicate clone")
        add("Mute All Tabs", self.mute_all_tabs, "Mute audio across every open tab", "Tabs", "mute all")
        add("Open Download Folder", self.open_download_folder, "Jump to the downloads directory", "Tools", "folder downloads")
        add("Clear Browser Cache", self.clear_browser_cache, "Clear cached files and reload fresh data", "Privacy", "cache clear")
        add("Browser Stats", self.show_browser_stats, "Show tab, bookmark, and blocker statistics", "Tools", "stats info")
        add("Save Session Snapshot", self.save_session_snapshot, "Save the current tab set to disk", "Tools", "snapshot save")
        add("Restore Session Snapshot", self.restore_session_snapshot, "Restore tabs from the last saved snapshot", "Tools", "snapshot restore")
        add("Export History", self.export_history, "Export browsing history as JSON or HTML", "Tools", "history export")
        add("Import Bookmarks", self.import_bookmarks, "Import bookmarks from HTML or JSON", "Tools", "bookmark import")
        add("Copy All Tab URLs", self.copy_all_tab_urls, "Copy every open tab URL to clipboard", "Tools", "clipboard urls")
        add("Open Clipboard URL", self.open_clipboard_url, "Open the clipboard text as a URL", "Tools", "clipboard open")
        add("Close Blank Tabs", self.close_blank_tabs, "Remove placeholder about:newtab tabs", "Tabs", "clean tabs")
        add("Bookmark All Tabs", self.bookmark_all_tabs, "Save every open tab into a dated bookmark folder", "Tabs", "bookmark all session")
        add("Close Duplicate Tabs", self.close_duplicate_tabs, "Close repeated URLs while keeping one copy", "Tabs", "duplicates clean")
        add("Close Tabs to Left", self.close_tabs_to_left, "Close every tab left of the current tab", "Tabs", "close left")
        add("Close Tabs to Right", self.close_tabs_to_right, "Close every tab right of the current tab", "Tabs", "close right")
        add("Reload All Tabs", self.reload_all_tabs, "Reload all open web pages", "Tabs", "refresh all")
        add("Stop All Tabs", self.stop_all_tabs, "Stop loading in every tab", "Tabs", "stop loading")
        add("Sort Tabs by Title", self.sort_tabs_by_title, "Alphabetize open tabs by title", "Tabs", "sort title")
        add("Sort Tabs by URL", self.sort_tabs_by_url, "Alphabetize open tabs by URL", "Tabs", "sort url")
        add("Reverse Tab Order", self.reverse_tab_order, "Reverse the current tab order", "Tabs", "reverse")
        add("Copy Tabs as Markdown", self.copy_tabs_as_markdown, "Copy a Markdown link list for all tabs", "Tools", "markdown tabs")
        add("Open Clipboard URLs", self.open_clipboard_urls, "Open every URL found on the clipboard", "Tools", "multi url clipboard")
        add("QR Code for Current URL", self.open_current_url_qr, "Open a QR code for the active tab", "Tools", "qr code")
        add("Keyboard Shortcuts", self.show_keyboard_shortcuts, "View all keyboard shortcuts", "Browser", "shortcuts keys")
        add("New Window", self.open_new_window, "Open a fresh browser window", "Browser", "window new")
        add("Scroll to Top", self.scroll_top, "Jump to the top of the current page", "Page", "scroll top")
        add("Scroll to Bottom", self.scroll_bottom, "Jump to the bottom of the current page", "Page", "scroll bottom")
        add("Copy as Markdown Link", self.copy_page_as_markdown_link, "Copy [Title](URL) for the current page", "Page", "markdown copy link")
        add("Extension Store", self.open_extension_store, "Open the SPS extension store", "Extensions", "store install")
        add("Install Extension from URL", self.install_extension_from_url_prompt, "Paste a .json URL to install an extension", "Extensions", "install url")
        add("Toggle Bookmarks Bar", self.toggle_bookmarks_bar, "Show or hide the bookmarks bar", "View", "bookmarks bar")
        add("Clear URL Bar", self.clear_url_bar, "Clear the address bar for quick typing", "Browser", "clear url")
        add("Tab Count", self.show_tab_count_popup, "Show how many tabs are open", "Tabs", "count tabs")

        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            if not browser:
                continue
            title = self.tabs.tabText(i) or browser.page().title() or "Tab"
            url = browser.url().toString()
            add(
                f"Switch to Tab: {title[:60]}",
                lambda idx=i: self.tabs.setCurrentIndex(idx),
                url,
                "Tabs",
                f"{title} {url}",
            )

        for bm in self._load_bookmarks()[:40]:
            add(
                f"Open Bookmark: {bm.get('title', 'Bookmark')[:60]}",
                lambda url=bm.get("url", ""), title=bm.get("title", "Bookmark"): self.add_new_tab(QUrl(url), title),
                bm.get("url", ""),
                "Bookmarks",
                f"{bm.get('title', '')} {bm.get('url', '')}",
            )

        if os.path.exists(self._hist_path()):
            try:
                with open(self._hist_path()) as f:
                    history = json.load(f)
                for h in reversed(history[-40:]):
                    add(
                        f"Open History: {h.get('title', h.get('url', 'Page'))[:60]}",
                        lambda url=h.get("url", ""), title=h.get("title", "Page"): self.add_new_tab(QUrl(url), title),
                        h.get("url", ""),
                        "History",
                        f"{h.get('title', '')} {h.get('url', '')}",
                    )
            except Exception:
                pass

        return commands

    def show_command_palette(self):
        dlg = CommandPaletteDialog(self, self._build_command_palette_commands(), self._theme, self)
        dlg.exec()

    def show_browser_stats(self):
        t = self._theme
        dlg = QDialog(self)
        dlg.setWindowTitle("Browser Stats")
        dlg.resize(520, 420)
        dlg.setStyleSheet(f"background:{t['bg_primary']};color:{t['text_primary']};")
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(16, 16, 16, 16)
        title = QLabel("Browser Stats")
        title.setStyleSheet(f"font-size:22px;font-weight:700;color:{t['accent']};")
        lay.addWidget(title)
        recent_tabs, bookmarks, history, workspaces = self._newtab_context()
        rows = [
            ("Open tabs", str(self.tabs.count())),
            ("Recent tabs", str(len(recent_tabs))),
            ("Bookmarks", str(len(bookmarks))),
            ("Blocked items", str(self.interceptor.total_blocked)),
            ("Profile", self.profile_name),
            ("Search engine", self.settings_data.get("search_engine", "SPS Search")),
        ]
        for label, value in rows:
            row = QFrame()
            row.setStyleSheet(f"background:{t['bg_secondary']};border-radius:12px;margin:3px 0;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(14, 10, 14, 10)
            rl.addWidget(QLabel(label), 1)
            v = QLabel(value)
            v.setStyleSheet(f"font-weight:700;color:{t['accent']};")
            rl.addWidget(v)
            lay.addWidget(row)
        lay.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        lay.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
        dlg.exec()

    def clear_browser_cache(self):
        try:
            self.browser_profile.clearHttpCache()
            self.incognito_profile.clearHttpCache()
            self.status.showMessage("Cache cleared.", 2500)
        except Exception as e:
            self.status.showMessage(f"Cache clear failed: {e}", 3000)

    def open_download_folder(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.settings_data.get("download_path", os.path.expanduser("~/Downloads"))))

    def copy_current_url(self):
        browser = self.tabs.currentWidget()
        if browser:
            QApplication.clipboard().setText(browser.url().toString())
            self.status.showMessage("URL copied.", 2000)

    def copy_current_title(self):
        browser = self.tabs.currentWidget()
        if browser:
            QApplication.clipboard().setText(browser.page().title() or browser.url().toString())
            self.status.showMessage("Title copied.", 2000)

    def duplicate_current_tab(self):
        browser = self.tabs.currentWidget()
        if browser:
            self.add_new_tab(browser.url(), browser.page().title() or "Duplicate")

    def mute_all_tabs(self):
        for i in range(self.tabs.count()):
            page = self.tabs.widget(i).page()
            page.setAudioMuted(True)
        self.status.showMessage("All tabs muted.", 2000)

    def save_session_snapshot(self):
        path = os.path.join(self.profile_path, "session_snapshot.json")
        tabs = []
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            if browser and browser.url().toString() and not browser.url().toString().startswith("about:"):
                tabs.append({"url": browser.url().toString(), "title": self.tabs.tabText(i)})
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"saved": str(datetime.datetime.now()), "tabs": tabs}, f, indent=2)
        self.status.showMessage("Session snapshot saved.", 2500)

    def restore_session_snapshot(self):
        path = os.path.join(self.profile_path, "session_snapshot.json")
        if not os.path.exists(path):
            self.status.showMessage("No session snapshot found.", 2500)
            return
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            for tab in data.get("tabs", []):
                self.add_new_tab(QUrl(tab.get("url", "")), tab.get("title", "Tab"))
            self.status.showMessage("Session snapshot restored.", 2500)
        except Exception as e:
            self.status.showMessage(f"Restore failed: {e}", 3000)

    def open_current_page_externally(self):
        browser = self.tabs.currentWidget()
        if browser:
            QDesktopServices.openUrl(browser.url())
            self.status.showMessage("Opened in external browser.", 2000)

    def save_page_as_text(self):
        browser = self.tabs.currentWidget()
        if not browser:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Page as Text", "", "Text Files (*.txt);;All Files (*.*)")
        if not path:
            return
        def save_text(text):
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text or "")
                self.status.showMessage(f"Saved text to {path}", 2500)
            except Exception as e:
                self.status.showMessage(f"Save failed: {e}", 3000)
        browser.page().toPlainText(save_text)

    def clear_current_site_data(self):
        reply = QMessageBox.question(
            self, "Clear Site Data",
            "Delete all cookies and cache for this browser profile?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            self.browser_profile.cookieStore().deleteAllCookies()
            self.incognito_profile.cookieStore().deleteAllCookies()
            self.browser_profile.clearHttpCache()
            self.incognito_profile.clearHttpCache()
            self.status.showMessage("Site data cleared.", 2500)
        except Exception as e:
            self.status.showMessage(f"Could not clear site data: {e}", 3000)

    def toggle_current_tab_images(self):
        browser = self.tabs.currentWidget()
        if not browser:
            return
        settings = browser.settings()
        enabled = not getattr(browser, "_sps_images_enabled_override", settings.testAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages))
        browser._sps_images_enabled_override = enabled
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, enabled)
        browser.reload()
        self.status.showMessage("Images enabled." if enabled else "Images disabled.", 2000)

    def toggle_current_tab_dark_filter(self):
        browser = self.tabs.currentWidget()
        if not browser:
            return
        enabled = not getattr(browser, "_sps_dark_filter_enabled", False)
        browser._sps_dark_filter_enabled = enabled
        js = """
        (function(){
          var existing=document.getElementById('sps-dark-filter');
          if(existing){ existing.remove(); return; }
          var style=document.createElement('style');
          style.id='sps-dark-filter';
          style.textContent='html{filter:invert(1) hue-rotate(180deg) !important;background:#111 !important;} img,video,iframe,canvas,svg{filter:invert(1) hue-rotate(180deg) !important;}';
          document.head.appendChild(style);
        })();
        """
        browser.page().runJavaScript(js)
        self.status.showMessage("Dark filter toggled.", 2000)

    def toggle_current_tab_text_only(self):
        browser = self.tabs.currentWidget()
        if not browser:
            return
        enabled = not getattr(browser, "_sps_text_only_enabled", False)
        browser._sps_text_only_enabled = enabled
        js = """
        (function(){
          var existing=document.getElementById('sps-text-only');
          if(existing){ existing.remove(); return; }
          var style=document.createElement('style');
          style.id='sps-text-only';
          style.textContent='img,video,iframe,canvas,svg,object,embed{display:none !important;}';
          document.head.appendChild(style);
        })();
        """
        browser.page().runJavaScript(js)
        self.status.showMessage("Text-only mode toggled.", 2000)

    def toggle_auto_refresh(self):
        browser = self.tabs.currentWidget()
        if not browser:
            return
        enabled = not getattr(browser, "_sps_auto_refresh_enabled", False)
        browser._sps_auto_refresh_enabled = enabled
        if enabled:
            interval = max(5, int(self.settings_data.get("auto_refresh_interval", 60)))
            if not hasattr(browser, "_sps_auto_refresh_timer"):
                browser._sps_auto_refresh_timer = QTimer(browser)
                browser._sps_auto_refresh_timer.timeout.connect(browser.reload)
            browser._sps_auto_refresh_timer.start(interval * 1000)
            self.status.showMessage(f"Auto refresh on every {interval}s.", 2500)
        else:
            if hasattr(browser, "_sps_auto_refresh_timer"):
                browser._sps_auto_refresh_timer.stop()
            self.status.showMessage("Auto refresh off.", 2000)

    def _pin_tab(self,i):
        title=self.tabs.tabText(i)
        self.tabs.setTabText(i,title[0] if len(title)>3 else title)

    def _mute_tab(self,i):
        page=self.tabs.widget(i).page(); page.setAudioMuted(not page.isAudioMuted())

    def _move_to_window(self,i):
        url=self.tabs.widget(i).url(); self._close_tab(i)
        w=MainWindow(self.profile_name); w.show(); w.add_new_tab(url)

    def _close_others(self,keep):
        for i in reversed(range(self.tabs.count())):
            if i!=keep: self._close_tab(i)

    def _update_title(self):
        if self.settings_data.get("show_tab_count"):
            self.setWindowTitle(f"{APP_NAME} v{VERSION}  [{self.tabs.count()} tabs]  —  {self.profile_name}")

    # ── URL handling ──────────────────────────
    def _url_changed(self,url,browser):
        if browser!=self.tabs.currentWidget(): return
        s=url.toString()
        self.url_bar.setText(s)
        is_https=s.startswith("https://")
        self.lock_btn.setText("🔒" if is_https else "🔓")
        self.lock_btn.setStyleSheet(
            f"color:{self._theme['success' if is_https else 'warning']};font-size:15px;background:transparent;border:none;")
        self._security_lbl.setText("🔒 Secure" if is_https else "⚠️ Not Secure")
        if not browser.page().profile().isOffTheRecord():
            self._save_history(s,browser.page().title())
        browser._last_active=time.time()

    def _url_focus_in(self,event):
        QLineEdit.focusInEvent(self.url_bar,event); self.url_bar.selectAll()

    def navigate_to_url(self):
        text=self.url_bar.text().strip()
        if not text: return
        if text.startswith("@"): self._handle_at_shortcut(text); return
        # Local file
        if text.startswith("file://") or (not text.startswith("http") and os.path.exists(text) and os.path.isfile(text)):
            if not text.startswith("file://"): text=QUrl.fromLocalFile(text).toString()
            self.tabs.currentWidget().setUrl(QUrl(text)); return
        if "." in text and " " not in text:
            if not text.startswith(("http://","https://","ftp://")): text="https://"+text
            self.tabs.currentWidget().setUrl(QUrl(text))
        else:
            engine_url=SEARCH_ENGINES.get(self.settings_data.get("search_engine","SPS Search"),
                                          SEARCH_ENGINES["SPS Search"])
            self.tabs.currentWidget().setUrl(QUrl(engine_url+quote_plus(text)))

    def _handle_at_shortcut(self,text):
        cmds={"@history":self.show_history,"@bookmarks":self.show_bookmarks,
              "@downloads":self.download_manager.show,"@settings":self.show_settings,
              "@passwords":self.show_password_manager,"@privacy":self.show_privacy_dashboard,
              "@devtools":self.open_dev_tools,"@reader":self.toggle_reader_mode,
              "@screenshot":self.take_screenshot,"@source":self.view_source,
              "@print":self.print_page,"@pdf":self.export_pdf,
              "@notes":self.show_notes,"@reading":self.show_reading_list,
              "@cookies":self.show_cookie_manager,"@extensions":self.show_extensions,
              "@focus":self._toggle_focus_mode}
        fn=cmds.get(text.lower())
        if fn: fn()
        else:
            self.status.showMessage(f"Unknown shortcut: {text}  |  Try @history, @bookmarks, @notes, @settings…",3000)

    def navigate_home(self):
        custom=self.settings_data.get("custom_homepage_url","")
        if custom:
            self.tabs.currentWidget().setUrl(QUrl(custom))
        else:
            recent_tabs, bookmarks, history, workspaces = self._newtab_context()
            html=build_speed_dial_html(self._theme,recent_tabs,bookmarks,history,workspaces,self.settings_data)
            self.tabs.currentWidget().setHtml(html,QUrl("about:newtab"))

    def _load_finished(self,ok):
        self.reload_btn.setText("↻")
        self._update_blocked_count()

    def _instant_answers(self,text):
        self.instant_label.hide()
        if not self.settings_data.get("instant_answers"): return
        # Calculator
        if re.match(r'^[\d\s\+\-\*/\(\)\.%\^]+$',text) and any(c in text for c in "+-*/"):
            try:
                res=eval(text.replace("^","**"))
                self.instant_label.setText(f"= {res}"); self.instant_label.show(); return
            except: pass
        # Conversions
        patterns=[
            (r'^([\d.]+)\s*km\s+to\s+miles?$',   lambda m:f"{m.group(1)} km = {round(float(m.group(1))*0.621371,3)} miles"),
            (r'^([\d.]+)\s*miles?\s+to\s+km$',    lambda m:f"{m.group(1)} mi = {round(float(m.group(1))/0.621371,3)} km"),
            (r'^([\d.]+)\s*kg\s+to\s+lbs?$',      lambda m:f"{m.group(1)} kg = {round(float(m.group(1))*2.20462,3)} lbs"),
            (r'^([\d.]+)\s*lbs?\s+to\s+kg$',      lambda m:f"{m.group(1)} lbs = {round(float(m.group(1))/2.20462,3)} kg"),
            (r'^([\d.]+)\s*°?c\s+to\s+f$',        lambda m:f"{m.group(1)}°C = {round(float(m.group(1))*9/5+32,1)}°F"),
            (r'^([\d.]+)\s*°?f\s+to\s+c$',        lambda m:f"{m.group(1)}°F = {round((float(m.group(1))-32)*5/9,1)}°C"),
            (r'^([\d.]+)\s*m\s+to\s+ft$',         lambda m:f"{m.group(1)} m = {round(float(m.group(1))*3.28084,3)} ft"),
            (r'^([\d.]+)\s*ft\s+to\s+m$',         lambda m:f"{m.group(1)} ft = {round(float(m.group(1))/3.28084,3)} m"),
            (r'^([\d.]+)\s*mb?\s+to\s+gb$',       lambda m:f"{m.group(1)} MB = {round(float(m.group(1))/1024,3)} GB"),
            (r'^([\d.]+)\s*gb\s+to\s+mb$',        lambda m:f"{m.group(1)} GB = {round(float(m.group(1))*1024,1)} MB"),
            (r'^([\d.]+)\s*usd?\s+to\s+eur?$',    lambda m:f"${m.group(1)} ≈ €{round(float(m.group(1))*0.92,2)} (approx)"),
            (r'^([\d.]+)\s*eur?\s+to\s+usd?$',    lambda m:f"€{m.group(1)} ≈ ${round(float(m.group(1))/0.92,2)} (approx)"),
            (r'^sqrt\s*([\d.]+)$',                 lambda m:f"√{m.group(1)} = {round(float(m.group(1))**0.5,6)}"),
        ]
        for pat,fmt in patterns:
            match=re.match(pat,text.strip(),re.IGNORECASE)
            if match: self.instant_label.setText(fmt(match)); self.instant_label.show(); return
        # Time/date
        tl=text.lower().strip()
        if tl in ("time","what time is it","current time"):
            self.instant_label.setText(f"🕒 {datetime.datetime.now().strftime('%H:%M:%S')}")
            self.instant_label.show()
        elif tl in ("date","today","today's date"):
            self.instant_label.setText(f"📅 {datetime.datetime.now().strftime('%A, %B %d %Y')}")
            self.instant_label.show()
        elif tl in ("ip","my ip"):
            self.instant_label.setText("🌐 Use a site like whatismyip.com to find your IP")
            self.instant_label.show()

    # ── Nav helpers ───────────────────────────
    def go_back(self):     self.tabs.currentWidget().back()
    def go_forward(self):  self.tabs.currentWidget().forward()
    def reload_page(self):
        if self.reload_btn.text()=="✕": self.tabs.currentWidget().stop()
        else: self.tabs.currentWidget().reload()
    def hard_reload(self):
        self.tabs.currentWidget().page().triggerAction(QWebEnginePage.WebAction.ReloadAndBypassCache)
    def zoom_in(self):
        step=max(1,int(self.settings_data.get("page_zoom_step",10)))/100
        b=self.tabs.currentWidget(); z=min(b.zoomFactor()+step,5.0)
        b.setZoomFactor(z); self.zoom_lbl.setText(f"{int(z*100)}%"); self._zoom_status.setText(f"{int(z*100)}%")
    def zoom_out(self):
        step=max(1,int(self.settings_data.get("page_zoom_step",10)))/100
        b=self.tabs.currentWidget(); z=max(b.zoomFactor()-step,0.1)
        b.setZoomFactor(z); self.zoom_lbl.setText(f"{int(z*100)}%"); self._zoom_status.setText(f"{int(z*100)}%")
    def reset_zoom(self):
        self.tabs.currentWidget().setZoomFactor(1.0); self.zoom_lbl.setText("100%"); self._zoom_status.setText("100%")
    def view_source(self):
        self.add_new_tab(QUrl("view-source:"+self.tabs.currentWidget().url().toString()),"Source")
    def print_page(self):
        printer=QPrinter(QPrinter.PrinterMode.HighResolution)
        dlg=QPrintDialog(printer,self)
        if dlg.exec()==QPrintDialog.DialogCode.Accepted:
            self.tabs.currentWidget().page().print(printer,lambda ok: None)
    def save_page(self):
        path,_=QFileDialog.getSaveFileName(self,"Save Page","","HTML (*.html);;All (*)")
        if path: self.tabs.currentWidget().page().save(path)

    # ── Sidebar actions ───────────────────────
    def _sidebar_click(self,item):
        tag=item.data(Qt.ItemDataRole.UserRole)
        actions={"home":self.navigate_home,"bookmarks":self.show_bookmarks,
                 "history":self.show_history,"downloads":self.download_manager.show,
                 "passwords":self.show_password_manager,"reading_list":self.show_reading_list,
                 "notes":self.show_notes,"extensions":self.show_extensions,
                 "cookies":self.show_cookie_manager,"privacy":self.show_privacy_dashboard,
                 "screenshot":self.take_screenshot,"pdf":self.export_pdf,
                 "lens":self.open_sps_lens,"translate":self.translate_page,
                 "reader":self.toggle_reader_mode,"devtools":self.open_dev_tools,
                 "profiles":self.manage_profiles,"settings":self.show_settings}
        fn=actions.get(tag)
        if fn: fn()

    def _toggle_sidebar(self):
        v=not self.sidebar.isVisible(); self.sidebar.setVisible(v)
        self.settings_data["sidebar_visible"]=v
        save_settings_to_disk(self.profile_name,self.settings_data)

    def _toggle_focus_mode(self):
        self._focus_mode=not self._focus_mode
        self.toolbar.setVisible(not self._focus_mode)
        self.bookmarks_bar.setVisible(not self._focus_mode and self.settings_data.get("show_bookmarks_bar",True))
        self.sidebar.setVisible(not self._focus_mode and self.settings_data.get("sidebar_visible",True))
        self.status.setVisible(not self._focus_mode)
        self.status.showMessage("Focus mode ON — press F11 to exit" if self._focus_mode else "Focus mode OFF",3000)

    # ── Bookmarks ─────────────────────────────
    def _bm_path(self): return os.path.join(self.profile_path,"bookmarks.json")
    def _load_bookmarks(self):
        try:
            if os.path.exists(self._bm_path()):
                with open(self._bm_path()) as f: return json.load(f)
        except: pass
        return []
    def _save_bookmarks(self,bms):
        with open(self._bm_path(),"w") as f: json.dump(bms,f,indent=2)
        self._refresh_bookmarks_bar()

    def add_bookmark_current(self):
        browser = self.tabs.currentWidget()
        url = browser.url().toString()
        title = browser.page().title() or url
        bms = self._load_bookmarks()
        if any(b["url"] == url for b in bms):
            self.status.showMessage("Already bookmarked.", 2000); return
        bms.append({"title": title, "url": url, "folder": "General",
                     "added": str(datetime.datetime.now())})
        self._save_bookmarks(bms)
        self.status.showMessage(f"⭐ Bookmarked: {title[:40]}", 2500)

    def _refresh_bookmarks_bar(self):
        while self.bm_bar_layout.count():
            item=self.bm_bar_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        t=self._theme
        for bm in self._load_bookmarks()[:14]:
            btn=QPushButton(bm.get("title","?")[:18])
            btn.setStyleSheet(f"background:transparent;color:{t['text_primary']};font-size:12px;padding:2px 8px;border-radius:5px;")
            btn.clicked.connect(partial(self.add_new_tab,QUrl(bm["url"]),bm["title"],False,not self.settings_data.get("open_bookmarks_in_background",False)))
            self.bm_bar_layout.addWidget(btn)
        self.bm_bar_layout.addStretch()

    def show_bookmarks(self):
        t=self._theme; accent=self.settings_data.get("accent_color",t["accent"])
        dlg=QDialog(self); dlg.setWindowTitle("⭐ Bookmarks"); dlg.resize(680,500)
        dlg.setStyleSheet(f"background:{t['bg_primary']};color:{t['text_primary']};")
        lay=QVBoxLayout(dlg)
        hdr=QLabel("⭐ Bookmarks"); hdr.setStyleSheet(f"font-size:20px;font-weight:700;color:{t['text_primary']};padding:10px 0;")
        lay.addWidget(hdr)
        sr=QHBoxLayout()
        search=QLineEdit(); search.setPlaceholderText("Search bookmarks…")
        search.setStyleSheet(f"background:{t['bg_secondary']};color:{t['text_primary']};border:1px solid {t['border']};border-radius:8px;padding:7px 12px;")
        sr.addWidget(search,1)
        # Folder filter
        folder_cb=QComboBox()
        folders=sorted(set(b.get("folder","General") for b in self._load_bookmarks()))
        folder_cb.addItem("All Folders"); folder_cb.addItems(folders)
        folder_cb.setStyleSheet(f"background:{t['bg_secondary']};color:{t['text_primary']};border:1px solid {t['border']};border-radius:8px;padding:6px;")
        sr.addWidget(folder_cb); lay.addLayout(sr)
        lst=QListWidget()
        lst.setStyleSheet(f"background:{t['bg_secondary']};color:{t['text_primary']};border:1px solid {t['border']};border-radius:8px;")
        def load(q="",folder="All Folders"):
            lst.clear()
            for bm in self._load_bookmarks():
                if folder!="All Folders" and bm.get("folder")!=folder: continue
                if q.lower() in bm["title"].lower() or q.lower() in bm["url"].lower():
                    item=QListWidgetItem(f"[{bm.get('folder','General')}] ⭐ {bm['title']}")
                    item.setData(Qt.ItemDataRole.UserRole,bm["url"]); item.setToolTip(bm["url"]); lst.addItem(item)
        load()
        search.textChanged.connect(lambda q: load(q,folder_cb.currentText()))
        folder_cb.currentTextChanged.connect(lambda f: load(search.text(),f))
        lst.itemDoubleClicked.connect(lambda it: (self.add_new_tab(QUrl(it.data(Qt.ItemDataRole.UserRole)),it.text(),False,not self.settings_data.get("open_bookmarks_in_background",False)),dlg.accept()))
        lay.addWidget(lst,1)
        br=QHBoxLayout()
        for txt,fn,col in [("➕ Add Current",lambda:(self.add_bookmark_current(),load()),accent),
                           ("🗑 Delete",lambda:(self._delete_selected_bm(lst),load()),t['danger']),
                           ("📤 Export",self._export_bookmarks,t['bg_tertiary'])]:
            b=QPushButton(txt); b.setStyleSheet(f"background:{col};color:{'white' if col!=t['bg_tertiary'] else t['text_primary']};border-radius:8px;padding:8px 16px;")
            b.clicked.connect(fn); br.addWidget(b)
        br.addStretch(); lay.addLayout(br); dlg.exec()

    def _delete_selected_bm(self,lst):
        item=lst.currentItem()
        if item:
            url=item.data(Qt.ItemDataRole.UserRole)
            self._save_bookmarks([b for b in self._load_bookmarks() if b["url"]!=url])

    def _export_bookmarks(self):
        path,_=QFileDialog.getSaveFileName(self,"Export Bookmarks","bookmarks.html","HTML (*.html)")
        if path:
            bms=self._load_bookmarks()
            with open(path,"w") as f:
                f.write("<!DOCTYPE NETSCAPE-Bookmark-file-1><META HTTP-EQUIV='Content-Type' CONTENT='text/html; charset=UTF-8'>\n")
                f.write("<TITLE>Bookmarks</TITLE>\n<H1>Bookmarks</H1>\n<DL><p>\n")
                for bm in bms:
                    f.write(f'    <DT><A HREF="{bm["url"]}">{bm["title"]}</A>\n')
                f.write("</DL><p>")
            self.status.showMessage(f"📤 Bookmarks exported to {path}",3000)

    # ── History ───────────────────────────────
    def _hist_path(self): return os.path.join(self.profile_path,"history.json")
    def _save_history(self,url,title):
        if not url or url.startswith("about:"): return
        try:
            hist=[]
            if os.path.exists(self._hist_path()):
                with open(self._hist_path()) as f: hist=json.load(f)
            hist.append({"url":url,"title":title or url,"time":str(datetime.datetime.now())})
            cutoff_days=max(1,int(self.settings_data.get("history_retention_days",30)))
            cutoff=datetime.datetime.now()-datetime.timedelta(days=cutoff_days)
            cleaned=[]
            for item in hist:
                try:
                    t=datetime.datetime.fromisoformat(item.get("time","1970"))
                    if t>=cutoff:
                        cleaned.append(item)
                except Exception:
                    cleaned.append(item)
            with open(self._hist_path(),"w") as f: json.dump(cleaned[-5000:],f)
        except: pass

    def show_history(self):
        t=self._theme; accent=self.settings_data.get("accent_color",t["accent"])
        dlg=QDialog(self); dlg.setWindowTitle("🕒 History"); dlg.resize(720,540)
        dlg.setStyleSheet(f"background:{t['bg_primary']};color:{t['text_primary']};")
        lay=QVBoxLayout(dlg)
        hdr=QLabel("🕒 Browsing History"); hdr.setStyleSheet(f"font-size:20px;font-weight:700;color:{t['text_primary']};padding:10px 0;")
        lay.addWidget(hdr)
        sr=QHBoxLayout()
        search=QLineEdit(); search.setPlaceholderText("Search history…")
        search.setStyleSheet(f"background:{t['bg_secondary']};color:{t['text_primary']};border:1px solid {t['border']};border-radius:8px;padding:7px 12px;")
        # Date filter
        date_combo=QComboBox()
        date_combo.addItems(["All Time","Today","This Week","This Month"])
        date_combo.setStyleSheet(f"background:{t['bg_secondary']};color:{t['text_primary']};border:1px solid {t['border']};border-radius:8px;padding:6px;")
        sr.addWidget(search,1); sr.addWidget(date_combo); lay.addLayout(sr)
        lst=QListWidget()
        lst.setStyleSheet(f"background:{t['bg_secondary']};color:{t['text_primary']};border:1px solid {t['border']};border-radius:8px;")
        def load(q="",period="All Time"):
            lst.clear()
            if os.path.exists(self._hist_path()):
                with open(self._hist_path()) as f: hist=json.load(f)
                now=datetime.datetime.now()
                for h in reversed(hist):
                    try:
                        ht=datetime.datetime.fromisoformat(h.get("time","1970"))
                        if period=="Today" and ht.date()!=now.date(): continue
                        if period=="This Week" and (now-ht).days>7: continue
                        if period=="This Month" and ht.month!=now.month: continue
                    except: pass
                    if q.lower() in h.get("title","").lower() or q.lower() in h.get("url","").lower():
                        item=QListWidgetItem(f"{h.get('time','')[:16]}  •  {h.get('title','') or h.get('url','')}")
                        item.setData(Qt.ItemDataRole.UserRole,h["url"]); lst.addItem(item)
        load()
        search.textChanged.connect(lambda q: load(q,date_combo.currentText()))
        date_combo.currentTextChanged.connect(lambda p: load(search.text(),p))
        lst.itemDoubleClicked.connect(lambda it: (self.add_new_tab(QUrl(it.data(Qt.ItemDataRole.UserRole)), "History", False, not self.settings_data.get("open_links_in_background", False)),dlg.accept()))
        lay.addWidget(lst,1)
        br=QHBoxLayout()
        for txt,fn,col in [("🗑 Delete Selected",lambda:(self._delete_selected_hist(lst),load()),t['warning']),
                           ("🗑 Clear All",lambda:(self._clear_history(dlg),load()),t['danger'])]:
            b=QPushButton(txt); b.setStyleSheet(f"background:{col};color:white;border-radius:8px;padding:8px 16px;")
            b.clicked.connect(fn); br.addWidget(b)
        br.addStretch(); lay.addLayout(br); dlg.exec()

    def _delete_selected_hist(self,lst):
        item=lst.currentItem()
        if item and os.path.exists(self._hist_path()):
            url=item.data(Qt.ItemDataRole.UserRole)
            with open(self._hist_path()) as f: hist=json.load(f)
            hist=[h for h in hist if h["url"]!=url]
            with open(self._hist_path(),"w") as f: json.dump(hist,f)

    def _clear_history(self,parent):
        if QMessageBox.question(parent,"Clear History","Delete all history?")==QMessageBox.StandardButton.Yes:
            with open(self._hist_path(),"w") as f: json.dump([],f)
            self.browser_profile.clearAllVisitedLinks()

    # ── Downloads ─────────────────────────────
    def _download_dest_path(self, filename):
        folder = self.settings_data.get("download_path", os.path.expanduser("~/Downloads"))
        os.makedirs(folder, exist_ok=True)
        base = safe_filename_from_url(filename, "download.bin")
        dest = os.path.join(folder, base)
        if not os.path.exists(dest):
            return dest
        stem, ext = os.path.splitext(base)
        for i in range(1, 1000):
            candidate = os.path.join(folder, f"{stem} ({i}){ext}")
            if not os.path.exists(candidate):
                return candidate
        return os.path.join(folder, f"{stem}_{int(time.time())}{ext}")

    def _quarantine_download(self, temp_path, filename, reasons):
        qdir = os.path.join(BASE_DATA_DIR, "download_quarantine")
        os.makedirs(qdir, exist_ok=True)
        qname = f"{int(time.time())}_{safe_filename_from_url(filename, 'blocked_download.bin')}"
        qpath = os.path.join(qdir, qname)
        shutil.move(temp_path, qpath)
        with open(qpath + ".json", "w") as f:
            json.dump({"file": filename, "quarantined_at": str(datetime.datetime.now()), "reasons": reasons}, f, indent=2)
        return qpath

    def _finish_safe_download(self, temp_path, filename, reasons):
        self.status.showMessage("Download scan complete.", 2500)
        ext = os.path.splitext(filename.lower())[1]

        # Double-extension check (e.g. photo.jpg.bat) — always block
        double_ext_block = False
        if self.settings_data.get("block_double_extension_downloads"):
            parts = filename.lower().split(".")
            if len(parts) >= 3 and f".{parts[-2]}" in DOCUMENT_EXTENSIONS and f".{parts[-1]}" in DANGEROUS_DOWNLOAD_EXTENSIONS:
                double_ext_block = True
                if not any("Double extension" in r for r in reasons):
                    reasons = list(reasons) + [f"Double extension hides an executable: .{parts[-2]}.{parts[-1]}"]

        # Only block truly dangerous script types (bat, cmd, ps1, vbs, etc.) OR double-ext tricks
        # .exe / .msi always download immediately — just show status message
        real_malware = any(r for r in reasons if "malware" in r.lower() or "ransom" in r.lower()
                           or "injection" in r.lower() or "mimikatz" in r.lower()
                           or "credential" in r.lower() or "EICAR" in r)
        script_block = ext in DANGEROUS_DOWNLOAD_EXTENSIONS
        must_block = real_malware or double_ext_block or script_block

        if must_block:
            detail = "\n".join(f"- {r}" for r in reasons[:10]) or "- Dangerous file type"
            reply = QMessageBox.warning(
                self, "Risky Download Detected",
                f"SPS detected a potential threat in:\n{filename}\n\n{detail}\n\nSave this file anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                if self.settings_data.get("quarantine_blocked_downloads", True):
                    qpath = self._quarantine_download(temp_path, filename, reasons)
                    self.status.showMessage(f"Download blocked and quarantined: {os.path.basename(qpath)}", 5000)
                else:
                    try: os.remove(temp_path)
                    except Exception: pass
                    self.status.showMessage("Download blocked and deleted.", 4000)
                return
        elif ext in WARN_ONLY_EXTENSIONS and self.settings_data.get("warn_executable_downloads", True):
            # Soft info notice for .exe/.msi — download proceeds immediately regardless
            self.status.showMessage(f"📥 Downloading executable: {filename}", 4000)

        dest = self._download_dest_path(filename)
        shutil.move(temp_path, dest)
        self.status.showMessage(f"✅ Download saved: {os.path.basename(dest)}", 5000)

    def _safe_download_error(self, msg):
        self.status.showMessage(f"Protected download failed: {msg}", 5000)
        QMessageBox.warning(self, "Download Failed", msg)

    def _trusted_download_domain(self, url):
        if not self.settings_data.get("allow_trusted_download_domains", True):
            return False
        host = urlparse(url).netloc.lower().split(":")[0]
        domains = [
            d.strip().lower()
            for d in self.settings_data.get("trusted_download_domains", "").split(",")
            if d.strip()
        ]
        return any(host == d or host.endswith("." + d) for d in domains)

    def _download_needs_deep_scan(self, url, filename):
        if not self.settings_data.get("scan_downloads_before_saving") or requests is None:
            return False
        ext = os.path.splitext(filename.lower())[1]
        parts = filename.lower().split(".")
        if self._trusted_download_domain(url):
            return False
        # .exe and .msi always go through native fast download — never deep-scan them
        if ext in WARN_ONLY_EXTENSIONS:
            return False
        if url.lower().startswith("http://"):
            return True
        # Double-extension trick: photo.jpg.bat
        if len(parts) >= 3 and f".{parts[-2]}" in DOCUMENT_EXTENSIONS and ext in DANGEROUS_DOWNLOAD_EXTENSIONS:
            return True
        if ext in DANGEROUS_DOWNLOAD_EXTENSIONS:
            return True
        if self.settings_data.get("scan_archives_before_saving") and ext in ARCHIVE_DOWNLOAD_EXTENSIONS:
            return True
        if self.settings_data.get("fast_download_scanning", True):
            return False
        if self.settings_data.get("skip_safe_file_deep_scan", True) and ext in SAFE_FAST_DOWNLOAD_EXTENSIONS:
            return False
        return True

    def _accept_normal_download(self, download):
        download.setDownloadDirectory(self.settings_data.get("download_path", os.path.expanduser("~/Downloads")))
        download.accept()
        self.download_manager.add_download(download)
        self.status.showMessage(f"Downloading: {download.downloadFileName()}", 3000)

    def _handle_download(self, download):
        """V27 fixed download handler — auto-installs .json extension downloads, no .exe malicious warning."""
        target = ""
        filename = ""

        # ── Step 1: Get URL + filename safely ────────────────────
        try:
            target = download.url().toString() if hasattr(download, "url") else ""
        except Exception:
            target = ""
        try:
            filename = download.downloadFileName() or safe_filename_from_url(target) or "download.bin"
        except Exception:
            filename = "download.bin"

        # ── Step 1b: Auto-install .json extension downloads ──────
        # If the file is a .json and comes from a page that looks like an extension store,
        # or if its name contains "extension" or "ext_", install it directly.
        ext_lower = os.path.splitext(filename.lower())[1]
        is_ext_json = ext_lower == ".json" and (
            EXTENSION_STORE_URL and EXTENSION_STORE_URL in target
            or "extension" in filename.lower()
            or "ext_" in filename.lower()
            or "spsext" in filename.lower()
            or (EXTENSION_STORE_URL and EXTENSION_STORE_URL in (
                self.tabs.currentWidget().url().toString() if self.tabs.currentWidget() else ""))
        )
        if is_ext_json and requests is not None:
            download.cancel()
            self.status.showMessage(f"📦 Installing extension from: {filename}", 3000)
            def _install_from_web(url=target):
                def on_done(ext):
                    self.status.showMessage(f"✅ Extension installed: {ext['name']}", 4000)
                    QTimer.singleShot(100, self._rebuild_extension_toolbar_buttons)
                def on_err(msg):
                    self.status.showMessage(f"❌ Extension install failed: {msg}", 5000)
                self.extension_manager.install_extension_from_url(url, on_done, on_err)
            QTimer.singleShot(0, _install_from_web)
            return

        # ── Step 2: Block insecure mixed-content downloads ────────
        if self.settings_data.get("block_insecure_downloads", False):
            try:
                current_url = ""
                w = self.tabs.currentWidget()
                if w: current_url = w.url().toString()
                if current_url.startswith("https://") and target.startswith("http://"):
                    download.cancel()
                    self.status.showMessage("🚫 Blocked insecure download (HTTP on HTTPS page).", 3000)
                    return
            except Exception:
                pass  # Never block on error — fall through

        # ── Step 3: Large download warning ───────────────────────
        if self.settings_data.get("ask_before_large_downloads", False):
            try:
                total = int(download.totalBytes()) if hasattr(download, "totalBytes") else 0
                limit = int(self.settings_data.get("large_download_warning_mb", 500)) * 1024 * 1024
                if total > 0 and total > limit:
                    reply = QMessageBox.question(
                        self, "Large Download",
                        f"This file is {total/1024/1024:.1f} MB. Continue?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.Yes,
                    )
                    if reply != QMessageBox.StandardButton.Yes:
                        download.cancel()
                        self.status.showMessage("Large download cancelled.", 3000)
                        return
            except Exception:
                pass  # If anything goes wrong, proceed

        # ── Step 4: Safe scanning path (only if requests available + scan enabled) ──
        scan_enabled = self.settings_data.get("scan_downloads_before_saving", True)
        # V26 FIX: if requests not available, always use native path (no broken scan)
        if scan_enabled and requests is not None and target.startswith(("http://","https://")):
            try:
                needs_scan = self._download_needs_deep_scan(target, filename)
                if needs_scan:
                    try:
                        total = int(download.totalBytes()) if hasattr(download, "totalBytes") else 0
                    except Exception:
                        total = 0
                    max_scan_bytes = int(self.settings_data.get("max_download_scan_mb", 150)) * 1024 * 1024
                    # V26 FIX: if file is too large for scan, use native path directly
                    if total > 0 and total > max_scan_bytes and self.settings_data.get("fast_download_scanning", True):
                        self.status.showMessage(f"⚡ Large file — using fast download path: {filename}", 3000)
                        self._accept_native_download(download, filename)
                        return
                    # Use safe worker scan path
                    download.cancel()
                    self.status.showMessage(f"🔍 Scanning before saving: {filename}", 4000)
                    worker = SafeDownloadWorker(
                        target, filename,
                        self.settings_data.get("download_scan_sample_kb", 512),
                        not self.settings_data.get("fast_download_scanning", True),
                        self,
                    )
                    if not hasattr(self, "_safe_download_workers"):
                        self._safe_download_workers = []
                    self._safe_download_workers.append(worker)
                    worker.progress.connect(lambda p, n=filename: self.status.showMessage(f"Scanning {n}: {p}%", 1500))
                    worker.finished.connect(self._finish_safe_download)
                    worker.error.connect(self._safe_download_scan_error_fallback)
                    worker.finished.connect(lambda *_a, w=worker: (self._safe_download_workers.remove(w) if w in self._safe_download_workers else None))
                    worker.error.connect(lambda _m, w=worker: (self._safe_download_workers.remove(w) if w in self._safe_download_workers else None))
                    worker.start()
                    return
            except Exception as exc:
                # V26 FIX: on any scan error, fall through to native download
                self.status.showMessage(f"⚠️ Scan error, using direct download: {exc}", 3000)

        # ── Step 5: Native browser download (always works) ───────
        self._accept_native_download(download, filename)

    def _accept_native_download(self, download, filename=""):
        """Always-working native download path using Qt's built-in download engine."""
        try:
            dl_dir = self.settings_data.get("download_path", os.path.expanduser("~/Downloads"))
            os.makedirs(dl_dir, exist_ok=True)
            download.setDownloadDirectory(dl_dir)
            if filename:
                try:
                    download.setDownloadFileName(filename)
                except Exception:
                    pass
            download.accept()
            self.download_manager.add_download(download)
            self.status.showMessage(f"📥 Downloading: {download.downloadFileName() or filename}", 3000)
            if self.settings_data.get("download_progress_in_title", True):
                def _on_progress():
                    try:
                        recv = download.receivedBytes()
                        total = download.totalBytes()
                        if total > 0:
                            pct = int(recv/total*100)
                            self.setWindowTitle(f"[{pct}%] {APP_NAME}")
                        S = QWebEngineDownloadRequest.DownloadState
                        if download.state() in (S.DownloadCompleted, S.DownloadCancelled, S.DownloadInterrupted):
                            self.setWindowTitle(f"{APP_NAME} v{VERSION}  —  {self.profile_name}")
                    except Exception:
                        pass
                download.receivedBytesChanged.connect(_on_progress)
                download.stateChanged.connect(_on_progress)
        except Exception as e:
            # Last resort: try to accept the download with no extra options
            try:
                download.accept()
                self.status.showMessage(f"📥 Download started (basic mode): {filename}", 3000)
            except Exception as e2:
                self.status.showMessage(f"❌ Download failed: {e2}", 5000)

    def _safe_download_scan_error_fallback(self, msg):
        """V26: when the scan worker fails, notify user but don't lose the file context."""
        self.status.showMessage(f"⚠️ Scan error (file may still be in Downloads): {msg}", 6000)

    # ── Password Manager ──────────────────────
    def show_password_manager(self):
        PasswordManagerDialog(self.password_manager,self._theme,self).exec()

    # ── Reading List ──────────────────────────
    def add_to_reading_list(self,url,title):
        path=os.path.join(self.profile_path,"reading_list.json")
        data=[]
        if os.path.exists(path):
            try:
                with open(path) as f: data=json.load(f)
            except: pass
        if any(i["url"]==url for i in data):
            self.status.showMessage("Already in reading list.",2000); return
        data.append({"url":url,"title":title or url,"added":str(datetime.datetime.now()),"read":False})
        with open(path,"w") as f: json.dump(data,f,indent=2)
        self.status.showMessage(f"📚 Added to reading list: {title[:40]}",2500)

    def show_reading_list(self):
        dlg=ReadingListDialog(self.profile_name,self._theme,self)
        dlg.open_url.connect(lambda url,title: self.add_new_tab(QUrl(url),title))
        dlg.exec()

    # ── Notes ─────────────────────────────────
    def show_notes(self):
        NotesDialog(self.profile_name,self._theme,self).exec()

    # ── Extensions ────────────────────────────
    def show_extensions(self):
        dlg = ExtensionsDialog(self.profile_name, self._theme, self.extension_manager, self)
        dlg.extensions_changed.connect(self._rebuild_extension_toolbar_buttons)
        dlg.exec()
        self._rebuild_extension_toolbar_buttons()

    def _show_add_extension(self):
        """Open the Extensions Manager directly on the Add Custom Script tab."""
        dlg = ExtensionsDialog(self.profile_name, self._theme, self.extension_manager, self)
        dlg.extensions_changed.connect(self._rebuild_extension_toolbar_buttons)
        # Switch to Add tab (index 1)
        try:
            for child in dlg.findChildren(QTabWidget):
                child.setCurrentIndex(1); break
        except Exception: pass
        dlg.exec()
        self._rebuild_extension_toolbar_buttons()

    def _rebuild_extension_toolbar_buttons(self):
        """Re-create extension buttons in the toolbar based on enabled+show_in_toolbar extensions."""
        # Remove old extension buttons
        for btn in getattr(self, "_ext_toolbar_btns", []):
            try: self.toolbar.removeAction(btn)
            except: pass
        self._ext_toolbar_btns = []
        if not self.settings_data.get("extensions_toolbar_visible", True):
            return
        for ext in self.extension_manager.get_toolbar_extensions():
            icon = ext.get("icon","🧩")
            name = ext.get("name","Ext")
            code = ext.get("code","")
            ext_type = ext.get("type","JavaScript")
            act = QAction(f"{icon} {name[:12]}", self)
            act.setToolTip(f"Extension: {name}\n{ext.get('description','')}")
            def _run_ext(checked=False, c=code, tp=ext_type):
                browser = self.tabs.currentWidget()
                if not browser: return
                if tp == "CSS":
                    js = f"""(function(){{var s=document.createElement('style');s.textContent={json.dumps(c)};document.head.appendChild(s);}})();"""
                    browser.page().runJavaScript(js)
                else:
                    browser.page().runJavaScript(c)
            act.triggered.connect(_run_ext)
            self.toolbar.addAction(act)
            self._ext_toolbar_btns.append(act)

    # ── Cookie Manager ────────────────────────
    def show_cookie_manager(self):
        CookieManagerDialog(self.browser_profile,self._theme,self).exec()

    # ── Site Info ─────────────────────────────
    def show_site_info(self):
        browser=self.tabs.currentWidget()
        SiteInfoDialog(browser.url().toString(),browser.page().title(),self._theme,self).exec()

    # ── Privacy Dashboard ─────────────────────
    def show_privacy_dashboard(self):
        t=self._theme; accent=self.settings_data.get("accent_color",t["accent"])
        dlg=QDialog(self); dlg.setWindowTitle("🛡️ Privacy Dashboard"); dlg.resize(520,460)
        dlg.setStyleSheet(f"background:{t['bg_primary']};color:{t['text_primary']};")
        lay=QVBoxLayout(dlg)
        title=QLabel("🛡️ SPS Privacy Shield")
        title.setStyleSheet(f"font-size:22px;font-weight:700;color:{accent};padding:12px 0;")
        lay.addWidget(title)
        i=self.interceptor
        for label,val,color in [
            ("🚫 Trackers blocked",     str(i.blocked_trackers),t["danger"]),
            ("🚫 Ads blocked",          str(i.blocked_ads),     t["accent"]),
            ("⛏ Crypto miners blocked", str(i.blocked_crypto),  t["warning"]),
            ("📱 Social trackers",       str(i.blocked_social),  t["warning"]),
            ("📊 Total blocked",        str(i.total_blocked),   t["success"]),
        ]:
            row=QFrame(); row.setStyleSheet(f"background:{t['bg_secondary']};border-radius:10px;margin:3px 0;")
            rh=QHBoxLayout(row); rh.setContentsMargins(16,12,16,12)
            l=QLabel(label); l.setStyleSheet(f"font-size:14px;color:{t['text_primary']};")
            v=QLabel(val);   v.setStyleSheet(f"font-size:22px;font-weight:700;color:{color};")
            rh.addWidget(l,1); rh.addWidget(v); lay.addWidget(row)
        active=[]
        if self.settings_data.get("tracking_protection"): active.append("Enhanced Tracking Protection")
        if self.settings_data.get("ad_blocker"):          active.append("Ad Blocker")
        if self.settings_data.get("block_cryptomining"):  active.append("Crypto Blocker")
        if self.settings_data.get("https_only"):          active.append("HTTPS-Only Mode")
        if self.settings_data.get("block_social_trackers"):active.append("Social Tracker Blocker")
        al=QLabel("Active: "+(" • ".join(active) if active else "None"))
        al.setWordWrap(True); al.setStyleSheet(f"color:{t['text_secondary']};font-size:12px;padding:12px 4px;")
        lay.addWidget(al); dlg.exec()

    # ── Screenshot ────────────────────────────
    def take_screenshot(self):
        t=self._theme
        dlg=QDialog(self); dlg.setWindowTitle("📸 Screenshot"); dlg.resize(400,220)
        dlg.setStyleSheet(f"background:{t['bg_primary']};color:{t['text_primary']};")
        lay=QVBoxLayout(dlg)
        lbl=QLabel("Screenshot Options"); lbl.setStyleSheet(f"font-size:16px;font-weight:700;color:{t['text_primary']};padding:8px 0;")
        lay.addWidget(lbl)
        for txt,fn in [("📸 Save as PNG",self._screenshot_png),
                       ("📸 Save as JPEG",self._screenshot_jpg),
                       ("📋 Copy to Clipboard",self._screenshot_clipboard)]:
            b=QPushButton(txt); b.setStyleSheet(f"background:{t['accent']};color:white;border-radius:8px;padding:10px;margin:3px;")
            b.clicked.connect(lambda _,f=fn: (f(),dlg.accept())); lay.addWidget(b)
        dlg.exec()

    def _screenshot_png(self):
        path,_=QFileDialog.getSaveFileName(self,"Save Screenshot",
            os.path.join(os.path.expanduser("~"),f"sps_screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"),
            "PNG (*.png)")
        if path: self.tabs.currentWidget().grab().save(path); self.status.showMessage(f"📸 Saved {path}",3000)

    def _screenshot_jpg(self):
        path,_=QFileDialog.getSaveFileName(self,"Save Screenshot","screenshot.jpg","JPEG (*.jpg)")
        if path: self.tabs.currentWidget().grab().save(path,"JPEG",92); self.status.showMessage(f"📸 Saved {path}",3000)

    def _screenshot_clipboard(self):
        QApplication.clipboard().setPixmap(self.tabs.currentWidget().grab())
        self.status.showMessage("📋 Screenshot copied to clipboard",2500)

    # ── PDF Export ────────────────────────────
    def export_pdf(self):
        path,_=QFileDialog.getSaveFileName(self,"Export PDF","","PDF (*.pdf)")
        if path:
            self.tabs.currentWidget().page().printToPdf(path)
            self.status.showMessage(f"📄 PDF exported to {path}",3000)

    # ── SPS Lens ──────────────────────────────
    def open_sps_lens(self):
        url=self.tabs.currentWidget().url().toString()
        self.add_new_tab(QUrl(f"https://lens.google.com/uploadbyurl?url={url}"),"SPS Lens")

    # ── Translate ─────────────────────────────
    def translate_page(self):
        url=self.tabs.currentWidget().url().toString()
        self.add_new_tab(QUrl(f"https://translate.google.com/translate?sl=auto&tl=en&u={url}"),"Translated")

    # ── Reader Mode ───────────────────────────
    def toggle_reader_mode(self):
        browser=self.tabs.currentWidget()
        if self._reading_mode:
            browser.back(); self._reading_mode=False
            self.status.showMessage("Reader mode off",2000)
        else:
            url=browser.url().toString()
            browser.setUrl(QUrl(f"https://www.readability.com/articles/create?url={url}"))
            self._reading_mode=True; self.status.showMessage("📖 Reader mode on",2000)

    # ── Dev Tools ─────────────────────────────
    def open_dev_tools(self):
        t=self._theme; dlg=QDialog(self); dlg.setWindowTitle("🔧 SPS DevTools"); dlg.resize(1050,720)
        dlg.setStyleSheet(f"background:{t['bg_primary']};")
        lay=QVBoxLayout(dlg); lay.setContentsMargins(0,0,0,0)
        dev_view=QWebEngineView()
        self.tabs.currentWidget().page().setDevToolsPage(dev_view.page())
        lay.addWidget(dev_view); dlg.show()

    # ── Settings ──────────────────────────────
    def show_settings(self):
        accent=self.settings_data.get("accent_color",self._theme["accent"])
        dlg=SettingsDialog(self.settings_data,self.profile_name,accent,self)
        if dlg.exec()==QDialog.DialogCode.Accepted:
            self.settings_data=load_settings(self.profile_name)
            self._theme=self.settings_data["theme"]
            self._apply_global_style(); self.tabs.setStyleSheet(self._tab_style())
            self.engine_btn.setText(self.settings_data.get("search_engine","SPS Search"))
            self.bookmarks_bar.setVisible(self.settings_data.get("show_bookmarks_bar",True))
            self._apply_tab_runtime_settings(self.tabs.currentWidget())
            self.status.setVisible(self.settings_data.get("show_status_bar",True))
            self.status.showMessage("✅ Settings saved.",2500)

    # ── Profiles ──────────────────────────────
    def manage_profiles(self):
        selector=ProfileSelector()
        if selector.exec():
            w=MainWindow(selector.selected_profile); w.show()

    # ── Search engine cycle ───────────────────
    def _cycle_engine(self):
        engines=list(SEARCH_ENGINES.keys())
        cur=self.settings_data.get("search_engine","SPS Search")
        nxt=engines[(engines.index(cur)+1)%len(engines)]
        self.settings_data["search_engine"]=nxt
        self.engine_btn.setText(nxt)
        save_settings_to_disk(self.profile_name,self.settings_data)
        self.status.showMessage(f"Search engine: {nxt}",1500)

    # ── AI Hub ────────────────────────────────
    def _show_ai_hub(self):
        m=QMenu(self)
        m.addAction("🧠 ChatGPT",           lambda: self.add_new_tab(QUrl("https://chat.openai.com"),"ChatGPT"))
        m.addAction("🔷 Google Gemini",     lambda: self.add_new_tab(QUrl("https://gemini.google.com"),"Gemini"))
        m.addAction("🤖 Claude (Anthropic)",lambda: self.add_new_tab(QUrl("https://claude.ai"),"Claude"))
        m.addAction("🦙 Meta AI",           lambda: self.add_new_tab(QUrl("https://meta.ai"),"Meta AI"))
        m.addAction("🌊 Perplexity",        lambda: self.add_new_tab(QUrl("https://www.perplexity.ai"),"Perplexity"))
        m.addAction("🐦 Grok (xAI)",        lambda: self.add_new_tab(QUrl("https://grok.com"),"Grok"))
        m.addAction("⭐ SPS AI Hub",        lambda: self.add_new_tab(QUrl("https://spscompany-rikdev.github.io/SPS-AI-STUDIO"),"SPS AI"))
        m.exec(QCursor.pos())

    # ── Main Menu ─────────────────────────────
    def _show_main_menu(self):
        m=QMenu(self)
        m.addAction("➕ New Tab",               lambda: self.add_new_tab())
        m.addAction("🕵️ New Incognito Tab",    lambda: self.add_new_tab(incognito=True))
        m.addAction("🔄 Reopen Closed Tab",     self._reopen_closed_tab)
        m.addSeparator()
        m.addAction("⭐ Bookmarks",             self.show_bookmarks)
        m.addAction("🕒 History",               self.show_history)
        m.addAction("📥 Downloads",             self.download_manager.show)
        m.addAction("🔐 Password Manager",      self.show_password_manager)
        m.addAction("📚 Reading List",          self.show_reading_list)
        m.addAction("📝 Notes",                 self.show_notes)
        m.addSeparator()
        m.addAction("🔍 Find in Page (Ctrl+F)",  self.find_bar.show_and_focus)
        m.addAction("📖 Toggle Reader Mode",    self.toggle_reader_mode)
        m.addAction("🌐 Translate Page",        self.translate_page)
        m.addAction("🔍 Site Information",      self.show_site_info)
        m.addAction("💻 Developer Tools (F12)", self.open_dev_tools)
        m.addAction("📄 View Source (Ctrl+U)",  self.view_source)
        m.addAction("🖨️ Print (Ctrl+P)",       self.print_page)
        m.addAction("💾 Save Page (Ctrl+S)",   self.save_page)
        m.addSeparator()
        m.addAction("📸 Screenshot",            self.take_screenshot)
        m.addAction("📄 Export PDF",            self.export_pdf)
        m.addAction("🔍 SPS Lens",              self.open_sps_lens)
        # V26 Extensions submenu
        ext_menu = m.addMenu("🧩 Extensions")
        ext_menu.addAction("📋 Manage Extensions", self.show_extensions)
        ext_menu.addAction("➕ Add Extension / Script", self._show_add_extension)
        ext_menu.addSeparator()
        ext_menu.addAction("🔄 Refresh Toolbar Buttons", self._rebuild_extension_toolbar_buttons)
        m.addAction("🍪 Cookie Manager",        self.show_cookie_manager)
        m.addAction("🛡️ Privacy Dashboard",    self.show_privacy_dashboard)
        m.addAction("📦 Focus Mode (F11)",      self._toggle_focus_mode)
        m.addSeparator()
        m.addAction("⚙️ Settings",              self.show_settings)
        m.addAction("👤 Manage Profiles",       self.manage_profiles)
        m.addAction("⌘ Command Palette",       self.show_command_palette)
        m.addAction("🗂️ Tab Organizer",        self.show_tab_organizer)
        m.addAction("🧩 Workspaces",            self.show_workspaces)
        if self.settings_data.get("feature_pack_menu_enabled", True):
            m.addAction("🧰 V27 Tools Pack",     self.show_tools_pack)
        m.addAction("📊 Browser Stats",         self.show_browser_stats)
        m.addAction("🧹 Clear Cache",           self.clear_browser_cache)
        m.addAction("💾 Save Session Snapshot", self.save_session_snapshot)
        m.addAction("↺ Restore Snapshot",       self.restore_session_snapshot)
        m.addAction("📤 Export History",        self.export_history)
        m.addAction("📥 Import Bookmarks",       self.import_bookmarks)
        m.addAction("📋 Copy All Tab URLs",     self.copy_all_tab_urls)
        m.addAction("📎 Open Clipboard URL",    self.open_clipboard_url)
        m.addAction("✕ Close Blank Tabs",       self.close_blank_tabs)
        m.addAction("↗ Open Externally",        self.open_current_page_externally)
        m.addAction("📝 Save Page as Text",      self.save_page_as_text)
        m.addAction("🍪 Clear Site Data",       self.clear_current_site_data)
        m.addAction("🖼 Toggle Images",         self.toggle_current_tab_images)
        m.addAction("🌑 Dark Filter",           self.toggle_current_tab_dark_filter)
        m.addAction("📄 Text Only Mode",        self.toggle_current_tab_text_only)
        m.addAction("⟳ Auto Refresh Tab",       self.toggle_auto_refresh)
        m.addAction("🔄 Check for Updates",     self._check_updates)
        m.addAction("ℹ️ About",                self._show_about)
        m.exec(self.menu_btn.mapToGlobal(QPoint(0,self.menu_btn.height())))

    def show_tab_organizer(self):
        t = self._theme
        accent = self.settings_data.get("accent_color", t["accent"])
        dlg = QDialog(self)
        dlg.setWindowTitle("Tab Organizer")
        dlg.resize(900, 620)
        dlg.setStyleSheet(f"background:{t['bg_primary']};color:{t['text_primary']};")

        outer = QVBoxLayout(dlg)
        outer.setContentsMargins(14, 14, 14, 14)
        outer.setSpacing(10)

        title = QLabel("Tab Organizer")
        title.setStyleSheet(f"font-size:24px;font-weight:700;color:{accent};")
        subtitle = QLabel(
            f"Open tabs: {self.tabs.count()}   |   Closed tabs: {len(self._closed_tabs)}   |   "
            f"Current profile: {self.profile_name}"
        )
        subtitle.setStyleSheet(f"color:{t['text_secondary']};font-size:12px;")
        outer.addWidget(title)
        outer.addWidget(subtitle)

        top = QHBoxLayout()
        search = QLineEdit()
        search.setPlaceholderText("Search title, URL, or state...")
        search.setStyleSheet(
            f"background:{t['bg_secondary']};color:{t['text_primary']};"
            f"border:1px solid {t['border']};border-radius:8px;padding:8px 12px;"
        )
        state_filter = QComboBox()
        state_filter.addItems(["All Tabs", "Normal Tabs", "Incognito Tabs", "Pinned Tabs", "Muted Tabs"])
        state_filter.setStyleSheet(
            f"background:{t['bg_secondary']};color:{t['text_primary']};"
            f"border:1px solid {t['border']};border-radius:8px;padding:6px;"
        )
        top.addWidget(search, 1)
        top.addWidget(state_filter)
        outer.addLayout(top)

        body = QHBoxLayout()
        tab_list = QListWidget()
        tab_list.setStyleSheet(
            f"background:{t['bg_secondary']};color:{t['text_primary']};"
            f"border:1px solid {t['border']};border-radius:8px;"
        )
        tab_list.setMinimumWidth(390)
        details = QTextEdit()
        details.setReadOnly(True)
        details.setStyleSheet(
            f"background:{t['bg_secondary']};color:{t['text_primary']};"
            f"border:1px solid {t['border']};border-radius:8px;padding:8px;"
        )
        body.addWidget(tab_list, 1)
        body.addWidget(details, 1)
        outer.addLayout(body, 1)

        def tab_meta(index):
            browser = self.tabs.widget(index)
            if not browser:
                return None
            title_text = self.tabs.tabText(index) or browser.page().title() or "Tab"
            url_text = browser.url().toString()
            is_incognito = browser.page().profile().isOffTheRecord()
            is_muted = browser.page().isAudioMuted()
            is_pinned = title_text.startswith("📌") or len(title_text) <= 2
            return {
                "index": index,
                "title": title_text,
                "url": url_text,
                "incognito": is_incognito,
                "muted": is_muted,
                "pinned": is_pinned,
                "active": index == self.tabs.currentIndex(),
            }

        def describe(meta):
            flags = []
            if meta["active"]:
                flags.append("current")
            if meta["incognito"]:
                flags.append("incognito")
            if meta["muted"]:
                flags.append("muted")
            if meta["pinned"]:
                flags.append("pinned")
            flag_text = ", ".join(flags) if flags else "normal"
            return (
                f"Title: {meta['title']}\n"
                f"URL: {meta['url']}\n"
                f"State: {flag_text}\n\n"
                f"Useful actions:\n"
                f"- Double-click to focus the tab\n"
                f"- Use the buttons below to duplicate, move, refresh, or close it\n"
                f"- Search to find a tab quickly when many are open"
            )

        def matches_filter(meta):
            mode = state_filter.currentText()
            if mode == "Normal Tabs" and meta["incognito"]:
                return False
            if mode == "Incognito Tabs" and not meta["incognito"]:
                return False
            if mode == "Pinned Tabs" and not meta["pinned"]:
                return False
            if mode == "Muted Tabs" and not meta["muted"]:
                return False
            q = search.text().strip().lower()
            if q and q not in meta["title"].lower() and q not in meta["url"].lower():
                state_blob = " ".join(
                    part for part, on in [
                        ("incognito", meta["incognito"]),
                        ("muted", meta["muted"]),
                        ("pinned", meta["pinned"]),
                        ("current", meta["active"]),
                    ] if on
                )
                if q not in state_blob:
                    return False
            return True

        def selected_index():
            item = tab_list.currentItem()
            if not item:
                return -1
            return int(item.data(Qt.ItemDataRole.UserRole))

        def refresh():
            current = selected_index()
            tab_list.blockSignals(True)
            tab_list.clear()
            for i in range(self.tabs.count()):
                meta = tab_meta(i)
                if not meta or not matches_filter(meta):
                    continue
                suffix = []
                if meta["active"]:
                    suffix.append("active")
                if meta["incognito"]:
                    suffix.append("incognito")
                if meta["muted"]:
                    suffix.append("muted")
                if meta["pinned"]:
                    suffix.append("pinned")
                label = meta["title"][:40]
                if suffix:
                    label += f"  [{', '.join(suffix)}]"
                item = QListWidgetItem(label)
                item.setData(Qt.ItemDataRole.UserRole, i)
                item.setToolTip(meta["url"])
                tab_list.addItem(item)
                if i == current:
                    tab_list.setCurrentItem(item)
            tab_list.blockSignals(False)
            subtitle.setText(
                f"Open tabs: {self.tabs.count()}   |   Closed tabs: {len(self._closed_tabs)}   |   "
                f"Current profile: {self.profile_name}"
            )
            update_details()

        def update_details():
            idx = selected_index()
            if idx < 0:
                details.setPlainText("Select a tab to see its details.")
                return
            meta = tab_meta(idx)
            if not meta:
                details.setPlainText("That tab is no longer available.")
                return
            details.setPlainText(describe(meta))

        def focus_selected():
            idx = selected_index()
            if idx >= 0:
                self.tabs.setCurrentIndex(idx)
                dlg.accept()

        def duplicate_selected():
            idx = selected_index()
            if idx >= 0:
                self.add_new_tab(self.tabs.widget(idx).url(), self.tabs.tabText(idx))
                refresh()

        def reload_selected():
            idx = selected_index()
            if idx >= 0:
                self.tabs.widget(idx).reload()
                refresh()

        def toggle_mute_selected():
            idx = selected_index()
            if idx >= 0:
                page = self.tabs.widget(idx).page()
                page.setAudioMuted(not page.isAudioMuted())
                refresh()

        def toggle_pin_selected():
            idx = selected_index()
            if idx >= 0:
                self._pin_tab(idx)
                refresh()

        def move_selected_window():
            idx = selected_index()
            if idx >= 0:
                self._move_to_window(idx)
                refresh()

        def close_selected():
            idx = selected_index()
            if idx >= 0:
                self._close_tab(idx)
                refresh()

        def close_others_selected():
            idx = selected_index()
            if idx >= 0:
                self._close_others(idx)
                refresh()

        def copy_url():
            idx = selected_index()
            if idx >= 0:
                QApplication.clipboard().setText(self.tabs.widget(idx).url().toString())
                self.status.showMessage("Tab URL copied to clipboard.", 2000)

        def open_all_in_window():
            idx = selected_index()
            if idx < 0:
                return
            url = self.tabs.widget(idx).url()
            title = self.tabs.tabText(idx)
            self.add_new_tab(url, title)
            self.tabs.setCurrentIndex(self.tabs.count() - 1)
            refresh()

        tab_list.itemSelectionChanged.connect(update_details)
        tab_list.itemDoubleClicked.connect(lambda _: focus_selected())
        search.textChanged.connect(lambda _: refresh())
        state_filter.currentIndexChanged.connect(lambda _: refresh())

        actions = QGridLayout()
        buttons = [
            ("Focus Tab", focus_selected),
            ("Duplicate", duplicate_selected),
            ("Reload", reload_selected),
            ("Mute/Unmute", toggle_mute_selected),
            ("Pin/Unpin", toggle_pin_selected),
            ("Move Window", move_selected_window),
            ("Copy URL", copy_url),
            ("Close Tab", close_selected),
            ("Close Others", close_others_selected),
        ]
        for pos, (label, fn) in enumerate(buttons):
            btn = QPushButton(label)
            btn.setStyleSheet(
                f"background:{accent};color:white;border-radius:8px;padding:8px 12px;"
            )
            btn.clicked.connect(fn)
            actions.addWidget(btn, pos // 3, pos % 3)
        outer.addLayout(actions)

        bottom = QHBoxLayout()
        bottom.addStretch()
        reopen = QPushButton("Reopen Last Closed Tab")
        reopen.setStyleSheet(
            f"background:{t['bg_secondary']};color:{t['text_primary']};"
            f"border:1px solid {t['border']};border-radius:8px;padding:8px 14px;"
        )
        reopen.clicked.connect(lambda: (self._reopen_closed_tab(), refresh()))
        bottom.addWidget(reopen)
        close = QPushButton("Close")
        close.setStyleSheet(
            f"background:{t['danger']};color:white;border-radius:8px;padding:8px 14px;"
        )
        close.clicked.connect(dlg.accept)
        bottom.addWidget(close)
        outer.addLayout(bottom)

        refresh()
        dlg.exec()

    def _confirm_bulk(self, title, message):
        if not self.settings_data.get("confirm_bulk_tab_actions", True):
            return True
        return QMessageBox.question(self, title, message) == QMessageBox.StandardButton.Yes

    def _reorder_tabs(self, order):
        current = self.tabs.currentWidget()
        items = []
        for i in order:
            widget = self.tabs.widget(i)
            items.append((widget, self.tabs.tabText(i), self.tabs.tabToolTip(i)))
        while self.tabs.count():
            self.tabs.removeTab(0)
        for widget, text, tip in items:
            idx = self.tabs.addTab(widget, text)
            self.tabs.setTabToolTip(idx, tip)
        if current:
            idx = self.tabs.indexOf(current)
            if idx >= 0:
                self.tabs.setCurrentIndex(idx)

    def bookmark_all_tabs(self):
        bms = self._load_bookmarks()
        existing = {b.get("url") for b in bms}
        folder = f"{self.settings_data.get('auto_bookmark_folder_prefix','Session')} {datetime.datetime.now().strftime('%Y-%m-%d %H-%M')}"
        added = 0
        for tab in self._capture_tabs():
            if tab["url"] not in existing:
                bms.append({"title": tab["title"], "url": tab["url"], "folder": folder, "added": str(datetime.datetime.now())})
                added += 1
        self._save_bookmarks(bms)
        self._refresh_bookmarks_bar()
        self.status.showMessage(f"Bookmarked {added} open tabs.", 2500)

    def close_duplicate_tabs(self):
        seen = set()
        active_url = self.tabs.currentWidget().url().toString() if self.tabs.currentWidget() else ""
        closed = 0
        for i in reversed(range(self.tabs.count())):
            browser = self.tabs.widget(i)
            url = browser.url().toString() if browser else ""
            if not url or url.startswith("about:"):
                continue
            key = url.rstrip("/")
            if key in seen and not (self.settings_data.get("close_duplicate_keep_active", True) and url == active_url):
                self._close_tab(i); closed += 1
            else:
                seen.add(key)
        self.status.showMessage(f"Closed {closed} duplicate tabs.", 2500)

    def close_tabs_to_left(self):
        idx = self.tabs.currentIndex()
        if idx > 0 and self._confirm_bulk("Close Tabs", f"Close {idx} tabs to the left?"):
            for i in reversed(range(idx)):
                self._close_tab(i)

    def close_tabs_to_right(self):
        idx = self.tabs.currentIndex()
        count = self.tabs.count() - idx - 1
        if count > 0 and self._confirm_bulk("Close Tabs", f"Close {count} tabs to the right?"):
            for i in reversed(range(idx + 1, self.tabs.count())):
                self._close_tab(i)

    def reload_all_tabs(self):
        for i in range(self.tabs.count()):
            b = self.tabs.widget(i)
            if b and (not self.settings_data.get("bulk_reload_skips_about_pages", True) or not b.url().toString().startswith("about:")):
                b.reload()
        self.status.showMessage("Reloaded open tabs.", 2000)

    def stop_all_tabs(self):
        for i in range(self.tabs.count()):
            b = self.tabs.widget(i)
            if b: b.stop()
        self.status.showMessage("Stopped loading tabs.", 2000)

    def pin_all_tabs(self):
        for i in range(self.tabs.count()):
            if not self.tabs.tabText(i).startswith("📌"):
                self.tabs.setTabText(i, "📌")
        self.status.showMessage("Pinned all tabs.", 2000)

    def unpin_all_tabs(self):
        for i in range(self.tabs.count()):
            b = self.tabs.widget(i)
            title = b.page().title() if b else "Tab"
            self.tabs.setTabText(i, (title or "Tab")[:28])
        self.status.showMessage("Unpinned all tabs.", 2000)

    def sort_tabs_by_title(self):
        order = sorted(range(self.tabs.count()), key=lambda i: re.sub(r"^[^\w]+", "", self.tabs.tabText(i)).lower())
        self._reorder_tabs(order)
        self.status.showMessage("Sorted tabs by title.", 2000)

    def sort_tabs_by_url(self):
        order = [i for _, i in sorted((self.tabs.widget(i).url().toString().lower(), i) for i in range(self.tabs.count()) if self.tabs.widget(i))]
        self._reorder_tabs(order)
        self.status.showMessage("Sorted tabs by URL.", 2000)

    def reverse_tab_order(self):
        self._reorder_tabs(list(reversed(range(self.tabs.count()))))
        self.status.showMessage("Reversed tab order.", 2000)

    def duplicate_all_tabs(self):
        tabs = self._capture_tabs()
        if tabs and self._confirm_bulk("Duplicate Tabs", f"Duplicate {len(tabs)} tabs?"):
            for tab in tabs:
                self.add_new_tab(QUrl(tab["url"]), tab["title"], focus=False)
            self.status.showMessage(f"Duplicated {len(tabs)} tabs.", 2500)

    def copy_tabs_as_markdown(self):
        lines = []
        for tab in self._capture_tabs():
            if self.settings_data.get("markdown_export_include_titles", True):
                lines.append(f"- [{tab['title']}]({tab['url']})")
            else:
                lines.append(f"- {tab['url']}")
        QApplication.clipboard().setText("\n".join(lines))
        self.status.showMessage("Copied tabs as Markdown.", 2500)

    def copy_session_as_json(self):
        data = {"saved": str(datetime.datetime.now()), "profile": self.profile_name, "tabs": self._capture_tabs()}
        QApplication.clipboard().setText(json.dumps(data, indent=2))
        self.status.showMessage("Copied session JSON.", 2500)

    def open_clipboard_urls(self):
        urls = re.findall(r"https?://[^\s<>'\"]+", QApplication.clipboard().text())
        limit = int(self.settings_data.get("clipboard_multi_url_open_limit", 30))
        for url in urls[:limit]:
            self.add_new_tab(QUrl(url), "Clipboard URL", focus=False)
        self.status.showMessage(f"Opened {min(len(urls), limit)} clipboard URLs.", 2500)

    def move_current_tab_first(self):
        self.tabs.tabBar().moveTab(self.tabs.currentIndex(), 0)

    def move_current_tab_last(self):
        self.tabs.tabBar().moveTab(self.tabs.currentIndex(), self.tabs.count() - 1)

    def reset_all_tab_zoom(self):
        for i in range(self.tabs.count()):
            b = self.tabs.widget(i)
            if b: b.setZoomFactor(1.0)
        self.status.showMessage("Reset zoom on all tabs.", 2000)

    def mute_all_tabs(self):
        for i in range(self.tabs.count()):
            b = self.tabs.widget(i)
            if b: b.page().setAudioMuted(True)
        self.status.showMessage("Muted all tabs.", 2000)

    def unmute_all_tabs(self):
        for i in range(self.tabs.count()):
            b = self.tabs.widget(i)
            if b: b.page().setAudioMuted(False)
        self.status.showMessage("Unmuted all tabs.", 2000)

    def open_current_url_qr(self):
        b = self.tabs.currentWidget()
        url = b.url().toString() if b else ""
        if url:
            service = self.settings_data.get("default_qr_service") or DEFAULT_SETTINGS["default_qr_service"]
            self.add_new_tab(QUrl(service + quote_plus(url)), "QR Code")

    def save_quick_note_from_page(self):
        b = self.tabs.currentWidget()
        if not b:
            return
        title = self.tabs.tabText(self.tabs.currentIndex()) or b.page().title() or "Page"
        note = f"{title}\n{b.url().toString()}\nSaved: {datetime.datetime.now()}\n"
        path = os.path.join(NOTES_DIR, f"quick_page_{int(time.time())}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(note)
        self.status.showMessage("Saved quick page note.", 2500)

    def show_tools_pack(self):
        t = self._theme
        dlg = QDialog(self); dlg.setWindowTitle("V27 Browser Tools Pack"); dlg.resize(760, 520)
        dlg.setStyleSheet(f"background:{t['bg_primary']};color:{t['text_primary']};")
        lay = QVBoxLayout(dlg)
        title = QLabel("V27 Browser Tools Pack")
        title.setStyleSheet(f"font-size:22px;font-weight:700;color:{t['accent']};")
        lay.addWidget(title)
        grid = QGridLayout(); lay.addLayout(grid, 1)
        tools = [
            ("Bookmark All Tabs", self.bookmark_all_tabs), ("Close Duplicates", self.close_duplicate_tabs),
            ("Close Left", self.close_tabs_to_left), ("Close Right", self.close_tabs_to_right),
            ("Reload All", self.reload_all_tabs), ("Stop All", self.stop_all_tabs),
            ("Pin All", self.pin_all_tabs), ("Unpin All", self.unpin_all_tabs),
            ("Sort Title", self.sort_tabs_by_title), ("Sort URL", self.sort_tabs_by_url),
            ("Reverse Tabs", self.reverse_tab_order), ("Duplicate All", self.duplicate_all_tabs),
            ("Copy Markdown", self.copy_tabs_as_markdown), ("Copy JSON", self.copy_session_as_json),
            ("Open Clipboard URLs", self.open_clipboard_urls), ("Tab First", self.move_current_tab_first),
            ("Tab Last", self.move_current_tab_last), ("Reset All Zoom", self.reset_all_tab_zoom),
            ("Mute All", self.mute_all_tabs), ("Unmute All", self.unmute_all_tabs),
            ("QR Current URL", self.open_current_url_qr), ("Quick Page Note", self.save_quick_note_from_page),
            ("Scroll Top", self.scroll_top), ("Scroll Bottom", self.scroll_bottom),
            ("Copy MD Link", self.copy_page_as_markdown_link), ("New Window", self.open_new_window),
            ("Ext Store", self.open_extension_store), ("Install Ext URL", self.install_extension_from_url_prompt),
            ("Toggle BM Bar", self.toggle_bookmarks_bar), ("Shortcuts Guide", self.show_keyboard_shortcuts),
        ]
        for i, (label, fn) in enumerate(tools):
            btn = QPushButton(label)
            btn.setStyleSheet(f"background:{t['bg_secondary']};color:{t['text_primary']};border:1px solid {t['border']};border-radius:8px;padding:10px;")
            btn.clicked.connect(fn)
            grid.addWidget(btn, i // 3, i % 3)
        close = QPushButton("Close"); close.clicked.connect(dlg.accept)
        lay.addWidget(close, alignment=Qt.AlignmentFlag.AlignRight)
        dlg.exec()

    # ══════════════════════════════════════════════════════════
    #  V27 NEW FEATURES (10+)
    # ══════════════════════════════════════════════════════════

    def focus_url_bar(self):
        """Jump focus to the URL bar and select all text."""
        self.url_bar.setFocus()
        self.url_bar.selectAll()

    def show_keyboard_shortcuts(self):
        """Show a quick-reference shortcut cheat-sheet dialog."""
        t = self._theme
        dlg = QDialog(self); dlg.setWindowTitle("⌨️ Keyboard Shortcuts"); dlg.resize(560, 480)
        dlg.setStyleSheet(f"background:{t['bg_primary']};color:{t['text_primary']};")
        lay = QVBoxLayout(dlg)
        hdr = QLabel("⌨️ Keyboard Shortcuts")
        hdr.setStyleSheet(f"font-size:20px;font-weight:700;color:{t['accent']};padding:8px 0;")
        lay.addWidget(hdr)
        shortcuts = [
            ("Ctrl+T", "New tab"), ("Ctrl+W", "Close tab"), ("Ctrl+Shift+T", "Reopen closed tab"),
            ("Ctrl+L", "Focus URL bar"), ("Ctrl+R / F5", "Reload"), ("Ctrl+Shift+R", "Hard reload"),
            ("Ctrl+B", "Toggle sidebar"), ("Ctrl+D", "Add bookmark"), ("Ctrl+H", "History"),
            ("Ctrl+J", "Downloads"), ("Ctrl++", "Zoom in"), ("Ctrl+-", "Zoom out"),
            ("Ctrl+0", "Reset zoom"), ("F12", "Dev tools"), ("Ctrl+U", "View source"),
            ("Ctrl+P", "Print"), ("Ctrl+S", "Save page"), ("Ctrl+F", "Find in page"),
            ("Alt+←", "Back"), ("Alt+→", "Forward"), ("Ctrl+Tab", "Next tab"),
            ("Ctrl+Shift+Tab", "Previous tab"), ("Ctrl+M", "Mute tab"),
            ("Ctrl+Shift+N", "New incognito"), ("Ctrl+K", "Command palette"), ("F11", "Focus mode"),
        ]
        tbl = QTableWidget(len(shortcuts), 2)
        tbl.setHorizontalHeaderLabels(["Shortcut", "Action"])
        tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tbl.setStyleSheet(f"background:{t['bg_secondary']};color:{t['text_primary']};gridline-color:{t['border']};")
        for i, (k, v) in enumerate(shortcuts):
            tbl.setItem(i, 0, QTableWidgetItem(k))
            tbl.setItem(i, 1, QTableWidgetItem(v))
        lay.addWidget(tbl, 1)
        close = QPushButton("Close"); close.clicked.connect(dlg.accept)
        lay.addWidget(close, alignment=Qt.AlignmentFlag.AlignRight)
        dlg.exec()

    def open_new_window(self):
        """Open a fresh browser window."""
        w = MainWindow(self.profile_name); w.show()

    def show_source_current(self):
        """View the HTML source of the current page in a new tab."""
        self.view_source()

    def scroll_top(self):
        """Scroll the current page to the very top."""
        b = self.tabs.currentWidget()
        if b: b.page().runJavaScript("window.scrollTo(0,0);")
        self.status.showMessage("Scrolled to top.", 1500)

    def scroll_bottom(self):
        """Scroll the current page to the bottom."""
        b = self.tabs.currentWidget()
        if b: b.page().runJavaScript("window.scrollTo(0,document.body.scrollHeight);")
        self.status.showMessage("Scrolled to bottom.", 1500)

    def copy_page_as_markdown_link(self):
        """Copy the current page as a Markdown link [Title](URL)."""
        b = self.tabs.currentWidget()
        if not b: return
        title = b.page().title() or b.url().toString()
        url = b.url().toString()
        QApplication.clipboard().setText(f"[{title}]({url})")
        self.status.showMessage("Copied as Markdown link.", 2000)

    def show_tab_count_popup(self):
        """Show a quick popup with how many tabs are open."""
        n = self.tabs.count()
        self.status.showMessage(f"📋 {n} tab{'s' if n != 1 else ''} open.", 2500)

    def open_extension_store(self):
        """Open the SPS extension website in a new tab."""
        if EXTENSION_STORE_URL:
            self.add_new_tab(QUrl(EXTENSION_STORE_URL), "Extension Store")
        else:
            QMessageBox.information(self, "Extension Store",
                "No extension store URL configured.\n\n"
                "Set EXTENSION_STORE_URL at the top of the script\n"
                "to point to your extensions website.")

    def install_extension_from_url_prompt(self):
        """Quick dialog to install an extension by entering a URL."""
        t = self._theme
        url, ok = QInputDialog.getText(self, "Install Extension from URL",
                                       "Enter the URL of a .json extension file:")
        if not ok or not url.strip(): return
        url = url.strip()
        self.status.showMessage(f"⏳ Installing extension from {url}…", 4000)
        def on_done(ext):
            self.status.showMessage(f"✅ Extension installed: {ext['name']}", 4000)
            self._rebuild_extension_toolbar_buttons()
        def on_err(msg):
            self.status.showMessage(f"❌ Extension install failed: {msg}", 5000)
            QMessageBox.warning(self, "Extension Install Failed", msg)
        self.extension_manager.install_extension_from_url(url, on_done, on_err)

    def show_page_info_panel(self):
        """Show a quick info panel about the current page — title, URL, load state, security."""
        self.show_site_info()

    def toggle_bookmarks_bar(self):
        """Toggle the bookmarks bar on/off."""
        vis = not self.bookmarks_bar.isVisible()
        self.bookmarks_bar.setVisible(vis)
        self.settings_data["show_bookmarks_bar"] = vis
        save_settings_to_disk(self.profile_name, self.settings_data)
        self.status.showMessage("Bookmarks bar " + ("shown." if vis else "hidden."), 2000)

    def clear_url_bar(self):
        """Clear the URL bar for quick typing."""
        self.url_bar.clear()
        self.url_bar.setFocus()

    def zoom_reset_current(self):
        """Reset zoom to 100% on the current tab."""
        self.reset_zoom()

    def show_about(self):
        self._show_about()

    def _show_about(self):
        t=self._theme; dlg=QDialog(self); dlg.setWindowTitle("About"); dlg.resize(440,300)
        dlg.setStyleSheet(f"background:{t['bg_primary']};color:{t['text_primary']};")
        lay=QVBoxLayout(dlg)
        title=QLabel("<b>SPS Web Browser Pro</b>")
        title.setStyleSheet(f"font-size:24px;color:{t['accent']};padding:12px;"); title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)
        info=QLabel(f"Version {VERSION}  •  Built with PyQt6 + QtWebEngine\n\n"
                    "V27 NEW: .exe/.msi downloads work immediately — no false alarms\n"
                    "Auto-install extensions from your website (click = install)\n"
                    "Toolbar buttons fully visible — no clipping on any screen\n"
                    "Scroll Top/Bottom • Copy as Markdown • New Window\n"
                    "Extension Store shortcut • Install Ext from URL prompt\n"
                    "Toggle Bookmarks Bar • Keyboard Shortcuts guide\n"
                    "10+ new tools added to Tools Pack and Command Palette\n\n"
                    "Features: Privacy Shield • Password Manager • Ad Blocker\n"
                    "Reading List • Notes • Extensions • Cookie Manager • DevTools\n"
                    "Session Restore • Multi-Profile • Custom Themes • and more.")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet(f"color:{t['text_secondary']};font-size:13px;line-height:1.6;")
        lay.addWidget(info,1)
        cp=QPushButton("📋 Copy Version")
        cp.setStyleSheet(f"background:{t['accent']};color:white;border-radius:8px;padding:8px 16px;")
        cp.clicked.connect(lambda: QApplication.clipboard().setText(f"SPS Browser Pro v{VERSION}"))
        lay.addWidget(cp,alignment=Qt.AlignmentFlag.AlignCenter)
        dlg.exec()

    # ── Auto-Updater ──────────────────────────
    def _startup_update_check(self):
        hist = load_update_history()
        last = hist.get("last_check_time", "")
        try:
            last_dt = datetime.datetime.fromisoformat(last)
            hours = max(1, int(self.settings_data.get("update_check_interval_hours", 12)))
            if (datetime.datetime.now() - last_dt).total_seconds() < hours * 3600:
                return
        except Exception:
            pass
        self._check_updates()

    def _check_updates(self):
        self.status.showMessage("🔄 Checking for updates…",3000)
        update_url = self.settings_data.get("update_check_url") or UPDATE_CHECK_URL
        hist = load_update_history()
        hist["last_check_time"] = datetime.datetime.now().isoformat()
        hist["last_check_url"] = update_url
        save_update_history(hist)
        self._update_worker=UpdateWorker(VERSION, update_url, self.settings_data, self)
        self._update_worker.update_available.connect(self._on_update_available)
        self._update_worker.no_update.connect(lambda: self.status.showMessage(f"✅ You have the latest version ({VERSION})",4000))
        self._update_worker.error.connect(lambda e: self.status.showMessage(f"⚠️ Update check failed: {e}",4000))
        self._update_worker.start()

    def _on_update_available(self,version,url,sha256=""):
        dlg=UpdateDialog(version,url,sha256,self._theme,self)
        if self.settings_data.get("auto_download_updates", False):
            QTimer.singleShot(300, dlg._start_download)
        dlg.exec()

    # ── Session ───────────────────────────────
    def _auto_save_session(self):
        tabs_info=[]
        for i in range(self.tabs.count()):
            b=self.tabs.widget(i)
            if b: tabs_info.append({"url":b.url().toString(),"title":self.tabs.tabText(i)})
        self.session_manager.save(tabs_info)

    def _restore_session(self):
        tabs=self.session_manager.load()
        if not tabs: return
        for tab in tabs:
            url=tab.get("url",""); title=tab.get("title","Tab")
            if url and not url.startswith("about:"):
                self.add_new_tab(QUrl(url),title)

    # ── Tab memory management ─────────────────
    def _check_tab_memory(self):
        limit=self.settings_data.get("tab_memory_limit",50)*60
        now=time.time()
        current=self.tabs.currentWidget()
        for i in range(self.tabs.count()):
            b=self.tabs.widget(i)
            if b and b!=current:
                idle=now-getattr(b,"_last_active",now)
                if idle>limit:
                    # Discard unused tab content to save memory
                    b.page().setLifecycleState(QWebEnginePage.LifecycleState.Discarded)

    # ── Status helpers ────────────────────────
    def _update_blocked_count(self):
        count=self.interceptor.total_blocked
        self._blocked_lbl.setText(f"🛡️ {count} blocked")
        self.shield_badge.setText(f"🛡️ {count} blocked")
        QTimer.singleShot(8000,self._update_blocked_count)

    def closeEvent(self,event):
        self._auto_save_session()
        if self.settings_data.get("confirm_before_close"):
            result=QMessageBox.question(self,"Exit SPS Browser Pro","Close the browser?")
            if result!=QMessageBox.StandardButton.Yes:
                event.ignore(); return
        if self.settings_data.get("save_last_workspace"):
            self.save_workspace("Last Session", silent=True)
        if self.settings_data.get("clear_on_exit"):
            self.browser_profile.clearAllVisitedLinks()
            self.browser_profile.cookieStore().deleteAllCookies()
        event.accept()

# ═══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════
if __name__=="__main__":
    app=QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)
    app.setFont(QFont("Segoe UI",10))

    profile=None
    if "--profile" in sys.argv:
        idx=sys.argv.index("--profile")
        if idx+1<len(sys.argv): profile=sys.argv[idx+1]

    if profile is None:
        selector=ProfileSelector()
        if selector.exec(): profile=selector.selected_profile
        else: sys.exit(0)

    window=MainWindow(profile)
    window.show()
    sys.exit(app.exec())
