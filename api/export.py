"""Export of clan_data.json for the dashboards."""

import json
import os
from collections import defaultdict

from config import BENCHMARKS_FILE, DASHBOARD_DATA_FILE
from history import utc_now
from ranked import load_snapshots, load_th_table, ranked_history_export
from rush import get_max_level_for_th, rush_method


def export_dashboard_data(clan: dict, players_data: list, rush_reports: list, 
                          historical_data: dict, warlog: list, current_war: dict,
                          capital_raids: list, gold_pass: dict, cwl_group: dict):
    """Export comprehensive data to JSON for the Next.js dashboard."""
    print("\n⏳ Exporting data for Next.js dashboard...")
    
    # Build comprehensive player data with rush info
    players_export = []
    for player in players_data:
        # Find matching rush report
        rush_report = next((r for r in rush_reports if r.get('player_tag') == player.get('tag')), {})
        
        # Get historical stats for this player
        hist_player = historical_data.get('players', {}).get(player.get('tag'), {})
        
        # Extract hero data with correct max levels for player's TH
        th_level = player.get('townHallLevel', 1)
        heroes = []
        for hero in player.get('heroes', []):
            if hero.get('village') == 'home':
                hero_name = hero.get('name')
                # Get max level for this hero at player's current TH from our defined data
                max_at_th = get_max_level_for_th(hero_name, th_level, "hero")
                heroes.append({
                    'name': hero_name,
                    'level': hero.get('level'),
                    'maxLevel': max_at_th if max_at_th else hero.get('maxLevel'),
                })
        
        # Extract key troops with correct max levels for player's TH
        troops = []
        for troop in player.get('troops', []):
            if troop.get('village') == 'home':
                troop_name = troop.get('name')
                # Get max level for this troop at player's current TH from our defined data
                max_at_th = get_max_level_for_th(troop_name, th_level, "troop")
                troops.append({
                    'name': troop_name,
                    'level': troop.get('level'),
                    # Use our defined max if available, otherwise fall back to API value
                    'maxLevel': max_at_th if max_at_th else troop.get('maxLevel'),
                })
        
        # Extract spells with correct max levels for player's TH
        spells = []
        for spell in player.get('spells', []):
            if spell.get('village') == 'home':
                spell_name = spell.get('name')
                # Get max level for this spell at player's current TH from our defined data
                max_at_th = get_max_level_for_th(spell_name, th_level, "spell")
                spells.append({
                    'name': spell_name,
                    'level': spell.get('level'),
                    # Use our defined max if available, otherwise fall back to API value
                    'maxLevel': max_at_th if max_at_th else spell.get('maxLevel'),
                })
        
        # Extract hero equipment
        hero_equipment = []
        for equip in player.get('heroEquipment', []):
            hero_equipment.append({
                'name': equip.get('name'),
                'level': equip.get('level'),
                'maxLevel': equip.get('maxLevel'),
                'village': equip.get('village'),
            })
        
        player_export = {
            'tag': player.get('tag'),
            'name': player.get('name'),
            'townHallLevel': player.get('townHallLevel'),
            'townHallWeaponLevel': player.get('townHallWeaponLevel'),
            'expLevel': player.get('expLevel'),
            'trophies': player.get('trophies'),
            'bestTrophies': player.get('bestTrophies'),
            'warStars': player.get('warStars'),
            'attackWins': player.get('attackWins'),
            'defenseWins': player.get('defenseWins'),
            'builderHallLevel': player.get('builderHallLevel'),
            'builderBaseTrophies': player.get('builderBaseTrophies'),
            'bestBuilderBaseTrophies': player.get('bestBuilderBaseTrophies'),
            'role': player.get('role'),
            'warPreference': player.get('warPreference'),
            'donations': player.get('donations'),
            'donationsReceived': player.get('donationsReceived'),
            'clanCapitalContributions': player.get('clanCapitalContributions'),
            'clan': player.get('clan'),
            'league': player.get('league'),
            # Ranked battles league (since Oct 2025); 'league' is no longer filled
            'leagueTier': player.get('leagueTier'),
            'builderBaseLeague': player.get('builderBaseLeague'),
            'achievements': player.get('achievements', []),
            'labels': player.get('labels', []),
            'heroes': heroes,
            'troops': troops,
            'spells': spells,
            'heroEquipment': hero_equipment,
            # Rush analysis
            'rushAnalysis': {
                'isRushed': rush_report.get('is_rushed', False),
                'rushScore': rush_report.get('rush_score', 0),
                'rushPercentage': rush_report.get('rush_percentage', 0),
                'status': rush_report.get('status', 'Unknown'),
                'heroScore': rush_report.get('hero_score', 0),
                'troopScore': rush_report.get('troop_score', 0),
                'spellScore': rush_report.get('spell_score', 0),
                'totalMissingHeroLevels': rush_report.get('total_missing_hero_levels', 0),
                'rushedHeroes': rush_report.get('rushed_heroes', []),
                'rushedTroops': rush_report.get('rushed_troops', []),
                'rushedSpells': rush_report.get('rushed_spells', []),
            },
            # Historical war stats
            'warStats': {
                'totalAttacks': hist_player.get('total_attacks', 0),
                'totalStars': hist_player.get('total_stars', 0),
                'totalDestruction': hist_player.get('total_destruction', 0),
                'threeStars': hist_player.get('three_stars', 0),
                'twoStars': hist_player.get('two_stars', 0),
                'oneStars': hist_player.get('one_star', 0),
                'zeroStars': hist_player.get('zero_stars', 0),
                'warsParticipated': hist_player.get('wars_participated', 0),
            }
        }
        players_export.append(player_export)
    
    # Process war log
    warlog_export = []
    if warlog:
        for war in warlog[:50]:  # Last 50 wars
            warlog_export.append({
                'result': war.get('result'),
                'endTime': war.get('endTime'),
                'teamSize': war.get('teamSize'),
                'attacksPerMember': war.get('attacksPerMember'),
                'clan': {
                    'tag': war.get('clan', {}).get('tag'),
                    'name': war.get('clan', {}).get('name'),
                    'stars': war.get('clan', {}).get('stars'),
                    'destructionPercentage': war.get('clan', {}).get('destructionPercentage'),
                    'expEarned': war.get('clan', {}).get('expEarned'),
                },
                'opponent': {
                    'tag': war.get('opponent', {}).get('tag'),
                    'name': war.get('opponent', {}).get('name'),
                    'stars': war.get('opponent', {}).get('stars'),
                    'destructionPercentage': war.get('opponent', {}).get('destructionPercentage'),
                }
            })
    
    # Process current war
    current_war_export = None
    if current_war and current_war.get('state') not in ['notInWar', None]:
        current_war_export = {
            'state': current_war.get('state'),
            'teamSize': current_war.get('teamSize'),
            'attacksPerMember': current_war.get('attacksPerMember'),
            'preparationStartTime': current_war.get('preparationStartTime'),
            'startTime': current_war.get('startTime'),
            'endTime': current_war.get('endTime'),
            'clan': current_war.get('clan'),
            'opponent': current_war.get('opponent'),
        }
    
    # Process capital raids
    capital_raids_export = []
    if capital_raids:
        for raid in capital_raids[:10]:
            capital_raids_export.append({
                'state': raid.get('state'),
                'startTime': raid.get('startTime'),
                'endTime': raid.get('endTime'),
                'capitalTotalLoot': raid.get('capitalTotalLoot'),
                'raidsCompleted': raid.get('raidsCompleted'),
                'totalAttacks': raid.get('totalAttacks'),
                'enemyDistrictsDestroyed': raid.get('enemyDistrictsDestroyed'),
                'offensiveReward': raid.get('offensiveReward'),
                'defensiveReward': raid.get('defensiveReward'),
                'members': raid.get('members', []),
                'attackLog': raid.get('attackLog', []),
                'defenseLog': raid.get('defenseLog', []),
            })
    
    # Calculate clan statistics
    th_distribution = defaultdict(int)
    role_distribution = defaultdict(int)
    league_distribution = defaultdict(int)
    rush_distribution = defaultdict(int)
    
    for player in players_data:
        th_distribution[player.get('townHallLevel', 0)] += 1
        role_distribution[player.get('role', 'unknown')] += 1
        league = player.get('leagueTier') or player.get('league')
        league_name = league.get('name', 'Unranked') if league else 'Unranked'
        league_distribution[league_name] += 1
    
    for report in rush_reports:
        status = report.get('status', 'Unknown')
        if 'Maxed' in status:
            rush_distribution['Maxed'] += 1
        elif 'Slightly' in status:
            rush_distribution['Slightly Behind'] += 1
        elif 'Moderately' in status:
            rush_distribution['Moderately Rushed'] += 1
        elif 'Severely' in status:
            rush_distribution['Severely Rushed'] += 1
        elif 'Rushed' in status:
            rush_distribution['Rushed'] += 1
        else:
            rush_distribution['Other'] += 1
    
    # Build final export object
    dashboard_data = {
        'lastUpdated': utc_now(),
        'clan': {
            'tag': clan.get('tag'),
            'name': clan.get('name'),
            'description': clan.get('description'),
            'type': clan.get('type'),
            'location': clan.get('location'),
            'chatLanguage': clan.get('chatLanguage'),
            'clanLevel': clan.get('clanLevel'),
            'clanPoints': clan.get('clanPoints'),
            'clanBuilderBasePoints': clan.get('clanBuilderBasePoints'),
            'clanCapitalPoints': clan.get('clanCapitalPoints'),
            'capitalLeague': clan.get('capitalLeague'),
            'requiredTrophies': clan.get('requiredTrophies'),
            'warFrequency': clan.get('warFrequency'),
            'warWinStreak': clan.get('warWinStreak'),
            'warWins': clan.get('warWins'),
            'warTies': clan.get('warTies'),
            'warLosses': clan.get('warLosses'),
            'isWarLogPublic': clan.get('isWarLogPublic'),
            'warLeague': clan.get('warLeague'),
            'members': clan.get('members'),
            'labels': clan.get('labels', []),
            'clanCapital': clan.get('clanCapital'),
            'badgeUrls': clan.get('badgeUrls'),
        },
        'players': players_export,
        'warLog': warlog_export,
        'currentWar': current_war_export,
        'capitalRaids': capital_raids_export,
        'goldPass': gold_pass,
        'cwlGroup': cwl_group,
        'historicalData': {
            'cwlSeasons': historical_data.get('cwl_seasons', {}),
            'lastUpdated': historical_data.get('last_updated'),
        },
        'rushMethod': rush_method(),
        # Weekly ranked league per member and the minimum league we expect per
        # Town Hall, for the Players tab (written by the weekly ranked workflow)
        'rankedHistory': ranked_history_export(load_snapshots()),
        'rankedBenchmarks': {str(th): league for th, league in sorted(load_th_table(BENCHMARKS_FILE).items())},
        'statistics': {
            'thDistribution': dict(th_distribution),
            'roleDistribution': dict(role_distribution),
            'leagueDistribution': dict(league_distribution),
            'rushDistribution': dict(rush_distribution),
            'totalWarStars': sum(p.get('warStars', 0) for p in players_data),
            'totalDonations': sum(p.get('donations', 0) for p in players_data),
            'totalCapitalContributions': sum(p.get('clanCapitalContributions', 0) for p in players_data),
            'averageTrophies': sum(p.get('trophies', 0) for p in players_data) / len(players_data) if players_data else 0,
            'rushedCount': sum(1 for r in rush_reports if r.get('is_rushed', False)),
            'averageRushScore': sum(r.get('rush_score', 0) for r in rush_reports) / len(rush_reports) if rush_reports else 0,
        }
    }
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(DASHBOARD_DATA_FILE), exist_ok=True)
    
    # Save to JSON file
    with open(DASHBOARD_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Dashboard data exported to: {DASHBOARD_DATA_FILE}")
    return dashboard_data
