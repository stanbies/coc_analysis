"""Configuration: environment, clan tag and file locations."""

import os
from pathlib import Path

from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)

# Load environment variables from .env in the repo root. Real environment
# variables (e.g. GitHub Actions secrets) take precedence.
load_dotenv(Path(REPO_ROOT) / '.env')

API_TOKEN = os.getenv('api_key', '')
BASE_URL = os.getenv('coc_base_url', "https://api.clashofclans.com/v1")
CLAN_TAG = "#2J28LL2VU"

# Committed data files, read by every run
PUBLISHED_HISTORY_FILE = os.path.join(SCRIPT_DIR, "clan_history.json")
PUBLISHED_RANKED_FILE = os.path.join(SCRIPT_DIR, "ranked_snapshots.json")
PUBLISHED_DASHBOARD_FILE = os.path.join(REPO_ROOT, "coc-dashboard", "public", "clan_data.json")

# Only the daily workflow publishes (publish_data=true). Local runs write to
# api/out/ (gitignored) so they never collide with the bot's data commits.
PUBLISH = os.getenv('publish_data', '').lower() in ('1', 'true', 'yes')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "out")

DATA_FILE = PUBLISHED_HISTORY_FILE if PUBLISH else os.path.join(OUTPUT_DIR, "clan_history.json")
DASHBOARD_DATA_FILE = PUBLISHED_DASHBOARD_FILE if PUBLISH else os.path.join(OUTPUT_DIR, "clan_data.json")
RANKED_FILE = PUBLISHED_RANKED_FILE if PUBLISH else os.path.join(OUTPUT_DIR, "ranked_snapshots.json")

# Weekly mail subscribers (email,#TAG per line). The workflow gets them from
# the mail_subscribers secret; locally they're read from this gitignored file.
SUBSCRIBERS_FILE = os.path.join(SCRIPT_DIR, "subscribers.csv")

# Weekly mail: our own editable tables, the sender (also where unsubscribe
# requests go) and where --dry-run writes its previews
MAIL_CONFIG_DIR = os.path.join(SCRIPT_DIR, "mail_config")
BENCHMARKS_FILE = os.path.join(MAIL_CONFIG_DIR, "benchmarks.yaml")
STRATEGIES_FILE = os.path.join(MAIL_CONFIG_DIR, "strategies.yaml")
MAIL_ADDRESS = "cocanalysis686@gmail.com"
MAIL_SENDER_NAME = "Zwegerneet Ranked"
# Gmail SMTP login: a Google app password, not the account password
SMTP_USER = os.getenv('smtp_user', MAIL_ADDRESS)
SMTP_PASSWORD = os.getenv('smtp_password', '').replace(' ', '')
MAIL_PREVIEW_DIR = os.path.join(OUTPUT_DIR, "mails")
