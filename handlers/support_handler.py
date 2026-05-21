import time
from datetime import datetime
from services.api_service import send_message
from keyboards.support_keyboards import (
    support_panel_keyboard, support_request_keyboard,
    support_chat_keyboard, rate_keyboard
)
from keyboards.user_keyboards import main_keyboard
from db import user_states, active_chats, blocked_users, support_admins
from utils.helpers import generate_ticket_id
from services.storage_service import (
    save_ticket, get_blocked_users, get_open_tickets,
    get_closed_tickets, get_tickets, get_admin_average_rating,
    get_admin_ratings, save_user_info, get_support_admins,
    is_support_admin  # ← اضافه شد
)

def handle_support_commands(message, is_command=False):
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    text = message.get("text", "")

    state = user_states.setdefault(user_id, {})

    # =========================
    # پنل پشتیبانی (/support برای پشتیبان)
    # =========================
    if is_command and text == "/support" and is_support_admin(user_id):
        send_message(
            chat_id,
            """👨‍💼 پنل پشتیبانی


            📊 آمار پشتیبانی

            📋 لیست مسدودها

            🔍 جستجوی کاربر

            ⭐ میانگین امتیازات""",
            support_panel_keyboard()
        )
        return True

    # =========================
    # دکمه‌های پنل پشتیبانی
    # =========================
    if  is_support_admin(user_id):
        # 📊 آمار پشتیبانی
        if text == "📊 آمار پشتیبانی":
            open_t = len(get_open_tickets())
            closed_t = len(get_closed_tickets())
            total_t = len(get_tickets())
            active_c = len(active_chats)

            send_message(
                chat_id,
                f"""
📊 آمار پشتیبانی

🧾 تیکت‌های باز: {open_t}
✅ تیکت‌های بسته: {closed_t}
📊 کل تیکت‌ها: {total_t}
💬 گفتگوهای فعال: {active_c}
""",
                support_panel_keyboard()
            )
            return True

        # 📋 لیست کاربران مسدود
        if text == "📋 لیست کاربران مسدود":
            blocked = get_blocked_users()
            if not blocked:
                send_message(chat_id, "✅ هیچ کاربر مسدودی وجود ندارد.", support_panel_keyboard())
                return True

            msg = "🚫 لیست کاربران مسدود:"
            for uid in blocked:
                msg += f"• 👤 {uid}"

            send_message(chat_id, msg, support_panel_keyboard())
            return True

        # 🔍 جستجوی کاربر
        if text == "🔍 جستجوی کاربر":
            state["flow"] = "support_search"
            state["step"] = "waiting_user_id"
            send_message(
                chat_id,
                """🔍 لطفاً آیدی عددی کاربر را وارد کنید:


                مثال: 123456789


                برای لغو بنویسید: /cancel""",
                support_panel_keyboard()
            )
            return True

        if state.get("flow") == "support_search" and state.get("step") == "waiting_user_id":
            if text == "/cancel":
                state["flow"] = None
                state["step"] = None
                send_message(chat_id, "❌ عملیات لغو شد.", support_panel_keyboard())
                return True

            if not text.isdigit():
                send_message(chat_id, "❌ فقط عدد وارد کنید.")
                return True

            target_id = int(text)
            from services.storage_service import get_user_info
            info = get_user_info(target_id)

            if info:
                msg = f"""
👤 اطلاعات کاربر

🆔 آیدی عددی: {target_id}
📅 اولین بازدید: {info.get('first_seen', 'نامشخص')}
📝 اطلاعات:
"""
                for key, value in info.get("info", {}).items():
                    msg += f"• {key}: {value}"
            else:
                msg = f"""
👤 اطلاعات کاربر

🆔 آیدی عددی: {target_id}
📌 این کاربر هنوز اطلاعاتی ثبت نکرده است.
"""

            send_message(chat_id, msg, support_panel_keyboard())
            state["flow"] = None
            state["step"] = None
            return True

        # ⭐ میانگین امتیازات من
        if text == "⭐ میانگین امتیازات من":
            avg = get_admin_average_rating(user_id)
            ratings = get_admin_ratings(user_id)
            total = len(ratings)

            stars_display = "⭐" * int(avg) + "☆" * (5 - int(avg))

            send_message(
                chat_id,
                f"""
⭐ امتیازات شما

{stars_display} ({avg}/5.0)

📊 تعداد امتیازها: {total}
""",
                support_panel_keyboard()
            )
            return True

        # 🗑 پاک کردن تیکت‌ها
        if text == "🗑 پاک کردن تیکت‌ها":
            from services.storage_service import load_json, save_json
            data = load_json()
            
            # فقط تیکت‌های باز و بسته رو پاک می‌کنیم، کاربران و بقیه اطلاعات می‌مونه
            open_count = len(get_open_tickets())
            closed_count = len(get_closed_tickets())
            total_deleted = open_count + closed_count
            
            data["tickets"] = [] # لیست تیکت‌ها رو خالی می‌کنیم
            
            save_json(data)
            
            send_message(
                chat_id,
                f"🗑 تیکت‌ها پاک شدند.\n\n"
                f"🧾 تیکت‌های باز حذف شده: {open_count}\n"
                f"✅ تیکت‌های بسته حذف شده: {closed_count}\n"
                f"📊 کل حذف شده: {total_deleted}",
                support_panel_keyboard()
            )
            return True

        # 🟢 آنلاین شدن
        if text == "🟢 آنلاین شدن":
            support_admins[user_id] = True
            send_message(chat_id, "🟢 شما آنلاین شدید.", support_panel_keyboard())
            return True

        # 🔴 آفلاین شدن
        if text == "🔴 آفلاین شدن":
            support_admins[user_id] = False
            send_message(chat_id, "🔴 شما آفلاین شدید.", support_panel_keyboard())
            return True

        # 🧾 تیکت‌های باز
        if text == "🧾 تیکت‌های باز":
            tickets = get_open_tickets()
            if not tickets:
                send_message(chat_id, "✅ هیچ تیکت بازی وجود ندارد.", support_panel_keyboard())
                return True

            msg = "🧾 تیکت‌های باز:"
            for t in tickets[-10:]:
                msg += f"🎫 {t.get('ticket_id')} | 👤 {t.get('user_id')}📝 {t.get('text', '')[:50]}..."

            send_message(chat_id, msg, support_panel_keyboard())
            return True

        # ✅ تیکت‌های بسته
        if text == "✅ تیکت‌های بسته":
            tickets = get_closed_tickets()
            if not tickets:
                send_message(chat_id, "📭 هیچ تیکت بسته‌ای وجود ندارد.", support_panel_keyboard())
                return True

            msg = "✅ تیکت‌های بسته:"
            for t in tickets[-10:]:
                msg += f"🎫 {t.get('ticket_id')} | 👤 {t.get('user_id')}"

            send_message(chat_id, msg, support_panel_keyboard())
            return True

        # 🔙 بازگشت
        if text == "🔙 بازگشت":
            send_message(chat_id, "✅ به منوی اصلی بازگشتید.", main_keyboard())
            return True

    # =========================
    # شروع پشتیبانی (کاربر عادی)
    # =========================
    if is_command and (text == "/support" or text == "💬 پشتیبانی"):
        if user_id in blocked_users:
            from utils.helpers import user_blocked_text
            send_message(chat_id, user_blocked_text())
            return True

        if user_id in active_chats:
            send_message(
                chat_id,
                "⚠️ شما در حال گفتگو با پشتیبانی هستید."
                "پیام خود را ارسال کنید."
            )
            return True

        state["flow"] = "support"
        state["step"] = "waiting_message"

        send_message(
            chat_id,
            "💬 پیام خود را ارسال کنید.\n\nپشتیبان به زودی پاسخ خواهد داد."
        )
        return True

    # =========================
    # ارسال پیام پشتیبانی (کاربر)
    # =========================
    if state.get("flow") == "support":
        if state.get("step") == "waiting_message":
            ticket_id = generate_ticket_id()
            state["ticket_id"] = ticket_id

            save_ticket({
                "ticket_id": ticket_id,
                "user_id": user_id,
                "text": text,
                "status": "open",
                "created_at": str(datetime.now())
            })

            for admin_id in get_support_admins():
                try:
                    send_message(
                        admin_id,
                        f"""
📨 تیکت جدید

🎫 شماره تیکت: {ticket_id}
👤 کاربر: {user_id}

📝 متن:
{text}
""",
                        support_request_keyboard(user_id)
                    )
                except:
                    pass

            send_message(
                chat_id,
                f"✅ پیام شما برای پشتیبانی ارسال شد."
                f"🎫 شماره تیکت: {ticket_id}"
                f"⏳ لطفاً منتظر پاسخ باشید."
            )

            state["step"] = "waiting_reply"
            return True

        if state.get("step") == "waiting_reply" and user_id in active_chats:
            admin_id = active_chats[user_id]

            send_message(
                admin_id,
                f"👤 پیام از کاربر {user_id}:{text}",
                support_chat_keyboard(user_id)
            )
            send_message(chat_id, "✅ پیام شما ارسال شد.")
            return True

    # =========================
    # ارسال پیام از ادمین به کاربر
    # =========================
    if  is_support_admin(user_id):
        for uid, aid in active_chats.items():
            if aid == user_id and text not in ["🔚 پایان گفتگو", "🚫 بلاک کاربر", "✅ آنبلاک کاربر"]:
                send_message(
                    uid,
                    f"👨‍💼 پشتیبان:{text}"
                )
                send_message(
                    user_id,
                    "✅ پیام ارسال شد.",
                    support_chat_keyboard(uid)
                )
                return True

    return False
