#!/usr/bin/env python3
"""
CoC API Key Manager - Dynamic IP Token Management

This script automatically manages your Clash of Clans API key when your
public IP address changes (common with non-static IPs).

Flow:
  1. Detect your current public IP address
  2. Log into the CoC Developer portal
  3. Check if an existing key matches the current IP
  4. If not, revoke the old key and create a new one with the new IP
  5. Update the .env file so all other scripts use the fresh key

Usage:
  python manage_api_key.py              # Run once
  python manage_api_key.py --install    # Install daily launchd schedule (macOS)
  python manage_api_key.py --uninstall  # Remove the daily schedule

Requires COC_DEV_EMAIL and COC_DEV_PASSWORD in your .env file.
"""

import requests
import json
import base64
import os
import sys
import subprocess
import argparse
import getpass
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv, set_key

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
ENV_FILE = SCRIPT_DIR / ".env"
LOG_FILE = SCRIPT_DIR / "api_key_manager.log"

# The name we give our auto-managed keys (so we can identify them)
KEY_NAME = "coc_analysis_auto"
KEY_DESCRIPTION_PREFIX = "Auto-managed key"
MAX_KEYS_PER_ACCOUNT = 10

COC_DEV_BASE = "https://developer.clashofclans.com/api"
COC_API_BASE = "https://api.clashofclans.com/v1"

# Services to detect public IP (try multiple for reliability)
IP_SERVICES = [
    "https://api.ipify.org?format=json",
    "https://ipinfo.io/json",
    "https://httpbin.org/ip",
]


def log(message: str):
    """Log a message to both console and log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


# ---------------------------------------------------------------------------
# Step 1: Detect current public IP
# ---------------------------------------------------------------------------

def get_public_ip() -> str:
    """Get the current public IP address using multiple fallback services."""
    for url in IP_SERVICES:
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            # Different services use different keys
            ip = data.get("ip") or data.get("origin") or data.get("query")
            if ip:
                # httpbin.org may return "x.x.x.x, y.y.y.y" — take first
                ip = ip.split(",")[0].strip()
                log(f"✅ Current public IP: {ip}")
                return ip
        except Exception as e:
            log(f"⚠️  Failed to get IP from {url}: {e}")
            continue

    raise RuntimeError("Could not determine public IP from any service")


# ---------------------------------------------------------------------------
# Step 2 & 3: CoC Developer Portal session
# ---------------------------------------------------------------------------

class CocDeveloperPortal:
    """Manages interaction with the CoC Developer website API."""

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.session = requests.Session()

    def login(self):
        """Log into the developer portal and establish a session."""
        log("🔑 Logging into CoC Developer portal...")
        resp = self.session.post(
            f"{COC_DEV_BASE}/login",
            json={"email": self.email, "password": self.password},
        )
        if resp.status_code == 403:
            raise RuntimeError(
                "❌ Login failed — invalid email/password. "
                "Check COC_DEV_EMAIL and COC_DEV_PASSWORD in your .env file."
            )
        resp.raise_for_status()
        log("✅ Successfully logged into the developer portal.")
        return resp.json()

    def list_keys(self) -> list:
        """List all API keys on the account."""
        resp = self.session.post(f"{COC_DEV_BASE}/apikey/list")
        resp.raise_for_status()
        keys = resp.json().get("keys", [])
        log(f"📋 Found {len(keys)} API key(s) on your account.")
        return keys

    def create_key(self, ip: str) -> dict:
        """Create a new API key whitelisted for the given IP."""
        data = {
            "name": KEY_NAME,
            "description": f"{KEY_DESCRIPTION_PREFIX} — created {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} for IP {ip}",
            "cidrRanges": [ip],
            "scopes": ["clash"],
        }
        log(f"🆕 Creating new API key for IP {ip}...")
        resp = self.session.post(f"{COC_DEV_BASE}/apikey/create", json=data)
        if resp.status_code != 200:
            error = resp.json()
            raise RuntimeError(f"❌ Failed to create key: {error.get('description', resp.text)}")
        key_data = resp.json()
        log("✅ New API key created successfully.")
        return key_data["key"]

    def revoke_key(self, key_id: str):
        """Revoke (delete) an API key by its ID."""
        log(f"🗑️  Revoking key ID {key_id}...")
        resp = self.session.post(
            f"{COC_DEV_BASE}/apikey/revoke",
            json={"id": key_id},
        )
        if resp.status_code == 200:
            log(f"✅ Key {key_id} revoked.")
        else:
            log(f"⚠️  Failed to revoke key {key_id}: {resp.text}")


# ---------------------------------------------------------------------------
# Step 4: Test the API key
# ---------------------------------------------------------------------------

def test_api_key(api_key: str) -> bool:
    """Quick test to check if the API key is working."""
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    # Use a simple endpoint — get our clan info
    try:
        resp = requests.get(
            f"{COC_API_BASE}/clans/%232J28LL2VU",
            headers=headers,
            timeout=15,
        )
        if resp.status_code == 200:
            clan = resp.json()
            log(f"✅ API key works! Clan: {clan.get('name', 'Unknown')} ({clan.get('tag', '')})")
            return True
        elif resp.status_code == 403:
            reason = resp.json().get("reason", "")
            log(f"❌ API key rejected (403): {reason}")
            return False
        else:
            log(f"⚠️  Unexpected status {resp.status_code} when testing key")
            return False
    except Exception as e:
        log(f"⚠️  Error testing API key: {e}")
        return False


# ---------------------------------------------------------------------------
# Step 5: Update the .env file
# ---------------------------------------------------------------------------

def update_env_file(api_key: str):
    """Update the .env file with the new API key."""
    if not ENV_FILE.exists():
        log(f"📝 Creating .env file at {ENV_FILE}")
        ENV_FILE.touch()

    set_key(str(ENV_FILE), "api_key", api_key)
    log(f"✅ Updated .env file with new API key.")


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def ensure_credentials() -> tuple:
    """Load or prompt for CoC Developer credentials."""
    load_dotenv(ENV_FILE)

    email = os.getenv("COC_DEV_EMAIL", "").strip()
    password = os.getenv("COC_DEV_PASSWORD", "").strip()

    if not email or not password:
        log("⚠️  CoC Developer credentials not found in .env file.")
        log("   You need your developer.clashofclans.com login credentials.")
        print()
        email = input("Enter your CoC Developer email: ").strip()
        password = getpass.getpass("Enter your CoC Developer password: ").strip()

        if not email or not password:
            raise RuntimeError("Email and password are required.")

        # Save for next time
        if not ENV_FILE.exists():
            ENV_FILE.touch()
        set_key(str(ENV_FILE), "COC_DEV_EMAIL", email)
        set_key(str(ENV_FILE), "COC_DEV_PASSWORD", password)
        log("✅ Credentials saved to .env file.")

    return email, password


def manage_key():
    """Main key management flow."""
    log("=" * 60)
    log("🏰 CoC API Key Manager — Starting")
    log("=" * 60)

    # 1. Get current IP
    current_ip = get_public_ip()

    # 2. Load credentials and login
    email, password = ensure_credentials()
    portal = CocDeveloperPortal(email, password)
    portal.login()

    # 3. List existing keys and check if any match current IP
    keys = portal.list_keys()

    matching_key = None
    our_old_keys = []  # Keys with our name but wrong IP

    for key in keys:
        is_ours = key["name"] == KEY_NAME
        ip_matches = current_ip in key.get("cidrRanges", [])

        if is_ours and ip_matches:
            matching_key = key
            log(f"✅ Found existing key matching current IP ({current_ip}).")
        elif is_ours and not ip_matches:
            our_old_keys.append(key)
            log(f"🔄 Found our key with old IP: {key.get('cidrRanges', [])}")

    # 4. If we already have a valid key, just test it
    if matching_key:
        api_key = matching_key["key"]
        if test_api_key(api_key):
            update_env_file(api_key)
            log("🎉 Existing key is still valid — no changes needed!")
            return True
        else:
            log("⚠️  Key matched IP but failed test, will recreate...")
            our_old_keys.append(matching_key)
            matching_key = None

    # 5. Revoke old keys with our name to make room
    for old_key in our_old_keys:
        portal.revoke_key(old_key["id"])

    # 6. Check if we have room (max 10 keys per account)
    remaining_keys = [k for k in keys if k not in our_old_keys and k.get("id") != (matching_key or {}).get("id")]
    if len(remaining_keys) >= MAX_KEYS_PER_ACCOUNT:
        log(f"⚠️  Account has {len(remaining_keys)} keys (max {MAX_KEYS_PER_ACCOUNT}).")
        log("   You may need to delete some keys manually at developer.clashofclans.com")
        # Try to delete the oldest non-matching key
        oldest = remaining_keys[-1]
        log(f"   Attempting to revoke oldest key: {oldest['name']} (ID: {oldest['id']})")
        portal.revoke_key(oldest["id"])

    # 7. Create new key
    new_key_data = portal.create_key(current_ip)
    api_key = new_key_data["key"]

    # 8. Test the new key
    if test_api_key(api_key):
        update_env_file(api_key)
        log("🎉 New API key created and verified successfully!")
        return True
    else:
        log("❌ New key was created but failed validation test.")
        log("   The IP might have changed during the process. Try again.")
        # Still save it — it's the best we have
        update_env_file(api_key)
        return False


# ---------------------------------------------------------------------------
# Scheduling (macOS launchd)
# ---------------------------------------------------------------------------

PLIST_LABEL = "com.cocanalysis.apikeymanager"
PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / f"{PLIST_LABEL}.plist"


def get_plist_content() -> str:
    """Generate the launchd plist for daily execution."""
    script_path = Path(__file__).resolve()
    python_path = sys.executable
    log_stdout = SCRIPT_DIR / "api_key_manager_launchd.log"
    log_stderr = SCRIPT_DIR / "api_key_manager_launchd_err.log"

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{PLIST_LABEL}</string>

    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{script_path}</string>
    </array>

    <key>WorkingDirectory</key>
    <string>{SCRIPT_DIR}</string>

    <!-- Run daily at 06:00 -->
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>6</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>

    <!-- Also run when the machine boots / user logs in (catches missed runs) -->
    <key>RunAtLoad</key>
    <true/>

    <key>StandardOutPath</key>
    <string>{log_stdout}</string>
    <key>StandardErrorPath</key>
    <string>{log_stderr}</string>

    <!-- Retry on failure after 30 minutes -->
    <key>StartInterval</key>
    <integer>1800</integer>
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
</dict>
</plist>
"""


def install_schedule():
    """Install the launchd job for daily execution."""
    log("📅 Installing daily schedule via launchd...")

    # Ensure the LaunchAgents directory exists
    PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Write the plist
    PLIST_PATH.write_text(get_plist_content())
    log(f"   Plist written to: {PLIST_PATH}")

    # Unload first if it already exists (ignore errors)
    subprocess.run(
        ["launchctl", "unload", str(PLIST_PATH)],
        capture_output=True,
    )

    # Load the new job
    result = subprocess.run(
        ["launchctl", "load", str(PLIST_PATH)],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        log("✅ Daily schedule installed!")
        log("   → Runs every day at 06:00")
        log("   → Also runs on login/boot")
        log(f"   → Logs: {SCRIPT_DIR}/api_key_manager_launchd.log")
    else:
        log(f"❌ Failed to load schedule: {result.stderr}")


def uninstall_schedule():
    """Remove the launchd job."""
    log("🗑️  Removing daily schedule...")

    if PLIST_PATH.exists():
        subprocess.run(
            ["launchctl", "unload", str(PLIST_PATH)],
            capture_output=True,
        )
        PLIST_PATH.unlink()
        log("✅ Schedule removed.")
    else:
        log("ℹ️  No schedule was installed.")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Manage CoC API keys automatically when your IP changes."
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install a daily launchd schedule (macOS) to run this script automatically.",
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Remove the daily launchd schedule.",
    )
    parser.add_argument(
        "--test-only",
        action="store_true",
        help="Only test if the current API key works (don't create/revoke).",
    )
    args = parser.parse_args()

    if args.install:
        install_schedule()
        # Also do an immediate key check
        log("\n🔄 Running an immediate key check...")
        manage_key()
        return

    if args.uninstall:
        uninstall_schedule()
        return

    if args.test_only:
        load_dotenv(ENV_FILE)
        api_key = os.getenv("api_key", "")
        if not api_key:
            log("❌ No API key found in .env file.")
            sys.exit(1)
        ip = get_public_ip()
        success = test_api_key(api_key)
        sys.exit(0 if success else 1)

    # Default: run the full key management
    try:
        success = manage_key()
        sys.exit(0 if success else 1)
    except Exception as e:
        log(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
