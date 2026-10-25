
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from websites.models import Website
from ai_services.models import AIRequest
from ai_services.services import generate_store_content
from products.models import Product
from .models import GeneratedPage

logger = logging.getLogger(__name__)


@login_required
def generate_homepage(request, website_id):
    website = get_object_or_404(
        Website,
        id=website_id,
        owner=request.user,
    )

    if request.method != "POST":
        return redirect("websites:dashboard")

    ai_request = AIRequest.objects.create(
        user=request.user,
        website=website,
        prompt=f"تولید محتوای صفحه اصلی فروشگاه {website.name}",
        status="processing",
    )

    try:
        content = generate_store_content(website)

        GeneratedPage.objects.update_or_create(
            website=website,
            slug="home",
            defaults={
                "title": content["title"],
                "content": content,
                "is_homepage": True,
            },
        )

        ai_request.result = content
        ai_request.status = "completed"
        ai_request.save(update_fields=["result", "status"])

        messages.success(request, "محتوای صفحه اصلی تولید شد.")

    except Exception as exc:
        logger.exception("Homepage content generation failed")

        ai_request.status = "failed"
        ai_request.error_message = str(exc)[:2000]
        ai_request.save(update_fields=["status", "error_message"])

        messages.error(
            request,
            "تولید ناموفق بود؛ خطای واقعی در CMD ثبت شده است.",
        )

    return redirect("websites:dashboard")


@login_required
def publish_website(request, website_id):
    website = get_object_or_404(
        Website,
        id=website_id,
        owner=request.user,
    )

    if request.method != "POST":
        return redirect("websites:dashboard")

    has_homepage = GeneratedPage.objects.filter(
        website=website,
        is_homepage=True,
    ).exists()

    if not has_homepage:
        messages.error(
            request,
            "ابتدا محتوای صفحه اصلی را با هوش مصنوعی تولید کنید.",
        )
        return redirect("websites:dashboard")

    website.status = "published"
    website.save(update_fields=["status", "updated_at"])

    messages.success(request, "فروشگاه با موفقیت منتشر شد.")
    return redirect("websites:dashboard")


def public_website(request, website_id):
    website = get_object_or_404(
        Website,
        id=website_id,
        status="published",
    )

    homepage = GeneratedPage.objects.filter(
        website=website,
        is_homepage=True,
    ).first()

    products = Product.objects.filter(
        website=website,
        is_active=True,
    ).select_related("category")

    return render(
        request,
        "site_generator/public_website.html",
        {
            "website": website,
            "homepage": homepage,
            "products": products,
        },
    )
