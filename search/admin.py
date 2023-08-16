from django.contrib import admin
from .models import SearchQuery, ArticlePosts

admin.site.register(ArticlePosts)


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ["query", "timestamp"]
    search_fields = ["query"]
