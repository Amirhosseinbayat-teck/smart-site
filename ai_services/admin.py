
from django.contrib import admin
from .models import AIRequest


@admin.register(AIRequest)
class AIRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "website", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("prompt", "user__username")
    readonly_fields = ("created_at",)