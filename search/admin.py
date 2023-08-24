from django.contrib import admin
from .models import SearchQuery, ArticlePosts, Tag

admin.site.register(ArticlePosts)
admin.site.register(Tag)


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ["query", "timestamp"]
    search_fields = ["query"]
