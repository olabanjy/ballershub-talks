from django.db import models
from django.utils import timezone


from django.utils.translation import gettext_lazy as _
from . import choices


SUB_STATUS = (
    ("active", "Active"),
    ("inactive", "Inactive"),
    ("no_sub", "No Subscribtion"),
)


TEST_PHASE = (
    ("live_prod", "Live Prod"),
    ("phase_one", "Phase One"),
    ("phase_two", "Phase Two"),
    ("beta", "Beta"),
)


class WebhookBackup(models.Model):

    req_body = models.TextField(blank=True, null=True)
    telco = models.CharField(max_length=20, blank=True, null=True)
    operator = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.created_at}"


class UserProfile(models.Model):
    phone = models.CharField(
        max_length=40,
        null=True,
    )
    first_name = models.CharField(blank=True, null=True, max_length=200)
    last_name = models.CharField(blank=True, null=True, max_length=200)
    dob = models.DateField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    state = models.CharField(max_length=200, blank=True, null=True)
    nationality = models.CharField(max_length=200, blank=True, null=True)
    test_phase = models.CharField(
        max_length=200, choices=TEST_PHASE, default="live_prod"
    )
    traffic_source = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=choices.PROVIDER_CHOICES,
        verbose_name=_("traffic_source"),
    )
    sub_status = models.CharField(max_length=200, choices=SUB_STATUS, default="no_sub")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.phone}"


class UserSubscribtion(models.Model):
    user = models.ForeignKey("UserProfile", on_delete=models.CASCADE, null=True)
    sub_active = models.BooleanField(default=False)
    starts_date = models.DateTimeField(blank=True, null=True)
    ends_date = models.DateTimeField(blank=True, null=True)
    first_sub = models.BooleanField(default=False)
    renewal_sub = models.BooleanField(default=False)
    auto_renewal = models.BooleanField(default=False)
    traffic_source = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=choices.PROVIDER_CHOICES,
        verbose_name=_("traffic_source"),
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user}"


class CampaignNotificationBackup(models.Model):
    req_body = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.created_at}"


class Vendor(models.Model):
    first_name = models.CharField(blank=True, null=True, max_length=200)
    last_name = models.CharField(blank=True, null=True, max_length=200)
    company_name = models.CharField(blank=True, null=True, max_length=250)
    company_alias = models.CharField(blank=True, null=True, max_length=250)
    company_banner = models.ImageField(
        upload_to="vendor/banner/", blank=True, null=True
    )
    company_thumbnail = models.ImageField(
        upload_to="vendor/thumbnail/", blank=True, null=True
    )
    onboarded = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    state = models.CharField(max_length=200, blank=True, null=True)
    nationality = models.CharField(max_length=200, blank=True, null=True)
    address = models.CharField(blank=True, null=True, max_length=500)
    contact_phone = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.first_name} - {self.last_name}, {self.company_name}"


class CampaignTracker(models.Model):
    msisdn = models.CharField(max_length=200, blank=True, null=True)
    partner = models.CharField(max_length=200, blank=True, null=True)
    click_id = models.CharField(max_length=200, blank=True, null=True)
    telco = models.CharField(max_length=200, blank=True, null=True)
    req_body = models.TextField(blank=True, null=True)

    provider = models.TextField(
        choices=choices.PROVIDER_CHOICES,
        default=choices.CampaignProvider.NETH.value,
        verbose_name=_("provider"),
    )
    pubid = models.CharField(max_length=200, blank=True, null=True)
    amt = models.CharField(max_length=200, blank=True, null=True)
    currency = models.CharField(max_length=200, blank=True, null=True)
    occurence = models.IntegerField(default=0)
    converted = models.BooleanField(default=False)
    is_convertable = models.BooleanField(default=True)
    converted_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.click_id}"


class DataSync(models.Model):
    type = models.CharField(max_length=100, blank=True, null=True)
    telco = models.CharField(max_length=100, blank=True, null=True)
    product_id = models.CharField(max_length=100, blank=True, null=True)
    product_name = models.CharField(max_length=200, blank=True, null=True)
    product_not_type = models.CharField(max_length=100, blank=True, null=True)
    product_sub_type = models.CharField(max_length=100, blank=True, null=True)
    amount = models.IntegerField(default=0)
    channel = models.CharField(max_length=100, blank=True, null=True)
    auto_renewal = models.BooleanField(default=False)
    sub_date = models.DateTimeField(blank=True, null=True)
    sub_expiry = models.DateTimeField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    telco_ref = models.CharField(max_length=50, blank=True, null=True)
    bearer_id = models.CharField(max_length=100, blank=True, null=True)
    webhook_backup = models.ForeignKey(
        WebhookBackup, on_delete=models.DO_NOTHING, blank=True, null=True
    )
    campaign_tracker = models.ForeignKey(
        CampaignTracker, on_delete=models.DO_NOTHING, blank=True, null=True
    )
    operator = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.type} - {self.phone}"


class CampaignDuplicate(models.Model):
    msisdn = models.CharField(max_length=200, blank=True, null=True)
    provider = models.TextField(
        choices=choices.PROVIDER_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("provider"),
    )
    occurence = models.IntegerField(default=1)
    remarketed = models.BooleanField(default=False)
    last_subscribtion = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.msisdn} - {self.occurence}"


class CallbackNotification(models.Model):
    msisdn = models.CharField(max_length=200, blank=True, null=True)
    activation = models.IntegerField(blank=True, null=True)
    product_id = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    timestamp = models.CharField(max_length=200, blank=True, null=True)
    trx_id = models.CharField(max_length=200, blank=True, null=True)
    sequence_no = models.CharField(max_length=200, blank=True, null=True)
    raw_payload = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Raw callback payload",
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.msisdn} - {self.product_id} - {self.timestamp}"

    class Meta:
        verbose_name = "Callback notification"
        verbose_name_plural = "Callback notifications"
        ordering = ["-created_at"]
