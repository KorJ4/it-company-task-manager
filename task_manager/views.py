from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from task_manager.models import Task, Worker


@login_required
def index(request: HttpRequest) -> HttpResponse:
    num_visits = request.session.get("num_visits", 0) + 1
    request.session["num_visits"] = num_visits
    my_tasks = (
        request.user.tasks.filter(is_completed=False)
        .select_related("task_type")
        .order_by("deadline")[:5]
    )
    context = {
        "num_tasks": Task.objects.count(),
        "num_active_tasks": Task.objects.filter(is_completed=False).count(),
        "num_completed_tasks": Task.objects.filter(is_completed=True).count(),
        "num_workers": Worker.objects.count(),
        "my_tasks": my_tasks,
        "num_visits": num_visits,
    }
    return render(request, "task_manager/index.html", context=context)
