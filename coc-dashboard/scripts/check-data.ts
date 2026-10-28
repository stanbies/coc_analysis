// Compile-time contract between the scraper's output and the dashboard types.
// `npm run typecheck` (and `next build`) fail if clan_data.json no longer
// matches DashboardData, e.g. when the scraper starts emitting null for a field
// the types don't allow. Fix the types (and the components that use the field)
// rather than casting here.
import data from '../public/clan_data.json';
import type { DashboardData } from '../app/types';

export const checked: DashboardData = data;
