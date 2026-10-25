from django.contrib import admin
from django.db import transaction

from .forms import ProductAdminForm
from .models import Category, Product, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "website", "created_at")
    list_filter = ("website",)
    search_fields = ("name", "description", "website__name")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm

    list_display = (
        "name",
        "website",
        "category",
        "price",
        "stock",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "website", "category")
    search_fields = ("name", "description", "website__name")
    list_editable = ("price", "stock", "is_active")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "product_name",
        "unit_price_display",
        "quantity",
    )
    fields = (
        "product",
        "product_name",
        "unit_price_display",
        "quantity",
    )

    @admin.display(description="قیمت واحد (تومان)")
    def unit_price_display(self, obj):
        if not obj or obj.unit_price is None:
            return "—"
        return f"{obj.unit_price:,.0f}"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "phone",
        "website",
        "total_price_display",
        "status",
        "created_at",
    )
    list_filter = ("status", "website", "created_at")
    search_fields = ("customer_name", "phone", "address")
    readonly_fields = ("created_at", "total_price_display")
    inlines = [OrderItemInline]

    @admin.display(description="مبلغ کل (تومان)")
    def total_price_display(self, obj):
        return f"{obj.total_price:,.0f}"

    def save_model(self, request, obj, form, change):
        with transaction.atomic():
            if change:
                old_order = (
                    Order.objects
                    .select_for_update()
                    .get(pk=obj.pk)
                )

                if (
                    old_order.status != "cancelled"
                    and obj.status == "cancelled"
                ):
                    for item in old_order.items.select_related("product"):
                        if item.product_id:
                            product = Product.objects.select_for_update().get(
                                pk=item.product_id
                            )
                            product.stock += item.quantity
                            product.save(update_fields=["stock"])

            super().save_model(request, obj, form, change)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "product_name",
        "order",
        "unit_price",
        "quantity",
    )
    search_fields = ("product_name",)