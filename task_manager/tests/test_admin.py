from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from task_manager.models import Position


class AdminSiteTests(TestCase):
    def setUp(self) -> None:
        self.client.force_login(
            get_user_model().objects.create_superuser(
                username="admin", password="Admin12345!"
            )
        )
        self.worker = get_user_model().objects.create_user(
            username="worker",
            password="Worker12345!",
            position=Position.objects.create(name="Project manager"),
        )

    def test_position_in_worker_changelist(self) -> None:
        response = self.client.get(
            reverse("admin:task_manager_worker_changelist")
        )
        self.assertContains(response, "Project manager")

    def test_position_on_worker_add_page(self) -> None:
        response = self.client.get(reverse("admin:task_manager_worker_add"))
        self.assertContains(response, "Additional info")
        self.assertContains(response, "position")
