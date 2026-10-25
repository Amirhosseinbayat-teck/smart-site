from django.contrib import admin
from .models import Website


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
        "business_type",
        "status",
        "created_at",
    )
    list_filter = ("business_type", "status", "created_at")
    search_fields = ("name", "description", "owner__username")
    readonly_fields = ("created_at", "updated_at")