# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Clash of Clans clan analyzer and dashboard. Three-part architecture:
1. **Python scraper** (`api/`) — fetches data from the CoC API and exports to JSON
2. **Next.js web dashboard** (`coc-dashboard/`) — reads `public/clan_data.json` and renders a tabbed UI
3. **Expo/React Native mobile app** (`mobile-coc-dashboard/`) — reads `assets/data/clan_data.json` with the same data

Data flows one-way: scraper → JSON file → dashboards (no live API calls from frontends).

## Common Commands

### Python scraper
```bash
# Activate venv (from repo root)
source venv/Scripts/activate   # Windows Git Bash
# or: venv\Scripts\activate    # Windows CMD

# Install dependencies (requirements-dev.txt adds pytest)
pip install -r api/requirements-dev.txt

# Run scraper (local runs write to api/out/, see "Publishing" below)
python api/clan_analyzer.py

# Tests
python -m pytest api/

# Check the max-level tables against exported data
python api/check_caps.py coc-dashboard/public/clan_data.json
```

### Web dashboard (Next.js)
```bash
cd coc-dashboard
npm install
npm run dev       # dev server on localhost:3000
npm run build     # production build
npm run lint      # ESLint
npm run typecheck # tsc, includes the data contract check (scripts/check-data.ts)
```
On the BCG laptop, npm needs the Windows certificate store (corporate TLS inspection): prefix commands with `NODE_OPTIONS=--use-system-ca`.

### Mobile app (Expo)
```bash
cd mobile-coc-dashboard
npm install
npx expo start          # start dev server
npx expo start --web    # web preview
npx expo lint           # ESLint
```

## Architecture Details

### Scraper modules (`api/`)
- `clan_analyzer.py` — entry point: `main()` fetches everything, prints the console analysis, records war history and exports.
- `config.py` — env loading (`.env` in repo root), `CLAN_TAG`, output paths.
- `coc_api.py` — API client; `api_request()` retries 5xx/connection errors with backoff (the proxy is flaky).
- `rush.py` — max-level tables and `generate_rush_report()`.
- `history.py` — `clan_history.json` persistence and per-war attack recording.
- `export.py` — builds `clan_data.json`.
- `check_caps.py` — warns when a player exceeds the max-level tables.
- `test_*.py` — pytest tests, run in the workflow before every scrape.

The scraper exits non-zero if the clan or member fetches fail, or if more than `MAX_MISSING_PLAYERS` (3) players still fail after a retry pass. Fewer missing players produce a `::warning::` annotation. All stored timestamps are UTC with an explicit offset.

### Publishing
- Only the GitHub workflow publishes data. It sets `publish_data=true`, which makes the scraper write to `coc-dashboard/public/clan_data.json` and `api/clan_history.json`. Without it (local runs) output goes to the gitignored `api/out/`, and history is read from `api/out/` or else the committed file. Don't commit data files by hand: it collides with the bot's commits.
- `.github/workflows/update-data.yml` runs every 6 hours (or via workflow_dispatch): tests → scraper → `check_caps.py` → dashboard `npm run typecheck` (data contract) → copies the JSON into `mobile-coc-dashboard/assets/data/` → commits to `main` unless only timestamps changed. Vercel redeploys on the push. Secrets: `api_key`, `coc_base_url`.

### War history
`update_player_historical_stats()` replaces a war's attacks on every run (keyed by war id) and recomputes totals from `attacks_history`, so repeat runs during a war pick up new attacks without double counting. Prep-day wars are not recorded. Attack `date` is the war's start time. Only wars seen while `inWar`/`warEnded` are captured, hence the 6-hour schedule. History recorded before October 2026 undercounts attacks (it kept only the first snapshot of each war) and can't be recovered.

### Web Dashboard
- Next.js 16 with React 19, Tailwind CSS v4, TypeScript
- `app/page.tsx` is a server component that reads `public/clan_data.json` at build time, so the page is pre-rendered on each deploy. The interactive UI (tabs, modal) is the client component `app/components/Dashboard.tsx`.
- Because of pre-rendering, anything locale- or timezone-dependent must not differ between server and browser: numbers use `toLocaleString('en-US')`, and "Last updated" is formatted client-side in `ClanHeader`.
- Never sort `players` in place (`[...players].sort(...)`); it's shared across tabs.
- Both dashboards share the same `DashboardData` TypeScript interface shape (defined separately in `coc-dashboard/app/types.ts` and `mobile-coc-dashboard/types/index.ts`). Keep these in sync with `export.py` when modifying data structures. `coc-dashboard/scripts/check-data.ts` assigns the real `clan_data.json` to `DashboardData`, so a mismatch fails `npm run typecheck`, the workflow (before committing) and `next build`. Fields the scraper can emit as `null` must be typed `| null`.

### Mobile App
- Expo SDK 54, React Native 0.81, expo-router with file-based routing
- Tab navigation in `mobile-coc-dashboard/app/(tabs)/` — overview, players, wars, capital, explore
- Data loaded via `DataContext` (`context/DataContext.tsx`) using `require('@/assets/data/clan_data.json')`. The workflow keeps that file in sync, but the data is bundled, so the app needs a rebuild to show it.

### Rush Detection
`generate_rush_report()` in `rush.py` compares each home-village hero, troop and spell against the max level at the player's **previous** Town Hall. Each missing level adds to the score: heroes 1.0, troops 0.3, spells 0.4. Thresholds: ≤3 Maxed, ≤10 Slightly Behind, ≤25 Moderately Rushed, ≤50 Rushed, >50 Severely Rushed; more than 20 missing hero levels always means Severely Rushed (Heroes). `rush_percentage` is separate and unweighted (100 − % of benchmark levels reached).
- Max levels live in `HERO_MAX_LEVELS`, `TROOP_MAX_LEVELS` and `SPELL_MAX_LEVELS` (TH → level). Items missing from these tables are ignored by the score. Pets, siege machines and super troops are deliberately excluded.
- Heroes in `RUSH_EXCLUDED_HEROES` (currently Minion Prince, which the clan doesn't use) stay in `HERO_MAX_LEVELS` for the displayed cap and `check_caps.py`, but `generate_rush_report()` skips them entirely. Remove a name from the set to score it again.
- `export_dashboard_data()` also uses these tables for the `maxLevel` the dashboards display (cap at the player's current TH), falling back to the API value only for items not in the tables.
- Don't rebuild these tables from the API's `maxLevel`: it's stale after updates and for many items it's the global max, not the TH cap. When `check_caps.py` warns in the workflow, update the tables from a current max-levels reference.

## Key Configuration
- **Clan tag**: `CLAN_TAG` in `api/config.py`
- **API key**: stored in root `.env` as `api_key` (IP-locked CoC developer token, allowed IP `45.79.218.79` for the proxy)
- **Base URL**: `coc_base_url` in `.env`, set to `https://cocproxy.royaleapi.dev/v1` (RoyaleAPI proxy, needed because Action runners have dynamic IPs). Defaults to the official API if unset.
- **Python dependencies** are pinned exactly in `api/requirements.txt`; bump them deliberately.
- `legacy/` holds unmaintained code (old Streamlit dashboard, old static HTML report). Don't extend it.
