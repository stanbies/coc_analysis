# Clash of Clans Clan Analyzer & Dashboard

A comprehensive tool for analyzing Clash of Clans clan data, tracking player statistics, monitoring war performance, and displaying everything in a beautiful Next.js dashboard.

## Architecture

1. **Python Scraper** (`api/`, entry point `clan_analyzer.py`) - Fetches all data from the CoC API
2. **JSON Data File** (`coc-dashboard/public/clan_data.json`) - Intermediate storage for scraped data
3. **Next.js Dashboard** (`coc-dashboard/`) - Web UI that reads from the JSON file, hosted on Vercel

A GitHub Action (`.github/workflows/update-data.yml`) runs the scraper every 6 hours and commits the updated JSON to `main` (only when more than the timestamps changed). Vercel redeploys on that push. Because CoC API keys are IP-locked and Action runners have changing IPs, the scraper goes through the [RoyaleAPI proxy](https://docs.royaleapi.com/proxy.html), which has a fixed IP.

## Features

### Python Scraper
- **Comprehensive API Coverage**: Fetches data from all relevant CoC API endpoints
- **Clan Analysis**: Detailed clan information, war statistics, capital data
- **Player Analysis**: All members with troops, spells, heroes, equipment
- **Rush Detection**: Advanced algorithm to identify rushed players
- **War Performance**: War log, current wars, CWL tracking
- **Capital Raids**: Raid weekend statistics and top raiders
- **Historical Tracking**: Persistent storage for trend analysis

### Next.js Dashboard
- **Modern Dark UI**: Beautiful gradient design with glassmorphism effects
- **Overview Tab**: Key stats, TH distribution, rush analysis charts
- **Players Tab**: Sortable/filterable table with all members
- **Wars Tab**: War log with results, stars, destruction
- **Capital Tab**: Raid statistics and top contributors
- **Player Details Modal**: Click any player for detailed breakdown
- **Rush Analysis**: Visual indicators for rushed players
- **Rush Score Explained** (`/rush-score`): How the score is calculated, with a worked example from your own clan

## Setup

### 1. Python Environment

```bash
pip install -r api/requirements-dev.txt   # scraper deps + pytest
```

### 2. Configure API Key

Create a `.env` file in the root directory:

```env
api_key=YOUR_COC_API_TOKEN_HERE
coc_base_url=https://cocproxy.royaleapi.dev/v1
```

Get your API token from [Clash of Clans Developer Portal](https://developer.clashofclans.com/)

> ⚠️ **Important**: API tokens are IP-locked. For the proxy, create the token with `45.79.218.79` as the allowed IP. To call the API directly instead, allow your own IP and leave out `coc_base_url`.

For the scheduled update, add the same two values as GitHub Actions secrets (`api_key`, `coc_base_url`) under Settings → Secrets and variables → Actions.

### 3. Update Clan Tag

Edit `api/config.py` and update the `CLAN_TAG` variable:

```python
CLAN_TAG = "#YOUR_CLAN_TAG"
```

### 4. Install Dashboard Dependencies

```bash
cd coc-dashboard
npm install
```

## Usage

### Step 1: Scrape Data

Run the Python scraper to fetch all clan data:

```bash
python api/clan_analyzer.py
```

This will:
- Fetch all clan and player data from the CoC API
- Analyze rush status for all members
- Track war performance and CWL
- Fetch capital raid data
- Export everything to `api/out/clan_data.json`

Local runs write to the gitignored `api/out/` so they never collide with the workflow's data commits. Only the workflow (with `publish_data=true`) writes the published files: `coc-dashboard/public/clan_data.json`, `api/clan_history.json` and the mobile copy. Run the tests with `python -m pytest api/`.

### Step 2: View Dashboard

Start the Next.js development server. It shows the published data in `coc-dashboard/public/clan_data.json`; `git pull` for the latest:

```bash
cd coc-dashboard
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Updating Data

The hosted site updates itself every 6 hours through the GitHub Action. To refresh sooner, open the repo's Actions tab, choose "Update clan data" and click **Run workflow**. Each run first runs the tests and afterwards warns (in the run summary) if the max-level tables look out of date.

## Project Structure

```
COC_analysis/
├── .env                    # API key + base URL (gitignored)
├── .github/workflows/
│   └── update-data.yml     # Scheduled scrape + commit
├── api/
│   ├── clan_analyzer.py    # Entry point + console analysis
│   ├── config.py           # Env, clan tag, output paths
│   ├── coc_api.py          # API client with retries
│   ├── rush.py             # Max-level tables + rush score
│   ├── history.py          # War history (clan_history.json)
│   ├── export.py           # Builds clan_data.json
│   ├── check_caps.py       # Warns when max-level tables are outdated
│   ├── test_*.py           # pytest tests
│   ├── clan_history.json   # Historical data storage
│   └── requirements*.txt   # Pinned Python dependencies
├── coc-dashboard/
│   ├── app/
│   │   ├── components/     # React components
│   │   ├── types.ts        # TypeScript interfaces
│   │   ├── page.tsx        # Server component, reads the data at build time
│   │   └── globals.css     # Styling
│   ├── public/
│   │   └── clan_data.json  # Scraped data (generated)
│   └── package.json
├── mobile-coc-dashboard/   # Expo mobile app
├── legacy/                 # Old Streamlit app + HTML report (unmaintained)
└── README.md
```

## API Endpoints Used

The scraper fetches data from these CoC API endpoints:

| Endpoint | Description |
|----------|-------------|
| `/clans/{clanTag}` | Clan information |
| `/clans/{clanTag}/members` | Clan members list |
| `/clans/{clanTag}/warlog` | War history |
| `/clans/{clanTag}/currentwar` | Current war status |
| `/clans/{clanTag}/currentwar/leaguegroup` | CWL group info |
| `/clans/{clanTag}/capitalraidseasons` | Capital raid data |
| `/players/{playerTag}` | Detailed player info |
| `/goldpass/seasons/current` | Gold pass info |

## Rush Detection Algorithm

The rush detection system compares each player's heroes, troops and spells against the **maximum levels available at the previous Town Hall** (a TH17 player is measured against TH16 caps). Every missing level adds to the rush score:

- **Heroes**: 1.0 per missing level
- **Troops**: 0.3 per missing level
- **Spells**: 0.4 per missing level

Levels above the benchmark earn no extra credit. Pets, siege machines and super troops are not counted. The Minion Prince isn't counted either, because the clan doesn't use it (`RUSH_EXCLUDED_HEROES` in `api/rush.py`); it's still shown on the dashboard.

### Status Classifications:
- ✅ **Maxed** (score ≤ 3)
- 🟢 **Slightly Behind** (≤ 10)
- 🟡 **Moderately Rushed** (≤ 25)
- 🟠 **Rushed** (≤ 50)
- 🔴 **Severely Rushed** (> 50)
- 🔴 **Severely Rushed (Heroes)**: more than 20 missing hero levels, regardless of total score

**Rush %** is shown separately: the share of benchmark levels the player hasn't reached yet, unweighted.

The max-level tables (`HERO_MAX_LEVELS`, `TROOP_MAX_LEVELS`, `SPELL_MAX_LEVELS` in `api/rush.py`) need updating whenever a game update raises level caps. The workflow's cap check flags this.

## Data Persistence

The analyzer stores historical war attack data in `clan_history.json`, allowing you to track performance trends over time.

## API Rate Limits

The Clash of Clans API has rate limits. The script includes delays between requests to avoid hitting these limits.

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](LICENSE)

## Disclaimer

This project is not affiliated with, endorsed, sponsored, or specifically approved by Supercell and Supercell is not responsible for it. For more information see Supercell's Fan Content Policy.
