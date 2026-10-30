import type { Metadata } from 'next';
import Link from 'next/link';
import { loadDashboardData } from '../lib/data';
import { Player, RushedItem, RushMethod } from '../types';
import GameIcon from '../components/GameIcon';

export const metadata: Metadata = {
  title: 'How the Rush Score Works | Clash of Clans Dashboard',
  description: 'How the dashboard decides whether a player is rushed',
};

function getRushStatusClass(status: string): string {
  if (status.includes('Maxed')) return 'rush-maxed';
  if (status.includes('Slightly')) return 'rush-slight';
  if (status.includes('Moderately')) return 'rush-moderate';
  if (status.includes('Severely')) return 'rush-severe';
  if (status.includes('Rushed')) return 'rush-rushed';
  return 'bg-slate-600';
}

const stripEmoji = (status: string) => status.replace(/[✅🟢🟡🟠🔴]\s?/g, '');
const fmt = (n: number) => Number(n.toFixed(1)).toString();

// A player with both hero and troop/spell gaps, and as few gaps as possible,
// so the example shows every kind of weight but stays short enough to follow.
function pickExample(players: Player[]): Player | undefined {
  return players
    .filter(p => p.rushAnalysis.rushedHeroes.length > 0 &&
      (p.rushAnalysis.rushedTroops.length > 0 || p.rushAnalysis.rushedSpells.length > 0))
    .sort((a, b) => {
      const count = (p: Player) => p.rushAnalysis.rushedHeroes.length +
        p.rushAnalysis.rushedTroops.length + p.rushAnalysis.rushedSpells.length;
      return count(a) - count(b);
    })[0];
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="card p-6">
      <h2 className="text-xl font-bold text-white mb-3">{title}</h2>
      <div className="space-y-3 text-slate-300 leading-relaxed">{children}</div>
    </section>
  );
}

function ExampleRows({ label, items, weight }: { label: string; items: RushedItem[]; weight: number }) {
  return items.map(item => (
    <tr key={`${label}-${item.name}`} className="border-b border-slate-800">
      <td className="py-2 px-2 text-slate-400 text-sm">{label}</td>
      <td className="py-2 px-2 text-white">{item.name}</td>
      <td className="py-2 px-2 text-right">{item.current}</td>
      <td className="py-2 px-2 text-right">{item.target}</td>
      <td className="py-2 px-2 text-right text-red-400">{item.missing}</td>
      <td className="py-2 px-2 text-right text-slate-400">× {weight}</td>
      <td className="py-2 px-2 text-right text-orange-400 font-medium">{fmt(item.missing * weight)}</td>
    </tr>
  ));
}

function HeroCapsTable({ method }: { method: RushMethod }) {
  const heroes = Object.keys(method.heroCaps);
  const ths = [...new Set(heroes.flatMap(h => Object.keys(method.heroCaps[h]).map(Number)))].sort((a, b) => a - b);
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-700">
            <th className="text-left py-2 px-2 text-slate-400 font-medium">Town Hall</th>
            {heroes.map(h => (
              <th key={h} className="text-right py-2 px-2 text-slate-400 font-medium whitespace-nowrap">
                {h}
                {method.excludedHeroes.includes(h) && <span className="block text-xs text-slate-500">not scored</span>}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {ths.map(th => (
            <tr key={th} className="border-b border-slate-800">
              <td className="py-2 px-2 text-white">TH{th}</td>
              {heroes.map(h => (
                <td key={h} className={`py-2 px-2 text-right ${method.excludedHeroes.includes(h) ? 'text-slate-600' : 'text-slate-300'}`}>
                  {method.heroCaps[h][String(th)] ?? '–'}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default async function RushScorePage() {
  const data = await loadDashboardData();
  const method = data?.rushMethod;
  const example = data ? pickExample(data.players) : undefined;

  return (
    <div className="min-h-screen p-4 md:p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <Link href="/" className="text-sm text-orange-400 hover:text-orange-300">← Back to dashboard</Link>
          <h1 className="text-3xl font-bold text-white mt-3"><GameIcon name="magnifier" size={34} className="mr-2" />How the Rush Score Works</h1>
          <p className="text-slate-400 mt-2">
            A player is &ldquo;rushed&rdquo; when they upgraded their Town Hall before finishing the one
            before it. The rush score measures how far behind they still are.
          </p>
        </div>

        {!method ? (
          <Section title="Details coming soon">
            <p>
              The exact weights and level targets appear here after the next data update, which runs
              automatically every 6 hours.
            </p>
          </Section>
        ) : (
          <>
            <Section title="1. The target: your previous Town Hall">
              <p>
                Every hero, troop and spell is compared against the <strong className="text-white">maximum level
                of the previous Town Hall</strong>. A TH17 player is measured against TH16 max levels: everything you
                could have finished before upgrading.
              </p>
              <p>Levels above that target don&apos;t earn extra credit, so being ahead on one item doesn&apos;t hide being behind on another.</p>
            </Section>

            <Section title="2. Points per missing level">
              <p>Each missing level adds points to the rush score. Heroes count most, because they matter most in attacks.</p>
              <div className="grid grid-cols-3 gap-4 pt-2">
                {[
                  { label: 'Hero level', weight: method.weights.hero, color: 'text-red-400' },
                  { label: 'Spell level', weight: method.weights.spell, color: 'text-purple-400' },
                  { label: 'Troop level', weight: method.weights.troop, color: 'text-cyan-400' },
                ].map(w => (
                  <div key={w.label} className="bg-slate-800 rounded-xl p-4 text-center">
                    <p className={`text-3xl font-bold ${w.color}`}>{w.weight}</p>
                    <p className="text-xs text-slate-400 mt-1">
                      {w.weight === 1 ? 'point' : 'points'} per missing {w.label.toLowerCase()}
                    </p>
                  </div>
                ))}
              </div>
              <p className="text-sm text-slate-400">
                Scored: {Object.keys(method.heroCaps).length - method.excludedHeroes.length} heroes,{' '}
                {method.scoredTroopCount} troops and {method.scoredSpellCount} spells.
              </p>
            </Section>

            <Section title="3. From score to status">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <tbody>
                    {method.statusThresholds.map((t, i) => {
                      const from = i === 0 ? 0 : method.statusThresholds[i - 1].maxScore;
                      return (
                        <tr key={t.status} className="border-b border-slate-800">
                          <td className="py-2 px-2 text-slate-300 whitespace-nowrap">
                            {i === 0 ? `up to ${t.maxScore}` : `${from} – ${t.maxScore}`}
                          </td>
                          <td className="py-2 px-2">
                            <span className={`${getRushStatusClass(t.status)} text-sm px-3 py-1 rounded-full text-white font-medium`}>
                              {stripEmoji(t.status)}
                            </span>
                          </td>
                          <td className="py-2 px-2 text-sm text-slate-400">{t.isRushed ? 'counts as rushed' : 'not rushed'}</td>
                        </tr>
                      );
                    })}
                    <tr className="border-b border-slate-800">
                      <td className="py-2 px-2 text-slate-300 whitespace-nowrap">
                        above {method.statusThresholds[method.statusThresholds.length - 1].maxScore}
                      </td>
                      <td className="py-2 px-2">
                        <span className={`${getRushStatusClass(method.severeStatus)} text-sm px-3 py-1 rounded-full text-white font-medium`}>
                          {stripEmoji(method.severeStatus)}
                        </span>
                      </td>
                      <td className="py-2 px-2 text-sm text-slate-400">counts as rushed</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <p>
                <strong className="text-white">Hero rule:</strong> more than {method.heroSevereMissing} missing hero
                levels always means <em>{stripEmoji(method.heroSevereStatus)}</em>, whatever the total score.
              </p>
            </Section>

            {example && (
              <Section title={`4. Example: ${example.name} (TH${example.townHallLevel})`}>
                <p>
                  {example.name} is compared against TH{example.townHallLevel - 1} max levels. These are the items
                  below that target:
                </p>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-slate-700 text-sm text-slate-400">
                        <th className="text-left py-2 px-2 font-medium">Type</th>
                        <th className="text-left py-2 px-2 font-medium">Item</th>
                        <th className="text-right py-2 px-2 font-medium">Level</th>
                        <th className="text-right py-2 px-2 font-medium">Target</th>
                        <th className="text-right py-2 px-2 font-medium">Missing</th>
                        <th className="text-right py-2 px-2 font-medium">Weight</th>
                        <th className="text-right py-2 px-2 font-medium">Points</th>
                      </tr>
                    </thead>
                    <tbody>
                      <ExampleRows label="Hero" items={example.rushAnalysis.rushedHeroes} weight={method.weights.hero} />
                      <ExampleRows label="Troop" items={example.rushAnalysis.rushedTroops} weight={method.weights.troop} />
                      <ExampleRows label="Spell" items={example.rushAnalysis.rushedSpells} weight={method.weights.spell} />
                      <tr>
                        <td colSpan={6} className="py-3 px-2 text-right text-white font-semibold">Rush score</td>
                        <td className="py-3 px-2 text-right text-orange-400 font-bold text-lg">
                          {fmt(example.rushAnalysis.rushScore)}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p>
                  That&apos;s {example.rushAnalysis.totalMissingHeroLevels} missing hero levels and a score
                  of {fmt(example.rushAnalysis.rushScore)}, so the status is{' '}
                  <span className={`${getRushStatusClass(example.rushAnalysis.status)} text-sm px-3 py-1 rounded-full text-white font-medium`}>
                    {stripEmoji(example.rushAnalysis.status)}
                  </span>
                </p>
              </Section>
            )}

            <Section title="5. Rush % (“Behind Target”)">
              <p>
                The player popup also shows a percentage. It adds up all target levels and shows what share
                the player hasn&apos;t reached yet. It treats every level equally (no weights), so it&apos;s a
                rough &ldquo;how much is left&rdquo; figure, while the rush score decides the status.
              </p>
            </Section>

            <Section title="6. What isn't counted">
              <ul className="list-disc pl-5 space-y-1">
                {method.excludedHeroes.length > 0 && (
                  <li>
                    <strong className="text-white">{method.excludedHeroes.join(', ')}</strong>: the clan doesn&apos;t
                    use {method.excludedHeroes.length === 1 ? 'it' : 'them'}, so missing levels don&apos;t count.
                    Still shown in the player popup.
                  </li>
                )}
                <li>Pets, siege machines and super troops</li>
                <li>Builder Base heroes and troops</li>
                <li>Hero equipment, buildings and walls</li>
              </ul>
            </Section>

            <Section title="Hero targets per Town Hall">
              <p>Max hero levels per Town Hall. Your target is the row for the Town Hall <em>before</em> yours.</p>
              <HeroCapsTable method={method} />
            </Section>
          </>
        )}

        <p className="text-center text-sm">
          <Link href="/" className="text-orange-400 hover:text-orange-300">← Back to dashboard</Link>
        </p>
      </div>
    </div>
  );
}
