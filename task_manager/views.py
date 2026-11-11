from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import generic

from task_manager.models import Position, Tag, Task, TaskType, Worker


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


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    paginate_by = 10
    queryset = Task.objects.select_related("task_type").prefetch_related(
        "tags"
    )


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task
    queryset = Task.objects.select_related("task_type").prefetch_related(
        "assignees__position", "tags"
    )


class WorkerListView(LoginRequiredMixin, generic.ListView):
    model = Worker
    paginate_by = 10
    queryset = Worker.objects.select_related("position")


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    model = Worker
    queryset = Worker.objects.select_related("position")

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        tasks = self.object.tasks.select_related("task_type")
        context["active_tasks"] = tasks.filter(is_completed=False)
        context["completed_tasks"] = tasks.filter(is_completed=True)
        return context


class PositionListView(LoginRequiredMixin, generic.ListView):
    model = Position
    paginate_by = 10


class TaskTypeListView(LoginRequiredMixin, generic.ListView):
    model = TaskType
    paginate_by = 10


class TagListView(LoginRequiredMixin, generic.ListView):
    model = Tag
    paginate_by = 10
