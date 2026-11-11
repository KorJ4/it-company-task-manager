import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from task_manager.models import Position, Tag, Task, TaskType

TASK_LIST_URL = reverse("task_manager:task-list")


class PublicViewsTests(TestCase):
    def test_login_required(self) -> None:
        for name in (
            "index",
            "task-list",
            "worker-list",
            "position-list",
            "task-type-list",
            "tag-list",
        ):
            with self.subTest(name=name):
                response = self.client.get(reverse(f"task_manager:{name}"))
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("login"), response.url)


class PrivateViewsTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="tester", password="Tester12345!"
        )
        self.client.force_login(self.user)
        self.task_type = TaskType.objects.create(name="Bug")
        self.deadline = datetime.date.today() + datetime.timedelta(days=2)

    def create_task(self, name: str, **kwargs) -> Task:
        return Task.objects.create(
            name=name,
            deadline=self.deadline,
            task_type=self.task_type,
            **kwargs,
        )

    def test_index_counts(self) -> None:
        self.create_task("Open").assignees.add(self.user)
        self.create_task("Closed", is_completed=True)
        response = self.client.get(reverse("task_manager:index"))
        self.assertEqual(response.context["num_tasks"], 2)
        self.assertEqual(response.context["num_active_tasks"], 1)
        self.assertEqual(response.context["num_completed_tasks"], 1)
        self.assertEqual(
            [task.name for task in response.context["my_tasks"]], ["Open"]
        )

    def test_index_counts_visits(self) -> None:
        for visit in range(1, 4):
            response = self.client.get(reverse("task_manager:index"))
            self.assertEqual(response.context["num_visits"], visit)

    def test_task_search(self) -> None:
        self.create_task("Fix login bug")
        self.create_task("Write docs")
        response = self.client.get(TASK_LIST_URL, {"query": "LOGIN"})
        self.assertEqual(
            [task.name for task in response.context["task_list"]],
            ["Fix login bug"],
        )
        self.assertEqual(
            response.context["search_form"].initial["query"], "LOGIN"
        )

    def test_worker_search_by_username(self) -> None:
        get_user_model().objects.create_user(
            username="alice", password="Alice12345!"
        )
        response = self.client.get(
            reverse("task_manager:worker-list"), {"query": "ali"}
        )
        self.assertEqual(
            [worker.username for worker in response.context["worker_list"]],
            ["alice"],
        )

    def test_simple_lists_search_by_name(self) -> None:
        Position.objects.create(name="Designer")
        Position.objects.create(name="Developer")
        Tag.objects.create(name="frontend")
        Tag.objects.create(name="backend")
        cases = (
            ("position-list", "position_list", "sign", ["Designer"]),
            ("tag-list", "tag_list", "front", ["frontend"]),
            ("task-type-list", "tasktype_list", "bu", ["Bug"]),
        )
        for name, context_name, query, expected in cases:
            with self.subTest(name=name):
                response = self.client.get(
                    reverse(f"task_manager:{name}"), {"query": query}
                )
                self.assertEqual(
                    [item.name for item in response.context[context_name]],
                    expected,
                )

    def test_pagination_keeps_search_query(self) -> None:
        for number in range(11):
            self.create_task(f"Task {number}")
        response = self.client.get(TASK_LIST_URL, {"query": "task"})
        self.assertContains(response, "?query=task&amp;page=2")

    def test_create_task(self) -> None:
        response = self.client.post(
            reverse("task_manager:task-create"),
            {
                "name": "New feature",
                "deadline": self.deadline,
                "priority": "urgent",
                "task_type": self.task_type.pk,
                "assignees": [self.user.pk],
            },
        )
        task = Task.objects.get(name="New feature")
        self.assertRedirects(response, task.get_absolute_url())
        self.assertIn(self.user, task.assignees.all())

    def test_toggle_completed(self) -> None:
        task = self.create_task("Toggle me")
        url = reverse("task_manager:task-toggle-completed", args=[task.pk])
        self.client.post(url)
        task.refresh_from_db()
        self.assertTrue(task.is_completed)
        self.client.post(url)
        task.refresh_from_db()
        self.assertFalse(task.is_completed)

    def test_toggle_assign(self) -> None:
        task = self.create_task("Help needed")
        url = reverse("task_manager:task-toggle-assign", args=[task.pk])
        self.client.post(url)
        self.assertIn(self.user, task.assignees.all())
        self.client.post(url)
        self.assertNotIn(self.user, task.assignees.all())

    def test_toggles_reject_get(self) -> None:
        task = self.create_task("Safe")
        for name in ("task-toggle-completed", "task-toggle-assign"):
            with self.subTest(name=name):
                response = self.client.get(
                    reverse(f"task_manager:{name}", args=[task.pk])
                )
                self.assertEqual(response.status_code, 405)

    def test_worker_detail_splits_tasks(self) -> None:
        self.create_task("Active").assignees.add(self.user)
        self.create_task("Finished", is_completed=True).assignees.add(
            self.user
        )
        response = self.client.get(self.user.get_absolute_url())
        self.assertEqual(
            [task.name for task in response.context["active_tasks"]],
            ["Active"],
        )
        self.assertEqual(
            [task.name for task in response.context["completed_tasks"]],
            ["Finished"],
        )

    def test_delete_position(self) -> None:
        position = Position.objects.create(name="Intern")
        response = self.client.post(
            reverse("task_manager:position-delete", args=[position.pk])
        )
        self.assertRedirects(response, reverse("task_manager:position-list"))
        self.assertFalse(Position.objects.filter(pk=position.pk).exists())
