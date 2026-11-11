from django.core.management import call_command
from django.core.management.base import BaseCommand

from task_manager.models import Task


class Command(BaseCommand):
    help = "Load demo data once: skipped if the database already has tasks."

    def handle(self, *args, **options) -> None:
        if Task.objects.exists():
            self.stdout.write("Demo data skipped: tasks already exist.")
            return
        call_command("loaddata", "demo_data.json")
        self.stdout.write(self.style.SUCCESS("Demo data loaded."))
