from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("websites.urls")),
    path("", include("site_generator.urls")),
    path("", include("products.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
]