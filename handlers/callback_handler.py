from datetime import datetime
from services.api_service import send_message, answer_callback
from services.membership_service import is_member
from services.storage_service import (
    block_user, unblock_user, update_ad_status, get_pending_ads,
    add_vip_user, save_rating, close_ticket, is_vip, load_json, save_json,
    is_support_admin  # ← اضافه شد
)
from services.scheduler import generate_random_times
from keyboards.user_keyboards import rules_keyboard, main_keyboard
from keyboards.support_keyboards import support_chat_keyboard, rate_keyboard
from db import user_states, active_chats, blocked_users, vip_users, rated_users

def handle_callback(callback):
    data = callback["data"]
    callback_id = callback["id"]
    user_id = callback["from"]["id"]
    chat_id = callback["message"]["chat"]["id"]

    answer_callback(callback_id)

    # =========================
    # بررسی بلاک بودن
    # =========================
    from services.storage_service import get_blocked_users
    if user_id in get_blocked_users():
        send_message(chat_id, "🚫 شما مسدود شده‌اید و نمی‌توانید از ربات استفاده کنید.")
        return

    # =========================
    # بررسی چت فعال
    # =========================
    if user_id in active_chats:
        if not data.startswith("rate") and not data.startswith("end_chat"):
            send_message(
                chat_id,
                "⚠️ شما در حال گفتگو با پشتیبانی هستید.\n\n"
                "⏳ لطفاً منتظر بمانید تا گفتگو به اتمام برسد.\n"
                "🔚 یا اینکه از پشتیبان بخواهید گفتگو را پایان دهد."
            )
            return

    # =========================
    # عضویت
    # =========================
    if data == "check_join":
        if is_member(user_id):
            user_states[user_id]["joined"] = True
            send_message(
                chat_id,
                """✅ عضویت شما تایید شد.\n\n📜 قوانین و مقررات «فوتبال‌تایمز | 𝙁𝙤𝙤𝙩𝙗𝙖𝙡𝙡 𝙏𝙞𝙢𝙚𝙨»

لطفاً پیش از هرگونه ثبت درخواست یا پرداخت، موارد زیر را با دقت مطالعه فرمایید. ثبت درخواست به منزله پذیرش کامل این قوانین است.

*۱. رعایت ادب و احترام*
رعایت شئونات اخلاقی و احترام در تمامی پیام‌ها الزامی است. در صورت مشاهده هرگونه بی‌احترامی، همکاری فوراً متوقف خواهد شد.

*۲. مسئولیت محتوای ارسالی*
مسئولیت کامل محتوای ارسالی (متن، تصویر، لینک، بنر و …) بر عهده ارسال‌کننده است. در صورت وجود هرگونه تخلف قانونی یا محتوای نامناسب، مسئولیت حقوقی آن متوجه کاربر خواهد بود.

*۳. عدم استرداد وجه*
وجوه پرداخت‌شده تحت هیچ شرایطی قابل عودت نمی‌باشد.

*۴. پرداخت ناقص*  
در صورت واریز مبلغ کمتر از تعرفه تعیین‌شده — حتی به میزان ۱ ریال — وجه پرداختی بازگردانده نخواهد شد و کاربر موظف است مابه‌التفاوت را به طور کامل پرداخت نماید.

*۵. ثبت نهایی پس از پرداخت کامل * 
ارائه خدمات صرفاً پس از تأیید پرداخت کامل و نهایی انجام خواهد شد.

*۶. حق بررسی و رد درخواست*
مدیریت «فوتبال‌تایمز» حق بررسی، تأیید یا رد هرگونه درخواست را بدون الزام به ارائه توضیح محفوظ می‌دارد.

*۷. تغییر قوانین*
در صورت لزوم، قوانین و شرایط ممکن است به‌روزرسانی شوند و نسخه جدید از زمان انتشار لازم‌الاجرا خواهد بود.


*۸. فیش جعلی*

در صورت ارسال هرگونه فیشه جعلی، پشتیبانان قادر به انجام اقدام قضایی خواهند بود. شما با پذیرفتن این قوانین این قانون مهم را می پذیرید.

*با ثبت درخواست و استفاده از خدمات، شما تأیید می‌کنید که تمامی موارد فوق را مطالعه کرده و می‌پذیرید.*

*با احترام مدیریت «فوتبال‌تایمز | 𝙁𝙤𝙤𝙩𝙗𝙖𝙡𝙡 𝙏𝙞𝙢𝙚𝙨»*""",
                rules_keyboard()
            )
        else:
            send_message(chat_id, "❌ هنوز داخل کانال عضو نشده‌اید.")
        return

    # =========================
    # تایید قوانین
    # =========================
    if data == "accept_rules":
        user_states[user_id]["rules"] = True
        send_message(
            chat_id,
            """*کاربر گرامی⚠️*

قوانین توسط شما تایید شد!✅️

به ربات 《فوتبال‌تایمز | 𝙁𝙤𝙤𝙩𝙗𝙖𝙡𝙡 𝙏𝙞𝙢𝙚𝙨》خوش آمدید!🖐""",
            main_keyboard()
        )
        return

    # =========================
    # تایید پرداخت
    # =========================
    if data == "confirm_payment":
        user_states[user_id]["step"] = "send_receipt"
        send_message(
            chat_id,
            """*کاربر گرامی⚠️*

پس از واریز مبلغ، تصویری از فیش را برای ربات ارسال نمایید و منتظر تایید پشتیبانی بمانید!

پرداخت مبلغ به دو صورت انجام می‌گیرد:

*1- کارت به کارت به شماره کارت زیر :*

5892-1012-8072-1867

سید محمد مانی حسینی

*2- ارسال به صورت پاکت هدیه به آیدی زیر :*

@mani_11H 

با تشکر از صبوری شما!"""
        )
        return

    # =========================
    # لغو
    # =========================
    if data == "cancel_payment":
        user_states[user_id] = {}
        send_message(chat_id, "❌ عملیات لغو شد.", main_keyboard())
        return

    # =========================
    # قبول گفتگو (پشتیبان)
    # =========================
    if data.startswith("accept_chat"):
        parts = data.split(":")
        target_user_id = int(parts[1])

        if not is_support_admin(user_id):
            send_message(chat_id, "⛔ شما پشتیبان نیستید.")
            return

        active_chats[target_user_id] = user_id
        from services.storage_service import save_active_chat
        save_active_chat(target_user_id, user_id)

        send_message(
            target_user_id,
            "✅ پشتیبان به گفتگو پیوست.\n\n💬 پیام خود را ارسال کنید."
        )
        send_message(
            chat_id,
            f"✅ گفتگو با کاربر {target_user_id} شروع شد.",
            support_chat_keyboard(target_user_id)
        )
        return

    # =========================
    # پایان گفتگو
    # =========================
    if data.startswith("end_chat"):
        parts = data.split(":")
        target_user_id = int(parts[1])

        if target_user_id in active_chats:
            admin_id = active_chats[target_user_id]
            del active_chats[target_user_id]
            from services.storage_service import remove_active_chat
            remove_active_chat(target_user_id)

            # بستن تیکت
            state = user_states.get(target_user_id, {})
            ticket_id = state.get("ticket_id")
            if ticket_id:
                close_ticket(ticket_id)

            send_message(
                target_user_id,
                "🔚 گفتگو با پشتیبانی پایان یافت.\n\n"
                "⭐ لطفاً به پشتیبانی امتیاز دهید:",
                rate_keyboard(admin_id)
            )
            send_message(chat_id, "✅ گفتگو پایان یافت.")

        return

    # =========================
    # بلاک کاربر
    # =========================
    if data.startswith("block"):
        parts = data.split(":")
        target_user_id = int(parts[1])

        block_user(target_user_id)
        blocked_users.add(target_user_id)

        if target_user_id in active_chats:
            del active_chats[target_user_id]
            from services.storage_service import remove_active_chat
            remove_active_chat(target_user_id)

        send_message(chat_id, f"🚫 کاربر {target_user_id} مسدود شد.")
        send_message(target_user_id, "🚫 شما توسط پشتیبانی مسدود شدید.")
        return

    # =========================
    # آنبلاک کاربر
    # =========================
    if data.startswith("unblock"):
        parts = data.split(":")
        target_user_id = int(parts[1])

        unblock_user(target_user_id)
        blocked_users.discard(target_user_id)

        send_message(chat_id, f"✅ کاربر {target_user_id} آزاد شد.")
        send_message(target_user_id, "✅ مسدودیت شما برداشته شد.")
        return

    # =========================
    # تایید تبلیغ + تنظیم زمان‌بندی روزانه
    # =========================
    if data.startswith("approve_ad"):
        parts = data.split(":")
        target_user_id = int(parts[1])

        pending = get_pending_ads()
        target_ad = None
        for ad in pending:
            if ad.get("user_id") == target_user_id:
                target_ad = ad
                break

        if not target_ad:
            send_message(chat_id, "❌ تبلیغ یافت نشد یا قبلاً بررسی شده.")
            return

        # 🔧 FIX: تولید زمان‌های تصادفی برای هر روز
        days = target_ad.get("days", 1)
        schedule = generate_random_times(days, target_user_id)

        # چک VIP بودن
        user_is_vip = is_vip(target_user_id)

        # آپدیت تبلیغ با زمان‌بندی
        data_db = load_json()
        ads = data_db.get("ads", [])
        for ad in ads:
            if ad.get("user_id") == target_user_id and ad.get("status") == "pending":
                ad["status"] = "approved"
                ad["schedule"] = schedule
                ad["publish_count"] = 0
                ad["max_publish"] = days
                ad["is_vip"] = user_is_vip
                ad["updated_at"] = str(datetime.now())
                break
        data_db["ads"] = ads
        save_json(data_db)

        # ساخت پیام زمان‌بندی
        schedule_msg = "📅 زمان‌بندی انتشار:\n\n"
        for slot in schedule:
            day_num = slot["day"]
            time_str = slot["time"]
            schedule_msg += f"روز {day_num}: {time_str}\n"

        send_message(
            target_user_id,
            f"✅ تبلیغ شما تایید شد!\n\n"
            f"📅 روز: {days}\n"
            f"💰 قیمت: {target_ad.get('price'):,} تومان\n\n"
            f"{schedule_msg}\n"
            f"📢 تبلیغ هر روز یکبار در کانال منتشر می‌شود.\n"
            f"⏳ لطفاً منتظر باشید..."
        )

        send_message(chat_id, f"✅ تبلیغ کاربر {target_user_id} تایید شد.\n\n{schedule_msg}")

        return

    # =========================
    # رد تبلیغ
    # =========================
    if data.startswith("reject_ad"):
        parts = data.split(":")
        target_user_id = int(parts[1])

        update_ad_status(target_user_id, "rejected")
        send_message(target_user_id, """*متن تبلیغ شما توسط پشتیبانان ما رد شد!❌️*

در صورت بروز مشکل به پشتیبانی پیام دهید.

ممکن است تبلیغ شما دارای الفاظ نامناسب بوده باشد!

شما می توانید بنر تبلیغ جدیدی ارسال کنید.""")
        send_message(chat_id, f"❌ تبلیغ کاربر {target_user_id} رد شد.")
        return

    # =========================
    # VIP کردن کاربر
    # =========================
    if data.startswith("vip_user"):
        parts = data.split(":")
        target_user_id = int(parts[1])

        add_vip_user(target_user_id)
        vip_users.add(target_user_id)

        send_message(
            target_user_id,
            "🎉 تبریک! شما به عنوان کاربر VIP انتخاب شدید.\n\n"
            "از این پس ۲۰٪ تخفیف در ثبت تبلیغات دارید!"
        )
        send_message(chat_id, f"⭐ کاربر {target_user_id} VIP شد.")
        return

    # =========================
    # امتیازدهی
    # =========================
    if data.startswith("rate"):
        parts = data.split(":")
        admin_id = int(parts[1])
        stars = int(parts[2])

        user_ratings = rated_users.get(user_id, [])
        if admin_id in user_ratings:
            send_message(chat_id, "❌ شما قبلاً به این پشتیبان امتیاز داده‌اید.")
            return

        if user_id not in rated_users:
            rated_users[user_id] = []
        rated_users[user_id].append(admin_id)
        save_rating(user_id, admin_id, stars)

        send_message(
            admin_id,
            f"⭐ امتیاز جدید دریافت کردید!\n\n"
            f"👤 کاربر: {user_id}\n"
            f"⭐ {stars} ستاره از ۵ ستاره"
        )
        send_message(
            chat_id,
            "✅ امتیاز شما ثبت شد.\n\nممنون از بازخورد شما! 🙏",
            main_keyboard()
        )
        return
