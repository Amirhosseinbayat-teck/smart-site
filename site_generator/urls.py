from django.urls import path
from . import views

app_name = "site_generator"

urlpatterns = [
    path(
        "site/<int:website_id>/",
        views.public_website,
        name="public_website",
    ),
    path(
        "website/<int:website_id>/generate/",
        views.generate_homepage,
        name="generate_homepage",
    ),
    path(
        "website/<int:website_id>/publish/",
        views.publish_website,
        name="publish_website",
    ),
]
