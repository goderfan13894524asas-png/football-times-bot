from datetime import datetime
import json
import os

DB_FILE = "data/database.json"


def load_json():
    if not os.path.exists(DB_FILE):
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_json(data):
    try:
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print("Storage Error:", e)


# =========================
# کاربران
# =========================

def add_user(user_id):
    data = load_json()
    users = data.get("users", [])
    if user_id not in users:
        users.append(user_id)
    data["users"] = users
    save_json(data)


def get_users():
    data = load_json()
    return data.get("users", [])


# =========================
# تبلیغات
# =========================

def save_ad(ad_data):
    data = load_json()
    ads = data.get("ads", [])
    ads.append(ad_data)
    data["ads"] = ads
    save_json(data)


def get_ads():
    data = load_json()
    return data.get("ads", [])


def update_ad_status(user_id, status):
    data = load_json()
    ads = data.get("ads", [])
    for ad in ads:
        if ad.get("user_id") == user_id and ad.get("status") == "pending":
            ad["status"] = status
            ad["updated_at"] = str(datetime.now())
            break
    data["ads"] = ads
    save_json(data)


def get_pending_ads():
    data = load_json()
    ads = data.get("ads", [])
    return [ad for ad in ads if ad.get("status") == "pending"]


def get_active_ads():
    """تبلیغات approved یا active که هنوز کامل نشدن"""
    data = load_json()
    ads = data.get("ads", [])
    active = []
    for ad in ads:
        status = ad.get("status", "")
        if status in ["approved", "active"]:
            publish_count = ad.get("publish_count", 0)
            max_publish = ad.get("max_publish", ad.get("days", 0))
            if publish_count < max_publish:
                active.append(ad)
    return active


def get_ad_by_user_id(user_id):
    """پیدا کردن تبلیغ کاربر"""
    data = load_json()
    ads = data.get("ads", [])
    for ad in ads:
        if ad.get("user_id") == user_id:
            return ad
    return None


# =========================
# تیکت‌ها
# =========================

def save_ticket(ticket):
    data = load_json()
    tickets = data.get("tickets", [])
    tickets.append(ticket)
    data["tickets"] = tickets
    save_json(data)


def get_tickets():
    data = load_json()
    return data.get("tickets", [])


def get_open_tickets():
    data = load_json()
    tickets = data.get("tickets", [])
    return [t for t in tickets if t.get("status") == "open"]


def get_closed_tickets():
    data = load_json()
    tickets = data.get("tickets", [])
    return [t for t in tickets if t.get("status") == "closed"]


def close_ticket(ticket_id):
    data = load_json()
    tickets = data.get("tickets", [])
    for t in tickets:
        if t.get("ticket_id") == ticket_id:
            t["status"] = "closed"
            t["closed_at"] = str(datetime.now())
            break
    data["tickets"] = tickets
    save_json(data)


# =========================
# کاربران مسدود
# =========================

def block_user(user_id):
    data = load_json()
    blocked = data.get("blocked_users", [])
    if user_id not in blocked:
        blocked.append(user_id)
    data["blocked_users"] = blocked
    save_json(data)


def unblock_user(user_id):
    data = load_json()
    blocked = data.get("blocked_users", [])
    if user_id in blocked:
        blocked.remove(user_id)
    data["blocked_users"] = blocked
    save_json(data)


def get_blocked_users():
    data = load_json()
    return data.get("blocked_users", [])


# =========================
# VIP
# =========================

def add_vip_user(user_id):
    data = load_json()
    vips = data.get("vip_users", [])
    if user_id not in vips:
        vips.append(user_id)
    data["vip_users"] = vips
    save_json(data)


def remove_vip_user(user_id):
    data = load_json()
    vips = data.get("vip_users", [])
    if user_id in vips:
        vips.remove(user_id)
    data["vip_users"] = vips
    save_json(data)


def get_vip_users():
    data = load_json()
    return data.get("vip_users", [])


def is_vip(user_id):
    return user_id in get_vip_users()


# =========================
# امتیازات (RATINGS)
# =========================

def save_rating(user_id, admin_id, stars):
    data = load_json()
    ratings = data.get("ratings", [])
    ratings.append({
        "user_id": user_id,
        "admin_id": admin_id,
        "stars": stars,
        "created_at": str(datetime.now())
    })
    data["ratings"] = ratings
    save_json(data)


def get_admin_ratings(admin_id):
    data = load_json()
    ratings = data.get("ratings", [])
    return [r for r in ratings if r.get("admin_id") == admin_id]


def get_admin_average_rating(admin_id):
    ratings = get_admin_ratings(admin_id)
    if not ratings:
        return 0.0
    total = sum(r.get("stars", 0) for r in ratings)
    return round(total / len(ratings), 1)


def get_all_ratings():
    data = load_json()
    return data.get("ratings", [])


# =========================
# اطلاعات کاربران (USER INFO)
# =========================

def save_user_info(user_id, info):
    data = load_json()
    user_info = data.get("user_info", {})
    if str(user_id) not in user_info:
        user_info[str(user_id)] = {
            "user_id": user_id,
            "first_seen": str(datetime.now()),
            "info": {}
        }
    user_info[str(user_id)]["info"].update(info)
    user_info[str(user_id)]["last_updated"] = str(datetime.now())
    data["user_info"] = user_info
    save_json(data)


def get_user_info(user_id):
    data = load_json()
    user_info = data.get("user_info", {})
    return user_info.get(str(user_id), {})


def get_all_user_info():
    data = load_json()
    return data.get("user_info", {})


# =========================
# آمار پشتیبانی
# =========================

def get_support_stats():
    open_t = len(get_open_tickets())
    closed_t = len(get_closed_tickets())
    total_t = len(get_tickets())
    active_c = len(get_active_chats_from_db())
    return {
        "open": open_t,
        "closed": closed_t,
        "total": total_t,
        "active_chats": active_c
    }


def get_active_chats_from_db():
    data = load_json()
    return data.get("active_chats", {})


def save_active_chat(user_id, admin_id):
    data = load_json()
    active = data.get("active_chats", {})
    active[str(user_id)] = admin_id
    data["active_chats"] = active
    save_json(data)


def remove_active_chat(user_id):
    data = load_json()
    active = data.get("active_chats", {})
    if str(user_id) in active:
        del active[str(user_id)]
    data["active_chats"] = active
    save_json(data)

# =========================
# مدیریت ادمین‌ها (پویا)
# =========================

def load_admins():
    """لود لیست ادمین‌ها از فایل"""
    data = load_json()
    admins = data.get("dynamic_admins", {})
    return {
        "main": admins.get("main", [324157864, 994865959]),
        "support": admins.get("support", [890352247, 1050936429])
    }

def save_admins(main_ids, support_ids):
    """ذخیره لیست ادمین‌ها"""
    data = load_json()
    data["dynamic_admins"] = {
        "main": main_ids,
        "support": support_ids
    }
    save_json(data)

def add_main_admin(user_id):
    """اضافه کردن ادمین اصلی"""
    admins = load_admins()
    if user_id not in admins["main"]:
        admins["main"].append(user_id)
        save_admins(admins["main"], admins["support"])
        return True
    return False

def remove_main_admin(user_id):
    """حذف ادمین اصلی"""
    admins = load_admins()
    if user_id in admins["main"]:
        admins["main"].remove(user_id)
        save_admins(admins["main"], admins["support"])
        return True
    return False

def add_support_admin(user_id):
    """اضافه کردن پشتیبان"""
    admins = load_admins()
    if user_id not in admins["support"]:
        admins["support"].append(user_id)
        save_admins(admins["main"], admins["support"])
        return True
    return False

def remove_support_admin(user_id):
    """حذف پشتیبان"""
    admins = load_admins()
    if user_id in admins["support"]:
        admins["support"].remove(user_id)
        save_admins(admins["main"], admins["support"])

def is_main_admin(user_id):
    """چک کردن ادمین اصلی بودن"""
    return user_id in load_admins()["main"]

def is_support_admin(user_id):
    """چک کردن پشتیبان بودن"""
    return user_id in load_admins()["support"]

def get_main_admins():
    """گرفتن لیست ادمین‌های اصلی"""
    return load_admins()["main"]

def get_support_admins():
    """گرفتن لیست پشتیبان‌ها"""
    return load_admins()["support"]
