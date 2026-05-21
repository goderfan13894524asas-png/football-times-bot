from collections import defaultdict

# وضعیت کاربران
user_states = defaultdict(dict)

# کاربران
users = set()

# کاربران بلاک
blocked_users = set()

# کاربران VIP
vip_users = set()

# چت‌های فعال پشتیبانی (در حافظه)
active_chats = {}

# امتیازات (در حافظه موقت)
rated_users = {}

# تبلیغات تایید شده
approved_ads = []

# صف تبلیغات
ads_queue = []

# وضعیت ادمین‌های پشتیبانی (آنلاین/آفلاین)
support_admins = {}

# آمار
stats = {
    "total_users": 0,
    "total_ads": 0,
    "total_tickets": 0
}
