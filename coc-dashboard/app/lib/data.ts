import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { DashboardData } from '../types';

// Read at build time: pages are pre-rendered on every deploy, and every data
// commit triggers a deploy, so visitors get the data with the HTML instead of
// a loading spinner and a separate fetch.
//
// DASHBOARD_DATA_FILE points at another export for local previews, e.g. a
// local scraper run: DASHBOARD_DATA_FILE=../api/out/clan_data.json npm run dev
export async function loadDashboardData(): Promise<DashboardData | null> {
  const file = process.env.DASHBOARD_DATA_FILE ?? path.join('public', 'clan_data.json');
  try {
    return JSON.parse(await readFile(path.resolve(process.cwd(), file), 'utf-8')) as DashboardData;
  } catch {
    return null;
  }
}
