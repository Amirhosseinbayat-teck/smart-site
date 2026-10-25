
from django.conf import settings
from django.db import models


class AIRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "در انتظار"),
        ("processing", "در حال پردازش"),
        ("completed", "تکمیل‌شده"),
        ("failed", "ناموفق"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_requests",
        verbose_name="کاربر",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="ai_requests",
        null=True,
        blank=True,
        verbose_name="وب‌سایت",
    )
    prompt = models.TextField("درخواست کاربر")
    result = models.JSONField("نتیجه هوش مصنوعی", default=dict, blank=True)
    status = models.CharField(
        "وضعیت",
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    error_message = models.TextField("خطا", blank=True)
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)

    class Meta:
        verbose_name = "درخواست هوش مصنوعی"
        verbose_name_plural = "درخواست‌های هوش مصنوعی"
        ordering = ["-created_at"]

    def __str__(self):
        return f"AI Request #{self.pk} - {self.status}"