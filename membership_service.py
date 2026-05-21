import requests
from config import API_URL, CHANNEL_ID


def is_member(user_id):
    try:
        r = requests.get(
            f"{API_URL}/getChatMember",
            params={
                "chat_id": CHANNEL_ID,
                "user_id": user_id
            }
        )

        data = r.json()

        if not data.get("ok"):
            return False

        status = data["result"]["status"]

        return status in [
            "member",
            "administrator",
            "creator"
        ]

    except:
        return False