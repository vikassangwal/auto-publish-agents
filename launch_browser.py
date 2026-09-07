"""
Dedicated Persistent Browser Launcher.
Launches a dedicated Chrome profile that PERMANENTLY preserves your login sessions
across Gumroad, Etsy, Lemon Squeezy, Shopify, WooCommerce, and Whop.
Once you log in here, you NEVER get logged out!
"""
import os
import sys
import subprocess
from pathlib import Path

def find_chrome_path():
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None

def launch_persistent_browser():
    project_root = Path(__file__).resolve().parent
    profile_dir = project_root / "storage" / "browser_profile"
    profile_dir.mkdir(parents=True, exist_ok=True)

    chrome_exe = find_chrome_path()
    if not chrome_exe:
        print("[ERROR] Neither Google Chrome nor Microsoft Edge was found on your system.")
        return

    print("=" * 80)
    print(" DEDICATED PERSISTENT AGENT BROWSER")
    print("=" * 80)
    print(f" -> Profile Directory: {profile_dir}")
    print(f" -> Browser Executable: {chrome_exe}")
    print(" -> All logins here are saved PERMANENTLY and synced across your devices!")
    print("=" * 80)

    # Initial URLs to log in once
    startup_urls = [
        "https://app.gumroad.com/login",
        "https://www.etsy.com/signin",
        "https://app.lemonsqueezy.com/login",
        "https://dash.whop.com/login"
    ]

    args = [
        chrome_exe,
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--password-store=basic"
    ] + startup_urls

    print("\nLaunching dedicated browser window... (Log in to your accounts here once)")
    try:
        subprocess.Popen(args)
        print("\n[SUCCESS] Browser is running! You can keep this window open or close it anytime.")
        print("Your sessions will remain saved indefinitely.")
    except Exception as e:
        print(f"[ERROR] Failed to start browser: {e}")

if __name__ == "__main__":
    launch_persistent_browser()
