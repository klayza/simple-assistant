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


# def check_birthdays():
#     friends = get_snapchat_data()
#     close_friends = get_close_friends()
#     today = datetime.now().strftime("%m-%d")

#     birthdays_today = []
#     for friend in friends:
#         if friend.get("name") in close_friends and friend.get("birthday"):
#             if friend["birthday"] == today:
#                 birthdays_today.append(friend.get("display") or friend.get("name"))

#     if birthdays_today:
#         return f"Today's birthdays: {', '.join(birthdays_today)}"
#     else:
#         return "No birthdays today."
    

   
def check_birthdays(days_ahead=7):
    friends = get_snapchat_data()
    close_friends = get_close_friends()

    today = datetime.now()
    upcoming_birthdays = []

    # Check each friend's birthday
    for friend in friends:
        if friend.get("name") in close_friends and friend.get("birthday"):
            birthday_str = friend["birthday"]
            # Assuming birthday is stored in MM-DD format
            birthday_date = datetime.strptime(birthday_str, "%m-%d").replace(year=today.year)

            # If birthday is within the next `days_ahead` days
            if 0 <= (birthday_date - today).days <= days_ahead:
                upcoming_birthdays.append(f"{friend.get('display') or friend.get('name')} on {birthday_str}")

    if upcoming_birthdays:
        return f"Upcoming birthdays in the next {days_ahead} days: {', '.join(upcoming_birthdays)}"
    else:
            return f"No birthdays in the next {days_ahead} days."


# Example usage
if __name__ == "__main__":
    print(check_birthdays(20))
