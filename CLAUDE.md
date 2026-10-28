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
- `api/clan_analyzer.py` is a single script containing all scraping logic, rush detection algorithm, and data export. It reads `.env` from the repo root for `api_key` and `coc_base_url`.
- The scraper writes `clan_history.json` (historical war data) alongside itself in `api/`. It exits non-zero if the clan, member or player fetches fail.
- `.github/workflows/update-data.yml` runs the scraper daily (05:00 UTC, or manually via workflow_dispatch) and commits `clan_data.json` + `clan_history.json` to `main`; Vercel redeploys on the push. It reads `api_key` and `coc_base_url` from repo secrets.
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
`generate_rush_report()` in `clan_analyzer.py` compares each home-village hero, troop and spell against the max level at the player's **previous** Town Hall. Each missing level adds to the score: heroes 1.0, troops 0.3, spells 0.4. Thresholds: ≤3 Maxed, ≤10 Slightly Behind, ≤25 Moderately Rushed, ≤50 Rushed, >50 Severely Rushed; more than 20 missing hero levels always means Severely Rushed (Heroes). `rush_percentage` is separate and unweighted (100 − % of benchmark levels reached).
- Max levels live in `HERO_MAX_LEVELS`, `TROOP_MAX_LEVELS` and `SPELL_MAX_LEVELS` (TH → level). Items missing from these tables are ignored by the score. Pets, siege machines and super troops are deliberately excluded.
- `export_dashboard_data()` also uses these tables for the `maxLevel` the dashboards display (cap at the player's current TH), falling back to the API value only for items not in the tables.
- Don't rebuild these tables from the API's `maxLevel`: it's stale after updates and for many items it's the global max, not the TH cap. Update them from a current max-levels reference after each game update that raises caps, then check that no player in `clan_data.json` exceeds the cap for their TH.

## Key Configuration
- **Clan tag**: hardcoded as `CLAN_TAG` in `api/clan_analyzer.py`
- **API key**: stored in root `.env` as `api_key` (IP-locked CoC developer token, allowed IP `45.79.218.79` for the proxy)
- **Base URL**: `coc_base_url` in `.env`, set to `https://cocproxy.royaleapi.dev/v1` (RoyaleAPI proxy, needed because Action runners have dynamic IPs). Defaults to the official API if unset.
- `legacy/` holds unmaintained code (old Streamlit dashboard, old static HTML report). Don't extend it.
