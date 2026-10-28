# Legacy

Old code kept for reference. Nothing here is maintained or used by the scraper, dashboards or the daily update workflow.

- `streamlit_app.py`: the original Streamlit dashboard, replaced by the Next.js dashboard in `coc-dashboard/`. Dependencies are in `requirements.txt`.
- `html_report.py`: `generate_html_dashboard()`, which the scraper used to call to write a static `clan_dashboard.html` report. It was moved out of `api/clan_analyzer.py` and isn't wired up to run on its own.
