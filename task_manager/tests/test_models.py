import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from task_manager.models import Position, Tag, Task, TaskType


class ModelTests(TestCase):
    def setUp(self) -> None:
        self.position = Position.objects.create(name="Developer")
        self.worker = get_user_model().objects.create_user(
            username="john",
            password="Secret12345!",
            first_name="John",
            last_name="Doe",
            position=self.position,
        )
        self.task_type = TaskType.objects.create(name="Bug")

    def test_simple_models_str(self) -> None:
        self.assertEqual(str(self.position), "Developer")
        self.assertEqual(str(self.task_type), "Bug")
        self.assertEqual(str(Tag.objects.create(name="backend")), "backend")

    def test_worker_str(self) -> None:
        self.assertEqual(str(self.worker), "john (John Doe)")
        nameless = get_user_model().objects.create_user(
            username="anon", password="Secret12345!"
        )
        self.assertEqual(str(nameless), "anon")

    def test_worker_password_is_hashed(self) -> None:
        self.assertNotEqual(self.worker.password, "Secret12345!")
        self.assertTrue(self.worker.check_password("Secret12345!"))

    def test_task_defaults_and_url(self) -> None:
        task = Task.objects.create(
            name="Fix login",
            deadline=datetime.date.today(),
            task_type=self.task_type,
        )
        self.assertFalse(task.is_completed)
        self.assertEqual(task.priority, Task.Priority.MEDIUM)
        self.assertEqual(str(task), "Fix login")
        self.assertEqual(
            task.get_absolute_url(),
            reverse("task_manager:task-detail", kwargs={"pk": task.pk}),
        )

    def test_tasks_ordered_by_status_and_deadline(self) -> None:
        today = datetime.date.today()
        late = Task.objects.create(
            name="Later",
            deadline=today + datetime.timedelta(days=5),
            task_type=self.task_type,
        )
        done = Task.objects.create(
            name="Done",
            deadline=today,
            task_type=self.task_type,
            is_completed=True,
        )
        soon = Task.objects.create(
            name="Soon", deadline=today, task_type=self.task_type
        )
        self.assertEqual(list(Task.objects.all()), [soon, late, done])

    def test_deleting_position_keeps_worker(self) -> None:
        self.position.delete()
        self.worker.refresh_from_db()
        self.assertIsNone(self.worker.position)
