
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Website


@login_required
def dashboard(request):
    websites = Website.objects.filter(owner=request.user)
    return render(
        request,
        "websites/dashboard.html",
        {"websites": websites},
    )


@login_required
def create_website(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        business_type = request.POST.get("business_type", "other")
        description = request.POST.get("description", "").strip()

        valid_types = {choice[0] for choice in Website.BUSINESS_TYPES}

        if name and business_type in valid_types:
            Website.objects.create(
                owner=request.user,
                name=name,
                business_type=business_type,
                description=description,
            )
            return redirect("websites:dashboard")

    return render(request, "websites/create.html")