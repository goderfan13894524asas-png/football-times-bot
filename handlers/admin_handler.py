from services.api_service import send_message, send_photo, send_message_to_channel
from keyboards.admin_keyboards import admin_panel_keyboard, admin_management_keyboard
from services.storage_service import (
    get_users, get_ads, get_tickets, get_blocked_users,
    get_pending_ads, update_ad_status, get_vip_users,
    add_vip_user, remove_vip_user, get_all_user_info,
    get_active_ads,
    add_main_admin, remove_main_admin,
    add_support_admin, remove_support_admin,
    get_main_admins, get_support_admins,
    is_main_admin  # ← اضافه شد
)
# from services.scheduler import get_scheduler_status, POSTS_PER_AD  # REMOVED - not defined in scheduler.py
from db import user_states, vip_users



def handle_admin_commands(message):
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    text = message.get("text", "")

    # =========================
    # بررسی ادمین بودن
    # =========================
    if not is_main_admin(user_id):
        send_message(chat_id, "❌ شما ادمین نیستید")
        return

    # =========================
    # باز کردن پنل
    # =========================
    if text == "/admin":
        send_message(chat_id, "✅ پنل ادمین باز شد", admin_panel_keyboard())
        return

    # =========================
    # 📊 آمار
    # =========================
    if text == "📊 آمار":
        users = get_users()
        ads = get_ads()
        tickets = get_tickets()
        blocked = get_blocked_users()
        vips = get_vip_users()
        active_ads = get_active_ads()

        msg = f"""
📊 آمار کامل ربات

👥 تعداد کاربران: {len(users)}
📢 تعداد تبلیغات: {len(ads)}
🎫 تعداد تیکت‌ها: {len(tickets)}
🚫 کاربران مسدود: {len(blocked)}
⭐ کاربران VIP: {len(vips)}
📢 تبلیغات فعال: {len(active_ads)}
"""

        send_message(chat_id, msg, admin_panel_keyboard())
        return

        # =========================
    # 📨 ارسال همگانی
    # =========================
    if text == "📨 ارسال همگانی":
        user_states[user_id] = {"flow": "broadcast", "step": "waiting_text"}
        send_message(
            chat_id,
            "📨 متن پیام همگانی را وارد کنید:\n\nبرای لغو بنویسید: /cancel"
        )
        return

    # 🔧 FIX: چک کردن flow broadcast
    state = user_states.get(user_id, {})
    if state.get("flow") == "broadcast":
        if text == "/cancel":
            user_states[user_id] = {}
            send_message(chat_id, "❌ عملیات لغو شد.", admin_panel_keyboard())
            return

        # اگه هنوز توی step waiting_text هستیم
        if state.get("step") == "waiting_text":
            # ذخیره متن و رفتن به مرحله تایید
            state["broadcast_text"] = text
            state["step"] = "confirm"

            keyboard = {
                "keyboard": [
                    [{"text": "✅ بله، ارسال کن"}],
                    [{"text": "❌ لغو"}]
                ],
                "resize_keyboard": True
            }

            send_message(
                chat_id,
                f"📨 متن دریافت شد:\n\n{text}\n\nآیا ارسال شود؟",
                keyboard
            )
            return

        # مرحله تایید
        if state.get("step") == "confirm":
            if text == "✅ بله، ارسال کن":
                broadcast_text = state.get("broadcast_text", "")
                users = get_users()
                sent = 0
                failed = 0

                for uid in users:
                    try:
                        send_message(uid, broadcast_text)
                        sent += 1
                    except:
                        failed += 1

                user_states[user_id] = {}

                send_message(
                    chat_id,
                    f"""✅ ارسال همگانی انجام شد.

📤 موفق: {sent}
❌ ناموفق: {failed}""",
                    admin_panel_keyboard()
                )
                return

            elif text == "❌ لغو":
                user_states[user_id] = {}
                send_message(chat_id, "❌ عملیات لغو شد.", admin_panel_keyboard())
                return

            else:
                # اگه ادمین متن دیگه‌ای فرستاد توی مرحله تایید
                send_message(chat_id, "⚠️ لطفاً یکی از دکمه‌ها را انتخاب کنید.")
                return

    # =========================
    # ⏳ تبلیغات در انتظار
    # =========================
    if text == "⏳ تبلیغات در انتظار":
        pending = get_pending_ads()

        if not pending:
            send_message(chat_id, "✅ هیچ تبلیغ در انتظاری وجود ندارد.", admin_panel_keyboard())
            return

        for ad in pending:
            user_ad_id = ad.get("user_id")
            days = ad.get("days")
            price = ad.get("price")
            ad_text = ad.get("text", "")
            banner = ad.get("banner_file_id")
            receipt = ad.get("receipt", "")
            receipt_type = ad.get("receipt_type", "text")

            receipt_msg = ""
            if receipt:
                if receipt_type == "photo":
                    receipt_msg = "🖼 فیش پرداخت: [عکس]"
                else:
                    receipt_msg = f"🧾 فیش پرداخت: {receipt}"

            msg = f"""
📢 تبلیغ در انتظار تایید

👤 کاربر: {user_ad_id}
📅 روز: {days}
💰 قیمت: {price:,} تومان{receipt_msg}

📝 متن:
{ad_text}
"""

            keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "✅ تایید و انتشار", "callback_data": f"approve_ad:{user_ad_id}"},
                        {"text": "❌ رد", "callback_data": f"reject_ad:{user_ad_id}"}
                    ],
                    [
                        {"text": "⭐ VIP کردن کاربر", "callback_data": f"vip_user:{user_ad_id}"}
                    ]
                ]
            }

            if banner:
                send_photo(chat_id, banner, caption=msg, reply_markup=keyboard)
            else:
                send_message(chat_id, msg, keyboard)

            # ارسال فیش پرداخت به ادمین (اگه عکس باشه)
            if receipt_type == "photo" and receipt:
                send_photo(chat_id, receipt, caption="🧾 فیش پرداخت")

        return

    # =========================
    # 📢 تبلیغات تایید شده (فعال)
    # =========================
    if text == "📢 تبلیغات تایید شده":
        ads = get_ads()

        if not ads:
            send_message(chat_id, "📭 هیچ تبلیغی ثبت نشده.", admin_panel_keyboard())
            return

        msg = "📢 لیست تبلیغات:"
        for ad in ads[-10:]:
            status = ad.get("status", "unknown")
            status_emoji = "✅" if status == "approved" else "⏳" if status == "pending" else "🔄" if status == "active" else "✔️" if status == "completed" else "❌"
            publish_count = ad.get("publish_count", 0)
            max_publish = ad.get("max_publish", ad.get("days", 0))
            msg += f"{status_emoji} کاربر: {ad.get('user_id')} | روز: {ad.get('days')} | وضعیت: {status} | انتشار: {publish_count}/{max_publish}"

        send_message(chat_id, msg, admin_panel_keyboard())
        return

    # =========================
    # 🚫 کاربران مسدود
    # =========================
    if text == "🚫 کاربران مسدود":
        blocked = get_blocked_users()

        if not blocked:
            send_message(chat_id, "✅ هیچ کاربر مسدودی وجود ندارد.", admin_panel_keyboard())
            return

        msg = "🚫 لیست کاربران مسدود:"
        for uid in blocked:
            msg += f"• {uid}"

        send_message(chat_id, msg, admin_panel_keyboard())
        return

    # =========================
    # ⭐ کاربران VIP
    # =========================
    if text == "⭐ کاربران VIP":
        vips = get_vip_users()

        if not vips:
            send_message(chat_id, "📭 هیچ کاربر VIP وجود ندارد.", admin_panel_keyboard())
            return

        msg = "⭐ لیست کاربران VIP:"
        for uid in vips:
            msg += f"👤 {uid}"

        msg += "برای VIP کردن کاربر، از بخش 'تبلیغات در انتظار' استفاده کنید."

        send_message(chat_id, msg, admin_panel_keyboard())
        return

    # =========================
    # 📋 اطلاعات کاربران
    # =========================
    if text == "📋 اطلاعات کاربران":
        all_info = get_all_user_info()

        if not all_info:
            send_message(chat_id, "📭 هنوز اطلاعاتی ثبت نشده.", admin_panel_keyboard())
            return

        msg = "📋 اطلاعات کاربران:"
        for uid, info in list(all_info.items())[-20:]:
            user_data = info.get("info", {})
            msg += f"👤 {uid}"
            msg += f"  📅 اولین بازدید: {info.get('first_seen', 'نامشخص')[:10]}"
            if user_data.get("username"):
                msg += f"  📛 @{user_data['username']}"
            if user_data.get("first_name"):
                msg += f"  📝 {user_data['first_name']} {user_data.get('last_name', '')}"
            msg += ""

        send_message(chat_id, msg, admin_panel_keyboard())
        return

    # =========================
    # 👑 مدیریت ادمین‌ها
    # =========================
    if text == "👑 مدیریت ادمین‌ها":
        send_message(
            chat_id,
            "👑 پنل مدیریت ادمین‌ها\n\n"
            "از دکمه‌های زیر استفاده کنید:",
            admin_management_keyboard()
        )
        return
    
    if text == "🔙 بازگشت به پنل ادمین":
        send_message(chat_id, "✅ بازگشت به پنل ادمین", admin_panel_keyboard())
        return
    
    # ➕ اضافه کردن پشتیبان
    if text == "➕ اضافه کردن پشتیبان":
        user_states[user_id] = {"flow": "add_support", "step": "waiting_id"}
        send_message(
            chat_id,
            "➕ آیدی عددی کاربر را برای اضافه کردن به پشتیبان‌ها وارد کنید:\n\n"
            "مثال: 123456789\n\n"
            "❌ برای لغو: /cancel"
        )
        return
    
    if state.get("flow") == "add_support" and state.get("step") == "waiting_id":
        if text == "/cancel":
            user_states[user_id] = {}
            send_message(chat_id, "❌ عملیات لغو شد.", admin_management_keyboard())
            return
        
        if not text.isdigit():
            send_message(chat_id, "❌ فقط عدد وارد کنید.")
            return
        
        target_id = int(text)
        if add_support_admin(target_id):
            send_message(
                chat_id,
                f"✅ کاربر `{target_id}` به عنوان پشتیبان اضافه شد.",
                admin_management_keyboard()
            )
            # اطلاع به کاربر
            send_message(
                target_id,
                "🎉 تبریک! شما به عنوان پشتیبان ربات انتخاب شدید.\n\n"
                "برای ورود به پنل پشتیبانی، /support را بزنید."
            )
        else:
            send_message(
                chat_id,
                f"⚠️ کاربر `{target_id}` قبلاً پشتیبان است.",
                admin_management_keyboard()
            )
        user_states[user_id] = {}
        return
    
    # ➕ اضافه کردن ادمین اصلی
    if text == "➕ اضافه کردن ادمین اصلی":
        user_states[user_id] = {"flow": "add_main", "step": "waiting_id"}
        send_message(
            chat_id,
            "➕ آیدی عددی کاربر را برای اضافه کردن به ادمین‌های اصلی وارد کنید:\n\n"
            "مثال: 123456789\n\n"
            "❌ برای لغو: /cancel"
        )
        return
    
    if state.get("flow") == "add_main" and state.get("step") == "waiting_id":
        if text == "/cancel":
            user_states[user_id] = {}
            send_message(chat_id, "❌ عملیات لغو شد.", admin_management_keyboard())
            return

        if not text.isdigit():
            send_message(chat_id, "❌ فقط عدد وارد کنید.")
            return
        
        target_id = int(text)
        if add_main_admin(target_id):
            send_message(
                chat_id,
                f"✅ کاربر `{target_id}` به عنوان ادمین اصلی اضافه شد.",
                admin_management_keyboard()
            )
            send_message(
                target_id,
                "👑 تبریک! شما به عنوان ادمین اصلی ربات انتخاب شدید.\n\n"
                "برای ورود به پنل ادمین، /admin را بزنید."
            )
        else:
            send_message(
                chat_id,
                f"⚠️ کاربر `{target_id}` قبلاً ادمین اصلی است.",
                admin_management_keyboard()
            )
        user_states[user_id] = {}
        return

    # ➖ حذف پشتیبان
    if text == "➖ حذف پشتیبان":
        user_states[user_id] = {"flow": "remove_support", "step": "waiting_id"}
        send_message(
            chat_id,
            "➖ آیدی عددی پشتیبانی که می‌خواهید برکنار کنید را وارد کنید:\n\n"
            "❌ برای لغو: /cancel"
        )
        return

    if state.get("flow") == "remove_support" and state.get("step") == "waiting_id":
        if text == "/cancel":
            user_states[user_id] = {}
            send_message(chat_id, "❌ عملیات لغو شد.", admin_management_keyboard())
            return
        
        if not text.isdigit():
            send_message(chat_id, "❌ فقط عدد وارد کنید.")
            return
        
        target_id = int(text)
        if target_id == user_id:
            send_message(chat_id, "❌ نمی‌توانید خودتان را برکنار کنید!", admin_management_keyboard())
            user_states[user_id] = {}
            return
        
        if remove_support_admin(target_id):
            send_message(
                chat_id,
                f"✅ کاربر `{target_id}` از لیست پشتیبان‌ها حذف شد.",
                admin_management_keyboard()
            )
            send_message(
                target_id,
                "⚠️ شما از سمت پشتیبانی ربات برکنار شدید."
            )
        else:
            send_message(
                chat_id,
                f"❌ کاربر `{target_id}` توی لیست پشتیبان‌ها نیست.",
                admin_management_keyboard()
            )
        user_states[user_id] = {}
        return

    # ➖ حذف ادمین اصلی
    if text == "➖ حذف ادمین اصلی":
        user_states[user_id] = {"flow": "remove_main", "step": "waiting_id"}
        send_message(
            chat_id,
            "➖ آیدی عددی ادمینی که می‌خواهید برکنار کنید را وارد کنید:\n\n"
            "❌ برای لغو: /cancel"
        )
        return

    if state.get("flow") == "remove_main" and state.get("step") == "waiting_id":
        if text == "/cancel":
            user_states[user_id] = {}
            send_message(chat_id, "❌ عملیات لغو شد.", admin_management_keyboard())
            return
        
        if not text.isdigit():
            send_message(chat_id, "❌ فقط عدد وارد کنید.")
            return
        
        target_id = int(text)
        if target_id == user_id:
            send_message(chat_id, "❌ نمی‌توانید خودتان را برکنار کنید!", admin_management_keyboard())
            user_states[user_id] = {}
            return
        
        if remove_main_admin(target_id):
            send_message(
                chat_id,
                f"✅ کاربر `{target_id}` از لیست ادمین‌های اصلی حذف شد.",
                admin_management_keyboard()
            )
            send_message(
                target_id,
                "⚠️ شما از سمت ادمینی ربات برکنار شدید."
            )
        else:
            send_message(
                chat_id,
                f"❌ کاربر `{target_id}` توی لیست ادمین‌های اصلی نیست.",
                admin_management_keyboard()
            )
        user_states[user_id] = {}
        return

    # 📋 لیست ادمین‌ها
    if text == "📋 لیست ادمین‌ها":
        main_admins = get_main_admins()
        support_admins_list = get_support_admins()
        
        msg = "👑 لیست ادمین‌ها:\n\n"
        msg += "👑 ادمین‌های اصلی:\n"
        for uid in main_admins:
            msg += f"• `{uid}`\n"
        
        msg += "\n💬 پشتیبان‌ها:\n"
        for uid in support_admins_list:
            msg += f"• `{uid}`\n"
        
        send_message(chat_id, msg, admin_management_keyboard())
        return

        
    # =========================
    # 🔙 بازگشت
    # =========================
    if text == "🔙 بازگشت به منوی اصلی":
        from keyboards.user_keyboards import main_keyboard
        send_message(chat_id, "✅ به منوی اصلی بازگشتید.", main_keyboard())
        return
