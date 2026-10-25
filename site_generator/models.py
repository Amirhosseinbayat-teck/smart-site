from django.db import models
from websites.models import Website


class GeneratedPage(models.Model):
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="pages",
        verbose_name="وب‌سایت",
    )
    title = models.CharField("عنوان صفحه", max_length=150)
    slug = models.SlugField("آدرس صفحه", max_length=180)
    content = models.JSONField("محتوای ساختاریافته", default=dict)
    is_homepage = models.BooleanField("صفحه اصلی", default=False)
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین ویرایش", auto_now=True)

    class Meta:
        verbose_name = "صفحه تولیدشده"
        verbose_name_plural = "صفحات تولیدشده"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["website", "slug"],
                name="unique_page_slug_per_website",
            )
        ]

    def __str__(self):
        return f"{self.website.name} - {self.title}"