import requests

MERCHANT_ID = "YOUR_MERCHANT_ID"

ZARINPAL_REQUEST_URL = (
    "https://api.zarinpal.com/pg/v4/payment/request.json"
)

ZARINPAL_VERIFY_URL = (
    "https://api.zarinpal.com/pg/v4/payment/verify.json"
)

CALLBACK_URL = "https://yourdomain.com/callback"


def create_payment(amount, description, phone=None):

    payload = {
        "merchant_id": MERCHANT_ID,
        "amount": amount,
        "callback_url": CALLBACK_URL,
        "description": description,
        "metadata": {
            "mobile": phone
        }
    }

    try:

        r = requests.post(
            ZARINPAL_REQUEST_URL,
            json=payload
        )

        data = r.json()

        if (
            data["data"]["code"] == 100
        ):

            authority = data["data"]["authority"]

            payment_url = (
                f"https://www.zarinpal.com/pg/StartPay/{authority}"
            )

            return {
                "ok": True,
                "url": payment_url,
                "authority": authority
            }

        return {
            "ok": False
        }

    except Exception as e:

        print("Zarinpal Error:", e)

        return {
            "ok": False
        }


def verify_payment(amount, authority):

    payload = {
        "merchant_id": MERCHANT_ID,
        "amount": amount,
        "authority": authority
    }

    try:

        r = requests.post(
            ZARINPAL_VERIFY_URL,
            json=payload
        )

        data = r.json()

        if data["data"]["code"] == 100:

            return {
                "ok": True,
                "ref_id": data["data"]["ref_id"]
            }

        return {
            "ok": False
        }

    except Exception as e:

        print("Verify Error:", e)

        return {
            "ok": False
        }
