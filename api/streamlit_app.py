"""
Clash of Clans Clan Analyzer - Streamlit Dashboard
Interactive visualization of clan data with rush detection
"""

import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict
from datetime import datetime
import urllib.parse
import os

# Page configuration
st.set_page_config(
    page_title="CoC Clan Analyzer",
    page_icon="🏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #e94560;
        text-align: center;
        padding: 1rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #1f4068 0%, #162447 100%);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        color: white;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #e94560;
    }
    .stat-label {
        color: #aaa;
        font-size: 0.9rem;
    }
    .rushed-severe { color: #e74c3c; font-weight: bold; }
    .rushed-moderate { color: #f39c12; }
    .rushed-slight { color: #2ecc71; }
    .not-rushed { color: #27ae60; }
</style>
""", unsafe_allow_html=True)

# API Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "clan_history.json")

# Max levels for rush detection (TH level -> max level at that TH)
HERO_MAX_LEVELS = {
    "Barbarian King": {7: 5, 8: 10, 9: 30, 10: 40, 11: 50, 12: 65, 13: 75, 14: 80, 15: 90, 16: 95, 17: 100},
    "Archer Queen": {9: 30, 10: 40, 11: 50, 12: 65, 13: 75, 14: 80, 15: 90, 16: 95, 17: 100},
    "Grand Warden": {11: 20, 12: 40, 13: 50, 14: 55, 15: 65, 16: 70, 17: 75},
    "Royal Champion": {13: 25, 14: 30, 15: 40, 16: 45, 17: 50},
    "Minion Prince": {8: 15, 9: 20, 10: 25, 11: 30, 12: 40, 13: 50, 14: 55, 15: 65, 16: 70, 17: 75}
}

HEADERS = {}


def set_api_token(token):
    """Set the API token for requests."""
    global HEADERS
    HEADERS = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }


def make_api_request(endpoint):
    """Make an API request with error handling."""
    url = f"https://api.clashofclans.com/v1{endpoint}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            st.error("❌ API Token invalid or IP not authorized")
        elif response.status_code == 404:
            st.error("❌ Resource not found")
        else:
            st.error(f"❌ API Error: {response.status_code}")
        return None
    except Exception as e:
        st.error(f"❌ Request failed: {str(e)}")
        return None


def get_clan_info(clan_tag):
    """Fetch clan information."""
    encoded_tag = urllib.parse.quote(clan_tag)
    return make_api_request(f"/clans/{encoded_tag}")


def get_clan_members(clan_tag):
    """Fetch clan members."""
    encoded_tag = urllib.parse.quote(clan_tag)
    data = make_api_request(f"/clans/{encoded_tag}/members")
    return data.get('items', []) if data else []


def get_player_info(player_tag):
    """Fetch player information."""
    encoded_tag = urllib.parse.quote(player_tag)
    return make_api_request(f"/players/{encoded_tag}")


def get_clan_warlog(clan_tag):
    """Fetch clan war log."""
    encoded_tag = urllib.parse.quote(clan_tag)
    data = make_api_request(f"/clans/{encoded_tag}/warlog")
    return data.get('items', []) if data else []


def get_max_level_for_th(item_name, th_level, level_dict):
    """Get the max level available at the previous TH."""
    prev_th = th_level - 1
    if item_name not in level_dict:
        return None
    levels = level_dict[item_name]
    for th in range(prev_th, 0, -1):
        if th in levels:
            return levels[th]
    return None


def generate_rush_report(player):
    """Generate rush report for a player."""
    th_level = player.get('townHallLevel', 1)
    player_name = player.get('name', 'Unknown')
    player_tag = player.get('tag', '')
    
    if th_level <= 7:
        return {
            'player_name': player_name,
            'player_tag': player_tag,
            'th_level': th_level,
            'is_rushed': False,
            'rush_score': 0,
            'rush_percentage': 0,
            'rushed_heroes': [],
            'rushed_troops': [],
            'rushed_spells': [],
            'status': '✅ Maxed',
            'total_missing_hero_levels': 0
        }
    
    rushed_heroes = []
    total_hero_deficit = 0
    total_hero_max = 0
    
    # Check heroes
    heroes = player.get('heroes', [])
    for hero in heroes:
        hero_name = hero.get('name')
        current_level = hero.get('level', 0)
        
        if hero_name in HERO_MAX_LEVELS:
            target_level = get_max_level_for_th(hero_name, th_level, HERO_MAX_LEVELS)
            if target_level:
                total_hero_max += target_level
                if current_level < target_level:
                    deficit = target_level - current_level
                    total_hero_deficit += deficit
                    rushed_heroes.append({
                        'name': hero_name,
                        'current': current_level,
                        'target': target_level,
                        'deficit': deficit
                    })
    
    # Calculate rush score (simplified - heroes only for this version)
    hero_rush_pct = (total_hero_deficit / total_hero_max * 100) if total_hero_max > 0 else 0
    rush_score = hero_rush_pct
    
    # Determine status
    is_rushed = rush_score >= 10 or total_hero_deficit >= 15
    
    if rush_score < 3:
        status = '✅ Maxed'
    elif rush_score < 10:
        status = '🟢 Slightly Behind'
    elif rush_score < 25:
        if total_hero_deficit >= 15:
            status = '🔴 Severely Rushed (Heroes)'
        else:
            status = '🟡 Moderately Rushed'
    elif rush_score < 50:
        if total_hero_deficit >= 15:
            status = '🔴 Severely Rushed (Heroes)'
        else:
            status = '🟠 Rushed'
    else:
        status = '🔴 Severely Rushed (Heroes)'
    
    return {
        'player_name': player_name,
        'player_tag': player_tag,
        'th_level': th_level,
        'is_rushed': is_rushed,
        'rush_score': rush_score,
        'rush_percentage': hero_rush_pct,
        'rushed_heroes': rushed_heroes,
        'rushed_troops': [],
        'rushed_spells': [],
        'status': status,
        'total_missing_hero_levels': total_hero_deficit
    }


def load_historical_data():
    """Load historical data from JSON file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"players": {}, "cwl_seasons": {}, "wars": {}}


def main():
    # Header
    st.markdown('<h1 class="main-header">🏰 Clash of Clans Clan Analyzer</h1>', unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        api_token = st.text_input(
            "API Token",
            type="password",
            help="Get your token from developer.clashofclans.com"
        )
        
        clan_tag = st.text_input(
            "Clan Tag",
            value="#2J28LL2VU",
            help="Include the # symbol"
        )
        
        fetch_data = st.button("🔄 Fetch Clan Data", type="primary", use_container_width=True)
        
        st.divider()
        st.caption("Made with ❤️ for Clash of Clans")
    
    # Initialize session state
    if 'clan_data' not in st.session_state:
        st.session_state.clan_data = None
    if 'players_data' not in st.session_state:
        st.session_state.players_data = []
    if 'rush_reports' not in st.session_state:
        st.session_state.rush_reports = []
    
    # Fetch data when button clicked
    if fetch_data:
        if not api_token:
            st.error("⚠️ Please enter your API token")
            return
        
        set_api_token(api_token)
        
        with st.spinner("Fetching clan data..."):
            clan = get_clan_info(clan_tag)
            if clan:
                st.session_state.clan_data = clan
                
                # Fetch members
                members = get_clan_members(clan_tag)
                
                # Fetch player details
                players_data = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, member in enumerate(members):
                    status_text.text(f"Fetching player {i+1}/{len(members)}: {member.get('name')}")
                    player = get_player_info(member.get('tag'))
                    if player:
                        players_data.append(player)
                    progress_bar.progress((i + 1) / len(members))
                
                progress_bar.empty()
                status_text.empty()
                
                st.session_state.players_data = players_data
                
                # Generate rush reports
                rush_reports = [generate_rush_report(p) for p in players_data]
                rush_reports.sort(key=lambda x: -x['rush_score'])
                st.session_state.rush_reports = rush_reports
                
                st.success(f"✅ Loaded {len(players_data)} players!")
    
    # Display data if available
    clan = st.session_state.clan_data
    players_data = st.session_state.players_data
    rush_reports = st.session_state.rush_reports
    
    if clan:
        # Clan Overview Section
        st.header(f"🏰 {clan.get('name', 'Unknown Clan')}")
        st.caption(f"{clan.get('tag')} • Level {clan.get('clanLevel', 0)} • {clan.get('members', 0)}/50 members")
        
        # Stats cards
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        war_wins = clan.get('warWins', 0)
        war_losses = clan.get('warLosses', 0)
        war_ties = clan.get('warTies', 0)
        total_wars = war_wins + war_losses + war_ties
        win_rate = (war_wins / total_wars * 100) if total_wars > 0 else 0
        
        with col1:
            st.metric("👥 Members", clan.get('members', 0))
        with col2:
            st.metric("🏆 Clan Points", f"{clan.get('clanPoints', 0):,}")
        with col3:
            st.metric("⚔️ War Wins", war_wins)
        with col4:
            st.metric("❌ War Losses", war_losses)
        with col5:
            st.metric("📊 Win Rate", f"{win_rate:.1f}%")
        with col6:
            rushed_count = sum(1 for r in rush_reports if r.get('is_rushed', False))
            st.metric("⚠️ Rushed", rushed_count)
        
        st.divider()
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "👥 Members", "⚠️ Rush Analysis", "📈 Charts"])
        
        with tab1:
            # Clan description and details
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📝 Clan Description")
                st.info(clan.get('description', 'No description'))
                
                # War League
                war_league = clan.get('warLeague', {}).get('name', 'Unknown')
                st.write(f"**War League:** {war_league}")
                st.write(f"**War Frequency:** {clan.get('warFrequency', 'Unknown')}")
                st.write(f"**Location:** {clan.get('location', {}).get('name', 'Unknown')}")
                
                # Labels
                labels = clan.get('labels', [])
                if labels:
                    st.write("**Labels:** " + ", ".join([l.get('name', '') for l in labels]))
            
            with col2:
                st.subheader("🏛️ Clan Capital")
                capital = clan.get('clanCapital', {})
                if capital:
                    st.write(f"**Capital Hall Level:** {capital.get('capitalHallLevel', 0)}")
                    districts = capital.get('districts', [])
                    for district in districts[:5]:
                        st.write(f"• {district.get('name')}: Level {district.get('districtHallLevel')}")
        
        with tab2:
            # Members table
            if players_data:
                st.subheader(f"👥 All Members ({len(players_data)})")
                
                # Create DataFrame
                members_df = pd.DataFrame([{
                    'Name': p.get('name', 'Unknown'),
                    'TH': p.get('townHallLevel', 0),
                    'Level': p.get('expLevel', 0),
                    'Trophies': p.get('trophies', 0),
                    'War Stars': p.get('warStars', 0),
                    'Donations': p.get('donations', 0),
                    'Received': p.get('donationsReceived', 0),
                    'BK': next((h.get('level', 0) for h in p.get('heroes', []) if h.get('name') == 'Barbarian King'), 0),
                    'AQ': next((h.get('level', 0) for h in p.get('heroes', []) if h.get('name') == 'Archer Queen'), 0),
                    'GW': next((h.get('level', 0) for h in p.get('heroes', []) if h.get('name') == 'Grand Warden'), 0),
                    'RC': next((h.get('level', 0) for h in p.get('heroes', []) if h.get('name') == 'Royal Champion'), 0),
                } for p in players_data])
                
                # Sort options
                sort_by = st.selectbox("Sort by:", ['TH', 'Level', 'War Stars', 'Trophies', 'Donations'], index=0)
                members_df = members_df.sort_values(sort_by, ascending=False)
                
                st.dataframe(
                    members_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "TH": st.column_config.NumberColumn("TH", width="small"),
                        "Level": st.column_config.NumberColumn("Lvl", width="small"),
                        "Trophies": st.column_config.NumberColumn("🏆", format="%d"),
                        "War Stars": st.column_config.NumberColumn("⭐", format="%d"),
                        "Donations": st.column_config.NumberColumn("📤", format="%d"),
                        "Received": st.column_config.NumberColumn("📥", format="%d"),
                    }
                )
        
        with tab3:
            # Rush Analysis
            if rush_reports:
                st.subheader("⚠️ Rush Analysis")
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                rushed = sum(1 for r in rush_reports if r.get('is_rushed'))
                not_rushed = len(rush_reports) - rushed
                severely_rushed = sum(1 for r in rush_reports if 'Severely' in r.get('status', ''))
                avg_score = sum(r.get('rush_score', 0) for r in rush_reports) / len(rush_reports)
                
                with col1:
                    st.metric("✅ Not Rushed", not_rushed)
                with col2:
                    st.metric("⚠️ Rushed", rushed)
                with col3:
                    st.metric("🔴 Severely Rushed", severely_rushed)
                with col4:
                    st.metric("📊 Avg Rush Score", f"{avg_score:.1f}")
                
                st.divider()
                
                # Filter options
                filter_option = st.radio(
                    "Filter:",
                    ["All", "Rushed Only", "Not Rushed"],
                    horizontal=True
                )
                
                filtered_reports = rush_reports
                if filter_option == "Rushed Only":
                    filtered_reports = [r for r in rush_reports if r.get('is_rushed')]
                elif filter_option == "Not Rushed":
                    filtered_reports = [r for r in rush_reports if not r.get('is_rushed')]
                
                # Rush table
                rush_df = pd.DataFrame([{
                    'Player': r.get('player_name'),
                    'TH': r.get('th_level'),
                    'Rush Score': round(r.get('rush_score', 0), 1),
                    'Hero Deficit': f"-{r.get('total_missing_hero_levels', 0)}",
                    'Status': r.get('status', 'Unknown')
                } for r in filtered_reports])
                
                st.dataframe(
                    rush_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Rush Score": st.column_config.ProgressColumn(
                            "Rush Score",
                            min_value=0,
                            max_value=100,
                            format="%.1f"
                        )
                    }
                )
                
                # Detailed view for severely rushed
                st.subheader("🔴 Players with Most Rushed Heroes")
                severely = [r for r in rush_reports if r.get('total_missing_hero_levels', 0) >= 15][:10]
                
                for report in severely:
                    with st.expander(f"**{report['player_name']}** (TH{report['th_level']}) - {report['status']}"):
                        st.write(f"**Rush Score:** {report['rush_score']:.1f}")
                        st.write(f"**Total Missing Hero Levels:** {report['total_missing_hero_levels']}")
                        
                        if report['rushed_heroes']:
                            st.write("**Rushed Heroes:**")
                            for hero in report['rushed_heroes']:
                                progress = hero['current'] / hero['target'] * 100
                                st.write(f"• {hero['name']}: {hero['current']}/{hero['target']} (-{hero['deficit']})")
                                st.progress(progress / 100)
        
        with tab4:
            # Charts
            if players_data:
                col1, col2 = st.columns(2)
                
                with col1:
                    # TH Distribution
                    st.subheader("🏠 Town Hall Distribution")
                    th_counts = defaultdict(int)
                    for p in players_data:
                        th_counts[f"TH{p.get('townHallLevel', 0)}"] += 1
                    
                    th_df = pd.DataFrame([
                        {"Town Hall": th, "Count": count}
                        for th, count in sorted(th_counts.items(), key=lambda x: -int(x[0][2:]))
                    ])
                    
                    fig = px.bar(
                        th_df, x="Town Hall", y="Count",
                        color="Count",
                        color_continuous_scale="Reds"
                    )
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Rush Status Distribution
                    st.subheader("⚠️ Rush Status Distribution")
                    status_counts = defaultdict(int)
                    for r in rush_reports:
                        status = r.get('status', 'Unknown')
                        if '✅' in status:
                            status_counts['Maxed'] += 1
                        elif '🟢' in status:
                            status_counts['Slightly Behind'] += 1
                        elif '🟡' in status:
                            status_counts['Moderately Rushed'] += 1
                        elif '🟠' in status:
                            status_counts['Rushed'] += 1
                        elif '🔴' in status:
                            status_counts['Severely Rushed'] += 1
                    
                    fig = px.pie(
                        names=list(status_counts.keys()),
                        values=list(status_counts.values()),
                        color=list(status_counts.keys()),
                        color_discrete_map={
                            'Maxed': '#27ae60',
                            'Slightly Behind': '#2ecc71',
                            'Moderately Rushed': '#f39c12',
                            'Rushed': '#e67e22',
                            'Severely Rushed': '#e74c3c'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Hero Levels Distribution
                st.subheader("🦸 Hero Level Analysis")
                
                hero_data = []
                for p in players_data:
                    for hero in p.get('heroes', []):
                        if hero.get('village') == 'home':
                            hero_data.append({
                                'Player': p.get('name'),
                                'Hero': hero.get('name'),
                                'Level': hero.get('level', 0),
                                'TH': p.get('townHallLevel', 0)
                            })
                
                if hero_data:
                    hero_df = pd.DataFrame(hero_data)
                    fig = px.box(
                        hero_df, x="Hero", y="Level",
                        color="Hero",
                        title="Hero Level Distribution Across Clan"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # War Stars Leaders
                st.subheader("⭐ Top War Stars")
                top_stars = sorted(players_data, key=lambda x: -x.get('warStars', 0))[:10]
                
                stars_df = pd.DataFrame([{
                    'Player': p.get('name'),
                    'War Stars': p.get('warStars', 0)
                } for p in top_stars])
                
                fig = px.bar(
                    stars_df, x="Player", y="War Stars",
                    color="War Stars",
                    color_continuous_scale="YlOrRd"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    else:
        # No data yet
        st.info("👆 Enter your API token and clan tag in the sidebar, then click 'Fetch Clan Data' to begin!")
        
        st.markdown("""
        ### 📋 How to get your API Token:
        1. Go to [developer.clashofclans.com](https://developer.clashofclans.com)
        2. Create an account or log in
        3. Create a new API key with your current IP address
        4. Copy the token and paste it above
        
        ### ⚠️ Note:
        API tokens are IP-restricted. If you're on a dynamic IP, you may need to regenerate your token when your IP changes.
        """)


if __name__ == "__main__":
    main()
