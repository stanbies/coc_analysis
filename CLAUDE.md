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
- `export.py` — builds `clan_data.json`, including `rankedHistory` (from `ranked_snapshots.json`) and `rankedBenchmarks` (from `api/mail_config/benchmarks.yaml`) for the Players tab.
- `check_caps.py` — warns when a player exceeds the max-level tables.
- `ranked.py` — weekly ranked snapshots in `ranked_snapshots.json` (same publish/local split as the war history): per ISO week and player the TH + league when recorded, plus the finished week's `result` (league, placement, trophies, attacks played/allowed) merged in from the league history, which the API only keeps for 8 weeks.
- `weekly_mail.py` — weekly personal ranked mail, written as a LinkedIn-style motivational post (copy in `OPENERS`/`SUBJECTS` and `compose_mail()`). `--dry-run` writes previews to `api/out/mails/`, `--test-to <email>` sends everything to one address, `--send` mails the subscribers. Benchmarks (TH → minimum league) and strategy videos are in `api/mail_config/*.yaml`; Town Halls not listed use the closest lower one. Sending logs tags only, never addresses.
- `mailer.py` — Gmail SMTP from cocanalysis686@gmail.com. `smtp_password` must be a Google app password created on that account (the account password and app passwords of other accounts are rejected with 535).
- `subscribers.py` — subscriber list (`email,#TAG` lines) from the `mail_subscribers` secret, or locally the gitignored `api/subscribers.csv`. Never commit email addresses.
- `test_*.py` — pytest tests, run in the workflow before every scrape.

Ranked facts (checked live, Oct 2026): `leagueTier.id` is 105000000 + league number (1–33 Skeleton…Electro, 34–36 Legend III/II/I). A tournament week starts Monday 05:00 UTC and `currentLeagueSeasonId` is that start as a unix timestamp. `/players/{tag}/leaguehistory` lists finished weeks oldest first, with `leagueTierId`, `placement`, `leagueTrophies` and battle counts.

The scraper exits non-zero if the clan or member fetches fail, or if more than `MAX_MISSING_PLAYERS` (3) players still fail after a retry pass. Fewer missing players produce a `::warning::` annotation. All stored timestamps are UTC with an explicit offset.

### Publishing
- Only the GitHub workflow publishes data. It sets `publish_data=true`, which makes the scraper write to `coc-dashboard/public/clan_data.json` and `api/clan_history.json`. Without it (local runs) output goes to the gitignored `api/out/`, and history is read from `api/out/` or else the committed file. Don't commit data files by hand: it collides with the bot's commits.
- `.github/workflows/update-data.yml` runs every 6 hours, via workflow_dispatch, and right after the weekly ranked workflow (so the new ranked week reaches the site on Monday morning): tests → scraper → `check_caps.py` → dashboard `npm run typecheck` (data contract) → copies the JSON into `mobile-coc-dashboard/assets/data/` → commits to `main` unless only timestamps changed. Vercel redeploys on the push. Secrets: `api_key`, `coc_base_url`.
- `.github/workflows/weekly-ranked.yml` runs Monday 07:00 UTC (after the 05:00 UTC ranked reset): tests → `ranked.py` → commits `api/ranked_snapshots.json` (pull-rebases first, since the data job may have pushed) → `weekly_mail.py --send`. Manual runs only send when the `send_mails` input is ticked. Extra secrets: `smtp_password`, `mail_subscribers`.

### War history
`update_player_historical_stats()` replaces a war's attacks on every run (keyed by war id) and recomputes totals from `attacks_history`, so repeat runs during a war pick up new attacks without double counting. Prep-day wars are not recorded. Attack `date` is the war's start time. Only wars seen while `inWar`/`warEnded` are captured, hence the 6-hour schedule. History recorded before October 2026 undercounts attacks (it kept only the first snapshot of each war) and can't be recovered.

### Web Dashboard
- Next.js 16 with React 19, Tailwind CSS v4, TypeScript
- `app/page.tsx` is a server component that reads `public/clan_data.json` at build time, so the page is pre-rendered on each deploy. The interactive UI (tabs, modal) is the client component `app/components/Dashboard.tsx`.
- Because of pre-rendering, anything locale- or timezone-dependent must not differ between server and browser: numbers use `toLocaleString('en-US')`, and "Last updated" is formatted client-side in `ClanHeader`.
- The overview's "Zwegers of the Week" lists members below their benchmark in the second-newest week of `rankedHistory` and at or above it in the newest (`zwegersOfTheWeek()` in `app/lib/ranked.ts`), so it changes once a week.
- Each tab has its own layout: the overview keeps the full wooden `ClanHeader`; Players, Wars and Capital get `CompactHeader` plus a `TabHero` (`TabHeroes.tsx`) and their own graphs (`RankedCharts`, `WarCharts`, `CapitalCharts`; shared bits in `ChartParts`, data shaping in `app/lib/`). The active tab is in the URL hash (`#wars`). Graphs use Recharts; colours were checked with the dataviz palette validator, so keep them in `ChartParts.tsx`.
- The Clash of Clans look lives in `app/theme.css`, not `globals.css`: the Tailwind PostCSS plugin caches `globals.css` in the dev server, so edits there often don't show until `.next` is deleted. Game art comes from Supercell's fan kit (`public/icons/`, `public/backgrounds/`, see `public/icons/README.md`); the footer carries the required fan content notice.
- Preview a local scraper export without touching the published file: `DASHBOARD_DATA_FILE=../api/out/clan_data.json npm run dev`.
- `app/rush-score/page.tsx` explains the rush score (linked from the Most Rushed table, the rush chart and the player modal). It's data-driven from `rushMethod`, with a worked example using a real player, and shows a placeholder when `rushMethod` is missing. Data loading for both pages is in `app/lib/data.ts`.
- Never sort `players` in place (`[...players].sort(...)`); it's shared across tabs.
- Both dashboards share the same `DashboardData` TypeScript interface shape (defined separately in `coc-dashboard/app/types.ts` and `mobile-coc-dashboard/types/index.ts`). Keep these in sync with `export.py` when modifying data structures. `coc-dashboard/scripts/check-data.ts` assigns the real `clan_data.json` to `DashboardData`, so a mismatch fails `npm run typecheck`, the workflow (before committing) and `next build`. Fields the scraper can emit as `null` must be typed `| null`.
- Ranked battles (since Oct 2025) live in the player's `leagueTier`; the old `league` field is always `null` and `trophies` resets every weekly tournament. The dashboards show and sort by `leagueTier` (tier ids increase with the league).

### Mobile App
- Expo SDK 54, React Native 0.81, expo-router with file-based routing
- Tab navigation in `mobile-coc-dashboard/app/(tabs)/` — overview, players, wars, capital, explore
- Data loaded via `DataContext` (`context/DataContext.tsx`) using `require('@/assets/data/clan_data.json')`. The workflow keeps that file in sync, but the data is bundled, so the app needs a rebuild to show it.

### Rush Detection
`generate_rush_report()` in `rush.py` compares each home-village hero, troop and spell against the max level at the player's **previous** Town Hall. Each missing level adds to the score: heroes 1.0, troops 0.3, spells 0.4. Thresholds: ≤3 Maxed, ≤10 Slightly Behind, ≤25 Moderately Rushed, ≤50 Rushed, >50 Severely Rushed; more than 20 missing hero levels always means Severely Rushed (Heroes). `rush_percentage` is separate and unweighted (100 − % of benchmark levels reached).
- Max levels live in `HERO_MAX_LEVELS`, `TROOP_MAX_LEVELS` and `SPELL_MAX_LEVELS` (TH → level). Items missing from these tables are ignored by the score. Pets, siege machines and super troops are deliberately excluded.
- Weights, status thresholds and the hero rule are constants at the top of `rush.py`. `rush_method()` exports them (plus hero caps and excluded heroes) as `rushMethod` in `clan_data.json`, and the dashboard's `/rush-score` page renders its explanation from that. Change the constants, not the page text.
- Heroes in `RUSH_EXCLUDED_HEROES` (currently Minion Prince, which the clan doesn't use) stay in `HERO_MAX_LEVELS` for the displayed cap and `check_caps.py`, but `generate_rush_report()` skips them entirely. Remove a name from the set to score it again.
- `export_dashboard_data()` also uses these tables for the `maxLevel` the dashboards display (cap at the player's current TH), falling back to the API value only for items not in the tables.
- Don't rebuild these tables from the API's `maxLevel`: it's stale after updates and for many items it's the global max, not the TH cap. When `check_caps.py` warns in the workflow, update the tables from a current max-levels reference.

## Key Configuration
- **Clan tag**: `CLAN_TAG` in `api/config.py`
- **API key**: stored in root `.env` as `api_key` (IP-locked CoC developer token, allowed IP `45.79.218.79` for the proxy)
- **Base URL**: `coc_base_url` in `.env`, set to `https://cocproxy.royaleapi.dev/v1` (RoyaleAPI proxy, needed because Action runners have dynamic IPs). Defaults to the official API if unset.
- **Python dependencies** are pinned exactly in `api/requirements.txt`; bump them deliberately.
- `legacy/` holds unmaintained code (old Streamlit dashboard, old static HTML report). Don't extend it.
