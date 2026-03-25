from django.shortcuts import render, get_object_or_404, HttpResponse, redirect

from django.views.generic import View
from django.core.paginator import Paginator
from .models import *
from django.db.models import Q

from dateutil.relativedelta import relativedelta


import json
import random
from django.http import JsonResponse
from ums.decorators import allowed_users
from .context_processor import fetch_msisdn
from ums.models import CampaignTracker, UserSubscribtion
from ums import choices as ums_choices
import string
from ums.subscriptionManager import mtnSubscribe
from ums.tasks import handle_occurence, handle_remarketing

from django.utils.crypto import get_random_string

# Create your views here.


def error404(request, exception):
    return render(request, "errors/404.html", status=404)


def error500(request):
    return render(request, "errors/500.html")


def T_C(request):
    return render(request, "content/t_c.html")


class Homepage(View):
    def get(self, request):

        featured_shows_id = list(
            Show.objects.filter(verified=True, admin_favorite=True, total_views__gte=0)
        )

        selected_show = random.choice(featured_shows_id)

        sel_show_episodes_ids = list(
            Episode.objects.filter(verified=True, show=selected_show)
            .all()
            .order_by("-upload_date", "watch_times")
            .values_list("id", flat=True)[:3]
        )

        random.shuffle(sel_show_episodes_ids)
        sel_show_episodes = Episode.objects.filter(id__in=sel_show_episodes_ids).all()

        featured_episodes = (
            Episode.objects.filter(verified=True, featured=True)
            .all()
            .order_by("-upload_date")[:8]
        )

        popular = Episode.objects.filter(verified=True).all().order_by("-upload_date")
        paginator = Paginator(popular, 12)
        page = self.request.GET.get("page")
        contents = paginator.get_page(page)

        template = "content/index.html"

        context = {
            "contents": contents,
            "selected_show": selected_show,
            "sel_show_episodes": sel_show_episodes,
            "featured_episodes": featured_episodes,
        }

        return render(request, template, context)


class LatestEpisodesView(View):
    def get(self, request):

        lastest_ep = (
            Episode.objects.filter(verified=True).all().order_by("-upload_date")
        )

        paginator = Paginator(lastest_ep, 15)
        page = self.request.GET.get("page")
        contents = paginator.get_page(page)

        template = "content/latest_episodes.html"

        context = {"contents": contents}

        return render(request, template, context)


@allowed_users
def content_detail(request, slug=None):
    # the_content = Content.object.get(slug=slug)

    the_content = get_object_or_404(Episode, slug=slug)

    other_contents = Episode.objects.filter(verified=True).exclude(
        slug=the_content.slug
    )
    try:
        the_content.watch_times += 1
        the_content.save()

        user_profile = fetch_msisdn(request)
        msisdn = user_profile["msisdn"]
        if msisdn != "" or msisdn != None:
            fetch_profile = UserProfile.objects.get(phone=msisdn)
            # create watched content
            new_watched = WatchedContent.objects.get_or_create(
                user=fetch_profile, content=the_content
            )
            new_watched.count += 1
            new_watched.save()
        else:
            pass

    except:
        pass

    template = "content/single_podcast.html"

    context = {"the_content": the_content, "other_contents": other_contents}

    return render(request, template, context)


@allowed_users
def show_detail(request, slug=None):
    the_content = get_object_or_404(Show, slug=slug)
    episodes = Episode.objects.filter(show=the_content, verified=True).order_by(
        "-upload_date"
    )

    paginator = Paginator(episodes, 15)
    page = request.GET.get("page")
    episodes = paginator.get_page(page)

    template = "content/podcast_detail.html"

    context = {
        "the_content": the_content,
        "episodes": episodes,
    }

    return render(request, template, context)


def genre_detail(request, slug=None):

    genre = ContentGenre.objects.filter(slug=slug).first()
    episodes = Episode.objects.filter(genre=genre, verified=True)
    paginator = Paginator(episodes, 15)
    page = request.GET.get("page")
    contents = paginator.get_page(page)
    template = "content/genre_results.html"

    context = {
        "query": genre,
        "contents": contents,
    }

    return render(request, template, context)


class ShowListView(View):
    template_name = "content/show_list.html"

    def get(self, request, *args, **kwargs):
        # Get all verified shows
        shows = Show.objects.filter(verified=True).order_by("-total_views")

        # Get genre filter if provided
        genre_slug = request.GET.get("genre")
        if genre_slug:
            shows = shows.filter(genre__slug=genre_slug)

        # Implement pagination
        paginator = Paginator(shows, 12)  # Show 12 shows per page
        page = request.GET.get("page")
        shows = paginator.get_page(page)

        # Get all genres for the filter dropdown
        genres = ContentGenre.objects.all().order_by("name")

        context = {
            "shows": shows,
            "genres": genres,
            "current_genre": genre_slug,
        }
        return render(request, self.template_name, context)


class EpisodeSearchResultsView(View):

    template_name = "content/search_results.html"

    # @allowed_users
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get("s")
        episodes = Episode.objects.filter(Q(title__icontains=query))

        paginator = Paginator(episodes, 15)
        page = self.request.GET.get("page")
        contents = paginator.get_page(page)

        context = {
            "query": query,
            "contents": contents,
        }
        return render(request, self.template_name, context)


def faqPage(request):

    faq_data = [
        (
            "What is Mind Over Matter Podcast?",
            "Mind Over Matter Podcast service is a video-on-demand that entail daily dose of conversations that spans business, lifestyle, marketing and entertainment",
        ),
        (
            "How much does the Mind Over Matter Podcast service cost?",
            "Daily Subscription - N100, Weekly Subscription - N150, Monthly subscription - N200",
        ),
        (
            "How do I subscribe for this service?",
            "Daily Subscription - send PODD to 61445, Weekly Subscription - send PODW  to 61445, Monthly subscription - send PODM to 61445",
        ),
        (
            "What happens after I send the subscription request?",
            "Customer received a double opt-in prompt to either accept subscription or decline subscription",
        ),
        ("Do I need to register for the service?", "YES"),
        (
            "What benefits will I enjoy when using the Mind Over Matter Podcast service?",
            "Subscribers get to enjoy a collection of entertaining, informative, and educative video content on demand",
        ),
        ("Who can use the Mind Over Matter Podcast service?", "Everyone"),
        ("What devices can access the application?", "IOS and Andriod"),
        (
            "Do I get notified after my Mind Over Matter Podcast Plan has expired?",
            "Yes",
        ),
        (
            "How do I unsubscribe from Mind Over Matter Podcast service?",
            "'STOP KEYWORD'. E.g (STOP PODD) for daily",
        ),
    ]
    return render(request, "content/faq.html", {"faq_data": faq_data})


def getRequestInfo(request):

    theheaders = json.dumps(dict(request.headers))
    returnData = {"MSISDN": theheaders}
    # print(returnData)
    return JsonResponse(returnData)


def echoView(request):
    return HttpResponse("YES, MIND OVER MATTER PODCAST IS LIVE !!")


def neth_campaign_url(request):
    try:

        partner = request.GET.get("partner", None)
        click_id = request.GET.get("clickid", None)
        telco = request.GET.get("telco", None)

        try:
            new_promo_hit = CampaignTracker.objects.get(
                click_id=click_id, provider=ums_choices.CampaignProvider.NETH.value
            )
        except CampaignTracker.DoesNotExist:
            new_promo_hit = CampaignTracker.objects.create(
                click_id=click_id, provider=ums_choices.CampaignProvider.NETH.value
            )
        except CampaignTracker.MultipleObjectsReturned:
            new_promo_hit = CampaignTracker.objects.filter(
                click_id=click_id, provider=ums_choices.CampaignProvider.NETH.value
            ).last()

        if partner:
            new_promo_hit.partner = partner
        if telco:
            new_promo_hit.telco = telco

        try:
            req_data = json.loads(request.body)

            new_promo_hit.req_body = f"{req_data}"
        except:
            pass

        unique_sub_ref = get_random_string(length=48)

        if "Msisdn" in request.headers:
            msisdn = request.headers["Msisdn"]
            if msisdn.startswith("0") and len(msisdn) == 11:
                msisdn = msisdn.replace("0", "234", 1)

            # save the clickID and msisdn

            new_promo_hit.msisdn = msisdn

            user_prof_qs = UserProfile.objects.filter(phone=msisdn)
            if user_prof_qs.exists():
                user_prof = user_prof_qs.first()
                # check if user has active subscribtion
                now = timezone.now()
                one_month_ago = now - relativedelta(hours=24)
                # user deactivated active subscribtion
                user_sub = UserSubscribtion.objects.filter(user=user_prof).first()
                if user_sub.ends_date and user_sub.ends_date <= one_month_ago:
                    handle_remarketing.delay(
                        msisdn, ums_choices.CampaignProvider.NETH.value
                    )

                    # redirect to secured D
                    new_promo_hit.is_convertable = False
                    new_promo_hit.save()

                    traffic_source = "Organic Search"

                    redirect_url = f"http://ng-app.com/Pinesip/daily-digest-podcast-daily-en-doi-web?origin_banner=1&trxId={unique_sub_ref}&trfsrc={traffic_source}"
                    return redirect(redirect_url)
                else:
                    return redirect("content:home")

        new_promo_hit.save()
        handle_occurence.delay(new_promo_hit.id)
        traffic_source = "Traffic Company"
        redirect_url = f"http://ng-app.com/Pinesip/daily-digest-podcast-daily-en-doi-web?origin_banner=1&trxId={unique_sub_ref}&trfsrc={traffic_source}"
        return redirect(redirect_url)
    except Exception as ex:
        print(ex)
        return redirect("content:home")


def google_campaign_url(request):

    N = 32

    # using random.choices()
    # generating random strings
    click_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=N))
    telco = request.GET.get("telco", None)

    new_promo_hit = CampaignTracker.objects.create(
        click_id=click_id, provider=ums_choices.CampaignProvider.GOOGLE.value
    )

    if telco:
        new_promo_hit.telco = telco

    try:
        req_data = json.loads(request.body)

        new_promo_hit.req_body = f"{req_data}"
    except:
        pass
    new_promo_hit.save()
    if "Msisdn" in request.headers:
        msisdn = request.headers["Msisdn"]
        if msisdn.startswith("0") and len(msisdn) == 11:
            msisdn = msisdn.replace("0", "234", 1)

        # save the clickID and msisdn

        # try:
        #     CampaignTracker.objects.filter(msisdn=msisdn).delete()
        # except Exception as ex:
        #     print(ex)

        new_promo_hit.msisdn = msisdn
        new_promo_hit.save()
        new_promo_hit.msisdn = msisdn
        new_promo_hit.save()

        if telco and telco != "MTN":
            # subscribe airtel

            mtnSubscribe(msisdn)

            return redirect("content:home")
        else:
            N = 7

            # using random.choices()
            # generating random strings
            res = "".join(random.choices(string.ascii_lowercase + string.digits, k=N))
            traffic_source = f"Google - {request.META.get('HTTP_ORIGIN', '')}"

            # redirect_url = f"http://ng-app.com/CloudIntegrated/VESTV-24-No-23410220000022939-web?source={traffic_source}&trxId={res}"
            # return redirect(redirect_url)
            return redirect("content:home")
    else:
        return redirect("content:home")


def mobplus_campaign_url(request):
    try:
        partner = request.GET.get("partner", None)
        click_id = request.GET.get("clickid", None)
        telco = request.GET.get("telco", None)
        pubid = request.GET.get("pubid", None)

        unique_sub_ref = get_random_string(length=48)
        if "Msisdn" in request.headers:
            msisdn = request.headers["Msisdn"]
            if msisdn.startswith("0") and len(msisdn) == 11:
                msisdn = msisdn.replace("0", "234", 1)

            new_promo_hit = None

            new_promo_hit_qs = CampaignTracker.objects.filter(
                click_id=click_id, provider=ums_choices.CampaignProvider.MOBPLUS.value
            )

            if new_promo_hit_qs.exists():
                new_promo_hit = new_promo_hit_qs.last()
            else:
                new_promo_hit = CampaignTracker.objects.create(
                    click_id=click_id,
                    msisdn=msisdn,
                    provider=ums_choices.CampaignProvider.MOBPLUS.value,
                    currency="USD",
                    amt="0.40",
                )

            if partner:
                new_promo_hit.partner = partner
            if telco:
                new_promo_hit.telco = telco
            if pubid:
                new_promo_hit.pubid = pubid

            user_prof_qs = UserProfile.objects.filter(phone=msisdn)
            if user_prof_qs.exists():
                user_prof = user_prof_qs.first()
                # check if user has active subscribtion
                now = timezone.now()
                one_month_ago = now - relativedelta(hours=24)
                # user deactivated active subscribtion
                user_sub = UserSubscribtion.objects.filter(user=user_prof).first()
                if user_sub.ends_date and user_sub.ends_date <= one_month_ago:
                    handle_remarketing.delay(
                        msisdn, ums_choices.CampaignProvider.MOBPLUS.value
                    )

                    # redirect to secured D
                    new_promo_hit.is_convertable = False

                    ### redirect as organic source

                    traffic_source = "Organic Search"
                    redirect_url = f"http://ng-app.com/Pinesip/daily-digest-podcast-daily-en-doi-web?origin_banner=1&trxId={unique_sub_ref}&trfsrc={traffic_source}"
                    return redirect(redirect_url)

                else:
                    return redirect("content:home")

            new_promo_hit.save()

            handle_occurence.delay(new_promo_hit.id)
            traffic_source = "MobPlus Cloud"
            redirect_url = f"http://ng-app.com/Pinesip/daily-digest-podcast-daily-en-doi-web?origin_banner=1&trxId={unique_sub_ref}&trfsrc={traffic_source}"
            return redirect(redirect_url)

        traffic_source = "Organic Search"
        redirect_url = f"http://ng-app.com/Pinesip/daily-digest-podcast-daily-en-doi-web?origin_banner=1&trxId={unique_sub_ref}&trfsrc={traffic_source}"
        return redirect(redirect_url)
    except Exception as ex:
        print("exception", ex)
        return redirect("content:home")


def angel_media_campaign_url(request):
    try:
        click_id = request.GET.get("clickid", None)
        telco = request.GET.get("telco", None)

        try:
            new_promo_hit = CampaignTracker.objects.get(
                click_id=click_id,
                provider=ums_choices.CampaignProvider.ANGELMEDIA.value,
            )
        except CampaignTracker.DoesNotExist:
            new_promo_hit = CampaignTracker.objects.create(
                click_id=click_id,
                provider=ums_choices.CampaignProvider.ANGELMEDIA.value,
            )
        except CampaignTracker.MultipleObjectsReturned:
            new_promo_hit = CampaignTracker.objects.filter(
                click_id=click_id,
                provider=ums_choices.CampaignProvider.ANGELMEDIA.value,
            ).last()

        if telco:
            new_promo_hit.telco = telco

        new_promo_hit.currency = "USD"

        unique_sub_ref = get_random_string(length=48)

        if "Msisdn" in request.headers:
            msisdn = request.headers["Msisdn"]
            if msisdn.startswith("0") and len(msisdn) == 11:
                msisdn = msisdn.replace("0", "234", 1)

            new_promo_hit.msisdn = msisdn

            user_prof_qs = UserProfile.objects.filter(phone=msisdn)
            if user_prof_qs.exists():
                user_prof = user_prof_qs.first()
                # check if user has active subscribtion
                now = timezone.now()
                one_month_ago = now - relativedelta(months=2)
                # user deactivated active subscribtion
                user_sub = UserSubscribtion.objects.filter(user=user_prof).first()
                if user_sub.ends_date and user_sub.ends_date <= one_month_ago:
                    handle_remarketing.delay(
                        msisdn, ums_choices.CampaignProvider.ANGELMEDIA.value
                    )

                    # redirect to secured D
                    new_promo_hit.is_convertable = False
                    new_promo_hit.save()
                    ### redirect as organic source

                    traffic_source = "Organic Search"
                    redirect_url = f"http://ng-app.com/Pinesip/daily-digest-podcast-daily-en-doi-web?origin_banner=1&trxId={unique_sub_ref}&trfsrc={traffic_source}"
                    return redirect(redirect_url)

                else:
                    return redirect("content:home")

        new_promo_hit.save()
        handle_occurence.delay(new_promo_hit.id)
        traffic_source = "Janx"
        # traffic_source = "ANGEL MEDIA"
        redirect_url = f"http://ng-app.com/Pinesip/daily-digest-podcast-daily-en-doi-web?origin_banner=1&trxId={unique_sub_ref}&trfsrc={traffic_source}"
        return redirect(redirect_url)

    except Exception as ex:
        print(ex)
        return redirect("content:home")


def clickbyte_campaign_url(request):
    try:
        partner = request.GET.get("partner", None)
        click_id = request.GET.get("clickid", None)
        telco = request.GET.get("telco", None)
        pubid = request.GET.get("pubid", None)

        unique_sub_ref = get_random_string(length=48)
        if "Msisdn" in request.headers:
            msisdn = request.headers["Msisdn"]
            if msisdn.startswith("0") and len(msisdn) == 11:
                msisdn = msisdn.replace("0", "234", 1)

            new_promo_hit = None

            new_promo_hit_qs = CampaignTracker.objects.filter(
                click_id=click_id, provider=ums_choices.CampaignProvider.CLICKBYTE.value
            )

            if new_promo_hit_qs.exists():
                new_promo_hit = new_promo_hit_qs.last()
            else:
                new_promo_hit = CampaignTracker.objects.create(
                    click_id=click_id,
                    msisdn=msisdn,
                    provider=ums_choices.CampaignProvider.CLICKBYTE.value,
                    currency="USD",
                    amt="0.36",
                )

            if partner:
                new_promo_hit.partner = partner
            if telco:
                new_promo_hit.telco = telco
            if pubid:
                new_promo_hit.pubid = pubid

            user_prof_qs = UserProfile.objects.filter(phone=msisdn)
            if user_prof_qs.exists():
                user_prof = user_prof_qs.first()
                # check if user has active subscribtion
                now = timezone.now()
                one_month_ago = now - relativedelta(hours=24)
                # user deactivated active subscribtion
                user_sub = UserSubscribtion.objects.filter(user=user_prof).first()
                if user_sub.ends_date and user_sub.ends_date <= one_month_ago:
                    handle_remarketing.delay(
                        msisdn, ums_choices.CampaignProvider.CLICKBYTE.value
                    )

                    # redirect to secured D
                    new_promo_hit.is_convertable = False

                    ### redirect as organic source

                    traffic_source = "Organic Search"
                    redirect_url = f"http://ng-app.com/Pinesip/daily-digest-podcast-daily-en-doi-web?origin_banner=1&trxId={unique_sub_ref}&trfsrc={traffic_source}"
                    return redirect(redirect_url)

                else:
                    return redirect("content:home")

            new_promo_hit.save()

            handle_occurence.delay(new_promo_hit.id)
            traffic_source = "Click Byte"
            redirect_url = f"http://ng-app.com/Pinesip/daily-digest-podcast-daily-en-doi-web?origin_banner=1&trxId={unique_sub_ref}&trfsrc={traffic_source}"
            return redirect(redirect_url)

        traffic_source = "Organic Search"
        redirect_url = f"http://ng-app.com/Pinesip/daily-digest-podcast-daily-en-doi-web?origin_banner=1&trxId={unique_sub_ref}&trfsrc={traffic_source}"
        return redirect(redirect_url)
    except Exception as ex:
        print("exception", ex)
        return redirect("content:home")


def visiontrek_campaign_url(request):
    try:
        partner = request.GET.get("partner", None)
        click_id = request.GET.get("clickid", None)
        telco = request.GET.get("telco", None)
        pubid = request.GET.get("pubid", None)

        unique_sub_ref = get_random_string(length=48)
        if "Msisdn" in request.headers:
            msisdn = request.headers["Msisdn"]
            if msisdn.startswith("0") and len(msisdn) == 11:
                msisdn = msisdn.replace("0", "234", 1)

            new_promo_hit = None

            new_promo_hit_qs = CampaignTracker.objects.filter(
                click_id=click_id,
                provider=ums_choices.CampaignProvider.VISIONTREK.value,
            )

            if new_promo_hit_qs.exists():
                new_promo_hit = new_promo_hit_qs.last()
            else:
                new_promo_hit = CampaignTracker.objects.create(
                    click_id=click_id,
                    msisdn=msisdn,
                    provider=ums_choices.CampaignProvider.VISIONTREK.value,
                    currency="USD",
                    amt="0.36",
                )

            if partner:
                new_promo_hit.partner = partner
            if telco:
                new_promo_hit.telco = telco
            if pubid:
                new_promo_hit.pubid = pubid

            user_prof_qs = UserProfile.objects.filter(phone=msisdn)
            if user_prof_qs.exists():
                user_prof = user_prof_qs.first()
                # check if user has active subscribtion
                now = timezone.now()
                one_month_ago = now - relativedelta(hours=24)
                # user deactivated active subscribtion
                user_sub = UserSubscribtion.objects.filter(user=user_prof).first()
                if user_sub.ends_date and user_sub.ends_date <= one_month_ago:
                    handle_remarketing.delay(
                        msisdn, ums_choices.CampaignProvider.VISIONTREK.value
                    )

                    # redirect to secured D
                    new_promo_hit.is_convertable = False

                    ### redirect as organic source

                    traffic_source = "Organic Search"
                    redirect_url = f"http://ng-app.com/Pinesip/daily-digest-podcast-daily-en-doi-web?origin_banner=1&trxId={unique_sub_ref}&trfsrc={traffic_source}"
                    return redirect(redirect_url)

                else:
                    return redirect("content:home")

            new_promo_hit.save()

            handle_occurence.delay(new_promo_hit.id)
            traffic_source = "Vision Trek"
            redirect_url = f"http://ng-app.com/Pinesip/daily-digest-podcast-daily-en-doi-web?origin_banner=1&trxId={unique_sub_ref}&trfsrc={traffic_source}"
            return redirect(redirect_url)

        traffic_source = "Organic Search"
        redirect_url = f"http://ng-app.com/Pinesip/daily-digest-podcast-daily-en-doi-web?origin_banner=1&trxId={unique_sub_ref}&trfsrc={traffic_source}"
        return redirect(redirect_url)
    except Exception as ex:
        print("exception", ex)
        return redirect("content:home")
