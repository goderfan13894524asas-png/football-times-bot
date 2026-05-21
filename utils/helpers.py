import time
from datetime import datetime, timedelta


def now():
    return datetime.now()


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def format_price(price):
    return f"{price:,} تومان"


def calculate_ad_price(days, price_per_day):
    return days * price_per_day


def generate_ticket_id():
    return int(time.time())


def seconds_to_day(seconds):
    return round(seconds / 86400, 1)


def remaining_ban_time(until_timestamp):
    now_time = time.time()
    remain = until_timestamp - now_time

    if remain <= 0:
        return "پایان یافته"

    days = int(remain // 86400)
    hours = int((remain % 86400) // 3600)
    minutes = int((remain % 3600) // 60)

    return f"{days} روز و {hours} ساعت و {minutes} دقیقه"


def is_number(text):
    try:
        int(text)
        return True
    except:
        return False


def safe_int(value, default=0):
    try:
        return int(value)
    except:
        return default


def safe_float(value, default=0.0):
    try:
        return float(value)
    except:
        return default


def chunk_message(text, limit=3500):
    return [
        text[i:i + limit]
        for i in range(0, len(text), limit)
    ]


def create_user_caption(user_id, username=None):
    if username:
        return f"""
👤 اطلاعات کاربر

🆔 آیدی عددی:
{user_id}

📛 یوزرنیم:
@{username}
"""

    return f"""
👤 اطلاعات کاربر

🆔 آیدی عددی:
{user_id}
"""


def ad_preview(text, days, price):
    return f"""
📢 پیش نمایش تبلیغ

📝 متن تبلیغ:
{text}

📅 تعداد روز:
{days}

💵 مبلغ:
{format_price(price)}
"""


def support_ticket_preview(ticket_id, user_id, text):
    return f"""
📨 تیکت جدید

🎫 شماره تیکت:
{ticket_id}

👤 کاربر:
{user_id}

📝 متن:
{text}
"""


def admin_stats_text(users, ads, tickets, blocked, vip_users):
    return f"""
📊 آمار کامل ربات

👥 تعداد کاربران:
{users}

📢 تعداد تبلیغات:
{ads}

🎫 تعداد تیکت‌ها:
{tickets}

🚫 کاربران مسدود:
{blocked}

⭐ کاربران VIP:
{vip_users}
"""


def support_stats_text(open_tickets, closed_tickets, active_chats):
    return f"""
📊 آمار پشتیبانی

🧾 تیکت‌های باز:
{open_tickets}

✅ تیکت‌های بسته:
{closed_tickets}

💬 گفتگوهای فعال:
{active_chats}
"""


def make_ban_time(days=3):
    return time.time() + (days * 24 * 60 * 60)


def is_command(text):
    return text.startswith("/")


def clean_text(text):
    return text.strip()


def create_log_text(user_id, action):
    return (
        f"[{now_str()}] "
        f"USER:{user_id} -> {action}"
    )


def ad_publish_text(channel):
    return f"""
✅ تبلیغ با موفقیت منتشر شد.

📢 کانال:
{channel}
"""


def payment_success_text(ref_id):
    return f"""
✅ پرداخت موفق بود.

🧾 کد پیگیری:
{ref_id}
"""


def payment_failed_text():
    return """
*کاربر گرامی⚠️*

پرداخت شما توسط پشتیبانی تایید نشد!❌️

اگر فکر می کنید پرداخت به درستی انجام شده، به پشتیبانی پیام دهید.

با تشکر از صبوری شما!
"""


def wait_text():
    return """
⏳ لطفاً کمی صبر کنید...
"""


def access_denied_text():
    return """
⛔ شما دسترسی لازم را ندارید.
"""


def user_blocked_text():
    return """
🚫 شما توسط پشتیبانی به مدت سه روز مسدود شده‌اید.
"""


def force_join_text(channel_link):
    return f"""
برای ادامه، لطفاً ابتدا در کانال «فوتبال‌تایمز | 𝙁𝙤𝙤𝙩𝙗𝙖𝙡𝙡 𝙏𝙞𝙢𝙚𝙨» عضو شوید و سپس دوباره به ربات بازگردید.

پس از عضویت، دسترسی شما بعد از کلیک بر روی دکمه عضو شدم فعال خواهد شد.

{channel_link}
"""


def support_busy_text():
    return """
⏳ تمام پشتیبان‌ها در حال حاضر مشغول هستند.

لطفاً کمی بعد مجدد تلاش کنید.
"""


def active_chat_warning():
    return """
⚠️ شما در حال گفتگو با پشتیبانی هستید.

منتظر پایان دادن گفت و گو توسط پشتیبان بمانید!⏳
"""
