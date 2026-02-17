from django.http import (
    HttpResponse,
)
from django.views.decorators.http import require_GET, require_POST

from django.shortcuts import render, redirect

from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse

from datetime import datetime
from django.db.models import Sum


from .models import *
from .subscriptionManager import mtnSubscribe, mtnUnSubscribe
import json

from . import choices, tasks

from django.utils.crypto import get_random_string


def subscribe(request):
    try:
        if "Msisdn" in request.headers:
            msisdn = request.headers["Msisdn"]
            # get user msisdn
            print(f"redirecting {msisdn} to secureD DUI")

        # send to secureD for redirection

        res = get_random_string(length=32)
        traffic_source = "Organic Search"

        redirect_url = f"http://ng-app.com/Pinesip/daily-digest-podcast-daily-en-doi-web?origin_banner=1&trxId={res}&trfsrc={traffic_source}"

        return redirect(redirect_url)
    except Exception as ex:
        print(ex)
        return redirect("content:home")


######### Unsubscribe ###########


def cancelSubscribtion(request):
    if "Msisdn" in request.headers:
        msisdn = request.headers["Msisdn"]
        # get user msisdn

        sub = mtnUnSubscribe(msisdn)

        if sub != False:
            print("Un-Subscribtion Successfull")
            return redirect("content:home")
        else:
            print("Subscribtion UnSuccessfull")
            return redirect("content:home")
    else:
        return redirect("users:onboarding")


def after_signup(request):
    # get user msisdn
    msisdn = request.user.profile.phone
    sub = mtnSubscribe(msisdn)
    print(sub)
    # check subscription status
    ###########

    return redirect("users:awaiting_response")


def awaiting_response(request):
    template = "ums/awaiting_response.html"
    return render(request, template)


def onboarding(request):

    template = "ums/subscribe_page.html"

    context = {}

    return render(request, template, context)


def inactive_account(request):

    template = "ums/inactive_account.html"

    context = {}
    return render(request, template, context)


def fetch_stats(request):
    today = datetime.now()

    # start_date_str = "2024-06-24 00:00:01"
    the_day = request.GET.get("day", None)
    if the_day:
        date_format = "%Y-%m-%d %H:%M:%S"
        date_obj = datetime.strptime(f"{the_day} 00:00:00", date_format)

        campaing_tracker_cbt = CampaignTracker.objects.filter(
            created_at__date=date_obj.date(),
            provider=choices.CampaignProvider.CLICKBYTE.value,
            converted=True,
        ).count()

        campaing_tracker_cbt_month = CampaignTracker.objects.filter(
            created_at__month=date_obj.month,
            provider=choices.CampaignProvider.CLICKBYTE.value,
            converted=True,
        ).count()

        remarketing_today = CampaignDuplicate.objects.filter(
            created_at__date=date_obj.date(), remarketed=True
        ).count()
        remarketing_month = CampaignDuplicate.objects.filter(
            created_at__month=date_obj.month, remarketed=True
        ).count()

        campaing_tracker_neth = CampaignTracker.objects.filter(
            created_at__date=date_obj.date(),
            provider=choices.CampaignProvider.NETH.value,
            converted=True,
        ).count()

        campaing_tracker_neth_month = CampaignTracker.objects.filter(
            created_at__month=date_obj.month,
            provider=choices.CampaignProvider.NETH.value,
            converted=True,
        ).count()

        campaing_tracker_mob = CampaignTracker.objects.filter(
            created_at__date=date_obj.date(),
            provider=choices.CampaignProvider.MOBPLUS.value,
            converted=True,
        ).count()

        campaing_tracker_mob_month = CampaignTracker.objects.filter(
            created_at__month=date_obj.month,
            provider=choices.CampaignProvider.MOBPLUS.value,
            converted=True,
        ).count()

        campaing_tracker_mobedia = CampaignTracker.objects.filter(
            created_at__date=date_obj.date(),
            provider=choices.CampaignProvider.ANGELMEDIA.value,
            converted=True,
        ).count()

        campaing_tracker_mobedia_month = CampaignTracker.objects.filter(
            created_at__month=date_obj.month,
            provider=choices.CampaignProvider.ANGELMEDIA.value,
            converted=True,
        ).count()

        campaign_not = CampaignNotificationBackup.objects.filter(
            created_at__date=date_obj.date()
        ).count()

        user_prof = UserProfile.objects.filter(created_at__date=date_obj.date()).count()

        ## revenues
        datasync_qs = DataSync.objects.filter(created_at__date=date_obj.date())

        subscriptions = datasync_qs.filter(type="SYNC_NOTIFICATION")
        sub_revenue = (
            subscriptions.aggregate(total=Sum("amount"))["total"]
            if subscriptions.exists()
            else 0
        )

        unsubs = datasync_qs.filter(type="UNSUBSCRIPTION_NOTIFICATION")

        renewals = datasync_qs.filter(type="RENEWAL_NOTIFICATION")
        renewals_revenue = (
            renewals.aggregate(total=Sum("amount"))["total"] if renewals.exists() else 0
        )

        total_revenue = sub_revenue + renewals_revenue

    else:

        remarketing_today = CampaignDuplicate.objects.filter(
            created_at__month=today.month, remarketed=True
        ).count()
        remarketing_month = remarketing_today

        campaing_tracker_cbt = CampaignTracker.objects.filter(
            created_at__month=today.month,
            converted=True,
            provider=choices.CampaignProvider.CLICKBYTE.value,
        ).count()

        campaing_tracker_cbt_month = campaing_tracker_cbt

        campaing_tracker_neth = CampaignTracker.objects.filter(
            created_at__month=today.month,
            converted=True,
            provider=choices.CampaignProvider.NETH.value,
        ).count()

        campaing_tracker_neth_month = campaing_tracker_neth

        campaing_tracker_mob = CampaignTracker.objects.filter(
            created_at__month=today.month,
            converted=True,
            provider=choices.CampaignProvider.MOBPLUS.value,
        ).count()

        campaing_tracker_mob_month = campaing_tracker_mob

        campaing_tracker_mobedia = CampaignTracker.objects.filter(
            created_at__month=today.month,
            converted=True,
            provider=choices.CampaignProvider.ANGELMEDIA.value,
        ).count()

        campaing_tracker_mobedia_month = campaing_tracker_mobedia

        campaign_not = CampaignNotificationBackup.objects.filter(
            created_at__month=today.month
        ).count()

        user_prof = UserProfile.objects.filter(created_at__month=today.month).count()
        # revenue

        datasync_qs = DataSync.objects.filter(created_at__month=today.month)

        subscriptions = datasync_qs.filter(type="SYNC_NOTIFICATION")
        sub_revenue = (
            subscriptions.aggregate(total=Sum("amount"))["total"]
            if subscriptions.exists()
            else 0
        )

        unsubs = datasync_qs.filter(type="UNSUBSCRIPTION_NOTIFICATION")

        renewals = datasync_qs.filter(type="RENEWAL_NOTIFICATION")
        renewals_revenue = (
            renewals.aggregate(total=Sum("amount"))["total"] if renewals.exists() else 0
        )

        total_revenue = sub_revenue + renewals_revenue

    data = {
        "New Users Aquisition": user_prof,
        "Web Traffic Conversions[Daan]": campaing_tracker_neth,
        "Web Traffic Conversions[Daan][Month Count]": campaing_tracker_neth_month,
        "Web Traffic Conversions[MobPlus]": campaing_tracker_mob,
        "Web Traffic Conversions[MobPlus][Month Count]": campaing_tracker_mob_month,
        "Web Traffic [ANGEL MEDIA][Today]": campaing_tracker_mobedia,
        "Web Traffic [ANGEL MEDIA][Month Count]": campaing_tracker_mobedia_month,
        "Web Traffic [CLICKBYTE][Today]": campaing_tracker_cbt,
        "Web Traffic [CLICKBYTE][Month Count]": campaing_tracker_cbt_month,
        "Web Traffic [Re-Marketing][Today]": remarketing_today,
        "Web Traffic [Re-Marketing][Month Count]": remarketing_month,
        "campaign_notifications": campaign_not,
        "Revenue Data": {
            "New Subscribtion Count": subscriptions.count(),
            "New Subscribtion Revenue": sub_revenue,
            "Renewal Count": renewals.count(),
            "Renewal Revenue": renewals_revenue,
            "Unsubscription Count": unsubs.count(),
            "Total Revenue": total_revenue,
        },
    }
    return JsonResponse(data)


def generate_report(request):

    tasks.fetch_report.delay()

    return HttpResponse(200)


# DATA SYNC
@require_POST
@csrf_exempt
def data_sync(request):
    print("Receiving transaction")

    the_data = json.loads(request.body)
    print(the_data)

    if the_data.get("type"):
        print("saving data sync notification")
        tasks.process_datasync.delay(the_data)
    else:
        print("saving secure D notifications")
        CampaignNotificationBackup.objects.create(req_body=f"{the_data}")
    return JsonResponse({"status": 200, "message": "ok"})


# CampaignNotificationBackup
@require_POST
@csrf_exempt
def campaign_notification(request):
    try:
        CampaignNotificationBackup.objects.create(req_body=f"{request.body}")
    except:
        pass

    return HttpResponse(200)


def cleanup_data(request):

    month_num = request.GET.get("month", None)

    tasks.delete_redundant_records.delay(month_num)

    return HttpResponse(200)


def reconcile_subscribtions(request):

    tasks.reconcile_subscribtion.delay()

    return HttpResponse(200)


@require_GET
@csrf_exempt
def check_sub_status(request):
    data = dict(request.headers)

    print(request.headers)
    print(data)
    print(type(data))

    json_resp = {}

    msisdn_data = data.get("Msisdn")
    if msisdn_data:
        msisdn = data["Msisdn"]
        if msisdn.startswith("0") and len(msisdn) == 11:
            msisdn = msisdn.replace("0", "234", 1)

        theUser, _ = UserProfile.objects.get_or_create(phone=msisdn)
        fetchSubscribtion = UserSubscribtion.objects.filter(user=theUser)
        if fetchSubscribtion.exists():
            theSub = fetchSubscribtion.first()
            if theSub.sub_active == True:
                json_resp.update(
                    {
                        "status": True,
                        "message": "Msisdn has active subscribtion",
                    }
                )
            else:
                json_resp.update(
                    {
                        "status": False,
                        "message": "No Active subscribtion",
                    }
                )
        else:
            json_resp.update(
                {
                    "status": False,
                    "message": "No Active subscribtion",
                }
            )
    else:
        json_resp.update(
            {
                "status": False,
                "message": "No Active subscribtion",
            }
        )

    return JsonResponse(
        data=json_resp,
    )


def fetch_campaign_behaviour(request):

    start = request.GET.get("start", None)
    end = request.GET.get("end", None)

    if not start:
        return JsonResponse({"status": 400, "error": "start date is required"})
    if not end:
        return JsonResponse({"status": 400, "error": "end date is required"})

    if not datetime.strptime(start, "%Y-%m-%d"):
        return JsonResponse({"status": 400, "error": "invalid start date"})
    if not datetime.strptime(end, "%Y-%m-%d"):
        return JsonResponse({"status": 400, "error": "invalid end date"})

    tasks.campaign_behaviour.delay(start, end)

    return JsonResponse({"status": 200, "message": "Processing report!"})


def campaign_partner_user_behaviour_query(request):

    month_num = request.GET.get("month_num", None)

    tasks.campaign_partner_user_behaviour.delay(month_num)

    return JsonResponse({"status": 200, "message": "Processing report!"})


def fetch_sub_channel(request):
    channel = request.GET.get("channel", None)
    month_num = request.GET.get("month_num", None)

    print(channel, month_num)

    dtsync = DataSync.objects.filter(type="SYNC_NOTIFICATION")

    if channel:
        data_sync = data_sync.filter(channel=str(channel))
    if month_num:
        data_sync = data_sync.filter(created_at__month=int(month_num))

    return_resp = {"channel": channel, "count": dtsync.count()}

    return JsonResponse(return_resp)


def fetch_ussd_subscribers_query(request):
    tasks.fetch_ussd_subscribers.delay()

    return JsonResponse({"status": 200, "message": "Processing report!"})


def campaign_partner_user_behaviour_compiled_query(request):
    from .tasks import campaign_partner_user_behaviour_compilation

    month_num = request.GET.get("month_num", None)

    campaign_partner_user_behaviour_compilation.delay(month_num)

    return JsonResponse({"status": 200, "message": "Processing report!"})


def reconcile_subscribtions(request):

    tasks.reconcile_subscribtion.delay()

    return HttpResponse(200)


def get_cr_data(request):

    today = datetime.now()

    # start_date_str = "2024-06-24 00:00:01"
    the_day = request.GET.get("day", None)
    if the_day:
        date_format = "%Y-%m-%d %H:%M:%S"
        date_obj = datetime.strptime(f"{the_day} 00:00:00", date_format).date()
    else:
        date_obj = today.date()

    partner = request.GET.get("partner")
    if not partner:
        return JsonResponse({"status": 400, "message": "Partner required"})

    tracks_qs = CampaignTracker.objects.filter(
        created_at__date=date_obj, provider=partner
    )
    unique_tracks = tracks_qs.filter(occurence=0)
    converted = tracks_qs.filter(converted=True)

    traffic_hits = tracks_qs.count()
    unique_traffic = unique_tracks.count()
    converted_count = converted.count()

    cr = (converted_count / traffic_hits) * 100

    data = {
        "Traffic Hit": traffic_hits,
        "Unique Traffic Hits": unique_traffic,
        "Converted": converted_count,
        "CR": cr,
    }
    return JsonResponse(data)


def export_user_msisdn_query(request):

    month_num = request.GET.get("month")

    tasks.export_user_msisdn.delay(month_num)

    if not month_num:
        return JsonResponse({"status": 400, "message": "Month required"})

    return JsonResponse({"status": 200, "message": "Processing report!"})


def user_activation_report_query(request):

    month_num = request.GET.get("month")

    if not month_num:
        return JsonResponse({"status": 400, "message": "Month required"})

    tasks.user_behaviour_report.delay(month_num)

    return JsonResponse({"status": 200, "message": "Processing report!"})


def export_all_msisdn_query(request):

    tasks.export_all_msisdns.delay()

    return JsonResponse({"status": 200, "message": "Processing report!"})


@require_POST
@csrf_exempt
def callback_notification(request):
    """Receive provider callback JSON and save to CallbackNotification."""
    try:
        body = (
            request.body.decode("utf-8")
            if isinstance(request.body, (bytes, bytearray))
            else request.body
        )
        data = json.loads(body)
    except Exception:
        return JsonResponse(
            {"status": 400, "error": "invalid json"},
            status=400,
        )

    msisdn = data.get("msisdn")
    activation_raw = data.get("activation")
    activation = None
    if activation_raw is not None:
        try:
            activation = int(activation_raw)
        except (ValueError, TypeError):
            activation = None

    productId = data.get("productId") or data.get("productID")
    description = data.get("description")
    timestamp = data.get("timestamp")
    trxID = data.get("trxID") or data.get("trxId")
    sequenceNo = data.get("sequenceNo")

    try:
        CallbackNotification.objects.create(
            msisdn=msisdn,
            activation=activation,
            product_id=productId,
            description=description,
            timestamp=timestamp,
            trx_id=trxID,
            sequence_no=sequenceNo,
            raw_payload=data,
        )
        return JsonResponse({"status": 200, "message": "Saved"})
    except Exception:
        return JsonResponse(
            {"status": 500, "error": "Internal server error"},
            status=500,
        )


@require_POST
@csrf_exempt
def data_sync_v2(request):
    tasks.share_datasync.delay(request.body.decode("utf-8"))
    the_data = json.loads(request.body)

    tasks.process_datasync.delay(the_data)

    return HttpResponse(200)
