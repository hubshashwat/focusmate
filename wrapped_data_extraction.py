import json
import collections

# --- CONFIGURATION ---
MY_USER_ID = "63d819b5-d69c-46aa-90e7-7a20fb2cfe29"
DATA_FILENAME = "focusmate_data.json"
STATS_FILENAME = "stats.json"  # The new output file


# --- MAIN ANALYSIS SCRIPT ---

def analyze_focusmate_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        sessions = data.get('sessions', [])
        if not sessions:
            print(f"No 'sessions' found in {filename}.")
            return
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode the JSON from '{filename}'.")
        return

    # --- Initialize trackers ---
    duration_counter = collections.Counter()
    activity_counter = collections.Counter()
    all_partners = set()
    total_duration_ms = 0
    favorites_sessions = 0

    for session in sessions:
        if len(session.get('users', [])) < 2:
            continue

        if session['users'][0]['userId'] == MY_USER_ID:
            my_user_obj = session['users'][0]
            partner_obj = session['users'][1]
        else:
            my_user_obj = session['users'][1]
            partner_obj = session['users'][0]

        partner_id = partner_obj.get('userId')
        if not partner_id:
            continue

        # --- 1. Session Durations ---
        duration_ms = session.get('duration', 0)
        duration_counter[duration_ms] += 1

        # --- 2. Activity Type ---
        activity = my_user_obj.get('activityType', 'unknown')
        activity_counter[activity] += 1

        # --- 3. Sessions With Favourites ---
        if partner_obj.get('isFavorite', False):
            favorites_sessions += 1

        # --- 4. Unique Partners ---
        all_partners.add(partner_id)

        # --- 5. Hours Focused ---
        if my_user_obj.get('completed', False):
            total_duration_ms += duration_ms

    # --- Prepare data for JSON export ---

    # Hours Focused
    total_hours = total_duration_ms / (1000 * 60 * 60)

    # Unique Partners
    unique_partners_count = len(all_partners)

    # Session Durations (clean format)
    duration_map = {
        1500000: '25 min',
        3000000: '50 min',
        4500000: '75 min',
    }
    session_durations = [
        {"duration": duration_map.get(ms, f"{int(ms / 60000)} min"), "count": count}
        for ms, count in duration_counter.items()
    ]

    # Activity Type (clean format)
    activity_types = [
        {"type": activity.capitalize(), "count": count}
        for activity, count in activity_counter.items()
    ]

    # --- Create the final stats dictionary ---
    stats_output = {
        "hoursFocused": round(total_hours, 2),
        "uniquePartners": unique_partners_count,
        "sessionsWithFavorites": favorites_sessions,
        "sessionDurations": session_durations,
        "activityTypes": activity_types
    }

    # --- Write to stats.json file ---
    try:
        with open(STATS_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(stats_output, f, indent=4)

        print("=" * 40)
        print(f"🎉 Success! Analysis complete. 🎉")
        print(f"Data saved to {STATS_FILENAME}")
        print("=" * 40)
        print(f"Hours Focused: {stats_output['hoursFocused']}")
        print(f"Unique Partners: {stats_output['uniquePartners']}")
        print(f"Sessions with Favorites: {stats_output['sessionsWithFavorites']}")

    except IOError as e:
        print(f"Error: Could not write file {STATS_FILENAME}. {e}")


# --- Run the script ---
if __name__ == "__main__":
    analyze_focusmate_data(DATA_FILENAME)