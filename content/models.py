from datetime import datetime
from django.db import models
from django.urls import reverse
from django.utils import timezone
from ums.models import UserProfile, Vendor
from django.template.defaultfilters import slugify


class ContentCategory(models.Model):
    slug = models.SlugField()
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


class ContentGenre(models.Model):
    slug = models.SlugField()
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


class Show(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    banner = models.ImageField(upload_to="channel/banner", blank=True, null=True)
    banner_slit_1 = models.ImageField(upload_to="channel/banner", blank=True, null=True)
    banner_slit_2 = models.ImageField(upload_to="channel/banner", blank=True, null=True)
    thumbnail = models.ImageField(upload_to="channel/thumbnail", blank=True, null=True)
    total_views = models.IntegerField(default=0)
    admin_favorite = models.BooleanField(default=False)
    default_channel = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    about = models.TextField(blank=True, null=True)

    def get_recent_episodes(self, limit=3):
        return self.show_episodes.order_by("position")[:limit]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Episode(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=120)
    category = models.ForeignKey(
        ContentCategory, on_delete=models.CASCADE, blank=True, null=True
    )
    genre = models.ForeignKey(
        ContentGenre, on_delete=models.CASCADE, blank=True, null=True
    )
    show = models.ForeignKey(
        Show,
        on_delete=models.DO_NOTHING,
        related_name="show_episodes",
        blank=True,
        null=True,
    )
    description = models.TextField(default="Lorem Ipsum")
    img_banner = models.ImageField(
        upload_to="ballershub-podcast/content_images/banner/", blank=True
    )
    img_poster = models.ImageField(
        upload_to="ballershub-podcast/content_images/poster/", blank=True
    )
    img_detail_poster = models.ImageField(
        upload_to="ballershub-podcast/content_images/poster/", blank=True
    )
    img_detail_banner = models.ImageField(
        upload_to="ballershub-podcast/content_images/banner/", blank=True
    )
    img_trailer = models.ImageField(
        upload_to="ballershub-podcast/content_images/trailer/", blank=True
    )
    img_thumbnail = models.ImageField(
        upload_to="ballershub-podcast/content_images/thumbnai/", blank=True
    )
    trailer_mp4 = models.FileField(
        upload_to="ballershub-podcast/content_file/trailer/mp4/", blank=True
    )

    file_mp4 = models.FileField(
        upload_to="ballershub-podcast/content_file/mp4/", blank=True
    )
    upload_date = models.DateField(blank=True)
    timedelta = models.DurationField(null=True, blank=True)
    position = models.IntegerField()
    featured = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    watch_times = models.IntegerField(default=1)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"{self.title} - {self.position}"

    def get_next(self):
        next = Episode.objects.filter(id__gt=self.id).order_by("id").first()
        if next:
            return next
        elif next == Episode.objects.order_by("id").last():
            return reverse("")
        else:
            return Episode.objects.order_by("id").first()


class WatchedContent(models.Model):
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="profile_content",
        blank=True,
        null=True,
    )
    content = models.ForeignKey(
        Episode,
        on_delete=models.CASCADE,
        related_name="watched_content",
        blank=True,
        null=True,
    )
    count = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user} - {self.content.title} - {self.count}"
