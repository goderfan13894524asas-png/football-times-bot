from handlers.start_handler import handle_start
from handlers.callback_handler import handle_callback
from handlers.admin_handler import handle_admin_commands
from handlers.support_handler import handle_support_commands
from handlers.ads_handler import handle_ads_text
from handlers.photo_handler import handle_photo
from handlers.text_handler import handle_text_commands

from services.api_service import get_updates
from services.spam_service import anti_spam
from services.storage_service import add_user, get_blocked_users, block_user
from services.scheduler import start_scheduler
from db import user_states
from services.storage_service import is_main_admin, is_support_admin

import time

offset = None

print("Bot Started...")

# 🔧 FIX: شروع scheduler
start_scheduler()
print("[BOT] Scheduler started! Ads will be published daily at random times.")


while True:
    try:
        updates = get_updates(offset)

        if not updates:
            time.sleep(0.1)
            continue

        if not updates.get("ok"):
            time.sleep(0.1)
            continue

        for update in updates["result"]:
            offset = update["update_id"] + 1

            # =========================
            # CALLBACK
            # =========================
            if "callback_query" in update:
                handle_callback(update["callback_query"])
                continue

            # =========================
            # MESSAGE
            # =========================
            if "message" not in update:
                continue

            message = update["message"]
            chat = message.get("chat", {})
            chat_id = chat.get("id")
            user_data = message.get("from")
            if not user_data:
                user_data = message.get("sender", {})
            if not user_data:
                continue

            user_id = user_data.get("id")
            if not user_id:
                continue

            # ذخیره کاربر
            add_user(user_id)

            # ذخیره اطلاعات کاربر
            from services.storage_service import save_user_info
            username = user_data.get("username", "")
            first_name = user_data.get("first_name", "")
            last_name = user_data.get("last_name", "")
            save_user_info(user_id, {
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "chat_id": chat_id
            })

            # بررسی بلاک
            blocked_list = get_blocked_users()
            if user_id in blocked_list:
                from services.api_service import send_message
                from utils.helpers import user_blocked_text
                send_message(chat_id, user_blocked_text())
                continue

            # ضد اسپم - فقط برای کاربران عادی
            is_admin_user = is_main_admin(user_id)
            is_support_user = is_support_admin(user_id)

            if not is_admin_user and not is_support_user:
                spam_result = anti_spam(user_id)
                if spam_result == "ban":
                    from services.api_service import send_message
                    block_user(user_id)
                    send_message(
                        chat_id,
                        """*کاربر گرامی🚫*

شما به دلیل اسپم بیش از حد توسط ربات به مدت ۳ روز مسدود شدید!❌️

شما به اخطار های ارسال شده توجه نکردید!⚠️"""
                    )
                    continue
                elif spam_result == "warn":
                    from services.api_service import send_message
                    send_message(
                        chat_id,
                        """*اخطار⚠️*

شما به دلیل اسپم بیش از حد توسط ربات اخطار دریافت کردید!❌️

اگر اخطار های شما به عدد ۳ برسد؛ توسط ربات مسدود خواهید شد!🚫"""
                    )
                    continue

            text = message.get("text", "")

            # =========================
            # START
            # =========================
            if text == "/start":
                handle_start(chat_id, user_id)
                continue

                        # =========================
            # BROADCAST FLOW (اولویت بالاتر از بقیه)
            # =========================
            state = user_states.get(user_id, {})
            if state.get("flow") == "broadcast":
                handle_admin_commands(message)
                continue

            # =========================
            # ADMIN (فقط برای ادمین اصلی)
            # =========================
            if is_admin_user:
                admin_commands = ["/admin", "📊 آمار", "📨 ارسال همگانی", "🚫 کاربران مسدود", 
                                  "📢 تبلیغات تایید شده", "⏳ تبلیغات در انتظار", 
                                  "⭐ کاربران VIP", "🔙 بازگشت به منوی اصلی", "📋 اطلاعات کاربران",
                                  "👑 مدیریت ادمین‌ها", "➕ اضافه کردن پشتیبان",
                                  "➕ اضافه کردن ادمین اصلی", "➖ حذف پشتیبان",
                                  "➖ حذف ادمین اصلی", "📋 لیست ادمین‌ها",
                                  "🔙 بازگشت به پنل ادمین"]

                if text in admin_commands:
                    handle_admin_commands(message)
                    continue

            # =========================
            # SUPPORT (برای پشتیبان‌ها)
            # =========================
            if is_support_user:
                support_commands = ["/support", "🟢 آنلاین شدن", "🔴 آفلاین شدن", "📋 لیست کاربران مسدود",
                                    "📊 آمار پشتیبانی", "🧾 تیکت‌های باز", "✅ تیکت‌های بسته",
                                    "🔍 جستجوی کاربر", "⭐ میانگین امتیازات من", "🗑 پاک کردن تیکت‌ها", "🔙 بازگشت"]

                if text in support_commands:
                    handle_support_commands(message, is_command=True)
                    continue

            # =========================
            # SUPPORT COMMAND (کاربر عادی)
            # =========================
            if text == "/support" or text == "💬 پشتیبانی":
                handle_support_commands(message, is_command=True)
                continue

            # =========================
            # PHOTO
            # =========================
            if "photo" in message:
                handle_photo(message)
                continue

            # =========================
            # TEXT COMMANDS (قیمت، راهنما)
            # =========================
            handled = handle_text_commands(message)
            if handled:
                continue

            # =========================
            # SUPPORT FLOW (چت فعال)
            # =========================
            handled = handle_support_commands(message, is_command=False)
            if handled:
                continue

            # =========================
            # ADS FLOW
            # =========================
            handled = handle_ads_text(message)
            if handled:
                continue

    except Exception as e:
        print("MAIN LOOP ERROR =>", e)
        time.sleep(0.5)
