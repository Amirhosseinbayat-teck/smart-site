from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from websites.models import Website
from .models import Order, OrderItem, Product


def checkout(request, website_id):
    website = get_object_or_404(
        Website,
        id=website_id,
        status="published",
    )

    products = Product.objects.filter(
        website=website,
        is_active=True,
    )

    if request.method == "POST":
        customer_name = request.POST.get("customer_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()

        if not customer_name or not phone or not address:
            messages.error(request, "لطفاً تمام اطلاعات مشتری را وارد کنید.")
            return render(
                request,
                "products/checkout.html",
                {"website": website, "products": products},
            )

        selected = []

        for product in products:
            raw_quantity = request.POST.get(
                f"quantity_{product.id}", "0"
            ).strip()

            try:
                quantity = int(raw_quantity)
            except (ValueError, TypeError):
                quantity = 0

            if quantity < 0:
                messages.error(request, "تعداد محصول نامعتبر است.")
                return render(
                    request,
                    "products/checkout.html",
                    {"website": website, "products": products},
                )

            if quantity > 0:
                selected.append((product.id, quantity))

        if not selected:
            messages.error(request, "حداقل یک محصول انتخاب کنید.")
            return render(
                request,
                "products/checkout.html",
                {"website": website, "products": products},
            )

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    website=website,
                    customer_name=customer_name,
                    phone=phone,
                    address=address,
                )

                for product_id, quantity in selected:
                    product = Product.objects.select_for_update().get(
                        id=product_id,
                        website=website,
                        is_active=True,
                    )

                    if product.stock < quantity:
                        raise ValueError(
                            f"موجودی محصول «{product.name}» کافی نیست."
                        )

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        unit_price=product.price,
                        quantity=quantity,
                    )

                    product.stock -= quantity
                    product.save(update_fields=["stock"])

        except (ValueError, Product.DoesNotExist) as exc:
            messages.error(request, str(exc) or "ثبت سفارش انجام نشد.")
            return render(
                request,
                "products/checkout.html",
                {"website": website, "products": products},
            )

        messages.success(request, "سفارش شما با موفقیت ثبت شد.")
        return redirect("site_generator:public_website", website_id=website.id)

    return render(
        request,
        "products/checkout.html",
        {"website": website, "products": products},
    )