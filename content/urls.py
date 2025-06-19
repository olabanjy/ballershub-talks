from django.urls import path, include
from .views import *
from django.contrib.auth.decorators import login_required

app_name = "content"

urlpatterns = [
    path("", Homepage.as_view(), name="home"),
    path("latest_episodes", LatestEpisodesView.as_view(), name="latest_episodes"),
    path("headers/", getRequestInfo, name="getRequestInfo"),
    path("echo/", echoView, name="echo"),
    path("watch/<slug>/", content_detail, name="content_detail"),
    path("watch-show/<slug>/", show_detail, name="show_detail"),
    path("genre/<slug>/", genre_detail, name="genre_detail"),
    path("search/", EpisodeSearchResultsView.as_view(), name="search_results"),
    path("shows/", ShowListView.as_view(), name="all_shows"),
    path("terms/", T_C, name="t_c"),
    path("faq/", faqPage, name="faq"),
    path(
        "campaign/traffic-company/",
        neth_campaign_url,
        name="campaign-traffic-company",
    ),
    path("campaign/google/", google_campaign_url, name="campaign-google"),
    path("campaign/mobplus/", mobplus_campaign_url, name="campaign-mobplus"),
    path("campaign/angel-media/", angel_media_campaign_url, name="campaign-angel"),
    path("campaign/cbt/", clickbyte_campaign_url, name="click-byte"),
    path("campaign/vision-trek/", visiontrek_campaign_url, name="vision-trek"),
]
