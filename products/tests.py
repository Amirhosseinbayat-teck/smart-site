
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from websites.models import Website
from .models import Product, Order, OrderItem


class CheckoutTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
        )

        self.website = Website.objects.create(
            owner=self.user,
            name="فروشگاه آزمایشی",
            status="published",
        )

        self.product = Product.objects.create(
            website=self.website,
            name="محصول آزمایشی",
            description="برای تست",
            price="25000000",
            stock=5,
            is_active=True,
        )

        self.url = reverse(
            "products:checkout",
            kwargs={"website_id": self.website.id},
        )

        self.customer_data = {
            "customer_name": "مشتری آزمایشی",
            "phone": "09120000000",
            "address": "نشانی آزمایشی",
        }

    def test_successful_checkout_reduces_stock(self):
        response = self.client.post(
            self.url,
            {
                **self.customer_data,
                f"quantity_{self.product.id}": "2",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)

        item = OrderItem.objects.get()
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.unit_price, self.product.price)

    def test_checkout_rejects_quantity_above_stock(self):
        response = self.client.post(
            self.url,
            {
                **self.customer_data,
                f"quantity_{self.product.id}": "6",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)
        self.assertEqual(Order.objects.count(), 0)

    def test_checkout_requires_customer_information(self):
        response = self.client.post(
            self.url,
            {f"quantity_{self.product.id}": "1"},
        )

        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)
        self.assertEqual(Order.objects.count(), 0)


class OrderCancellationTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="canceluser",
            password="testpassword123",
            is_staff=True,
            is_superuser=True,
        )

        self.website = Website.objects.create(
            owner=self.user,
            name="فروشگاه لغو سفارش",
            status="published",
        )

        self.product = Product.objects.create(
            website=self.website,
            name="محصول آزمایشی",
            description="برای تست لغو",
            price="25000000",
            stock=3,
            is_active=True,
        )

        self.order = Order.objects.create(
            website=self.website,
            customer_name="مشتری آزمایشی",
            phone="09120000000",
            address="نشانی آزمایشی",
            status="pending",
        )

        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_name=self.product.name,
            unit_price=self.product.price,
            quantity=2,
        )

        self.product.stock = 1
        self.product.save(update_fields=["stock"])

    def test_cancelling_order_restores_stock(self):
        self.client.force_login(self.user)

        self.order.status = "cancelled"

        from django.contrib.admin.sites import AdminSite
        from products.admin import OrderAdmin

        admin_instance = OrderAdmin(Order, AdminSite())

        class FakeRequest:
            pass

        admin_instance.save_model(
            FakeRequest(),
            self.order,
            form=None,
            change=True,
        )

        self.product.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(self.order.status, "cancelled")
        self.assertEqual(self.product.stock, 3)

    def test_cancelling_order_twice_does_not_restore_stock_twice(self):
        from django.contrib.admin.sites import AdminSite
        from products.admin import OrderAdmin

        admin_instance = OrderAdmin(Order, AdminSite())

        class FakeRequest:
            pass

        self.order.status = "cancelled"
        admin_instance.save_model(
            FakeRequest(),
            self.order,
            form=None,
            change=True,
        )

        self.order.status = "cancelled"
        admin_instance.save_model(
            FakeRequest(),
            self.order,
            form=None,
            change=True,
        )

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
