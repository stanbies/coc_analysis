# Clash of Clans Clan Analyzer & Dashboard

A comprehensive tool for analyzing Clash of Clans clan data, tracking player statistics, monitoring war performance, and displaying everything in a beautiful Next.js dashboard.

## Architecture

1. **Python Scraper** (`api/clan_analyzer.py`) - Fetches all data from the CoC API
2. **JSON Data File** (`coc-dashboard/public/clan_data.json`) - Intermediate storage for scraped data
3. **Next.js Dashboard** (`coc-dashboard/`) - Web UI that reads from the JSON file, hosted on Vercel

A GitHub Action (`.github/workflows/update-data.yml`) runs the scraper every day at 05:00 UTC and commits the updated JSON to `main`. Vercel redeploys on that push. Because CoC API keys are IP-locked and Action runners have changing IPs, the scraper goes through the [RoyaleAPI proxy](https://docs.royaleapi.com/proxy.html), which has a fixed IP.

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

## Setup

### 1. Python Environment

```bash
cd api
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file in the root directory:

```env
api_key=YOUR_COC_API_TOKEN_HERE
coc_base_url=https://cocproxy.royaleapi.dev/v1
```

Get your API token from [Clash of Clans Developer Portal](https://developer.clashofclans.com/)

> ⚠️ **Important**: API tokens are IP-locked. For the proxy, create the token with `45.79.218.79` as the allowed IP. To call the API directly instead, allow your own IP and leave out `coc_base_url`.

For the daily update, add the same two values as GitHub Actions secrets (`api_key`, `coc_base_url`) under Settings → Secrets and variables → Actions.

### 3. Update Clan Tag

Edit `api/clan_analyzer.py` and update the `CLAN_TAG` variable:

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
cd api
python clan_analyzer.py
```

This will:
- Fetch all clan and player data from the CoC API
- Analyze rush status for all members
- Track war performance and CWL
- Fetch capital raid data
- Export everything to `coc-dashboard/public/clan_data.json`

### Step 2: View Dashboard

Start the Next.js development server:

```bash
cd coc-dashboard
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Updating Data

The hosted site updates itself daily through the GitHub Action. To refresh sooner, open the repo's Actions tab, choose "Update clan data" and click **Run workflow**. Locally, re-run `python api/clan_analyzer.py` and refresh the page.

## Project Structure

```
COC_analysis/
├── .env                    # API key + base URL (gitignored)
├── .github/workflows/
│   └── update-data.yml     # Daily scrape + commit
├── api/
│   ├── clan_analyzer.py    # Main scraper script
│   ├── clan_history.json   # Historical data storage
│   └── requirements.txt    # Python dependencies
├── coc-dashboard/
│   ├── app/
│   │   ├── components/     # React components
│   │   ├── types.ts        # TypeScript interfaces
│   │   ├── page.tsx        # Main dashboard page
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

The rush detection system compares each player's current levels against the **maximum levels available at the previous Town Hall**:

- **Heroes**: 50% weight (most important)
- **Troops**: 35% weight
- **Spells**: 15% weight

### Status Classifications:
- ✅ **Maxed** (score < 3): Fully caught up
- 🟢 **Slightly Behind** (3-10): Minor gaps
- 🟡 **Moderately Rushed** (10-25): Noticeable deficits
- 🟠 **Rushed** (25-50): Significant gaps
- 🔴 **Severely Rushed** (25+ with 15+ hero levels missing)

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
