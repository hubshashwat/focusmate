import requests
import json
import os
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# --- CONFIGURATION ---
# Reads the API key from a GitHub Secret (environment variable)
API_KEY = os.environ.get('FOCUSMATE_API_KEY')
JSON_FILE_PATH = 'location.json'  # The path to your data file
# --- Cache file for processed users ---
PROCESSED_USERS_FILE_PATH = 'processed_users.json'

# --- Geocoding Setup ---
geolocator = Nominatim(user_agent="focusmate_globe_script")

# A map to normalize old timezone names to their modern equivalent
timezone_aliases = {
    'Asia/Kolkata': 'Asia/Calcutta',
    'US/Central': 'America/Chicago'
}


def get_lat_lon(city_name):
    """Fetches latitude and longitude for a given city name."""
    try:
        location = geolocator.geocode(city_name)
        if location:
            return (location.latitude, location.longitude)
    except GeocoderTimedOut:
        print(f"Warning: Geocoding timed out for {city_name}.")
    except Exception as e:
        print(f"An error occurred during geocoding for {city_name}: {e}")
    print(f"Warning: Could not find coordinates for {city_name}.")
    return (None, None)


def load_existing_data(filepath, default_type=list):
    """Loads existing location data from the JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or is empty, start fresh
        return default_type()


def save_data(filepath, data):
    """Saves the updated data to the JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def main():
    """Main script logic."""
    if not API_KEY:
        print("Error: FOCUSMATE_API_KEY secret not found.")
        return

    # 1. Load existing data and create a lookup map for easy access
    print("Loading existing data...")
    existing_locations = load_existing_data(JSON_FILE_PATH, default_type=list)
    locations_map = {loc['tz']: loc for loc in existing_locations}

    # 2. Fetch sessions from Focusmate API
    print("Fetching sessions from Focusmate API...")
    headers = {'X-API-KEY': API_KEY}
    from datetime import datetime, timedelta, timezone

    # Get today's date in UTC
    end = datetime.now(timezone.utc)

    # Get 1 year before today
    start = end - timedelta(days=365)

    params = {
        "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    try:
        response = requests.get('https://api.focusmate.com/v1/sessions', params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # --- ADD THESE 3 LINES ---
        print("Saving raw session data to focusmate_data.json...")
        raw_data = response.json()
        save_data('focusmate_data.json', raw_data)
        # -------------------------

        sessions = raw_data.get('sessions', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching sessions: {e}")
        return

    # 3. Get all unique user IDs from sessions
    all_user_ids_from_sessions = set()
    for session in sessions:
        for user in session.get('users', []):
            if 'userId' in user:
                all_user_ids_from_sessions.add(user['userId'])
    ids = load_existing_data(PROCESSED_USERS_FILE_PATH)['users']
    processed_user_ids = set(ids)
    print(f"Loaded {len(processed_user_ids)} already processed users.")

    new_user_ids = all_user_ids_from_sessions - processed_user_ids
    if not new_user_ids:
        print("No new partners found. All data is up to date.")
        return

    print(f"Found {len(new_user_ids)} unique partners.")

    # 4. Process each user and update the locations map
    print("Fetching user profiles and updating data...")
    for user_id in new_user_ids:
        try:
            user_response = requests.get(f'https://api.focusmate.com/v1/users/{user_id}', headers=headers)
            user_response.raise_for_status()
            user = user_response.json().get('user', {})

            user_tz = user.get('timeZone')
            # Normalize the timezone using the alias map
            user_tz = timezone_aliases.get(user_tz, user_tz)
            user_name = user.get('name')

            if not user_tz or not user_name:
                continue  # Skip if essential data is missing

            firstname = user_name.split()[0]

            # Scenario 1: The timezone already exists in our data
            if user_tz in locations_map:
                # Add the person to the list if they're not already there
                if firstname not in locations_map[user_tz]['people']:
                    locations_map[user_tz]['people'].append(firstname)
                    print(f"Added {firstname} to {locations_map[user_tz]['name']}.")

            # Scenario 2: It's a brand new timezone
            else:
                print(f"Found new timezone: {user_tz}. Attempting to geocode...")
                # Try to guess a city name from the timezone
                city_name = user_tz.split('/')[-1].replace('_', ' ')
                lat, lon = get_lat_lon(city_name)

                if lat is not None and lon is not None:
                    new_location = {
                        "name": city_name,
                        "tz": user_tz,
                        "lat": lat,
                        "lon": lon,
                        "people": [firstname]
                    }
                    locations_map[user_tz] = new_location
                    print(f"Created new location: {city_name} for {firstname}.")

        except requests.exceptions.RequestException as e:
            print(f"Could not fetch profile for user {user_id}. Error: {e}")


    # 5. Update the processed users list and save it
    updated_processed_ids = list(processed_user_ids.union(new_user_ids))
    print(f"\nSaving {len(updated_processed_ids)} processed user IDs...")
    updated_processed_ids = {"users": updated_processed_ids}
    save_data(PROCESSED_USERS_FILE_PATH, updated_processed_ids)


    # 5. Convert the map back to a list and save it
    updated_locations_list = list(locations_map.values())
    print(f"\nSaving updated data to {JSON_FILE_PATH}...")
    save_data(JSON_FILE_PATH, updated_locations_list)
    print("Update complete!")


if __name__ == "__main__":
    main()

