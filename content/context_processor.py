##########

from .models import Show, ContentGenre


def fetch_msisdn(request):
    if "Msisdn" in request.headers:
        msisdn = request.headers["Msisdn"]
        return {"msisdn": msisdn}
    else:
        return {"msisdn": "Start Watching"}


def get_shows(request):
    shows = Show.objects.filter(verified=True)[:5]
    return {"menu_shows": shows}


def get_genres(request):
    genres = ContentGenre.objects.all()
    return {"menu_genres": genres}
