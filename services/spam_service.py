import time
from collections import defaultdict, deque

user_messages = defaultdict(deque)
banned_users = {}


def anti_spam(user_id):
    now = time.time()

    if user_id in banned_users:
        if now < banned_users[user_id]:
            return "banned"
        else:
            del banned_users[user_id]

    q = user_messages[user_id]
    q.append(now)

    while q and now - q[0] > 10:
        q.popleft()

    if len(q) >= 10:
        banned_users[user_id] = now + (3 * 24 * 60 * 60)
        return "ban"

    if len(q) >= 5:
        return "warn"

    return "ok"
