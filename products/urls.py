from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path(
        "site/<int:website_id>/checkout/",
        views.checkout,
        name="checkout",
    ),
]