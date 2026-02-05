#!/usr/bin/env python3
"""Quick script to update clan_data.json with CWL seasons from historical data."""

import json
from collections import defaultdict

# Load historical data  
with open('api/clan_history.json', 'r') as f:
    historical_data = json.load(f)

# Load existing dashboard data
with open('coc-dashboard/public/clan_data.json', 'r') as f:
    dashboard_data = json.load(f)

# Build CWL seasons from historical data
players_data = historical_data.get('players', {})

season_attacks = defaultdict(lambda: defaultdict(list))
season_wars = defaultdict(set)

for player_tag, player in players_data.items():
    for attack in player.get('attacks_history', []):
        war_type = attack.get('war_type', '')
        if war_type.startswith('CWL_'):
            season = war_type.replace('CWL_', '')
            war_id = attack.get('war_id', '')
            round_num = 0
            if '_round' in war_id:
                try:
                    round_num = int(war_id.split('_round')[1].split('_')[0])
                except:
                    pass
            
            season_attacks[season][player_tag].append({
                'warId': war_id,
                'round': round_num,
                'stars': attack.get('stars', 0),
                'destruction': attack.get('destruction', 0),
                'defenderTh': attack.get('defender_th', 0),
                'attackerTh': attack.get('attacker_th', 0),
                'hitType': attack.get('hit_type', 'unknown'),
                'date': attack.get('date', ''),
            })
            season_wars[season].add(war_id)

cwl_seasons_export = []

for season, player_attacks in season_attacks.items():
    player_stats = []
    total_stars = 0
    total_attacks_count = 0
    total_three_stars = 0
    
    for player_tag, attacks in player_attacks.items():
        player_info = players_data.get(player_tag, {})
        
        p_stars = sum(a['stars'] for a in attacks)
        p_destruction = sum(a['destruction'] for a in attacks)
        p_three_stars = sum(1 for a in attacks if a['stars'] == 3)
        p_two_stars = sum(1 for a in attacks if a['stars'] == 2)
        p_one_stars = sum(1 for a in attacks if a['stars'] == 1)
        p_zero_stars = sum(1 for a in attacks if a['stars'] == 0)
        p_hit_up = sum(1 for a in attacks if 'UP' in a['hitType'])
        p_hit_same = sum(1 for a in attacks if 'SAME' in a['hitType'])
        p_hit_down = sum(1 for a in attacks if 'DOWN' in a['hitType'])
        
        attack_count = len(attacks)
        
        player_stats.append({
            'tag': player_tag,
            'name': player_info.get('name', 'Unknown'),
            'townHallLevel': player_info.get('current_th', 0),
            'totalStars': p_stars,
            'totalDestruction': p_destruction,
            'attacksUsed': attack_count,
            'threeStars': p_three_stars,
            'twoStars': p_two_stars,
            'oneStars': p_one_stars,
            'zeroStars': p_zero_stars,
            'warsParticipated': len(set(a['warId'] for a in attacks)),
            'hitUp': p_hit_up,
            'hitSame': p_hit_same,
            'hitDown': p_hit_down,
            'averageStars': p_stars / attack_count if attack_count > 0 else 0,
            'averageDestruction': p_destruction / attack_count if attack_count > 0 else 0,
            'attacks': sorted(attacks, key=lambda x: x['round']),
        })
        
        total_stars += p_stars
        total_attacks_count += attack_count
        total_three_stars += p_three_stars
    
    # Sort player stats by total stars descending
    player_stats.sort(key=lambda x: (-x['totalStars'], -x['averageStars']))
    
    cwl_seasons_export.append({
        'season': season,
        'state': 'ended',
        'league': None,
        'clansInGroup': [],
        'wars': [],
        'playerStats': player_stats,
        'totalRounds': 7,
        'roundsCompleted': len(season_wars[season]),
        'totalStars': total_stars,
        'totalAttacks': total_attacks_count,
        'threeStarRate': (total_three_stars / total_attacks_count * 100) if total_attacks_count > 0 else 0,
        'averageStars': total_stars / total_attacks_count if total_attacks_count > 0 else 0,
    })

# Sort by season descending (most recent first)
cwl_seasons_export.sort(key=lambda x: x['season'], reverse=True)

# Update dashboard data
dashboard_data['cwlSeasons'] = cwl_seasons_export

# Save updated data
with open('coc-dashboard/public/clan_data.json', 'w', encoding='utf-8') as f:
    json.dump(dashboard_data, f, indent=2, ensure_ascii=False)

print(f'✅ Added {len(cwl_seasons_export)} CWL seasons to dashboard data')
for s in cwl_seasons_export:
    print(f'   - {s["season"]}: {len(s["playerStats"])} players, {s["totalAttacks"]} attacks, {s["totalStars"]} stars')
