from enum import unique
from django.db import models
from content.enum import DocEnum
from django.utils.translation import gettext_lazy as _


@unique
class Telco(DocEnum):
    """
    Telco Choices
    """

    MTN = "MTN", "MTN"
    AIRTEL = "AIRTEL", "AIRTEL"


_readable_telcos = {
    Telco.MTN.value: _("MTN"),
    Telco.AIRTEL.value: _("AIRTEL"),
}


TELCO_CHOICES = [(d.value, _readable_telcos[d.value]) for d in Telco]


@unique
class CampaignProvider(DocEnum):
    """
    Campaign Provider Choices
    """

    NETH = "NETH", "NETH"
    MOBPLUS = "MOBPLUS", "MOBPLUS"
    GOOGLE = "GOOGLE", "GOOGLE"
    ANGELMEDIA = "ANGELMEDIA", "ANGELMEDIA"
    CLICKBYTE = "CLICKBYTE", "CLICKBYTE"
    VISIONTREK = "VISIONTREK", "VISIONTREK"


_readable_provider = {
    CampaignProvider.NETH.value: _("NETH"),
    CampaignProvider.MOBPLUS.value: _("MOBPLUS"),
    CampaignProvider.GOOGLE.value: _("GOOGLE"),
    CampaignProvider.ANGELMEDIA.value: _("ANGELMEDIA"),
    CampaignProvider.CLICKBYTE.value: _("CLICKBYTE"),
    CampaignProvider.VISIONTREK.value: _("VISIONTREK"),
}


PROVIDER_CHOICES = [(d.value, _readable_provider[d.value]) for d in CampaignProvider]
