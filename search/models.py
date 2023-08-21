from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator


class SearchQuery(models.Model):
    query = models.CharField(max_length=500, blank=True, null=True, default="")
    result_title = models.TextField(blank=True, null=True, default="")
    result_desc = models.TextField(blank=True, null=True, default="")
    thumbnail = models.URLField(
        blank=True, null=True, default=None
    )  # Assuming the thumbnail is a URL
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.query


class ArticlePosts(models.Model):
    article_tag = models.CharField(
        max_length=10,
        validators=[MinLengthValidator(3)],
        blank=True,
        null=True,
        default="",
    )
    article_title = models.CharField(
        max_length=200, blank=False, null=False, default=""
    )
    article_image = models.ImageField(blank=False, null=False, default="")
    article_desc = models.TextField(max_length=500, blank=False, null=False, default="")
    article_link = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Article Posts"

    def __str__(self):
        return self.article_title
