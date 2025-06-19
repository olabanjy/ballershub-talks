from celery import shared_task

import os
import traceback

from datetime import datetime, date, timedelta
from django.utils import timezone
import calendar
from django.db.models import Sum
from dateutil.relativedelta import relativedelta

import pandas as pd
import requests


from content.mail import send_email

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


# from celery import shared_task

from .models import (
    DataSync,
    UserSubscribtion,
    WebhookBackup,
    CampaignNotificationBackup,
    CampaignTracker,
    CampaignDuplicate,
    UserProfile,
)
from . import choices


@shared_task
def fetch_report():

    try:

        month_first_day = date.today().replace(day=1)

        yesterday = date.today() - timedelta(days=1)

        date_list = []

        while month_first_day <= yesterday:
            date_list.append(month_first_day)
            month_first_day += timedelta(days=1)
        else:
            last_month_last_day = yesterday.replace(
                day=calendar.monthrange(date.today().year, date.today().month)[1]
            )
            last_month_first_day = yesterday.replace(day=1)
            while last_month_first_day <= last_month_last_day:
                date_list.append(last_month_first_day)
                last_month_first_day += timedelta(days=1)

        curr_path = os.path.dirname(os.path.realpath(__file__))

        report_path = os.path.join(curr_path, "reports/")

        filename = f'{report_path}Daily_Report_{yesterday.strftime("%d/%m/%Y").replace("/", "")}.xlsx'

        ####
        # do your workings here

        data_cols = [
            "Date",
            "Total revenue",
            "Active user",
            "New users",
            "Deactivation",
        ]

        data = {}

        for dt in data_cols:
            data[dt] = []

        logger.info(date_list)

        for dte in date_list:
            ### Fetch data cols and data

            data["Date"].append(dte.strftime("%d/%m/%Y"))

            datasync_qs = DataSync.objects.filter(created_at__date=dte)

            subscriptions = datasync_qs.filter(type="SYNC_NOTIFICATION")
            sub_revenue = (
                subscriptions.aggregate(total=Sum("amount"))["total"]
                if subscriptions.exists()
                else 0
            )

            unsubs = datasync_qs.filter(type="UNSUBSCRIPTION_NOTIFICATION")

            renewals = datasync_qs.filter(type="RENEWAL_NOTIFICATION")
            renewals_revenue = (
                renewals.aggregate(total=Sum("amount"))["total"]
                if renewals.exists()
                else 0
            )

            total_revenue = sub_revenue + renewals_revenue
            data["Total revenue"].append(total_revenue)
            data["New users"].append(subscriptions.count())
            data["Deactivation"].append(unsubs.count())

            # all active users
            active_subs = UserSubscribtion.objects.filter(
                sub_active=True, created_at__date__lte=dte
            ).count()
            data["Active user"].append(active_subs)

            # subscribtion count

        new_df = pd.DataFrame(
            {key: pd.Series(value, dtype=object) for key, value in data.items()},
            columns=data_cols,
        )
        new_df.to_excel(filename, index=False, header=True)

        logger.info(report_path, os.path.exists(report_path), filename)

        ### send email

        EMAIL_SUBJECT = f'Daily Digest Report Today, {yesterday.strftime("%d/%m/%Y")}'
        REPORTING_MSG = """
            Hello Admin,
            Please find the attached report for today.
            Regards.
            """
        send_email(
            recipients=[
                "olushola@scriptdeskng.com",
                "bernny@pinesip.com.ng",
                "techsupport@pinesip.com.ng",
                ###
            ],
            subject=EMAIL_SUBJECT,
            body_text=REPORTING_MSG,
            attachment=filename,
            attachment_mime_type="text/csv",
            quiet=False,
        )

    except Exception as e:
        logger.warning(traceback.format_exc())
        logger.warning(e)


@shared_task
def delete_redundant_records(num_of_month: None):

    try:
        nos_of_month = 3
        if num_of_month:
            nos_of_month = int(num_of_month)
        # get 3 months ago
        past_months = datetime.now() - relativedelta(months=nos_of_month)
        # fetch webhooks backup
        WebhookBackup.objects.filter(created_at__lte=past_months).delete()
        # fetch campaign trackers
        CampaignNotificationBackup.objects.filter(created_at__lte=past_months).delete()
        # clear campaign notifications without msisdn
        CampaignTracker.objects.filter(msisdn__isnull=True).delete()
    except Exception as ex:
        logger.warning(traceback.format_exc())
        logger.warning(ex)


@shared_task
def campaign_behaviour(start_date, end_date):

    from xhtml2pdf import pisa

    from io import BytesIO

    from django.template.loader import get_template

    logger.info(start_date, end_date)

    if not (start_date or end_date):
        logger.info(f"start or end date required")
        return

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    logger.info(f"pulling reports between {start_date} and {end_date}")
    if end_date <= start_date:
        logger.info(f"end date should be greater than start date")
        return
    if (end_date - start_date).days > 30:
        logger.info(f"max days allowed is 30")
        return

    # pull all datasync subscribtion for each provider
    neth_subscriptions = []
    mobplus_subscriptions = []

    neth_unsubs = []
    mobplus_unsubs = []

    notification_qs = DataSync.objects.filter(created_at__range=(start_date, end_date))

    campaign_tracker = CampaignTracker.objects.filter(
        created_at__range=(start_date, end_date)
    )

    sub_notifications = notification_qs.filter(
        type="SYNC_NOTIFICATION", campaign_tracker__isnull=False
    )
    for sub in sub_notifications:
        if sub.campaign_tracker.provider == choices.CampaignProvider.NETH.value:
            if sub.phone not in neth_subscriptions:
                neth_subscriptions.append(sub.phone)

        elif sub.campaign_tracker.provider == choices.CampaignProvider.MOBPLUS.value:
            if sub.phone not in mobplus_subscriptions:
                mobplus_subscriptions.append(sub.phone)

    unsub_notifications = notification_qs.filter(type="UNSUBSCRIPTION_NOTIFICATION")
    for unsub in unsub_notifications:
        if unsub.phone in neth_subscriptions:
            if unsub.phone not in neth_unsubs:
                neth_unsubs.append(unsub.phone)

        elif unsub.phone in mobplus_subscriptions:
            if unsub.phone not in mobplus_unsubs:
                mobplus_unsubs.append(unsub.phone)

    export_data = {
        "tc_clicks": campaign_tracker.filter(
            provider=choices.CampaignProvider.NETH.value
        ).count(),
        "tc_subs": len(neth_subscriptions),
        "tc_unsubs": len(neth_unsubs),
        "mobplus_clicks": campaign_tracker.filter(
            provider=choices.CampaignProvider.MOBPLUS.value
        ).count(),
        "mobplus_subs": len(mobplus_subscriptions),
        "mobplus_unsubs": len(mobplus_unsubs),
        "start_date": start_date,
        "end_date": end_date,
    }

    curr_path = os.path.dirname(os.path.realpath(__file__))
    report_path = os.path.join(curr_path, "reports/")

    filename = f'{report_path}campaign_behaviour{end_date.strftime("%Y-%m-%d").replace("-", "")}.pdf'

    template = get_template("ums/campaign_report.html")

    html = template.render(export_data)

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if pdf.err:
        logger.error(f"Error generating PDF {pdf.err}")
        return

    with open(filename, "wb+") as output:
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), output)

    # send email

    start_date_obj = start_date.date()
    end_date_obj = end_date.date()

    EMAIL_SUBJECT = f"Campaign Behaviour[{start_date_obj, end_date_obj}]"
    REPORTING_MSG = """
        Hello Admin,
        Please find the attached report for requested date range.
        Regards.
        """

    try:
        send_email(
            recipients=[
                "olushola@scriptdeskng.com",
                "bernny@pinesip.com.ng",
            ],
            subject=EMAIL_SUBJECT,
            body_text=REPORTING_MSG,
            attachment=filename,
            attachment_mime_type="application/pdf",
            quiet=False,
        )
    except Exception as ex:
        logger.error(f"Error sending email: {ex}")


@shared_task
def handle_occurence(promo_id):
    try:
        promo = CampaignTracker.objects.get(id=promo_id)
        if (
            CampaignTracker.objects.filter(msisdn=promo.msisdn)
            .exclude(id=promo.id)
            .exists()
        ):
            promo.occurence += 1
            promo.save()
            duplicate, _ = CampaignDuplicate.objects.get_or_create(
                msisdn=promo.msisdn, provider=promo.provider
            )
            duplicate.occurence += 1
            duplicate.save()

    except Exception:
        logger.error(traceback.format_exc())


@shared_task
def handle_remarketing(msisdn, provider):
    try:
        user_prof = UserProfile.objects.filter(phone=msisdn).first()
        user_sub = UserSubscribtion.objects.filter(user=user_prof).first()

        duplicate, _ = CampaignDuplicate.objects.get_or_create(
            msisdn=msisdn,
            provider=provider,
        )
        duplicate.remarketed = True
        duplicate.last_subscribtion = user_sub.ends_date
        duplicate.save()

    except Exception:
        logger.error(traceback.format_exc())


@shared_task
def reconcile_subscribtion():
    try:
        # fetch all ended User Subscription

        today = date.today()
        subs = UserSubscribtion.objects.filter(
            ends_date__date__lt=today, sub_active=True
        )
        for sub in subs:
            logger.info(f"{sub.user} ended at {sub.ends_date}")
            sub.sub_active = False
            sub.save()
            sub.user.sub_status = "inactive"
            sub.user.save()

        logger.info(f"done processing {subs.count()}")

    except Exception:
        logger.error(traceback.format_exc())


# process datasyncs


@shared_task
def process_datasync(payload):
    try:
        logger.info(f"handling payload {payload}")

        new_sync = WebhookBackup.objects.create(
            req_body=f"{payload}", operator="Forthsoft"
        )

        new_sync_data = DataSync.objects.create(
            type=payload["type"],
            telco=payload["telco"],
            product_id=payload["product"]["id"],
            product_name=payload["product"]["name"],
            product_not_type=payload["product"]["type"],
            product_sub_type=payload["product"]["subscription_type"],
            phone=payload["details"]["phone"],
            telco_ref=payload["details"]["telco_ref"],
            operator="Forthsoft",
        )

        if payload["details"]["amount"]:
            new_sync_data.amount = int(payload["details"]["amount"])
        if payload["details"]["channel"]:
            new_sync_data.channel = payload["details"]["channel"]
        if payload["details"]["date"]:
            new_sync_data.sub_date = payload["details"]["date"]
        if payload["details"]["auto_renewal"]:
            new_sync_data.auto_renewal = payload["details"]["auto_renewal"]
        if payload["details"]["expiry"]:
            new_sync_data.sub_expiry = payload["details"]["expiry"]
        if payload["details"].get("bearerId"):
            new_sync_data.bearer_id = payload["details"]["bearerId"]
        if new_sync:
            new_sync_data.webhook_backup = new_sync

        new_sync_data.save()

        if payload["telco"] == "MTN":

            new_sync.telco = "MTN"
            new_sync.save()

            not_type = payload["type"]  # UNSUBSCRIPTION_NOTIFICATION, SYNC_NOTIFICATION
            msisdn = payload["details"]["phone"]

            # "%Y-%m-%dT%H:%M:%S.%fZ",

            prod_type = payload["product"]["type"]
            # sub_type = the_data["product"]["subscription_type"]

            if msisdn.startswith("0") and len(msisdn) == 11:
                msisdn = msisdn.replace("0", "234", 1)

            # fetch user
            theUser, user_created = UserProfile.objects.get_or_create(phone=msisdn)
            theUser.telco = "MTN"
            theUser.save()
            userSub, sub_created = UserSubscribtion.objects.get_or_create(user=theUser)

            if not_type == "SYNC_NOTIFICATION":

                start_date = payload["details"]["date"]
                start_datetime = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
                end_date = payload["details"]["expiry"]
                end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

                # sub_amount = int(the_data["details"]["amount"]) / 100

                userSub.sub_active = True
                userSub.starts_date = start_datetime
                userSub.ends_date = end_datetime

                if not sub_created:
                    userSub.first_sub = True
                    if (
                        payload["details"].get("auto_renewal")
                        and payload["details"]["auto_renewal"] == True
                    ):
                        userSub.auto_renewal = True

                userSub.save()

                theUser.sub_status = "active"
                theUser.save()

                # find campaign tracker
                tracker_qs = CampaignTracker.objects.filter(msisdn=msisdn)

                if tracker_qs.exists():
                    tracker = tracker_qs.last()
                    if tracker.provider == choices.CampaignProvider.MOBPLUS.value:
                        # process mobplus
                        process_mobplus_postback.delay(
                            tracker.id, new_sync_data.id, userSub.id
                        )
                    elif tracker.provider == choices.CampaignProvider.NETH.value:
                        process_neth_postback.delay(
                            tracker.id, new_sync_data.id, userSub.id
                        )
                    elif tracker.provider == choices.CampaignProvider.ANGELMEDIA.value:
                        process_angel_media_postback.delay(
                            tracker.id, new_sync_data.id, userSub.id
                        )
                    elif tracker.provider == choices.CampaignProvider.CLICKBYTE.value:
                        process_clickbyte_postback.delay(
                            tracker.id, new_sync_data.id, userSub.id
                        )
                    elif tracker.provider == choices.CampaignProvider.VISIONTREK.value:
                        process_visiontrek_postback.delay(
                            tracker.id, new_sync_data.id, userSub.id
                        )
            elif not_type == "UNSUBSCRIPTION_NOTIFICATION":

                userSub.sub_active = False
                userSub.save()

                theUser.sub_status = "inactive"
                theUser.save()
            elif not_type == "RENEWAL_NOTIFICATION":
                """
                b'{"type":"RENEWAL_NOTIFICATION","telco":"MTN","action":"NONE","shortcode":null,"product":{"id":70,"name":"Magic Box Daily","identity":"PD-16541987951000","type":"SUBSCRIPTION","subscription_type":"ONETIME_AND_RECURRING","status":"LIVE"},"details":{"phone":"2347047344879","amount":5000,"channel":"system-renewal","date":"2023-01-07 08:58","expiry":"2023-01-08 08:58","auto_renewal":true,"telco_status_code":"0","telco_ref":"upstream_paid_2617724eebdbc3e8"}}'
                """
                start_date = payload["details"]["date"]
                start_datetime = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
                end_date = payload["details"]["expiry"]
                end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

                userSub.sub_active = True

                userSub.starts_date = start_datetime
                userSub.ends_date = end_datetime

                userSub.first_sub = False
                userSub.renewal_sub = True
                if (
                    payload["details"].get("auto_renewal")
                    and payload["details"]["auto_renewal"] == True
                ):
                    userSub.auto_renewal = True

                userSub.save()

                theUser.sub_status = "active"
                theUser.save()
        elif payload["telco"] == "AIRTEL":

            new_sync.telco = "AIRTEL"
            new_sync.save()

        logger.info(f"done processing {new_sync_data.phone}")
    except Exception as ex:
        logger.error(ex)


# process neth postback


@shared_task
def process_neth_postback(tracker_id, sync_id, sub_id):
    try:
        data_sync = DataSync.objects.get(id=sync_id)
        user_sub = UserSubscribtion.objects.get(id=sub_id)
        theUser = user_sub.user
        sub_amount = "0.40"
        today = timezone.now()
        # check campaign tracker is msisdn is there
        find_promo_msisdn = CampaignTracker.objects.get(id=tracker_id)

        if (
            not CampaignDuplicate.objects.filter(msisdn=find_promo_msisdn).exists()
            and find_promo_msisdn.converted == False
            and find_promo_msisdn.is_convertable == True
        ):

            postbackUrl = f"https://postback.level23.nl/?currency=USD&handler=11403&hash=b39e748e7ccc7783fbf7ee7c8f26eda8&tracker={find_promo_msisdn.click_id}"

            requests.get(postbackUrl)
            find_promo_msisdn.converted = True

            find_promo_msisdn.converted_at = today

            find_promo_msisdn.amt = sub_amount
            find_promo_msisdn.save()

            data_sync.campaign_tracker = find_promo_msisdn
            data_sync.save()

            theUser.traffic_source = choices.CampaignProvider.NETH.value
            theUser.save()
            user_sub.traffic_source = choices.CampaignProvider.NETH.value
            user_sub.save()

    except Exception as ex:
        logger.error(ex)


# process mobplus postback
@shared_task
def process_mobplus_postback(tracker_id, sync_id, sub_id):
    try:
        data_sync = DataSync.objects.get(id=sync_id)
        user_sub = UserSubscribtion.objects.get(id=sub_id)
        theUser = user_sub.user
        sub_amount = "0.40"
        today = timezone.now()

        # check campaign tracker is msisdn is there
        find_promo_msisdn = CampaignTracker.objects.get(id=tracker_id)

        if (
            not CampaignDuplicate.objects.filter(msisdn=find_promo_msisdn).exists()
            and find_promo_msisdn.converted == False
            and find_promo_msisdn.is_convertable == True
        ):
            postbackUrl = f"http://m.mobplus.net/c/p/9170b3d7bc4a4b11bb8761b02db15ba6?txid={find_promo_msisdn.click_id}&pubid={find_promo_msisdn.pubid}&amt={find_promo_msisdn.amt}&currency={find_promo_msisdn.currency}"

            requests.get(postbackUrl)

            find_promo_msisdn.converted = True

            find_promo_msisdn.converted_at = today

            # find_promo_msisdn.amt = sub_amount
            find_promo_msisdn.save()

            data_sync.campaign_tracker = find_promo_msisdn
            data_sync.save()

            theUser.traffic_source = choices.CampaignProvider.MOBPLUS.value
            theUser.save()
            user_sub.traffic_source = choices.CampaignProvider.MOBPLUS.value
            user_sub.save()
    except Exception as ex:
        logger.error(ex)


# process angel media postback
@shared_task
def process_angel_media_postback(tracker_id, sync_id, sub_id):
    try:
        data_sync = DataSync.objects.get(id=sync_id)
        user_sub = UserSubscribtion.objects.get(id=sub_id)
        theUser = user_sub.user
        sub_amount = "0.40"
        today = timezone.now()

        # check campaign tracker is msisdn is there
        find_promo_msisdn = CampaignTracker.objects.get(id=tracker_id)

        if (
            not CampaignDuplicate.objects.filter(msisdn=find_promo_msisdn).exists()
            and find_promo_msisdn.converted == False
            and find_promo_msisdn.is_convertable == True
        ):

            postbackUrl = f"http://postback.rustmobi.com/pb/408?click_id={find_promo_msisdn.click_id}&payout={sub_amount}"
            requests.get(postbackUrl)

            find_promo_msisdn.converted = True

            find_promo_msisdn.converted_at = today

            find_promo_msisdn.amt = sub_amount
            find_promo_msisdn.save()

            data_sync.campaign_tracker = find_promo_msisdn
            data_sync.save()

            theUser.traffic_source = choices.CampaignProvider.ANGELMEDIA.value
            theUser.save()
            user_sub.traffic_source = choices.CampaignProvider.ANGELMEDIA.value
            user_sub.save()
    except Exception as ex:
        logger.error(ex)


@shared_task
def campaign_partner_user_behaviour(month):
    # fetch all campaign partner
    partners = [
        # choices.CampaignProvider.ANGELMEDIA.value,
        # choices.CampaignProvider.MOBIDEA.value,
        choices.CampaignProvider.MOBPLUS.value,
        # choices.CampaignProvider.NETH.value,
    ]

    result_data = {}

    for partner in partners:
        # result_data.update({f"{partner}": ""})
        patner_campaign = CampaignTracker.objects.filter(
            converted=True, provider=partner, created_at__month=month
        ).distinct("msisdn")
        patner_msisdns = []
        for val in patner_campaign:
            patner_msisdns.append(val.msisdn)

        # find their datasync
        total_partner_revenue = 0
        for msisdn in patner_msisdns:
            datasync_rev = DataSync.objects.filter(
                phone=msisdn, created_at__month=month
            ).aggregate(total=Sum("amount"))["total"]
            total_partner_revenue += int(datasync_rev) if datasync_rev else 0

        all_partner_inactive = UserProfile.objects.filter(
            phone__in=patner_msisdns, sub_status="inactive"
        ).count()

        result_data.update(
            {
                f"{partner}": {
                    "total_partner_revenue": total_partner_revenue,
                    "all_partner_inactive": all_partner_inactive,
                    "total_msisdn_count": len(patner_msisdns),
                }
            }
        )
    logger.info(result_data)

    try:
        EMAIL_SUBJECT = "Campaign Partner user summary[DailyDigest] "
        REPORTING_MSG = f"""
            Hello Admin,
            Please find the attached query result.
            {result_data}
            Regards.
            """
        send_email(
            recipients=[
                "olushola@scriptdeskng.com",
                "bernny@pinesip.com.ng",
            ],
            subject=EMAIL_SUBJECT,
            body_text=REPORTING_MSG,
            quiet=False,
        )

    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(e)


@shared_task
def fetch_ussd_subscribers():

    dtsync = (
        DataSync.objects.filter(
            type__in=["RENEWAL_NOTIFICATION", "SYNC_NOTIFICATION"],
            channel__in=["SecureD"],
        )
        # .exclude(channel__in=["SecureD"])
        .all().distinct("phone")
    )
    logger.info(f"count is {dtsync.count()}")

    data_cols = ["Date", "MSISDN", "Channel"]

    data = {}

    for dt in data_cols:
        data[dt] = []

    curr_path = os.path.dirname(os.path.realpath(__file__))

    report_path = os.path.join(curr_path, "reports/")

    filename = f"{report_path}upstream_subscribers.xlsx"

    for val in dtsync:
        data["Date"].append(val.created_at.strftime("%d/%m/%Y"))
        data["MSISDN"].append(val.phone)
        data["Channel"].append(val.channel)

    new_df = pd.DataFrame(
        {key: pd.Series(value, dtype=object) for key, value in data.items()},
        columns=data_cols,
    )
    new_df.to_excel(filename, index=False, header=True)

    logger.info(report_path, os.path.exists(report_path), filename)

    ### send email

    EMAIL_SUBJECT = f"Daily Digest Subscribers report"
    REPORTING_MSG = """
        Hello Admin,
        Please find the attached report for today.
        Regards.
        """
    send_email(
        recipients=[
            "techsupport@pinesip.com.ng",
            "olushola@scriptdeskng.com",
            "bernny@pinesip.com.ng",
            ###
        ],
        subject=EMAIL_SUBJECT,
        body_text=REPORTING_MSG,
        attachment=filename,
        attachment_mime_type="text/csv",
        quiet=False,
    )


@shared_task
def campaign_partner_user_behaviour_compilation(month):
    # fetch all campaign partner
    partners = [
        # choices.CampaignProvider.ANGELMEDIA.value,
        # choices.CampaignProvider.MOBIDEA.value,
        choices.CampaignProvider.MOBPLUS.value,
        # choices.CampaignProvider.NETH.value,
    ]

    result_data = {}

    for partner in partners:
        # result_data.update({f"{partner}": ""})
        patner_campaign = CampaignTracker.objects.filter(
            converted=True, provider=partner, created_at__month__gte=month
        ).distinct("msisdn")
        patner_msisdns = []
        for val in patner_campaign:
            patner_msisdns.append(val.msisdn)

        # find their datasync
        total_partner_revenue = 0
        for msisdn in patner_msisdns:
            datasync_rev = DataSync.objects.filter(phone=msisdn).aggregate(
                total=Sum("amount")
            )["total"]
            total_partner_revenue += int(datasync_rev) if datasync_rev else 0

        all_partner_inactive = UserProfile.objects.filter(
            phone__in=patner_msisdns, sub_status="inactive"
        ).count()

        result_data.update(
            {
                f"{partner}": {
                    "total_partner_revenue": total_partner_revenue,
                    "all_partner_inactive": all_partner_inactive,
                    "total_msisdn_count": len(patner_msisdns),
                }
            }
        )
    logger.info(result_data)

    try:
        EMAIL_SUBJECT = "Daily Digest Compiled Campaign Partner user summary "
        REPORTING_MSG = f"""
            Hello Admin,
            Please find the attached query result.
            {result_data}
            Regards.
            """
        send_email(
            recipients=[
                "olushola@scriptdeskng.com",
                "bernny@pinesip.com.ng",
            ],
            subject=EMAIL_SUBJECT,
            body_text=REPORTING_MSG,
            quiet=False,
        )

    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(e)


@shared_task
def reconcile_subscribtion_deprecated():
    try:
        # fetch all ended User Subscription

        today = date.today()
        subs = UserSubscribtion.objects.filter(ends_date__date__lt=today)
        for sub in subs:
            logger.info(f"{sub.user} ended at {sub.ends_date}")
            sub.sub_active = False
            sub.save()
            sub.user.sub_status = "inactive"
            sub.user.save()

        logger.info(f"done processing {subs.count()}")

    except Exception:
        logger.error(traceback.format_exc())


@shared_task
def process_clickbyte_postback(tracker_id, sync_id, sub_id):
    try:
        data_sync = DataSync.objects.get(id=sync_id)
        user_sub = UserSubscribtion.objects.get(id=sub_id)
        theUser = user_sub.user
        sub_amount = "0.36"
        today = timezone.now()

        # check campaign tracker is msisdn is there
        find_promo_msisdn = CampaignTracker.objects.get(id=tracker_id)

        if (
            not CampaignDuplicate.objects.filter(msisdn=find_promo_msisdn).exists()
            and find_promo_msisdn.converted == False
            and find_promo_msisdn.is_convertable == True
        ):
            postbackUrl = postbackUrl = (
                f"https://weighting-gentosh.com/postback?cid={find_promo_msisdn.click_id}&payout={sub_amount}"
            )

            requests.get(postbackUrl)

            find_promo_msisdn.converted = True

            find_promo_msisdn.converted_at = today

            # find_promo_msisdn.amt = sub_amount
            find_promo_msisdn.save()

            data_sync.campaign_tracker = find_promo_msisdn
            data_sync.save()

            theUser.traffic_source = choices.CampaignProvider.CLICKBYTE.value
            theUser.save()
            user_sub.traffic_source = choices.CampaignProvider.CLICKBYTE.value
            user_sub.save()
    except Exception as ex:
        logger.error(ex)


@shared_task
def process_visiontrek_postback(tracker_id, sync_id, sub_id):
    try:
        data_sync = DataSync.objects.get(id=sync_id)
        user_sub = UserSubscribtion.objects.get(id=sub_id)
        theUser = user_sub.user
        sub_amount = "0.20"
        today = timezone.now()

        # check campaign tracker is msisdn is there
        find_promo_msisdn = CampaignTracker.objects.get(id=tracker_id)

        if (
            not CampaignDuplicate.objects.filter(msisdn=find_promo_msisdn).exists()
            and find_promo_msisdn.converted == False
            and find_promo_msisdn.is_convertable == True
        ):
            postbackUrl = f"https://dailydigest.visiontrek.io/callback"

            response_obj = requests.post(
                postbackUrl,
                json={"clickid": tracker_id},
            )
            print("response obj", response_obj.text)

            find_promo_msisdn.converted = True

            find_promo_msisdn.converted_at = today

            # find_promo_msisdn.amt = sub_amount
            find_promo_msisdn.save()

            data_sync.campaign_tracker = find_promo_msisdn
            data_sync.save()

            theUser.traffic_source = choices.CampaignProvider.VISIONTREK.value
            theUser.save()
            user_sub.traffic_source = choices.CampaignProvider.VISIONTREK.value
            user_sub.save()
    except Exception as ex:
        logger.error(ex)


@shared_task
def export_user_msisdn(month_num):
    try:
        # fetch all users

        today = date.today()
        user_profs = UserProfile.objects.filter(
            created_at__month=int(month_num)
        ).distinct("phone")
        curr_path = os.path.dirname(os.path.realpath(__file__))

        report_path = os.path.join(curr_path, "reports/")

        filename = f'{report_path}MSISDN_Exports_{today.strftime("%d/%m/%Y").replace("/", "")}.xlsx'

        data_cols = ["MSISDN", "Date"]

        data = {}

        for dt in data_cols:
            data[dt] = []

        for val in user_profs.all():
            print(f"{val.phone} - {val.created_at}")
            data["Date"].append(val.created_at.strftime("%d/%m/%Y"))
            data["MSISDN"].append(val.phone)

        new_df = pd.DataFrame(
            {key: pd.Series(value, dtype=object) for key, value in data.items()},
            columns=data_cols,
        )
        new_df.to_excel(filename, index=False, header=True)

        logger.info(report_path, os.path.exists(report_path), filename)

        ### send email

        EMAIL_SUBJECT = f"Daily Digest MSISDN report"
        REPORTING_MSG = """
            Hello Admin,
            Please find the attached report for today.
            Regards.
            """
        send_email(
            recipients=[
                "techsupport@pinesip.com.ng",
                "olushola@scriptdeskng.com",
                "bernny@pinesip.com.ng",
                ###
            ],
            subject=EMAIL_SUBJECT,
            body_text=REPORTING_MSG,
            attachment=filename,
            attachment_mime_type="text/csv",
            quiet=False,
        )

    except Exception:
        logger.error(traceback.format_exc())


@shared_task
def user_behaviour_report(month):

    try:
        curr_path = os.path.dirname(os.path.realpath(__file__))

        report_path = os.path.join(curr_path, "reports/")

        filename = f'{report_path}User_Activation_Report_{date.today().strftime("%d/%m/%Y").replace("/", "")}.xlsx'

        ####
        # do your workings here

        data_cols = ["Date", "Activations", "Renewals", "Total Churn"]

        data = {}

        for dt in data_cols:
            data[dt] = []

        month_tracker = DataSync.objects.filter(created_at__month=int(month)).order_by(
            "created_at"
        )

        for entry in month_tracker:
            ### Fetch data cols and data

            data["Date"].append(entry.created_at.date.strftime("%d/%m/%Y"))

            datasync_qs = DataSync.objects.filter(
                created_at__date=entry.created_at.date()
            )

            subscriptions = datasync_qs.filter(type="SYNC_NOTIFICATION")
            data["Activations"].append(subscriptions.count())

            unsubs = datasync_qs.filter(type="UNSUBSCRIPTION_NOTIFICATION")

            data["Total Churn"].append(unsubs.count())

            renewals = datasync_qs.filter(type="RENEWAL_NOTIFICATION")
            data["Renewals"].append(renewals.count())

            # subscribtion count

        new_df = pd.DataFrame(
            {key: pd.Series(value, dtype=object) for key, value in data.items()},
            columns=data_cols,
        )
        new_df.to_excel(filename, index=False, header=True)

        logger.info(report_path, os.path.exists(report_path), filename)

        ### send email

        EMAIL_SUBJECT = f"Daily Digest User Behaviour Report for {month}."
        REPORTING_MSG = """
            Hello Admin,
            Please find the attached report for today.
            Regards.
            """
        send_email(
            recipients=[
                "olushola@scriptdeskng.com",
                "bernny@pinesip.com.ng",
                "techsupport@pinesip.com.ng",
                ###
            ],
            subject=EMAIL_SUBJECT,
            body_text=REPORTING_MSG,
            attachment=filename,
            attachment_mime_type="text/csv",
            quiet=False,
        )

    except Exception as e:
        logger.warning(traceback.format_exc())
        logger.warning(e)


@shared_task
def export_all_msisdns():
    try:
        # fetch all ended User Subscription

        curr_path = os.path.dirname(os.path.realpath(__file__))

        report_path = os.path.join(curr_path, "reports/")

        filename = f"{report_path}msisdn_export.txt"

        all_profiles = UserProfile.objects.filter(phone__isnull=False).all()
        with open(filename, "w") as f:

            for profile in all_profiles:
                logger.info(f"{profile.phone}")
                f.writelines(profile.phone + "\n")
        f.close()
        logger.info(f"done processing {all_profiles.count()}")

        ### send email

        EMAIL_SUBJECT = f"Daily Digest Subscribers report"
        REPORTING_MSG = """
            Hello Admin,
            Please find the attached all the msisdn export.
            Regards.
            """
        send_email(
            recipients=[
                "techsupport@pinesip.com.ng",
                "olushola@scriptdeskng.com",
                "bernny@pinesip.com.ng",
                ###
            ],
            subject=EMAIL_SUBJECT,
            body_text=REPORTING_MSG,
            attachment=filename,
            attachment_mime_type="text/plain",
            quiet=False,
        )

    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(e)
