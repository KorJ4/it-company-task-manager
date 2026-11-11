import datetime

from django.test import TestCase

from task_manager.forms import SearchForm, TaskForm, WorkerCreationForm
from task_manager.models import Position, TaskType


class TaskFormTests(TestCase):
    def setUp(self) -> None:
        self.task_type = TaskType.objects.create(name="Feature")
        self.data = {
            "name": "Landing page",
            "description": "",
            "deadline": datetime.date.today() + datetime.timedelta(days=3),
            "priority": "high",
            "task_type": self.task_type.pk,
        }

    def test_valid_task_form(self) -> None:
        self.assertTrue(TaskForm(data=self.data).is_valid())

    def test_deadline_in_the_past_is_rejected(self) -> None:
        self.data["deadline"] = datetime.date.today() - datetime.timedelta(
            days=1
        )
        form = TaskForm(data=self.data)
        self.assertFalse(form.is_valid())
        self.assertIn("deadline", form.errors)

    def test_task_type_is_required(self) -> None:
        del self.data["task_type"]
        self.assertFalse(TaskForm(data=self.data).is_valid())


class WorkerCreationFormTests(TestCase):
    def test_form_with_position(self) -> None:
        position = Position.objects.create(name="QA")
        form = WorkerCreationForm(
            data={
                "username": "new.worker",
                "password1": "Worker12345test",
                "password2": "Worker12345test",
                "first_name": "New",
                "last_name": "Worker",
                "email": "new@example.com",
                "position": position.pk,
            }
        )
        self.assertTrue(form.is_valid())
        worker = form.save()
        self.assertEqual(worker.position, position)
        self.assertTrue(worker.check_password("Worker12345test"))


class SearchFormTests(TestCase):
    def test_empty_query_is_valid(self) -> None:
        form = SearchForm(data={"query": ""})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["query"], "")

    def test_too_long_query_is_invalid(self) -> None:
        self.assertFalse(SearchForm(data={"query": "a" * 256}).is_valid())
