from django.conf import settings
from django.db import models


class Website(models.Model):
    BUSINESS_TYPES = [
        ("clothing", "پوشاک"),
        ("digital", "کالای دیجیتال"),
        ("beauty", "زیبایی و بهداشتی"),
        ("food", "مواد غذایی"),
        ("home", "خانه و آشپزخانه"),
        ("other", "سایر"),
    ]

    STATUS_CHOICES = [
        ("draft", "پیش‌نویس"),
        ("published", "منتشرشده"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="websites",
        verbose_name="مالک",
    )
    name = models.CharField("نام وب‌سایت", max_length=150)
    business_type = models.CharField(
        "نوع کسب‌وکار",
        max_length=30,
        choices=BUSINESS_TYPES,
        default="other",
    )
    description = models.TextField("توضیحات", blank=True)
    status = models.CharField(
        "وضعیت",
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
    )
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین ویرایش", auto_now=True)

    class Meta:
        verbose_name = "وب‌سایت"
        verbose_name_plural = "وب‌سایت‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name