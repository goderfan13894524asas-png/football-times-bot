from services.api_service import send_message, send_photo
from keyboards.user_keyboards import (
    confirm_keyboard,
    main_keyboard
)
from db import user_states
from config import PRICE_PER_DAY
from services.storage_service import save_ad, get_main_admins
from datetime import datetime


def handle_ads_text(message):

    chat_id = message["chat"]["id"]

    user_id = message["from"]["id"]

    text = message.get("text", "")

    state = user_states.setdefault(user_id, {})

    # =========================
    # شروع ثبت تبلیغ
    # =========================

    if text == "📢 ثبت تبلیغات":

        state["flow"] = "ads"
        state["step"] = "days"

        send_message(
            chat_id,
            "📅 تعداد روز تبلیغ را وارد کنید.\n\nمثال: ۳"
        )

        return True

    # =========================
    # فلوی ثبت تبلیغ
    # =========================

    if state.get("flow") == "ads":

        # مرحله روزها
        if state.get("step") == "days":

            if not text.isdigit():

                send_message(
                    chat_id,
                    "❌ فقط عدد وارد کنید.\n\nمثال: 3"
                )

                return True

            days = int(text)

            if days < 1 or days > 31:

                send_message(
                    chat_id,
                    "❌ تعداد روز باید بین 1 تا 31 باشد."
                )

                return True

            # محاسبه قیمت با تخفیف VIP
            from services.storage_service import is_vip

            base_price = days * PRICE_PER_DAY

            if is_vip(user_id):
                price = int(base_price * 0.8)  # ۲۰٪ تخفیف
                vip_msg = "\n🎉 تخفیف VIP: ۲۰٪"
            else:
                price = base_price
                vip_msg = ""

            state["days"] = days
            state["price"] = price
            state["step"] = "confirm_payment"

            send_message(
                chat_id,
                f"""
📅 تعداد روز: {days}

💰 مبلغ: {price:,} تومان{vip_msg}

آیا تایید می‌کنید؟
""",
                confirm_keyboard()
            )

            return True

        # مرحله دریافت فیش پرداخت (متنی)
        if state.get("step") == "send_receipt":

            # اگه متن ارسال شده (نه عکس)
            if text and text != "[عکس ارسال شد]":
                # ذخیره اطلاعات فیش
                state["receipt"] = text
                state["receipt_type"] = "text"
                state["step"] = "send_ad_text"

                send_message(
                    chat_id,
                    """
✅ فیش پرداخت دریافت شد.

📝 حالا متن تبلیغ خود را ارسال کنید.
"""
                )

                return True

        # مرحله دریافت متن تبلیغ
        if state.get("step") == "send_ad_text":

            state["ad_text"] = text
            state["step"] = "send_banner"

            send_message(
                chat_id,
                """
✅ متن تبلیغ دریافت شد.

🖼 حالا بنر تبلیغ (عکس) را ارسال کنید.
"""
            )

            return True

    return False


def handle_ads_photo(message):
    """هندل کردن عکس بنر تبلیغ"""

    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]

    state = user_states.get(user_id, {})

    if state.get("flow") != "ads" or state.get("step") != "send_banner":
        return False

    photos = message.get("photo")
    if not photos:
        return False

    file_id = photos[-1]["file_id"]

    # ذخیره اطلاعات تبلیغ
    ad_data = {
        "user_id": user_id,
        "text": state.get("ad_text", ""),
        "banner_file_id": file_id,
        "days": state.get("days", 0),
        "price": state.get("price", 0),
        "receipt": state.get("receipt", ""),
        "receipt_type": state.get("receipt_type", "text"),
        "status": "pending",
        "created_at": str(datetime.now())
    }

    # ذخیره در دیتابیس
    save_ad(ad_data)

    # ارسال به ادمین برای تایید
    main_admins = get_main_admins()
    if not main_admins:
        print("[ADS] No main admin found!")
        send_message(chat_id, "❌ خطا: ادمینی یافت نشد.", main_keyboard())
        user_states[user_id] = {}
        return False
    
    MAIN_ADMIN_ID = main_admins[0]  # اولین ادمین اصلی

    # ارسال فیش پرداخت هم به ادمین
    receipt_msg = ""
    if ad_data.get("receipt"):
        if ad_data.get("receipt_type") == "photo":
            receipt_msg = "\n🖼 فیش پرداخت: [عکس]"
        else:
            receipt_msg = f"\n🧾 فیش پرداخت: {ad_data['receipt']}"

    send_message(
        MAIN_ADMIN_ID,
        f"""
📢 تبلیغ جدید برای تایید

👤 کاربر: {user_id}
📅 روز: {ad_data['days']}
💰 قیمت: {ad_data['price']:,} تومان{receipt_msg}

📝 متن:
{ad_data['text']}
""",
        {
            "inline_keyboard": [
                [
                    {"text": "✅ تایید و انتشار", "callback_data": f"approve_ad:{user_id}"},
                    {"text": "❌ رد", "callback_data": f"reject_ad:{user_id}"}
                ],
                [
                    {"text": "⭐ VIP کردن کاربر", "callback_data": f"vip_user:{user_id}"}
                ]
            ]
        }
    )

    # ارسال فیش پرداخت (اگه عکس باشه) به ادمین
    if ad_data.get("receipt_type") == "photo" and ad_data.get("receipt"):
        send_photo(
            MAIN_ADMIN_ID,
            ad_data["receipt"],
            caption="🧾 فیش پرداخت"
        )

    # ارسال بنر به ادمین
    send_photo(
        MAIN_ADMIN_ID,
        file_id,
        caption="🖼 بنر تبلیغ"
    )

    send_message(
        chat_id,
        """
✅ تبلیغ شما ثبت شد و برای بررسی ارسال شد.

⏳ لطفاً منتظر تایید ادمین باشید.
""",
        main_keyboard()
    )

    # پاک کردن وضعیت
    user_states[user_id] = {}

    return True
