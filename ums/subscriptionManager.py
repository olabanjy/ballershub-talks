import requests
from datetime import datetime


BASE_URL = "http://91.109.117.92:8001/"


productIDDaily = "70"
productIDWeekly = "71"
productIDMonthly = "72"
telco = "MTN"
channel = "SMS"
timeStamp = datetime.now()


def mtnSubscribe(msisdn):
    try:
        if msisdn.startswith("234"):
            msisdn = msisdn.replace("234", "0", 1)

        header = {"Authorization": "Bearer ClbUlFaBwT14g2xi2URb"}

        data = {
            "product_id": productIDDaily,
            "phone": msisdn,
            "telco": telco,
            "channel": channel,
        }

        response = requests.post(
            f"{BASE_URL}api/v1/product/subscription/initiate", json=data, headers=header
        )

        return response.json()
    except Exception as e:
        print(e)
        return False


def mtnUnSubscribe(msisdn):
    try:
        if msisdn.startswith("234"):
            msisdn = msisdn.replace("234", "0", 1)

        header = {"Authorization": "Bearer ClbUlFaBwT14g2xi2URb"}

        data = {
            "product_id": productIDDaily,
            "phone": msisdn,
            "telco": telco,
        }

        response = requests.post(
            f"{BASE_URL}api/v1/product/subscription/unsubscribe",
            json=data,
            headers=header,
        )

        return response.json()
    except Exception as e:
        print(e)
        return False
