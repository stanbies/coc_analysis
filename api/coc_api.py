"""Thin client for the Clash of Clans API (direct or via the RoyaleAPI proxy)."""

import time
import urllib.parse

import requests

from config import API_TOKEN, BASE_URL

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}


def encode_tag(tag: str) -> str:
    """URL encode a clan or player tag."""
    return urllib.parse.quote(tag)


def api_request(endpoint: str, retries: int = 5) -> dict | None:
    """Make an API request and return JSON response.

    Retries server errors and connection failures with backoff, since the
    proxy intermittently returns 5xx (Cloudflare 520/525, nginx 500).
    """
    url = f"{BASE_URL}{endpoint}"
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            if response.status_code >= 500 and attempt < retries:
                time.sleep(2 ** attempt)
                continue
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            print(f"Response: {response.text[:300]}")
            return None
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            print(f"Error: {e}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None


def get_clan_info(clan_tag: str) -> dict | None:
    """Get detailed clan information."""
    return api_request(f"/clans/{encode_tag(clan_tag)}")


def get_clan_members(clan_tag: str) -> list | None:
    """Get list of clan members."""
    data = api_request(f"/clans/{encode_tag(clan_tag)}/members")
    return data.get("items", []) if data else None


def get_clan_warlog(clan_tag: str) -> list | None:
    """Get clan war log."""
    data = api_request(f"/clans/{encode_tag(clan_tag)}/warlog")
    return data.get("items", []) if data else None


def get_current_war(clan_tag: str) -> dict | None:
    """Get current war information."""
    return api_request(f"/clans/{encode_tag(clan_tag)}/currentwar")


def get_player_info(player_tag: str) -> dict | None:
    """Get detailed player information."""
    return api_request(f"/players/{encode_tag(player_tag)}")


def get_player_league_history(player_tag: str) -> list | None:
    """Get a player's past ranked league results."""
    data = api_request(f"/players/{encode_tag(player_tag)}/leaguehistory")
    return data.get("items", []) if data else None


def get_cwl_group(clan_tag: str) -> dict | None:
    """Get CWL league group information."""
    return api_request(f"/clans/{encode_tag(clan_tag)}/currentwar/leaguegroup")


def get_cwl_war(war_tag: str) -> dict | None:
    """Get specific CWL war details."""
    return api_request(f"/clanwarleagues/wars/{encode_tag(war_tag)}")


def get_capital_raid_seasons(clan_tag: str, limit: int = 10) -> list | None:
    """Get clan's capital raid seasons."""
    data = api_request(f"/clans/{encode_tag(clan_tag)}/capitalraidseasons?limit={limit}")
    return data.get("items", []) if data else None


def get_leagues() -> list | None:
    """Get list of all leagues."""
    data = api_request("/leagues")
    return data.get("items", []) if data else None


def get_war_leagues() -> list | None:
    """Get list of all war leagues."""
    data = api_request("/warleagues")
    return data.get("items", []) if data else None


def get_capital_leagues() -> list | None:
    """Get list of all capital leagues."""
    data = api_request("/capitalleagues")
    return data.get("items", []) if data else None


def get_builder_base_leagues() -> list | None:
    """Get list of all builder base leagues."""
    data = api_request("/builderbaseleagues")
    return data.get("items", []) if data else None


def get_locations() -> list | None:
    """Get list of all locations."""
    data = api_request("/locations")
    return data.get("items", []) if data else None


def get_location_clan_rankings(location_id: int, limit: int = 200) -> list | None:
    """Get clan rankings for a specific location."""
    data = api_request(f"/locations/{location_id}/rankings/clans?limit={limit}")
    return data.get("items", []) if data else None


def get_location_player_rankings(location_id: int, limit: int = 200) -> list | None:
    """Get player rankings for a specific location."""
    data = api_request(f"/locations/{location_id}/rankings/players?limit={limit}")
    return data.get("items", []) if data else None


def get_location_capital_rankings(location_id: int, limit: int = 200) -> list | None:
    """Get capital rankings for a specific location."""
    data = api_request(f"/locations/{location_id}/rankings/capitals?limit={limit}")
    return data.get("items", []) if data else None


def get_player_labels() -> list | None:
    """Get list of all player labels."""
    data = api_request("/labels/players")
    return data.get("items", []) if data else None


def get_clan_labels() -> list | None:
    """Get list of all clan labels."""
    data = api_request("/labels/clans")
    return data.get("items", []) if data else None


def get_gold_pass_season() -> dict | None:
    """Get current gold pass season information."""
    return api_request("/goldpass/seasons/current")
