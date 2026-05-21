from services.api_service import send_message, send_photo
from handlers.ads_handler import handle_ads_photo
from db import user_states


def handle_photo(message):

    chat_id = message["chat"]["id"]

    user_id = message["from"]["id"]

    photos = message.get("photo")

    if not photos:

        send_message(
            chat_id,
            "❌ عکسی دریافت نشد"
        )

        return

    file_id = photos[-1]["file_id"]

    # بررسی آیا در فلوی تبلیغ هستیم
    state = user_states.get(user_id, {})

    # 🔧 FIX: هندل کردن عکس فیش پرداخت (مرحله send_receipt)
    if state.get("flow") == "ads" and state.get("step") == "send_receipt":
        # ذخیره فایل آیدی فیش به جای متن
        state["receipt"] = file_id
        state["receipt_type"] = "photo"
        state["step"] = "send_ad_text"

        send_message(
            chat_id,
            """
✅ فیش پرداخت (عکس) دریافت شد.

📝 حالا متن تبلیغ خود را ارسال کنید.
"""
        )
        return

    # بررسی آیا در مرحله ارسال بنر هستیم
    if state.get("flow") == "ads" and state.get("step") == "send_banner":

        handled = handle_ads_photo(message)

        if handled:
            return

    # بررسی آیا در فلوی پشتیبانی هستیم
    if state.get("flow") == "support" and state.get("step") == "waiting_message":

        # ارسال عکس به پشتیبان
        from handlers.support_handler import handle_support_commands
        # تبدیل پیام به متنی که support_handler بتونه هندل کنه
        message["text"] = "[عکس ارسال شد]"
        handle_support_commands(message)

        return

    send_message(
        chat_id,
        "✅ عکس دریافت شد"
    )

    print(f"PHOTO RECEIVED => {user_id} | {file_id}")
