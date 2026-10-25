
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from websites.models import Website
from ai_services.models import AIRequest
from .models import GeneratedPage


class WebsiteGenerationTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="generationuser",
            password="testpassword123",
        )

        self.website = Website.objects.create(
            owner=self.user,
            name="فروشگاه آزمایشی",
            business_type="food",
            description="فروش مواد غذایی",
            status="draft",
        )

        self.client.force_login(self.user)

    @patch("site_generator.views.generate_store_content")
    def test_generate_homepage_creates_page_and_completes_request(
        self, mock_generate
    ):
        content = {
            "title": "فروشگاه آزمایشی",
            "description": "به فروشگاه ما خوش آمدید",
        }
        mock_generate.return_value = content

        response = self.client.post(
            reverse(
                "site_generator:generate_homepage",
                kwargs={"website_id": self.website.id},
            )
        )

        self.assertEqual(response.status_code, 302)

        page = GeneratedPage.objects.get(
            website=self.website,
            slug="home",
        )
        self.assertEqual(page.content, content)
        self.assertTrue(page.is_homepage)

        request = AIRequest.objects.get(website=self.website)
        self.assertEqual(request.status, "completed")
        self.assertEqual(request.result, content)

    def test_publish_requires_generated_homepage(self):
        response = self.client.post(
            reverse(
                "site_generator:publish_website",
                kwargs={"website_id": self.website.id},
            )
        )

        self.assertEqual(response.status_code, 302)

        self.website.refresh_from_db()
        self.assertEqual(self.website.status, "draft")

    def test_publish_website_with_homepage(self):
        GeneratedPage.objects.create(
            website=self.website,
            title="صفحه اصلی",
            slug="home",
            content={"title": "فروشگاه آزمایشی"},
            is_homepage=True,
        )

        response = self.client.post(
            reverse(
                "site_generator:publish_website",
                kwargs={"website_id": self.website.id},
            )
        )

        self.assertEqual(response.status_code, 302)

        self.website.refresh_from_db()
        self.assertEqual(self.website.status, "published")

    def test_public_website_is_visible_when_published(self):
        self.website.status = "published"
        self.website.save(update_fields=["status"])

        response = self.client.get(
            reverse(
                "site_generator:public_website",
                kwargs={"website_id": self.website.id},
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_draft_website_is_not_publicly_visible(self):
        response = self.client.get(
            reverse(
                "site_generator:public_website",
                kwargs={"website_id": self.website.id},
            )
        )

        self.assertEqual(response.status_code, 404)
