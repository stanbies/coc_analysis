# Clash of Clans Clan Analyzer & Dashboard

A comprehensive tool for analyzing Clash of Clans clan data, tracking player statistics, monitoring war performance, and displaying everything in a beautiful Next.js dashboard.

## Architecture

This project uses a **manual scraping approach** to work around the CoC API's static IP requirement:

1. **Python Scraper** (`api/clan_analyzer.py`) - Run manually from your local machine to fetch all data
2. **JSON Data File** (`coc-dashboard/public/clan_data.json`) - Intermediate storage for scraped data
3. **Next.js Dashboard** (`coc-dashboard/`) - Beautiful web UI that reads from the JSON file

This architecture allows you to:
- Run the scraper from any machine with your API key
- Host the dashboard anywhere (Vercel, Netlify, etc.) without needing API access
- Update data on-demand without a server

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
```

Get your API token from [Clash of Clans Developer Portal](https://developer.clashofclans.com/)

> ⚠️ **Important**: API tokens are IP-locked. Create a token for your current IP address.

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

Simply re-run the Python scraper whenever you want fresh data:

```bash
python api/clan_analyzer.py
```

The dashboard will automatically show the new data on refresh.

## Project Structure

```
COC_analysis/
├── .env                    # API key (gitignored)
├── api/
│   ├── clan_analyzer.py    # Main scraper script
│   ├── clan_history.json   # Historical data storage
│   ├── requirements.txt    # Python dependencies
│   └── streamlit_app.py    # Legacy Streamlit dashboard
├── coc-dashboard/
│   ├── app/
│   │   ├── components/     # React components
│   │   ├── types.ts        # TypeScript interfaces
│   │   ├── page.tsx        # Main dashboard page
│   │   └── globals.css     # Styling
│   ├── public/
│   │   └── clan_data.json  # Scraped data (generated)
│   └── package.json
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
