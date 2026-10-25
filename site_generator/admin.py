
from django.contrib import admin
from .models import GeneratedPage


@admin.register(GeneratedPage)
class GeneratedPageAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "website",
        "slug",
        "is_homepage",
        "created_at",
    )
    list_filter = ("is_homepage", "created_at")
    search_fields = ("title", "slug", "website__name")
    readonly_fields = ("created_at", "updated_at")