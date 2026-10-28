"""
Clash of Clans Clan Analyzer
Fetches clan, player, war and capital data, scores rushed players and
exports clan_data.json for the dashboards. Entry point: python api/clan_analyzer.py
"""

import sys
import time
from collections import defaultdict
from datetime import datetime

from coc_api import (get_capital_raid_seasons, get_clan_info, get_clan_members, get_clan_warlog,
                     get_current_war, get_cwl_group, get_cwl_war, get_gold_pass_season,
                     get_player_info)
from config import API_TOKEN, CLAN_TAG, DASHBOARD_DATA_FILE
from export import export_dashboard_data
from history import (generate_war_id, load_historical_data, parse_coc_time,
                     save_historical_data, update_player_historical_stats, utc_now)
from rush import generate_rush_report

# A few players may fail even after retries; more than this aborts the run
# instead of publishing a half-empty roster.
MAX_MISSING_PLAYERS = 3



def print_separator(title: str = "", char: str = "=", length: int = 80):
    """Print a separator line."""
    if title:
        padding = (length - len(title) - 2) // 2
        print(f"\n{char * padding} {title} {char * padding}")
    else:
        print(char * length)


def analyze_clan_rush(players_data: list) -> list:
    """Analyze rush status for all clan members."""
    print_separator("RUSH ANALYSIS")
    
    rush_reports = []
    
    for player in players_data:
        report = generate_rush_report(player)
        report["player_name"] = player.get('name', 'Unknown')
        report["player_tag"] = player.get('tag', '')
        report["th_level"] = player.get('townHallLevel', 0)
        rush_reports.append(report)
    
    # Sort by rush score (most rushed first)
    rush_reports.sort(key=lambda x: -x["rush_score"])
    
    # Print summary
    rushed_count = sum(1 for r in rush_reports if r["is_rushed"])
    total = len(rush_reports)
    
    print(f"\n📊 CLAN RUSH OVERVIEW:")
    print(f"   Total Members: {total}")
    print(f"   Rushed Players: {rushed_count} ({rushed_count/total*100:.1f}%)")
    print(f"   Not Rushed: {total - rushed_count} ({(total-rushed_count)/total*100:.1f}%)")
    
    # Status distribution
    status_counts = defaultdict(int)
    for r in rush_reports:
        status_counts[r["status"]] += 1
    
    print(f"\n📈 STATUS DISTRIBUTION:")
    for status, count in sorted(status_counts.items(), key=lambda x: -x[1]):
        print(f"   {status}: {count}")
    
    # Print detailed table
    print(f"\n{'#':<3} {'Player':<18} {'TH':<4} {'Score':<8} {'Heroes':<8} {'Status':<25}")
    print(f"{'-'*75}")
    
    for i, report in enumerate(rush_reports, 1):
        name = report["player_name"][:17]
        th = report["th_level"]
        score = report["rush_score"]
        hero_missing = report["total_missing_hero_levels"]
        status = report["status"]
        
        print(f"{i:<3} {name:<18} {th:<4} {score:<8.1f} -{hero_missing:<7} {status}")
    
    # Most rushed heroes
    print(f"\n⚠️  PLAYERS WITH MOST RUSHED HEROES:")
    hero_rushed = [(r["player_name"], r["th_level"], r["total_missing_hero_levels"], r["rushed_heroes"]) 
                   for r in rush_reports if r["total_missing_hero_levels"] > 5]
    hero_rushed.sort(key=lambda x: -x[2])
    
    for name, th, missing, heroes in hero_rushed[:10]:
        hero_details = ", ".join([f"{h['name'][:2]}: {h['current']}/{h['target']}" for h in heroes[:4]])
        print(f"   • {name} (TH{th}): -{missing} levels [{hero_details}]")
    
    return rush_reports


def analyze_clan_info(clan: dict):
    """Analyze and display clan information."""
    print_separator("CLAN INFORMATION")
    
    print(f"\n🏰 Clan Name: {clan.get('name', 'N/A')}")
    print(f"🏷️  Clan Tag: {clan.get('tag', 'N/A')}")
    print(f"📝 Description: {clan.get('description', 'N/A')}")
    print(f"🌍 Location: {clan.get('location', {}).get('name', 'N/A')}")
    print(f"🗣️  Language: {clan.get('chatLanguage', {}).get('name', 'N/A')}")
    print(f"📊 Clan Level: {clan.get('clanLevel', 'N/A')}")
    print(f"🏆 Clan Points: {clan.get('clanPoints', 'N/A'):,}")
    print(f"⚔️  Clan Builder Base Points: {clan.get('clanBuilderBasePoints', 'N/A'):,}")
    print(f"🏅 Clan Capital Points: {clan.get('clanCapitalPoints', 'N/A'):,}")
    print(f"👥 Members: {clan.get('members', 'N/A')}/50")
    print(f"🔒 Type: {clan.get('type', 'N/A')}")
    print(f"⚔️  War Frequency: {clan.get('warFrequency', 'N/A')}")
    print(f"🏆 War Win Streak: {clan.get('warWinStreak', 'N/A')}")
    print(f"✅ War Wins: {clan.get('warWins', 'N/A')}")
    print(f"➖ War Ties: {clan.get('warTies', 'N/A')}")
    print(f"❌ War Losses: {clan.get('warLosses', 'N/A')}")
    print(f"⚔️  War League: {clan.get('warLeague', {}).get('name', 'N/A')}")
    print(f"🏛️  Capital League: {clan.get('capitalLeague', {}).get('name', 'N/A')}")
    
    # War statistics
    total_wars = clan.get('warWins', 0) + clan.get('warTies', 0) + clan.get('warLosses', 0)
    if total_wars > 0:
        win_rate = (clan.get('warWins', 0) / total_wars) * 100
        print(f"\n📈 War Win Rate: {win_rate:.1f}%")
    
    # Clan Labels
    labels = clan.get('labels', [])
    if labels:
        print(f"\n🏷️  Clan Labels:")
        for label in labels:
            print(f"   • {label.get('name', 'N/A')}")
    
    # Clan Capital
    clan_capital = clan.get('clanCapital', {})
    if clan_capital:
        print(f"\n🏛️  CLAN CAPITAL:")
        print(f"   Capital Hall Level: {clan_capital.get('capitalHallLevel', 'N/A')}")
        districts = clan_capital.get('districts', [])
        if districts:
            print(f"   Districts ({len(districts)}):")
            for district in districts:
                print(f"   • {district.get('name', 'N/A')} (Level {district.get('districtHallLevel', 'N/A')})")


def analyze_members(members: list, players_data: list):
    """Analyze clan members."""
    print_separator("MEMBER ANALYSIS")
    
    # Role distribution
    roles = defaultdict(int)
    for member in members:
        roles[member.get('role', 'unknown')] += 1
    
    print(f"\n👥 ROLE DISTRIBUTION:")
    role_emojis = {'leader': '👑', 'coLeader': '⭐', 'admin': '🛡️', 'member': '👤'}
    for role, count in sorted(roles.items(), key=lambda x: -x[1]):
        emoji = role_emojis.get(role, '❓')
        print(f"   {emoji} {role}: {count}")
    
    # Trophy analysis
    trophies = [m.get('trophies', 0) for m in members]
    print(f"\n🏆 TROPHY STATISTICS:")
    print(f"   Total Clan Trophies: {sum(trophies):,}")
    print(f"   Average Trophies: {sum(trophies)/len(trophies):,.0f}")
    print(f"   Highest: {max(trophies):,}")
    print(f"   Lowest: {min(trophies):,}")
    
    # Experience level analysis
    levels = [m.get('expLevel', 0) for m in members]
    print(f"\n📊 EXPERIENCE LEVEL STATISTICS:")
    print(f"   Average Level: {sum(levels)/len(levels):.1f}")
    print(f"   Highest: {max(levels)}")
    print(f"   Lowest: {min(levels)}")
    
    # League distribution
    leagues = defaultdict(int)
    for member in members:
        league = member.get('league', {}).get('name', 'Unranked')
        leagues[league] += 1
    
    print(f"\n🎖️  LEAGUE DISTRIBUTION:")
    for league, count in sorted(leagues.items(), key=lambda x: -x[1]):
        print(f"   • {league}: {count} members")
    
    # Donations analysis
    donations = [(m.get('name'), m.get('donations', 0), m.get('donationsReceived', 0)) for m in members]
    donations_sorted = sorted(donations, key=lambda x: -x[1])
    
    print(f"\n🎁 TOP 10 DONATORS:")
    for i, (name, donated, received) in enumerate(donations_sorted[:10], 1):
        ratio = donated / received if received > 0 else donated
        print(f"   {i}. {name}: {donated:,} donated | {received:,} received | Ratio: {ratio:.2f}")
    
    total_donations = sum(d[1] for d in donations)
    total_received = sum(d[2] for d in donations)
    print(f"\n   📊 Clan Total Donations: {total_donations:,}")
    print(f"   📊 Clan Total Received: {total_received:,}")


def analyze_player_details(players_data: list):
    """Analyze detailed player information."""
    print_separator("DETAILED PLAYER ANALYSIS")
    
    # Town Hall distribution
    th_distribution = defaultdict(int)
    for player in players_data:
        th_level = player.get('townHallLevel', 0)
        th_distribution[th_level] += 1
    
    print(f"\n🏠 TOWN HALL DISTRIBUTION:")
    for th, count in sorted(th_distribution.items(), reverse=True):
        bar = "█" * count
        print(f"   TH{th:2d}: {bar} ({count})")
    
    # Builder Hall distribution
    bh_distribution = defaultdict(int)
    for player in players_data:
        bh_level = player.get('builderHallLevel', 0)
        if bh_level > 0:
            bh_distribution[bh_level] += 1
    
    if bh_distribution:
        print(f"\n🏗️  BUILDER HALL DISTRIBUTION:")
        for bh, count in sorted(bh_distribution.items(), reverse=True):
            bar = "█" * count
            print(f"   BH{bh:2d}: {bar} ({count})")
    
    # Hero analysis
    print(f"\n⚔️  HERO ANALYSIS:")
    hero_stats = defaultdict(list)
    
    for player in players_data:
        heroes = player.get('heroes', [])
        for hero in heroes:
            hero_name = hero.get('name', 'Unknown')
            hero_level = hero.get('level', 0)
            hero_max = hero.get('maxLevel', 0)
            if hero.get('village', '') == 'home':
                hero_stats[hero_name].append((player.get('name'), hero_level, hero_max))
    
    for hero_name, data in hero_stats.items():
        levels = [d[1] for d in data]
        if levels:
            avg = sum(levels) / len(levels)
            max_level = max(levels)
            min_level = min(levels)
            print(f"\n   🦸 {hero_name}:")
            print(f"      Players with hero: {len(levels)}")
            print(f"      Average Level: {avg:.1f}")
            print(f"      Highest: {max_level}")
            print(f"      Lowest: {min_level}")
    
    # Top players by hero levels
    print(f"\n🏆 TOP 10 PLAYERS BY COMBINED HERO LEVELS:")
    player_hero_totals = []
    for player in players_data:
        heroes = player.get('heroes', [])
        home_heroes = [h for h in heroes if h.get('village', '') == 'home']
        total = sum(h.get('level', 0) for h in home_heroes)
        player_hero_totals.append((player.get('name'), total, len(home_heroes)))
    
    player_hero_totals.sort(key=lambda x: -x[1])
    for i, (name, total, count) in enumerate(player_hero_totals[:10], 1):
        print(f"   {i}. {name}: {total} total ({count} heroes)")
    
    # Troop/Spell levels analysis
    print(f"\n🔬 TROOP & SPELL STATISTICS:")
    max_troops_players = []
    for player in players_data:
        troops = player.get('troops', [])
        home_troops = [t for t in troops if t.get('village', '') == 'home']
        total_levels = sum(t.get('level', 0) for t in home_troops)
        max_troops_players.append((player.get('name'), total_levels, len(home_troops)))
    
    max_troops_players.sort(key=lambda x: -x[1])
    print(f"\n   🏆 TOP 10 BY TROOP LEVELS:")
    for i, (name, total, count) in enumerate(max_troops_players[:10], 1):
        print(f"   {i}. {name}: {total} total troop levels")
    
    # War Stars analysis
    print(f"\n⭐ WAR STARS ANALYSIS:")
    war_stars = [(p.get('name'), p.get('warStars', 0)) for p in players_data]
    war_stars.sort(key=lambda x: -x[1])
    
    total_war_stars = sum(w[1] for w in war_stars)
    avg_war_stars = total_war_stars / len(war_stars) if war_stars else 0
    
    print(f"   Total Clan War Stars: {total_war_stars:,}")
    print(f"   Average War Stars: {avg_war_stars:.0f}")
    
    print(f"\n   🏆 TOP 10 BY WAR STARS:")
    for i, (name, stars) in enumerate(war_stars[:10], 1):
        print(f"   {i}. {name}: {stars:,} ⭐")
    
    # Attack/Defense wins
    print(f"\n⚔️  ATTACK & DEFENSE STATISTICS:")
    attack_stats = [(p.get('name'), p.get('attackWins', 0), p.get('defenseWins', 0)) for p in players_data]
    attack_stats.sort(key=lambda x: -x[1])
    
    print(f"\n   🗡️  TOP 10 BY ATTACK WINS:")
    for i, (name, attacks, _) in enumerate(attack_stats[:10], 1):
        print(f"   {i}. {name}: {attacks:,} wins")
    
    defense_stats = sorted(attack_stats, key=lambda x: -x[2])
    print(f"\n   🛡️  TOP 10 BY DEFENSE WINS:")
    for i, (name, _, defenses) in enumerate(defense_stats[:10], 1):
        print(f"   {i}. {name}: {defenses:,} wins")
    
    # Clan Capital contributions
    print(f"\n🏛️  CLAN CAPITAL CONTRIBUTIONS:")
    capital_contributions = [(p.get('name'), p.get('clanCapitalContributions', 0)) for p in players_data]
    capital_contributions.sort(key=lambda x: -x[1])
    
    total_contributions = sum(c[1] for c in capital_contributions)
    print(f"   Total Clan Contributions: {total_contributions:,}")
    
    print(f"\n   🏆 TOP 10 CONTRIBUTORS:")
    for i, (name, contributions) in enumerate(capital_contributions[:10], 1):
        print(f"   {i}. {name}: {contributions:,}")


def analyze_warlog(warlog: list):
    """Analyze war log."""
    print_separator("WAR LOG ANALYSIS")
    
    if not warlog:
        print("\n⚠️  War log is not public or no wars found.")
        return
    
    print(f"\n📜 Total Wars in Log: {len(warlog)}")
    
    # Win/Loss/Tie breakdown
    results = defaultdict(int)
    for war in warlog:
        results[war.get('result', 'unknown')] += 1
    
    print(f"\n📊 WAR RESULTS:")
    result_emojis = {'win': '✅', 'lose': '❌', 'tie': '➖'}
    for result, count in results.items():
        emoji = result_emojis.get(result, '❓')
        percentage = (count / len(warlog)) * 100
        result_name = result.capitalize() if result else 'Unknown'
        print(f"   {emoji} {result_name}: {count} ({percentage:.1f}%)")
    
    # Stars analysis
    total_stars_for = 0
    total_stars_against = 0
    total_destruction_for = 0
    total_destruction_against = 0
    
    for war in warlog:
        clan_data = war.get('clan', {})
        opponent_data = war.get('opponent', {})
        
        total_stars_for += clan_data.get('stars', 0)
        total_stars_against += opponent_data.get('stars', 0)
        total_destruction_for += clan_data.get('destructionPercentage', 0)
        total_destruction_against += opponent_data.get('destructionPercentage', 0)
    
    print(f"\n⭐ STAR STATISTICS:")
    print(f"   Total Stars Earned: {total_stars_for}")
    print(f"   Total Stars Conceded: {total_stars_against}")
    print(f"   Star Difference: {total_stars_for - total_stars_against:+d}")
    print(f"   Average Stars per War: {total_stars_for / len(warlog):.1f}")
    
    print(f"\n💥 DESTRUCTION STATISTICS:")
    print(f"   Average Destruction Dealt: {total_destruction_for / len(warlog):.1f}%")
    print(f"   Average Destruction Received: {total_destruction_against / len(warlog):.1f}%")
    
    # War size analysis
    war_sizes = defaultdict(int)
    for war in warlog:
        size = war.get('teamSize', 0)
        war_sizes[size] += 1
    
    print(f"\n👥 WAR SIZE DISTRIBUTION:")
    for size, count in sorted(war_sizes.items(), reverse=True):
        print(f"   {size}v{size}: {count} wars")
    
    # Recent wars detail
    print(f"\n📋 RECENT 10 WARS:")
    print(f"   {'Opponent':<25} {'Result':<8} {'Stars':<10} {'Destruction':<15}")
    print(f"   {'-'*60}")
    
    for war in warlog[:10]:
        opponent_name = war.get('opponent', {}).get('name', 'Unknown')[:24]
        result = war.get('result') or 'N/A'  # CWL entries in the war log have result: null
        clan_stars = war.get('clan', {}).get('stars', 0)
        opp_stars = war.get('opponent', {}).get('stars', 0)
        clan_dest = war.get('clan', {}).get('destructionPercentage', 0)
        opp_dest = war.get('opponent', {}).get('destructionPercentage', 0)
        
        result_emoji = result_emojis.get(result, '❓')
        print(f"   {opponent_name:<25} {result_emoji} {result:<5} {clan_stars}-{opp_stars:<6} {clan_dest:.1f}% vs {opp_dest:.1f}%")


def analyze_current_war(war: dict):
    """Analyze current war if active."""
    print_separator("CURRENT WAR")
    
    state = war.get('state', 'notInWar')
    
    if state == 'notInWar':
        print("\n⚠️  Clan is not currently in a war.")
        return None
    
    print(f"\n⚔️  War State: {state}")
    
    clan = war.get('clan', {})
    opponent = war.get('opponent', {})
    
    print(f"\n🏰 {clan.get('name', 'Your Clan')} vs 🏰 {opponent.get('name', 'Opponent')}")
    print(f"   Team Size: {war.get('teamSize', 'N/A')}v{war.get('teamSize', 'N/A')}")
    
    if state in ['inWar', 'warEnded', 'preparation']:
        if state != 'preparation':
            print(f"\n📊 CURRENT SCORE:")
            print(f"   Your Clan: {clan.get('stars', 0)} ⭐ ({clan.get('destructionPercentage', 0):.1f}%)")
            print(f"   Opponent:  {opponent.get('stars', 0)} ⭐ ({opponent.get('destructionPercentage', 0):.1f}%)")
            print(f"   Attacks Used: {clan.get('attacks', 0)}/{war.get('teamSize', 0) * 2}")
        
        # Return attack data for further analysis
        return analyze_war_attacks(war, "Current War")
    
    return None


def analyze_war_attacks(war: dict, war_label: str = "War") -> dict:
    """Analyze individual attacks in a war and return player stats."""
    clan_members = war.get('clan', {}).get('members', [])
    opponent_members = war.get('opponent', {}).get('members', [])
    
    if not clan_members:
        return {}
    
    # Build opponent lookup by tag
    opponent_lookup = {m.get('tag'): m for m in opponent_members}
    
    print(f"\n{'='*80}")
    print(f"   📊 DETAILED ATTACK ANALYSIS - {war_label}")
    print(f"{'='*80}")
    
    # Collect all attack data
    player_stats = {}
    all_attacks = []
    
    members_sorted = sorted(clan_members, key=lambda x: x.get('mapPosition', 0))
    
    print(f"\n{'#':<4} {'Attacker':<16} {'TH':<4} {'Target':<4} {'⭐':<3} {'%':<6} {'New⭐':<5} {'Hit':<8}")
    print(f"{'-'*60}")
    
    for member in members_sorted:
        name = member.get('name', 'Unknown')
        tag = member.get('tag', '')
        th = member.get('townhallLevel', 0)
        map_pos = member.get('mapPosition', 0)
        attacks = member.get('attacks', [])
        
        # Initialize player stats
        if tag not in player_stats:
            player_stats[tag] = {
                'name': name,
                'tag': tag,
                'th': th,
                'attacks': [],
                'total_stars': 0,
                'total_destruction': 0,
                'new_stars': 0,
                'attacks_used': 0,
                'missed_attacks': 0,
                'three_stars': 0,
                'two_stars': 0,
                'one_star': 0,
                'zero_stars': 0,
                'hit_up': 0,
                'hit_same': 0,
                'hit_down': 0,
            }
        
        if attacks:
            for attack in attacks:
                defender_tag = attack.get('defenderTag', '')
                defender = opponent_lookup.get(defender_tag, {})
                defender_th = defender.get('townhallLevel', 0)
                defender_pos = defender.get('mapPosition', 0)
                stars = attack.get('stars', 0)
                destruction = attack.get('destructionPercentage', 0)
                
                # Calculate new stars (stars that weren't already earned)
                # This info is in the attack data
                new_stars = stars  # API doesn't always provide this clearly
                
                # Determine hit direction
                if defender_th > th:
                    hit_type = "↑ UP"
                    player_stats[tag]['hit_up'] += 1
                elif defender_th < th:
                    hit_type = "↓ DOWN"
                    player_stats[tag]['hit_down'] += 1
                else:
                    hit_type = "= SAME"
                    player_stats[tag]['hit_same'] += 1
                
                # Update stats
                player_stats[tag]['attacks'].append({
                    'stars': stars,
                    'destruction': destruction,
                    'defender_th': defender_th,
                    'defender_pos': defender_pos,
                    'hit_type': hit_type
                })
                player_stats[tag]['total_stars'] += stars
                player_stats[tag]['total_destruction'] += destruction
                player_stats[tag]['attacks_used'] += 1
                
                if stars == 3:
                    player_stats[tag]['three_stars'] += 1
                elif stars == 2:
                    player_stats[tag]['two_stars'] += 1
                elif stars == 1:
                    player_stats[tag]['one_star'] += 1
                else:
                    player_stats[tag]['zero_stars'] += 1
                
                all_attacks.append({
                    'attacker': name,
                    'attacker_th': th,
                    'attacker_pos': map_pos,
                    'defender_pos': defender_pos,
                    'defender_th': defender_th,
                    'stars': stars,
                    'destruction': destruction,
                    'hit_type': hit_type
                })
                
                print(f"{map_pos:<4} {name[:15]:<16} TH{th:<2} → #{defender_pos:<3} {stars}⭐   {destruction:>5.1f}%  {hit_type}")
        else:
            # No attacks made
            player_stats[tag]['missed_attacks'] = 2
            print(f"{map_pos:<4} {name[:15]:<16} TH{th:<2}   ❌ NO ATTACKS USED")
    
    # Print summary statistics
    print(f"\n{'='*60}")
    print(f"   📈 ATTACK SUMMARY - {war_label}")
    print(f"{'='*60}")
    
    total_attacks = len(all_attacks)
    if total_attacks > 0:
        total_stars = sum(a['stars'] for a in all_attacks)
        total_destruction = sum(a['destruction'] for a in all_attacks)
        three_stars = sum(1 for a in all_attacks if a['stars'] == 3)
        two_stars = sum(1 for a in all_attacks if a['stars'] == 2)
        one_star = sum(1 for a in all_attacks if a['stars'] == 1)
        zero_stars = sum(1 for a in all_attacks if a['stars'] == 0)
        
        print(f"\n   Total Attacks: {total_attacks}")
        print(f"   Total Stars: {total_stars} ({total_stars/total_attacks:.2f} avg)")
        print(f"   Total Destruction: {total_destruction:.1f}% ({total_destruction/total_attacks:.1f}% avg)")
        print(f"\n   ⭐⭐⭐ Three Stars: {three_stars} ({three_stars/total_attacks*100:.1f}%)")
        print(f"   ⭐⭐  Two Stars:   {two_stars} ({two_stars/total_attacks*100:.1f}%)")
        print(f"   ⭐   One Star:    {one_star} ({one_star/total_attacks*100:.1f}%)")
        print(f"   ❌   Zero Stars:  {zero_stars} ({zero_stars/total_attacks*100:.1f}%)")
        
        # Hit direction analysis
        hits_up = sum(1 for a in all_attacks if 'UP' in a['hit_type'])
        hits_same = sum(1 for a in all_attacks if 'SAME' in a['hit_type'])
        hits_down = sum(1 for a in all_attacks if 'DOWN' in a['hit_type'])
        
        print(f"\n   📊 HIT DIRECTION:")
        print(f"   ↑ Hit Up (higher TH):   {hits_up} attacks")
        print(f"   = Hit Same (equal TH):  {hits_same} attacks")
        print(f"   ↓ Hit Down (lower TH):  {hits_down} attacks")
    
    # Players who missed attacks
    missed = [(p['name'], 2 - p['attacks_used']) for tag, p in player_stats.items() if p['attacks_used'] < 2]
    if missed:
        print(f"\n   ⚠️  MISSED ATTACKS:")
        for name, missed_count in missed:
            print(f"   • {name}: {missed_count} attack(s) not used")
    
    return player_stats


def analyze_cwl(clan_tag: str, historical_data: dict) -> dict:
    """Analyze Clan War League performance."""
    print_separator("CLAN WAR LEAGUE ANALYSIS")
    
    print("\n⏳ Fetching CWL group information...")
    cwl_group = get_cwl_group(clan_tag)
    
    if not cwl_group:
        print("\n⚠️  No active CWL found or CWL data not available.")
        print("   CWL data is only available during and shortly after CWL week.")
        return historical_data
    
    state = cwl_group.get('state', 'unknown')
    season = cwl_group.get('season', 'N/A')
    
    # Check if this season was already fully recorded
    season_key = f"cwl_{season}"
    if season_key in historical_data.get("cwl_seasons", {}) and historical_data["cwl_seasons"][season_key].get("complete", False):
        print(f"\n✅ CWL Season {season} already recorded in history.")
        # Still show the data but don't re-record
    
    print(f"\n🏆 CWL Season: {season}")
    print(f"📊 State: {state}")
    
    # Get all clans in the group
    clans = cwl_group.get('clans', [])
    print(f"\n👥 Clans in Group ({len(clans)}):")
    for clan in clans:
        print(f"   • {clan.get('name', 'Unknown')} ({clan.get('tag', 'N/A')})")
    
    # Get all rounds
    rounds = cwl_group.get('rounds', [])
    print(f"\n📅 Rounds: {len(rounds)}")
    
    # Aggregate player stats across all CWL wars
    all_player_stats = defaultdict(lambda: {
        'name': '',
        'tag': '',
        'th': 0,
        'total_stars': 0,
        'total_destruction': 0,
        'attacks_used': 0,
        'three_stars': 0,
        'two_stars': 0,
        'one_star': 0,
        'zero_stars': 0,
        'wars_participated': 0,
        'hit_up': 0,
        'hit_same': 0,
        'hit_down': 0,
    })
    
    wars_analyzed = 0
    our_clan_tag = clan_tag
    
    # Fetch and analyze each war
    for round_num, round_data in enumerate(rounds, 1):
        war_tags = round_data.get('warTags', [])
        
        for war_tag in war_tags:
            if war_tag == '#0':  # Placeholder for unscheduled wars
                continue
            
            print(f"\n⏳ Fetching CWL Round {round_num} war...", end='\r')
            war = get_cwl_war(war_tag)
            
            if not war:
                continue
            
            # Check if our clan is in this war
            clan_data = war.get('clan', {})
            opponent_data = war.get('opponent', {})
            
            our_clan = None
            opponent = None
            
            if clan_data.get('tag') == our_clan_tag:
                our_clan = clan_data
                opponent = opponent_data
            elif opponent_data.get('tag') == our_clan_tag:
                our_clan = opponent_data
                opponent = clan_data
            
            if not our_clan:
                continue
            
            wars_analyzed += 1
            state = war.get('state', 'unknown')
            
            print(f"\n{'='*70}")
            print(f"   🏆 CWL ROUND {round_num}: {our_clan.get('name')} vs {opponent.get('name')}")
            print(f"   State: {state}")
            print(f"{'='*70}")
            
            # Generate unique war ID for this CWL war
            war_id = f"cwl_{season}_round{round_num}_{war_tag}"
            
            if state in ['inWar', 'warEnded']:
                print(f"\n   Score: {our_clan.get('stars', 0)}⭐ vs {opponent.get('stars', 0)}⭐")
                print(f"   Destruction: {our_clan.get('destructionPercentage', 0):.1f}% vs {opponent.get('destructionPercentage', 0):.1f}%")
                
                # Analyze attacks
                war_stats = analyze_war_attacks(
                    {'clan': our_clan, 'opponent': opponent},
                    f"CWL Round {round_num}"
                )
                
                # Aggregate stats and save to historical data
                for tag, stats in war_stats.items():
                    all_player_stats[tag]['name'] = stats['name']
                    all_player_stats[tag]['tag'] = stats['tag']
                    all_player_stats[tag]['th'] = max(all_player_stats[tag]['th'], stats['th'])
                    all_player_stats[tag]['total_stars'] += stats['total_stars']
                    all_player_stats[tag]['total_destruction'] += stats['total_destruction']
                    all_player_stats[tag]['attacks_used'] += stats['attacks_used']
                    all_player_stats[tag]['three_stars'] += stats['three_stars']
                    all_player_stats[tag]['two_stars'] += stats['two_stars']
                    all_player_stats[tag]['one_star'] += stats['one_star']
                    all_player_stats[tag]['zero_stars'] += stats['zero_stars']
                    all_player_stats[tag]['hit_up'] += stats['hit_up']
                    all_player_stats[tag]['hit_same'] += stats['hit_same']
                    all_player_stats[tag]['hit_down'] += stats['hit_down']
                    if stats['attacks_used'] > 0:
                        all_player_stats[tag]['wars_participated'] += 1
                    
                    # Update historical data
                    update_player_historical_stats(
                        historical_data,
                        player_tag=tag,
                        player_name=stats['name'],
                        th_level=stats['th'],
                        attack_data=stats,
                        war_type=f"CWL_{season}",
                        war_id=war_id,
                        war_date=parse_coc_time(war.get('startTime'))
                    )
            elif state == 'preparation':
                print(f"\n   ⏳ War is in preparation phase")
    
    # Store CWL season data
    if wars_analyzed > 0:
        historical_data["cwl_seasons"][season_key] = {
            "season": season,
            "wars_analyzed": wars_analyzed,
            "total_attacks": sum(p['attacks_used'] for p in all_player_stats.values()),
            "total_stars": sum(p['total_stars'] for p in all_player_stats.values()),
            "recorded_date": utc_now(),
            "complete": state == "ended"  # Mark as complete if CWL is over
        }
    
    # Print CWL overall summary
    if wars_analyzed > 0 and all_player_stats:
        print_separator("CWL OVERALL PLAYER PERFORMANCE")
        
        # Sort by total stars, then by destruction
        sorted_players = sorted(
            all_player_stats.values(),
            key=lambda x: (-x['total_stars'], -x['total_destruction'])
        )
        
        print(f"\n{'#':<3} {'Player':<18} {'TH':<4} {'Wars':<5} {'Atks':<5} {'⭐':<5} {'Avg⭐':<6} {'3⭐':<4} {'2⭐':<4} {'Avg%':<7}")
        print(f"{'-'*75}")
        
        for i, player in enumerate(sorted_players, 1):
            if player['attacks_used'] == 0:
                continue
            
            avg_stars = player['total_stars'] / player['attacks_used'] if player['attacks_used'] > 0 else 0
            avg_dest = player['total_destruction'] / player['attacks_used'] if player['attacks_used'] > 0 else 0
            
            print(f"{i:<3} {player['name'][:17]:<18} {player['th']:<4} {player['wars_participated']:<5} "
                  f"{player['attacks_used']:<5} {player['total_stars']:<5} {avg_stars:<6.2f} "
                  f"{player['three_stars']:<4} {player['two_stars']:<4} {avg_dest:<7.1f}")
        
        # Overall CWL stats
        total_attacks = sum(p['attacks_used'] for p in all_player_stats.values())
        total_stars = sum(p['total_stars'] for p in all_player_stats.values())
        total_three_stars = sum(p['three_stars'] for p in all_player_stats.values())
        
        print(f"\n📊 CWL TOTALS:")
        print(f"   Wars Analyzed: {wars_analyzed}")
        print(f"   Total Attacks: {total_attacks}")
        print(f"   Total Stars: {total_stars}")
        print(f"   Three Star Rate: {total_three_stars/total_attacks*100:.1f}%" if total_attacks > 0 else "   N/A")
        print(f"   Average Stars/Attack: {total_stars/total_attacks:.2f}" if total_attacks > 0 else "   N/A")
        
        # Top performers
        print(f"\n🏆 CWL TOP PERFORMERS:")
        
        # Most stars
        top_by_stars = sorted(all_player_stats.values(), key=lambda x: -x['total_stars'])[:5]
        print(f"\n   ⭐ Most Stars:")
        for i, p in enumerate(top_by_stars, 1):
            if p['total_stars'] > 0:
                print(f"   {i}. {p['name']}: {p['total_stars']}⭐ ({p['attacks_used']} attacks)")
        
        # Best average
        attackers = [p for p in all_player_stats.values() if p['attacks_used'] >= 2]
        if attackers:
            top_by_avg = sorted(attackers, key=lambda x: -x['total_stars']/x['attacks_used'])[:5]
            print(f"\n   📈 Best Average (min 2 attacks):")
            for i, p in enumerate(top_by_avg, 1):
                avg = p['total_stars'] / p['attacks_used']
                print(f"   {i}. {p['name']}: {avg:.2f}⭐/atk ({p['attacks_used']} attacks)")
        
        # Most three stars
        top_by_3star = sorted(all_player_stats.values(), key=lambda x: -x['three_stars'])[:5]
        print(f"\n   ⭐⭐⭐ Most Three Stars:")
        for i, p in enumerate(top_by_3star, 1):
            if p['three_stars'] > 0:
                print(f"   {i}. {p['name']}: {p['three_stars']} three-stars")
    
    return historical_data


def print_historical_summary(historical_data: dict):
    """Print a summary of all historical data collected."""
    print_separator("📚 HISTORICAL DATA SUMMARY")
    
    players = historical_data.get("players", {})
    cwl_seasons = historical_data.get("cwl_seasons", {})
    wars = historical_data.get("wars", {})
    
    print(f"\n📊 DATA OVERVIEW:")
    print(f"   Players tracked: {len(players)}")
    print(f"   CWL Seasons recorded: {len(cwl_seasons)}")
    print(f"   Wars recorded: {len(wars)}")
    print(f"   Last updated: {historical_data.get('last_updated', 'Never')}")
    
    if not players:
        print("\n   ℹ️  No historical attack data yet. Run during/after wars to collect data!")
        return
    
    # Calculate all-time stats
    total_attacks = sum(p.get('total_attacks', 0) for p in players.values())
    total_stars = sum(p.get('total_stars', 0) for p in players.values())
    total_three_stars = sum(p.get('three_stars', 0) for p in players.values())
    
    print(f"\n📈 ALL-TIME STATISTICS:")
    print(f"   Total Attacks Recorded: {total_attacks:,}")
    print(f"   Total Stars Earned: {total_stars:,}")
    print(f"   Total Three-Stars: {total_three_stars:,}")
    if total_attacks > 0:
        print(f"   All-Time Average: {total_stars/total_attacks:.2f}⭐/attack")
        print(f"   All-Time 3-Star Rate: {total_three_stars/total_attacks*100:.1f}%")
    
    # All-time leaderboard
    print(f"\n🏆 ALL-TIME LEADERBOARD (min 5 attacks):")
    
    # Filter players with enough attacks
    qualified_players = [p for p in players.values() if p.get('total_attacks', 0) >= 5]
    
    if qualified_players:
        # Sort by average stars
        sorted_by_avg = sorted(
            qualified_players,
            key=lambda x: (-x['total_stars'] / x['total_attacks'] if x['total_attacks'] > 0 else 0, -x['total_attacks'])
        )
        
        print(f"\n   📈 By Average Stars (min 5 attacks):")
        print(f"   {'#':<3} {'Player':<18} {'TH':<4} {'Attacks':<8} {'Stars':<7} {'Avg':<6} {'3⭐%':<7}")
        print(f"   {'-'*60}")
        
        for i, p in enumerate(sorted_by_avg[:15], 1):
            avg = p['total_stars'] / p['total_attacks'] if p['total_attacks'] > 0 else 0
            three_pct = p['three_stars'] / p['total_attacks'] * 100 if p['total_attacks'] > 0 else 0
            print(f"   {i:<3} {p['name'][:17]:<18} {p.get('current_th', '?'):<4} "
                  f"{p['total_attacks']:<8} {p['total_stars']:<7} {avg:<6.2f} {three_pct:<7.1f}")
    
    # Most attacks all-time
    sorted_by_attacks = sorted(players.values(), key=lambda x: -x.get('total_attacks', 0))
    
    print(f"\n   🎯 Most Attacks All-Time:")
    for i, p in enumerate(sorted_by_attacks[:10], 1):
        if p.get('total_attacks', 0) > 0:
            print(f"   {i}. {p['name']}: {p['total_attacks']} attacks, {p['total_stars']}⭐")
    
    # Most three-stars all-time
    sorted_by_3star = sorted(players.values(), key=lambda x: -x.get('three_stars', 0))
    
    print(f"\n   ⭐⭐⭐ Most Three-Stars All-Time:")
    for i, p in enumerate(sorted_by_3star[:10], 1):
        if p.get('three_stars', 0) > 0:
            print(f"   {i}. {p['name']}: {p['three_stars']} three-stars")
    
    # CWL history
    if cwl_seasons:
        print(f"\n📅 CWL SEASON HISTORY:")
        for season_id, data in sorted(cwl_seasons.items(), reverse=True):
            print(f"   • {data.get('season', season_id)}: {data.get('total_stars', 0)}⭐ "
                  f"({data.get('total_attacks', 0)} attacks) - "
                  f"{'Complete' if data.get('complete') else 'In Progress'}")


def create_member_report(players_data: list):
    """Create a detailed member report."""
    print_separator("COMPLETE MEMBER ROSTER")
    
    print(f"\n{'#':<3} {'Name':<18} {'TH':<4} {'Level':<6} {'Trophies':<9} {'War Stars':<10} {'Donations':<10}")
    print(f"{'-'*70}")
    
    # Sort by Town Hall level, then by trophies
    players_sorted = sorted(players_data, key=lambda x: (-x.get('townHallLevel', 0), -x.get('trophies', 0)))
    
    for i, player in enumerate(players_sorted, 1):
        name = player.get('name', 'Unknown')[:17]
        th = player.get('townHallLevel', '?')
        level = player.get('expLevel', 0)
        trophies = player.get('trophies', 0)
        war_stars = player.get('warStars', 0)
        donations = player.get('donations', 0)
        
        print(f"{i:<3} {name:<18} {th:<4} {level:<6} {trophies:<9,} {war_stars:<10,} {donations:<10,}")


def clan_strength_analysis(players_data: list):
    """Analyze overall clan strength."""
    print_separator("CLAN STRENGTH ANALYSIS")
    
    # Calculate weighted strength score
    print(f"\n💪 CLAN POWER METRICS:")
    
    # TH power (weighted)
    th_weights = {17: 100, 16: 90, 15: 80, 14: 70, 13: 60, 12: 50, 11: 40, 10: 30, 9: 20, 8: 10}
    th_power = sum(th_weights.get(p.get('townHallLevel', 1), 5) for p in players_data)
    print(f"   Town Hall Power Score: {th_power}")
    
    # Hero power
    total_hero_levels = 0
    for player in players_data:
        heroes = player.get('heroes', [])
        home_heroes = [h for h in heroes if h.get('village', '') == 'home']
        total_hero_levels += sum(h.get('level', 0) for h in home_heroes)
    print(f"   Total Hero Levels: {total_hero_levels}")
    
    # War experience
    total_war_stars = sum(p.get('warStars', 0) for p in players_data)
    print(f"   Total War Stars: {total_war_stars:,}")
    
    # Overall strength estimate
    strength_score = th_power + (total_hero_levels * 2) + (total_war_stars // 100)
    print(f"\n   🏆 OVERALL STRENGTH SCORE: {strength_score:,}")
    
    # Recommendations
    print(f"\n📝 RECOMMENDATIONS:")
    
    th_counts = defaultdict(int)
    for p in players_data:
        th_counts[p.get('townHallLevel', 0)] += 1
    
    low_th_count = sum(count for th, count in th_counts.items() if th < 12)
    high_th_count = sum(count for th, count in th_counts.items() if th >= 14)
    
    if low_th_count > len(players_data) * 0.3:
        print(f"   ⚠️  {low_th_count} members are below TH12. Consider recruiting higher TH players for CWL.")
    
    if high_th_count > len(players_data) * 0.5:
        print(f"   ✅ Strong high-level presence with {high_th_count} TH14+ members!")
    
    # Check for inactive players (low donations might indicate inactivity)
    low_activity = [p.get('name') for p in players_data if p.get('donations', 0) == 0 and p.get('donationsReceived', 0) == 0]
    if low_activity:
        print(f"   ⚠️  {len(low_activity)} members have 0 donations this season (possible inactives)")


def main():
    """Main function to run all analyses."""
    print("\n" + "="*80)
    print("   🎮 CLASH OF CLANS - COMPREHENSIVE CLAN ANALYSIS 🎮")
    print("="*80)
    print(f"\n📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🏷️  Clan Tag: {CLAN_TAG}")

    if not API_TOKEN:
        print("❌ API key not found! Set 'api_key' in your .env file (or as an environment variable).")
        sys.exit(1)

    # Load historical data
    print("\n💾 Loading historical data...")
    historical_data = load_historical_data()
    
    # Get clan info
    print("\n⏳ Fetching clan information...")
    clan = get_clan_info(CLAN_TAG)
    if not clan:
        print("❌ Failed to fetch clan information. Check your API token and clan tag.")
        sys.exit(1)
    
    analyze_clan_info(clan)
    
    # Get clan members
    print("\n⏳ Fetching clan members...")
    members = get_clan_members(CLAN_TAG)
    if not members:
        print("❌ Failed to fetch clan members.")
        sys.exit(1)
    
    # Get detailed player info for each member
    print(f"\n⏳ Fetching detailed info for {len(members)} players...")
    players_data = []
    failed = []
    for i, member in enumerate(members, 1):
        player_tag = member.get('tag')
        print(f"   Fetching player {i}/{len(members)}: {member.get('name')}", end='\r')
        player = get_player_info(player_tag)
        if player:
            players_data.append(player)
        else:
            failed.append(member)
        time.sleep(0.05)  # Small delay to avoid rate limiting
    print(" " * 60)  # Clear the line

    # The proxy has bad spells; give failed players a second chance after a pause
    if failed:
        print(f"\n⏳ Retrying {len(failed)} player(s) that failed...")
        time.sleep(30)
        still_failed = []
        for member in failed:
            player = get_player_info(member.get('tag'))
            if player:
                players_data.append(player)
            else:
                still_failed.append(member)
        failed = still_failed

    if len(failed) > MAX_MISSING_PLAYERS:
        print(f"❌ Failed to fetch {len(failed)} of {len(members)} players; not exporting incomplete data.")
        sys.exit(1)
    for member in failed:
        # GitHub Actions annotation, shown on the workflow run summary
        print(f"::warning::Player {member.get('name')} ({member.get('tag')}) could not be fetched and is missing from this export")
    
    # Run all analyses
    analyze_members(members, players_data)
    analyze_player_details(players_data)
    create_member_report(players_data)
    clan_strength_analysis(players_data)
    
    # Rush Analysis
    rush_reports = analyze_clan_rush(players_data)
    
    # Get war log
    print("\n⏳ Fetching war log...")
    warlog = get_clan_warlog(CLAN_TAG)
    analyze_warlog(warlog)
    
    # Get current war and save attack data
    print("\n⏳ Checking current war status...")
    current_war = get_current_war(CLAN_TAG)
    if current_war and current_war.get('state') not in ['notInWar', None]:
        war_stats = analyze_current_war(current_war)
        # Prep day has no attacks yet; recording it would only add empty entries
        if war_stats and current_war.get('state') in ('inWar', 'warEnded'):
            war_id = generate_war_id(current_war)
            war_date = parse_coc_time(current_war.get('startTime'))
            for tag, stats in war_stats.items():
                update_player_historical_stats(
                    historical_data,
                    player_tag=tag,
                    player_name=stats['name'],
                    th_level=stats['th'],
                    attack_data=stats,
                    war_type="regular_war",
                    war_id=war_id,
                    war_date=war_date
                )
    else:
        print_separator("CURRENT WAR")
        print("\n⚠️  Clan is not currently in a war.")
    
    # Analyze CWL
    print("\n⏳ Checking for Clan War League data...")
    cwl_group = get_cwl_group(CLAN_TAG)
    historical_data = analyze_cwl(CLAN_TAG, historical_data)
    
    # Fetch additional data for dashboard
    print("\n⏳ Fetching capital raid seasons...")
    capital_raids = get_capital_raid_seasons(CLAN_TAG)
    
    print("\n⏳ Fetching gold pass information...")
    gold_pass = get_gold_pass_season()
    
    # Print historical summary
    print_historical_summary(historical_data)
    
    # Update timestamp and save
    historical_data["last_updated"] = utc_now()
    save_historical_data(historical_data)

    # Export comprehensive data for Next.js dashboard
    export_dashboard_data(
        clan=clan,
        players_data=players_data,
        rush_reports=rush_reports,
        historical_data=historical_data,
        warlog=warlog,
        current_war=current_war,
        capital_raids=capital_raids,
        gold_pass=gold_pass,
        cwl_group=cwl_group
    )
    
    print_separator("ANALYSIS COMPLETE")
    print("\n✅ All analyses completed successfully!")
    print(f"📊 Dashboard data: {DASHBOARD_DATA_FILE}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
