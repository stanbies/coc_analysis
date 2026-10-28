import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { DashboardData } from '../types';

// Read at build time: pages are pre-rendered on every deploy, and every data
// commit triggers a deploy, so visitors get the data with the HTML instead of
// a loading spinner and a separate fetch.
export async function loadDashboardData(): Promise<DashboardData | null> {
  try {
    const file = await readFile(path.join(process.cwd(), 'public', 'clan_data.json'), 'utf-8');
    return JSON.parse(file) as DashboardData;
  } catch {
    return null;
  }
}
