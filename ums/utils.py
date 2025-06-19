from .models import UserProfile
import uuid

def fetch_active_user(request):
    if "Msisdn" in request.headers:
        msisdn = request.headers["Msisdn"]
        if msisdn.startswith("0") and len(msisdn) == 11:
            msisdn = msisdn.replace("0", "234", 1)
        the_user, created = UserProfile.objects.get_or_create(phone=msisdn)
        return the_user
    return None

def clean_uuid_int(level:int) -> str:
    return str(uuid.uuid4().int >> 90)[:level]