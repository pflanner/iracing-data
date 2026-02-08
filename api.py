import base64
from datetime import datetime
import hashlib
import json
import requests


def mask_secret(secret: str, identifier: str) -> str:
    """
    Mask a secret (client_secret or password) using iRacing's masking algorithm.

    Args:
        secret: The secret to mask
        identifier: client_id for client_secret, username for password

    Returns:
        Base64 encoded SHA-256 hash of secret + normalized_identifier
    """
    # Normalize the identifier (trim and lowercase)
    normalized_id = identifier.strip().lower()

    # Concatenate secret with normalized identifier
    combined = f"{secret}{normalized_id}"

    hasher = hashlib.sha256()
    hasher.update(combined.encode('utf-8'))

    return base64.b64encode(hasher.digest()).decode('utf-8')


def get_tokens(client_id, masked_client_secret, username, masked_password):
    r = requests.post(
        'https://oauth.iracing.com/oauth2/token',
        data={
            'grant_type': 'password_limited',
            'client_id': client_id,
            'client_secret': masked_client_secret,
            'username': username,
            'password': masked_password,
            'scope': 'iracing.auth iracing.profile',
        }
    )
    if r.status_code == 200:
        j = r.json()
        return j['access_token'], j['refresh_token']


def get_car_assets(session):
    """
    Note: image paths are relative to https://images-static.iracing.com/
    """
    result = session.get('https://members-ng.iracing.com/data/car/assets')
    return get_link(result)


def get_car(session):
    result = session.get(f'https://members-ng.iracing.com/data/car/get')
    return get_link(result)


def get_car_class(session):
    result = session.get(f'https://members-ng.iracing.com/data/carclass/get')
    return get_link(result)


def get_categories(session):
    return session.get('https://members-ng.iracing.com/data/constants/categories').json()


def get_divisions(session):
    return session.get('https://members-ng.iracing.com/data/constants/divisions').json()


def get_event_types(session):
    return session.get('https://members-ng.iracing.com/data/constants/event_types').json()


def get_hosted_combined_sessions(session, package_id: int = None):
    """
    Sessions that can be joined as a driver or spectator, and also includes non-league pending sessions for the user.
    :param session: requests.Session
    :param package_id: If set, return only sessions using this car or track package ID.
    :return:
    """
    params = None
    if package_id:
        params = {'package_id': package_id}
    r = session.get(
        'https://members-ng.iracing.com/data/hosted/combined_sessions',
        params=params,
    )
    return get_link(r)


def get_hosted_sessions(session):
    """
    Sessions that can be joined as a driver. Without spectator and non-league pending sessions for the user.
    :param session: requests.Session
    :return:
    """
    r = session.get('https://members-ng.iracing.com/data/hosted/combined_sessions')
    return get_link(r)


def get_participation_credits(session):
    result = session.get('https://members-ng.iracing.com/data/member/participation_credits')
    return result


def get_profile(session):
    result = session.get('https://members-ng.iracing.com/data/member/profile')
    return result


def get_results(session, subsession_id, include_licences=False):
    params = {'subsession_id': subsession_id, 'include_licenses': include_licences}
    return get_link(session.get('https://members-ng.iracing.com/data/results/get', params=params))


def get_lap_data(session, subsession_id, simsession_number, cust_id=None, team_id=None):
    assert (cust_id is not None) != (team_id is not None), 'exactly one of cust_id or team_id is required'
    params = {'subsession_id': subsession_id, 'simsession_number': simsession_number}
    if cust_id is not None:
        params['cust_id'] = cust_id
    else:
        params['team_id'] = team_id
    return session.get('https://members-ng.iracing.com/data/results/lap_data', params=params)


def get_lap_chart_data(session, subsession_id, simsession_number):
    params = {'subsession_id': subsession_id, 'simsession_number': simsession_number}
    return session.get('https://members-ng.iracing.com/data/results/lap_chart_data', params=params)


def get_formatted_time_string(d: datetime) -> str:
    return d.isoformat(timespec='minutes') + 'Z'


def get_season_results(session):
    params = {
        "season_id": 4032,
        "event_type": 2,
        "race_week_num": 7,
    }
    return session.get("https://members-ng.iracing.com/data/results/season_results", params=params)


def get_chunks(json_result, session):
    results = []
    data = json_result['data'] if 'data' in json_result else json_result
    base_download_url = data["chunk_info"]["base_download_url"]
    for filename in data["chunk_info"]["chunk_file_names"]:
        results.append(session.get(base_download_url + filename))
    return results


def get_all_series(session):
    return session.get('https://members-ng.iracing.com/data/series/get')


def lookup_drivers(search_term, session):
    params = {'search_term': search_term}
    raw_result =  session.get('https://members-ng.iracing.com/data/lookup/drivers', params=params)
    return get_link(raw_result)


def list_season(session, year, quarter):
    params = {'season_year': year, 'season_quarter': quarter}
    return session.get('https://members-ng.iracing.com/data/season/list', params=params)


def get_league(session, league_id):
    params = {'league_id': league_id}
    return session.get('https://members-ng.iracing.com/data/league/get', params=params)


def get_cust_league_sessions(session, league_id):
    params = {'league_id': league_id}
    return get_link(session.get('https://members-ng.iracing.com/data/league/cust_league_sessions', params=params))


def get_league_seasons(session, league_id, retired=False):
    params = {
        'league_id': league_id,
        'retired': retired,
    }
    return get_link(session.get('https://members-ng.iracing.com/data/league/seasons', params=params))


def get_league_season_sessions(session, league_id, season_id):
    params = {'league_id': league_id, 'season_id': season_id}
    return get_link(session.get('https://members-ng.iracing.com/data/league/season_sessions', params=params))


def get_link(api_result):
    j = api_result.json()

    link = j['link']
    link_result = requests.get(link)
    return link_result.json()


def pretty_print(json_dict):
    print(json.dumps(json_dict, default=str, indent=2))

