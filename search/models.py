from django.db import models


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
    article_title = models.CharField(
        max_length=200, blank=False, null=False, default=""
    )
    article_image = models.ImageField(blank=False, null=False, default='')
    article_desc = models.TextField(max_length=500, blank=False, null=False, default="")
    article_link = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.article_title} - {self.article_link}"
