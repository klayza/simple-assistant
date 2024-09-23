import json
from datetime import datetime


def get_close_friends():
    with open("./data/friends.json") as f:
        friends = json.load(f)
        return friends


def get_snapchat_data():
    with open("./data/snapchat_data.json", encoding="utf-8") as f:
        data = json.load(f)
        return data["friends"]


def check_birthdays():
    friends = get_snapchat_data()
    close_friends = get_close_friends()
    today = datetime.now().strftime("%m-%d")

    birthdays_today = []
    for friend in friends:
        if friend.get("name") in close_friends and friend.get("birthday"):
            if friend["birthday"] == today:
                birthdays_today.append(friend.get("display") or friend.get("name"))

    if birthdays_today:
        return f"Today's birthdays: {', '.join(birthdays_today)}"
    else:
        return "No birthdays today."


# Example usage
if __name__ == "__main__":
    print(check_birthdays())
