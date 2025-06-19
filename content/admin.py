from django.contrib import admin
from .models import *

# Register your models here.


# admin.site.register(ContentCategory)##
admin.site.register(ContentGenre)
admin.site.register(ContentCategory)
admin.site.register(WatchedContent)


class ShowAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "total_views",
        "verified",
        "admin_favorite",
        "default_channel",
    )
    list_filter = [
        "verified",
        "admin_favorite",
        "default_channel",
    ]
    list_editable = [
        "verified",
        "admin_favorite",
        "default_channel",
    ]
    search_fields = ["name"]


class EpisodeAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "show",
        "verified",
        "featured",
    )
    list_filter = [
        "verified",
        "featured",
    ]
    list_editable = [
        "verified",
        "featured",
    ]
    search_fields = ["title", "show"]

    class Meta:
        ordering = "show"


admin.site.register(Show, ShowAdmin)
admin.site.register(Episode, EpisodeAdmin)
