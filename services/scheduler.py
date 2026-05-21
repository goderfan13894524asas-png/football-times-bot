from datetime import datetime, timedelta
import random
import time
import threading
from services.api_service import send_message_to_channel, send_message
from services.storage_service import (
    load_json, save_json, get_active_ads
)
from config import CHANNEL_ID

# تنظیمات
MIN_HOUR = 9    # ساعت شروع (9 صبح)
MAX_HOUR = 21   # ساعت پایان (9 شب)
CHECK_INTERVAL = 60  # هر 60 ثانیه چک کن


def generate_random_times(days, user_id):
    """
    برای هر روز، یه زمان تصادفی بین 9 تا 21 تولید می‌کنه
    """
    schedule = []
    now = datetime.now()

    for i in range(days):
        day = now + timedelta(days=i)

        # زمان تصادفی بین 9:00 تا 21:00
        hour = random.randint(MIN_HOUR, MAX_HOUR)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)

        scheduled_time = day.replace(
            hour=hour, minute=minute, second=second, microsecond=0
        )

        # اگه برای امروزه و زمان گذشته، بذار برای فردا همون ساعت
        if scheduled_time < now and i == 0:
            scheduled_time = scheduled_time + timedelta(days=1)

        schedule.append({
            "day": i + 1,
            "time": scheduled_time.strftime("%Y-%m-%d %H:%M:%S"),
            "published": False
        })

    return schedule


def check_scheduled_ads():
    """
    هر دقیقه چک می‌کنه ببینه نوبت انتشار تبلیغی هست یا نه
    """
    now = datetime.now()
    data = load_json()
    ads = data.get("ads", [])

    published_any = False

    for ad in ads:
        if ad.get("status") not in ["approved", "active"]:
            continue

        schedule = ad.get("schedule", [])
        if not schedule:
            continue

        user_id = ad.get("user_id")
        ad_text = ad.get("text", "")
        banner = ad.get("banner_file_id")
        is_vip = ad.get("is_vip", False)

        for slot in schedule:
            if slot.get("published"):
                continue

            slot_time = datetime.strptime(slot["time"], "%Y-%m-%d %H:%M:%S")

            # اگه زمانش رسیده
            if now >= slot_time:
                # منتشر کن
                publish_ad(ad, is_vip)

                # علامت بزن published
                slot["published"] = True
                slot["published_at"] = now.strftime("%Y-%m-%d %H:%M:%S")

                # آپدیت publish_count
                ad["publish_count"] = ad.get("publish_count", 0) + 1
                ad["status"] = "active"

                # اگه همه روزها تموم شد
                all_published = all(s.get("published") for s in schedule)
                if all_published:
                    ad["status"] = "completed"
                    # اطلاع به کاربر
                    send_message(
                        user_id,
                        f"✅ تبلیغ شما به پایان رسید!\n\n"
                        f"📅 تعداد روز: {len(schedule)}\n"
                        f"📢 تعداد انتشار: {ad['publish_count']}\n\n"
                        f"ممنون از اعتماد شما! 🙏"
                    )

                published_any = True
                break  # هر دفعه فقط یه تبلیغ

    # ذخیره تغییرات
    data["ads"] = ads
    save_json(data)

    return published_any


def publish_ad(ad, is_vip=False):
    """
    تبلیغ رو توی کانال منتشر می‌کنه
    """
    ad_text = ad.get("text", "")
    banner = ad.get("banner_file_id")
    user_id = ad.get("user_id")

    # 🎉 VIP formatting
    if is_vip:
        vip_header = "🔥✨ *تبلیغ ویژه VIP* ✨🔥\n\n"
        vip_footer = "\n\n💎 *این تبلیغ توسط کاربر VIP فوتبال تایمز ثبت شده* 💎\n"
        vip_footer += "⭐ *مزایای VIP: ۲۰٪ تخفیف + اولویت انتشار* ⭐\n\n"
        vip_footer += "🤖 @footballtimes_bot"

        channel_msg = f"{vip_header}{ad_text}{vip_footer}"
    else:
        channel_msg = f"📢 تبلیغ\n\n{ad_text}\n\n---\n🤖 ربات فوتبال تایمز"

    try:
        if banner:
            send_message_to_channel(CHANNEL_ID, channel_msg, photo=banner)
        else:
            send_message_to_channel(CHANNEL_ID, channel_msg)

        print(f"[SCHEDULER] Ad published for user {user_id} at {datetime.now()}")
        return True
    except Exception as e:
        print(f"[SCHEDULER] Error publishing ad: {e}")
        return False


def start_scheduler():
    """
    شروع scheduler توی background
    """
    def run_scheduler():
        while True:
            try:
                check_scheduled_ads()
            except Exception as e:
                print(f"[SCHEDULER ERROR] {e}")

            time.sleep(CHECK_INTERVAL)

    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    print("[SCHEDULER] Started! Checking every 60 seconds...")


def get_user_schedule(user_id):
    """
    زمان‌بندی تبلیغ کاربر رو برمی‌گردونه
    """
    data = load_json()
    ads = data.get("ads", [])

    for ad in ads:
        if ad.get("user_id") == user_id:
            return ad.get("schedule", [])

    return []
