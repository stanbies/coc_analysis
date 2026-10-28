import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { DashboardData } from './types';
import Dashboard from './components/Dashboard';

// Read at build time: the page is pre-rendered on every deploy, and every data
// commit triggers a deploy, so visitors get the data with the HTML instead of
// a loading spinner and a separate fetch.
async function loadData(): Promise<DashboardData | null> {
  try {
    const file = await readFile(path.join(process.cwd(), 'public', 'clan_data.json'), 'utf-8');
    return JSON.parse(file) as DashboardData;
  } catch {
    return null;
  }
}

export default async function Home() {
  const data = await loadData();

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="card p-8 max-w-md text-center">
          <div className="text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-white mb-2">No Data Available</h1>
          <p className="text-slate-400">
            Clan data could not be loaded. Check the &quot;Update clan data&quot; workflow in the
            repository&apos;s Actions tab.
          </p>
        </div>
      </div>
    );
  }

  return <Dashboard data={data} />;
}
