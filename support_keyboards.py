def support_panel_keyboard():
    return {
        "keyboard": [
            [
                {"text": "🟢 آنلاین شدن"},
                {"text": "🔴 آفلاین شدن"}
            ],
            [
                {"text": "📋 لیست کاربران مسدود"},
                {"text": "📊 آمار پشتیبانی"}
            ],
            [
                {"text": "🧾 تیکت‌های باز"},
                {"text": "✅ تیکت‌های بسته"}
            ],
            [
                {"text": "🔍 جستجوی کاربر"},
                {"text": "⭐ میانگین امتیازات من"}
            ],
            [
                {"text": "🗑 پاک کردن تیکت‌ها"}
            ],
            [
                {"text": "🔙 بازگشت"}
            ]
        ],
        "resize_keyboard": True
    }


def support_request_keyboard(user_id):
    return {
        "inline_keyboard": [
            [
                {
                    "text": "✅ قبول گفتگو",
                    "callback_data": f"accept_chat:{user_id}"
                }
            ]
        ]
    }


def support_chat_keyboard(user_id):
    return {
        "inline_keyboard": [
            [
                {
                    "text": "🔚 پایان گفتگو",
                    "callback_data": f"end_chat:{user_id}"
                }
            ],
            [
                {
                    "text": "🚫 بلاک کاربر",
                    "callback_data": f"block:{user_id}"
                },
                {
                    "text": "✅ آنبلاک کاربر",
                    "callback_data": f"unblock:{user_id}"
                }
            ]
        ]
    }


def rate_keyboard(admin_id):
    return {
        "inline_keyboard": [
            [
                {"text": "⭐1", "callback_data": f"rate:{admin_id}:1"},
                {"text": "⭐2", "callback_data": f"rate:{admin_id}:2"},
                {"text": "⭐3", "callback_data": f"rate:{admin_id}:3"},
                {"text": "⭐4", "callback_data": f"rate:{admin_id}:4"},
                {"text": "⭐5", "callback_data": f"rate:{admin_id}:5"}
            ]
        ]
    }