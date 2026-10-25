
from django.core.validators import MinValueValidator
from django.db import models
from websites.models import Website


class Category(models.Model):
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="product_categories",
        verbose_name="فروشگاه",
    )
    name = models.CharField("نام دسته‌بندی", max_length=100)
    description = models.TextField("توضیحات", blank=True)
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["website", "name"],
                name="unique_category_name_per_website",
            )
        ]

    def __str__(self):
        return f"{self.name} - {self.website.name}"


class Product(models.Model):
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="فروشگاه",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="products",
        verbose_name="دسته‌بندی",
        null=True,
        blank=True,
    )
    name = models.CharField("نام محصول", max_length=200)
    description = models.TextField("توضیحات محصول", blank=True)
    price = models.DecimalField(
        "قیمت",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    stock = models.PositiveIntegerField("موجودی", default=0)
    image = models.ImageField(
        "تصویر محصول",
        upload_to="products/",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField("فعال", default=True)
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین ویرایش", auto_now=True)

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "در انتظار بررسی"),
        ("confirmed", "تأییدشده"),
        ("shipped", "ارسال‌شده"),
        ("delivered", "تحویل‌شده"),
        ("cancelled", "لغوشده"),
    ]

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="فروشگاه",
    )
    customer_name = models.CharField("نام مشتری", max_length=150)
    phone = models.CharField("شماره تماس", max_length=20)
    address = models.TextField("نشانی تحویل")
    status = models.CharField(
        "وضعیت سفارش",
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        ordering = ["-created_at"]

    @property
    def total_price(self):
        return sum(
            (item.unit_price * item.quantity for item in self.items.all()),
            start=0,
        )

    def __str__(self):
        return f"سفارش {self.pk} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="سفارش",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
        verbose_name="محصول",
    )
    product_name = models.CharField("نام محصول هنگام سفارش", max_length=200)
    unit_price = models.DecimalField(
        "قیمت واحد هنگام سفارش",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    quantity = models.PositiveIntegerField(
        "تعداد",
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = "قلم سفارش"
        verbose_name_plural = "اقلام سفارش"

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"
