from django.contrib import admin


from import_export import resources

from import_export.admin import ImportExportModelAdmin

from .models import *


# Register your models here.


@admin.register(WebhookBackup)
class WebhookBackupAdmin(admin.ModelAdmin):
    list_display = [
        "req_body",
        "telco",
        "operator",
        "created_at",
    ]


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = [
        "first_name",
        "last_name",
        "company_name",
        "company_alias",
        "company_banner",
        "company_thumbnail",
        "onboarded",
        "verified",
        "state",
        "nationality",
        "address",
        "contact_phone",
        "created_at",
    ]


admin.site.register(CampaignNotificationBackup)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        "phone",
        "sub_status",
        "traffic_source",
        "created_at",
    ]
    search_fields = ["phone"]


@admin.register(UserSubscribtion)
class UserSubscribtionAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "sub_active",
        "starts_date",
        "ends_date",
        "first_sub",
        "renewal_sub",
        "auto_renewal",
        "traffic_source",
        "created_at",
    ]
    search_fields = ["user__phone"]


class CampaignResource(resources.ModelResource):
    class Meta:
        model = CampaignTracker


@admin.register(CampaignTracker)
class CampaignTrackerAdmin(ImportExportModelAdmin):
    list_display = [
        "msisdn",
        "partner",
        "click_id",
        "amt",
        "telco",
        "is_convertable",
        "occurence",
        "converted",
        "provider",
        "created_at",
        "converted_at",
    ]
    search_fields = ["msisdn", "click_id", "provider"]
    resource_classes = [CampaignResource]


@admin.register(DataSync)
class DataSyncAdmin(admin.ModelAdmin):
    list_display = [
        "type",
        "telco",
        "product_id",
        "product_name",
        "product_not_type",
        "product_sub_type",
        "amount",
        "channel",
        "auto_renewal",
        "sub_date",
        "sub_expiry",
        "phone",
        "telco_ref",
        "webhook_backup",
        "campaign_tracker",
        "created_at",
    ]

    search_fields = ["phone", "type"]


@admin.register(CampaignDuplicate)
class CampaignDuplicateAdmin(admin.ModelAdmin):
    list_display = [
        "msisdn",
        "provider",
        "occurence",
        "remarketed",
        "last_subscribtion",
        "created_at",
    ]

    search_fields = ["msisdn", "provider"]


@admin.register(CallbackNotification)
class CallbackNotificationAdmin(admin.ModelAdmin):
    list_display = [
        "msisdn",
        "description",
        "product_id",
        "activation",
        "trx_id",
        "sequence_no",
        "created_at",
    ]
    search_fields = ["msisdn", "product_id", "trx_id", "sequence_no"]
    list_filter = ("description", "activation")
