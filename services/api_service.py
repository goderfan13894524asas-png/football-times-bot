import requests
from config import API_URL


# ==========================================
# POST REQUEST
# ==========================================

def api_post(method, payload=None):

    try:

        response = requests.post(
            f"{API_URL}/{method}",
            json=payload,
            timeout=15
        )

        return response.json()

    except Exception as e:

        print("API POST ERROR =>", e)

        return {
            "ok": False
        }


# ==========================================
# GET REQUEST
# ==========================================

def api_get(method, params=None):

    try:

        response = requests.get(
            f"{API_URL}/{method}",
            params=params,
            timeout=15
        )

        return response.json()

    except Exception as e:

        print("API GET ERROR =>", e)

        return {
            "ok": False
        }


# ==========================================
# SEND MESSAGE
# ==========================================

def send_message(chat_id, text, reply_markup=None):

    payload = {
        "chat_id": chat_id,
        "text": str(text)
    }

    if reply_markup:
        payload["reply_markup"] = reply_markup

    return api_post("sendMessage", payload)


# ==========================================
# SEND PHOTO
# ==========================================

def send_photo(chat_id, photo, caption="", reply_markup=None):

    payload = {
        "chat_id": chat_id,
        "photo": photo,
        "caption": caption
    }

    if reply_markup:
        payload["reply_markup"] = reply_markup

    return api_post("sendPhoto", payload)


# ==========================================
# SEND MESSAGE TO CHANNEL
# ==========================================

def send_message_to_channel(channel_id, text, photo=None):
    """
    ارسال پیام به کانال
    اگه photo داشته باشه عکس می‌فرسته،
    در غیر این صورت متن ساده
    """
    if photo:
        payload = {
            "chat_id": channel_id,
            "photo": photo,
            "caption": text
        }
        return api_post("sendPhoto", payload)
    else:
        payload = {
            "chat_id": channel_id,
            "text": text
        }
        return api_post("sendMessage", payload)

# ==========================================
# ANSWER CALLBACK
# ==========================================

def answer_callback(callback_id, text=None):

    payload = {
        "callback_query_id": callback_id
    }

    if text:
        payload["text"] = text

    return api_post(
        "answerCallbackQuery",
        payload
    )


# ==========================================
# GET UPDATES
# ==========================================

def get_updates(offset=None):

    params = {
        "timeout": 30
    }

    if offset:
        params["offset"] = offset

    return api_get(
        "getUpdates",
        params
    )
