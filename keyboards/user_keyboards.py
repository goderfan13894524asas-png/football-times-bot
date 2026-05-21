def join_keyboard():

    return {
        "inline_keyboard": [
            [
                {
                    "text": "📢 عضویت در کانال",
                    "url": "https://ble.ir/footballtimes_official"
                }
            ],
            [
                {
                    "text": "✅ عضو شدم",
                    "callback_data": "check_join"
                }
            ]
        ]
    }


def rules_keyboard():

    return {
        "inline_keyboard": [
            [
                {
                    "text": "قوانین را تایید میکنم✅",
                    "callback_data": "accept_rules"
                }
            ]
        ]
    }


def confirm_keyboard():

    return {
        "inline_keyboard": [
            [
                {
                    "text": "✅ تایید",
                    "callback_data": "confirm_payment"
                },
                {
                    "text": "❌ لغو",
                    "callback_data": "cancel_payment"
                }
            ]
        ]
    }


def main_keyboard():

    return {
        "keyboard": [
            [
                {
                    "text": "📢 ثبت تبلیغات"
                },
                {
                    "text": "💵 قیمت تبلیغات"
                }
            ],
            [
                {
                    "text": "💬 پشتیبانی"
                },
                {
                    "text": "📖 راهنما"
                }
            ]
        ],
        "resize_keyboard": True
    }
