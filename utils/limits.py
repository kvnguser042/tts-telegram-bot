from datetime import datetime

# Temporary memory store
user_usage = {}


def can_use(user_id: int, daily_limit: int):
    today = datetime.utcnow().date()

    if user_id not in user_usage:
        user_usage[user_id] = {
            "date": today,
            "count": 0
        }

    # Reset if new day
    if user_usage[user_id]["date"] != today:
        user_usage[user_id] = {
            "date": today,
            "count": 0
        }

    if user_usage[user_id]["count"] >= daily_limit:
        return False

    user_usage[user_id]["count"] += 1
    return True
