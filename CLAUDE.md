# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Clash of Clans clan analyzer and dashboard. Three-part architecture:
1. **Python scraper** (`api/clan_analyzer.py`) — fetches data from the CoC API and exports to JSON
2. **Next.js web dashboard** (`coc-dashboard/`) — reads `public/clan_data.json` and renders a tabbed UI
3. **Expo/React Native mobile app** (`mobile-coc-dashboard/`) — reads `assets/data/clan_data.json` with the same data

Data flows one-way: scraper → JSON file → dashboards (no live API calls from frontends).

## Common Commands

### Python scraper
```bash
# Activate venv (from repo root)
source venv/Scripts/activate   # Windows Git Bash
# or: venv\Scripts\activate    # Windows CMD

# Install dependencies
pip install -r api/requirements.txt

# Run scraper (outputs to coc-dashboard/public/clan_data.json)
python api/clan_analyzer.py
```

### Web dashboard (Next.js)
```bash
cd coc-dashboard
npm install
npm run dev       # dev server on localhost:3000
npm run build     # production build
npm run lint      # ESLint
```

### Mobile app (Expo)
```bash
cd mobile-coc-dashboard
npm install
npx expo start          # start dev server
npx expo start --web    # web preview
npx expo lint           # ESLint
```

## Architecture Details

### Data Pipeline
- `api/clan_analyzer.py` is a single ~97KB script containing all scraping logic, rush detection algorithm, and data export. It reads `.env` from the repo root for `api_key`.
- The scraper writes `clan_history.json` (historical war data) alongside itself in `api/`.
- Both dashboards share the same `DashboardData` TypeScript interface shape (defined separately in `coc-dashboard/app/types.ts` and `mobile-coc-dashboard/types/index.ts`). Keep these in sync when modifying data structures.

### Web Dashboard
- Next.js 16 with React 19, Tailwind CSS v4, TypeScript
- Single-page app: `coc-dashboard/app/page.tsx` is the main entry, client-rendered (`'use client'`)
- Loads data via `fetch('/clan_data.json')` from the public directory
- Components in `coc-dashboard/app/components/` (ClanHeader, PlayersTable, PlayerModal, WarLogTable, etc.)
- Four tabs: overview, players, wars, capital

### Mobile App
- Expo SDK 54, React Native 0.81, expo-router with file-based routing
- Tab navigation in `mobile-coc-dashboard/app/(tabs)/` — overview, players, wars, capital, explore
- Data loaded via `DataContext` (`context/DataContext.tsx`) using `require('@/assets/data/clan_data.json')`
- To update mobile data, copy `coc-dashboard/public/clan_data.json` to `mobile-coc-dashboard/assets/data/`

### Rush Detection
The scraper has a weighted rush scoring algorithm (heroes 50%, troops 35%, spells 15%) comparing player levels against max levels for their previous Town Hall. The classification thresholds and max-level lookup tables are defined inline in `clan_analyzer.py`.

## Key Configuration
- **Clan tag**: hardcoded as `CLAN_TAG` in `api/clan_analyzer.py`
- **API key**: stored in root `.env` as `api_key` (IP-locked CoC developer token)
- `api/streamlit_app.py` is a legacy Streamlit dashboard (not actively used)
