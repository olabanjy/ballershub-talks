from django.urls import path
from .views import *

app_name = "ums"

urlpatterns = [
    path("phone-login/", phone_login, name="phone_login"),
    path("awaiting_response/", awaiting_response, name="awaiting_response"),
    path("onboarding/", onboarding, name="onboarding"),
    path("subscribe/", subscribe, name="subscribe"),
    path("cancelSubscribtion/", cancelSubscribtion, name="cancelSubscribtion"),
    path("inactive_account/", inactive_account, name="inactive_account"),
    path("data-sync/", data_sync, name="data_sync_endpoint"),
    path("campaign_notification/", campaign_notification, name="campaign_notification"),
    path("check_sub_status/", check_sub_status, name="check_sub_status"),
    path("cleanup_data/", cleanup_data, name="cleanup-data"),
    path("campaign-stats/", fetch_campaign_behaviour, name="fetch_campaign_behaviour"),
    path(
        "reconcile_subscribtions/",
        reconcile_subscribtions,
        name="reconcile_subscribtions",
    ),
    path("generate_report/", generate_report, name="generate-report"),
    path("fetch_stats/", fetch_stats, name="fetch_stats"),
    path(
        "campaign_partner_user_behaviour_query/",
        campaign_partner_user_behaviour_query,
        name="campaign_partner_user_behaviour_query",
    ),
    path("fetch_sub_channel/", fetch_sub_channel, name="fetch_sub_channel"),
    path(
        "fetch_ussd_subscribers_query/",
        fetch_ussd_subscribers_query,
        name="fetch_ussd_subscribers_query",
    ),
    path(
        "campaign_partner_user_behaviour_compiled_query/",
        campaign_partner_user_behaviour_compiled_query,
        name="campaign_partner_user_behaviour_compiled_query",
    ),
    path("get_cr_data/", get_cr_data, name="get_cr_data"),
    path(
        "export-user-msisdn/",
        export_user_msisdn_query,
        name="export_user_msisdn_query",
    ),
    path(
        "user_activation_report_query/",
        user_activation_report_query,
        name="user_activation_report_query",
    ),
    path(
        "export_all_msisdn_query/",
        export_all_msisdn_query,
        name="export_all_msisdn_query",
    ),
    path(
        "callback_notification/",
        callback_notification,
        name="callback_notification",
    ),
    path("data-sync-v2/", data_sync_v2, name="data_sync_v2"),
]
