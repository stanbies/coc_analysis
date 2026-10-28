"""
Legacy static HTML report for the clan analyzer.
Replaced by the Next.js dashboard (coc-dashboard/). Not maintained.
Previously called from main() in api/clan_analyzer.py.
"""

import os
from collections import defaultdict
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_REPORT_FILE = os.path.join(SCRIPT_DIR, "clan_dashboard.html")


def generate_html_dashboard(clan: dict, players_data: list, rush_reports: list, historical_data: dict):
    """Generate a beautiful HTML dashboard for the clan analysis."""
    
    # Prepare data
    clan_name = clan.get('name', 'Unknown Clan')
    clan_tag = clan.get('tag', '')
    clan_level = clan.get('clanLevel', 0)
    members_count = clan.get('members', 0)
    war_wins = clan.get('warWins', 0)
    war_losses = clan.get('warLosses', 0)
    war_ties = clan.get('warTies', 0)
    total_wars = war_wins + war_losses + war_ties
    win_rate = (war_wins / total_wars * 100) if total_wars > 0 else 0
    
    # TH distribution
    th_dist = defaultdict(int)
    for p in players_data:
        th_dist[p.get('townHallLevel', 0)] += 1
    
    # Rush stats
    rushed_count = sum(1 for r in rush_reports if r.get('is_rushed', False))
    avg_rush_score = sum(r.get('rush_score', 0) for r in rush_reports) / len(rush_reports) if rush_reports else 0
    
    # Historical stats
    hist_players = historical_data.get('players', {})
    total_hist_attacks = sum(p.get('total_attacks', 0) for p in hist_players.values())
    total_hist_stars = sum(p.get('total_stars', 0) for p in hist_players.values())
    avg_stars = total_hist_stars / total_hist_attacks if total_hist_attacks > 0 else 0
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{clan_name} - Clan Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #ffffff;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }}
        .header h1 {{
            font-size: 2.5em;
            color: #e94560;
            margin-bottom: 10px;
        }}
        .header .clan-tag {{
            color: #888;
            font-size: 1.1em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #1f4068 0%, #162447 100%);
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #e94560;
        }}
        .stat-card .label {{
            color: #aaa;
            margin-top: 5px;
            font-size: 0.9em;
        }}
        .section {{
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        .section h2 {{
            color: #e94560;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e94560;
        }}
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }}
        .chart-container {{
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
            padding: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        th {{
            background: rgba(233, 69, 96, 0.2);
            color: #e94560;
            font-weight: 600;
        }}
        tr:hover {{
            background: rgba(255,255,255,0.05);
        }}
        .rush-status {{
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        .rush-maxed {{ background: #27ae60; }}
        .rush-slight {{ background: #2ecc71; }}
        .rush-moderate {{ background: #f39c12; }}
        .rush-rushed {{ background: #e67e22; }}
        .rush-severe {{ background: #e74c3c; }}
        .progress-bar {{
            width: 100%;
            height: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            border-radius: 10px;
            transition: width 0.5s ease;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            margin-top: 30px;
        }}
        .tab-container {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }}
        .tab {{
            padding: 10px 20px;
            background: rgba(255,255,255,0.1);
            border: none;
            color: #fff;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        .tab:hover, .tab.active {{
            background: #e94560;
        }}
        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
        }}
        .hero-bar {{
            display: flex;
            align-items: center;
            margin: 5px 0;
        }}
        .hero-name {{
            width: 100px;
            font-size: 0.85em;
        }}
        .hero-progress {{
            flex: 1;
            height: 15px;
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            overflow: hidden;
            margin: 0 10px;
        }}
        .hero-fill {{
            height: 100%;
            background: linear-gradient(90deg, #e94560, #f39c12);
            border-radius: 8px;
        }}
        .hero-level {{
            font-size: 0.85em;
            color: #aaa;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏰 {clan_name}</h1>
            <p class="clan-tag">{clan_tag} • Level {clan_level}</p>
            <p style="margin-top: 10px; color: #aaa;">Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="value">{members_count}</div>
                <div class="label">👥 Members</div>
            </div>
            <div class="stat-card">
                <div class="value">{win_rate:.1f}%</div>
                <div class="label">⚔️ War Win Rate</div>
            </div>
            <div class="stat-card">
                <div class="value">{war_wins}</div>
                <div class="label">✅ War Wins</div>
            </div>
            <div class="stat-card">
                <div class="value">{avg_stars:.2f}</div>
                <div class="label">⭐ Avg Stars/Attack</div>
            </div>
            <div class="stat-card">
                <div class="value">{total_hist_attacks}</div>
                <div class="label">🎯 Attacks Tracked</div>
            </div>
            <div class="stat-card">
                <div class="value">{rushed_count}</div>
                <div class="label">⚠️ Rushed Players</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Clan Composition</h2>
            <div class="charts-grid">
                <div class="chart-container">
                    <canvas id="thChart"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="rushChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>👥 Member Rush Analysis</h2>
            <div class="tab-container">
                <button class="tab active" onclick="showTab('all')">All Members</button>
                <button class="tab" onclick="showTab('rushed')">Rushed Only</button>
                <button class="tab" onclick="showTab('maxed')">Not Rushed</button>
            </div>
            <div id="tab-all" class="tab-content active">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Player</th>
                            <th>TH</th>
                            <th>Rush Score</th>
                            <th>Hero Deficit</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
'''
    
    # Add rows for all players
    for i, report in enumerate(rush_reports, 1):
        status = report.get('status', 'Unknown')
        status_class = 'rush-maxed'
        if 'Slightly' in status:
            status_class = 'rush-slight'
        elif 'Moderately' in status:
            status_class = 'rush-moderate'
        elif 'Rushed' in status and 'Severely' not in status:
            status_class = 'rush-rushed'
        elif 'Severely' in status:
            status_class = 'rush-severe'
        
        # Clean status for display
        display_status = status.replace('✅ ', '').replace('🟢 ', '').replace('🟡 ', '').replace('🟠 ', '').replace('🔴 ', '')
        
        html += f'''
                        <tr data-rushed="{str(report.get('is_rushed', False)).lower()}">
                            <td>{i}</td>
                            <td>{report.get('player_name', 'Unknown')}</td>
                            <td>{report.get('th_level', '?')}</td>
                            <td>{report.get('rush_score', 0):.1f}</td>
                            <td>-{report.get('total_missing_hero_levels', 0)}</td>
                            <td><span class="rush-status {status_class}">{display_status}</span></td>
                        </tr>'''
    
    html += '''
                    </tbody>
                </table>
            </div>
            <div id="tab-rushed" class="tab-content">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Player</th>
                            <th>TH</th>
                            <th>Rush Score</th>
                            <th>Hero Deficit</th>
                            <th>Rushed Heroes</th>
                        </tr>
                    </thead>
                    <tbody>
'''
    
    # Add rows for rushed players only
    rushed_only = [r for r in rush_reports if r.get('is_rushed', False)]
    for i, report in enumerate(rushed_only, 1):
        heroes_str = ', '.join([f"{h['name'][:2]}:{h['current']}/{h['target']}" for h in report.get('rushed_heroes', [])[:4]])
        html += f'''
                        <tr>
                            <td>{i}</td>
                            <td>{report.get('player_name', 'Unknown')}</td>
                            <td>{report.get('th_level', '?')}</td>
                            <td>{report.get('rush_score', 0):.1f}</td>
                            <td>-{report.get('total_missing_hero_levels', 0)}</td>
                            <td style="font-size: 0.85em;">{heroes_str}</td>
                        </tr>'''
    
    html += '''
                    </tbody>
                </table>
            </div>
            <div id="tab-maxed" class="tab-content">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Player</th>
                            <th>TH</th>
                            <th>Rush Score</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
'''
    
    # Add rows for non-rushed players
    not_rushed = [r for r in rush_reports if not r.get('is_rushed', False)]
    for i, report in enumerate(not_rushed, 1):
        html += f'''
                        <tr>
                            <td>{i}</td>
                            <td>{report.get('player_name', 'Unknown')}</td>
                            <td>{report.get('th_level', '?')}</td>
                            <td>{report.get('rush_score', 0):.1f}</td>
                            <td><span class="rush-status rush-maxed">Not Rushed</span></td>
                        </tr>'''
    
    html += '''
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="section">
            <h2>🏆 Historical War Performance</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Player</th>
                        <th>TH</th>
                        <th>Attacks</th>
                        <th>Stars</th>
                        <th>Avg ⭐</th>
                        <th>3-Star %</th>
                    </tr>
                </thead>
                <tbody>
'''
    
    # Historical performance table
    hist_sorted = sorted(hist_players.values(), key=lambda x: (-x.get('total_stars', 0) / x.get('total_attacks', 1) if x.get('total_attacks', 0) > 0 else 0, -x.get('total_attacks', 0)))
    
    for i, p in enumerate(hist_sorted[:30], 1):
        attacks = p.get('total_attacks', 0)
        stars = p.get('total_stars', 0)
        avg = stars / attacks if attacks > 0 else 0
        three_pct = p.get('three_stars', 0) / attacks * 100 if attacks > 0 else 0
        
        html += f'''
                    <tr>
                        <td>{i}</td>
                        <td>{p.get('name', 'Unknown')}</td>
                        <td>{p.get('current_th', '?')}</td>
                        <td>{attacks}</td>
                        <td>{stars}</td>
                        <td>{avg:.2f}</td>
                        <td>{three_pct:.1f}%</td>
                    </tr>'''
    
    # Prepare chart data
    th_labels = [f"TH{th}" for th in sorted(th_dist.keys(), reverse=True)]
    th_values = [th_dist[th] for th in sorted(th_dist.keys(), reverse=True)]
    
    rush_status_counts = defaultdict(int)
    for r in rush_reports:
        status = r.get('status', 'Unknown')
        if 'Maxed' in status:
            rush_status_counts['Maxed'] += 1
        elif 'Slightly' in status:
            rush_status_counts['Slightly Behind'] += 1
        elif 'Moderately' in status:
            rush_status_counts['Moderately Rushed'] += 1
        elif 'Severely' in status:
            rush_status_counts['Severely Rushed'] += 1
        elif 'Rushed' in status:
            rush_status_counts['Rushed'] += 1
        else:
            rush_status_counts['Other'] += 1
    
    html += f'''
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Generated by Clash of Clans Clan Analyzer | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
    
    <script>
        // TH Distribution Chart
        new Chart(document.getElementById('thChart'), {{
            type: 'bar',
            data: {{
                labels: {th_labels},
                datasets: [{{
                    label: 'Players',
                    data: {th_values},
                    backgroundColor: [
                        '#e94560', '#f39c12', '#3498db', '#2ecc71', '#9b59b6',
                        '#1abc9c', '#e74c3c', '#34495e', '#f1c40f', '#95a5a6'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Town Hall Distribution',
                        color: '#fff'
                    }},
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{ color: '#aaa' }},
                        grid: {{ color: 'rgba(255,255,255,0.1)' }}
                    }},
                    x: {{
                        ticks: {{ color: '#aaa' }},
                        grid: {{ color: 'rgba(255,255,255,0.1)' }}
                    }}
                }}
            }}
        }});
        
        // Rush Status Chart
        new Chart(document.getElementById('rushChart'), {{
            type: 'doughnut',
            data: {{
                labels: {list(rush_status_counts.keys())},
                datasets: [{{
                    data: {list(rush_status_counts.values())},
                    backgroundColor: ['#27ae60', '#2ecc71', '#f39c12', '#e74c3c', '#e67e22', '#95a5a6']
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Rush Status Distribution',
                        color: '#fff'
                    }},
                    legend: {{
                        position: 'bottom',
                        labels: {{ color: '#aaa' }}
                    }}
                }}
            }}
        }});
        
        // Tab functionality
        function showTab(tabName) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            document.getElementById('tab-' + tabName).classList.add('active');
            event.target.classList.add('active');
        }}
    </script>
</body>
</html>
'''
    
    # Save HTML file
    with open(HTML_REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"   ✅ Dashboard saved to: {HTML_REPORT_FILE}")
