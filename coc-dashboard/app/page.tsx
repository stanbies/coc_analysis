import { loadDashboardData } from './lib/data';
import Dashboard from './components/Dashboard';
import GameIcon from './components/GameIcon';

export default async function Home() {
  const data = await loadDashboardData();

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="card p-8 max-w-md text-center">
          <GameIcon name="upgradeHammer" size={72} className="mb-4" />
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
