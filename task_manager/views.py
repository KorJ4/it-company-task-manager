from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from task_manager.forms import (
    SearchForm,
    TaskForm,
    WorkerCreationForm,
    WorkerUpdateForm,
)
from task_manager.models import Position, Tag, Task, TaskType, Worker


class ModelNameMixin:
    """Adds a human-readable model name for the shared templates."""

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["model_name"] = self.model._meta.verbose_name
        return context


class SearchListMixin:
    """Filters a ListView by the ``?query=`` GET parameter."""

    search_lookup = "name__icontains"

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        form = SearchForm(self.request.GET)
        if form.is_valid() and form.cleaned_data["query"]:
            return queryset.filter(
                **{self.search_lookup: form.cleaned_data["query"]}
            )
        return queryset

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("query", "")
        context["search_form"] = SearchForm(initial={"query": query})
        return context


class FormPageMixin(LoginRequiredMixin, ModelNameMixin):
    template_name = "task_manager/form.html"


class DeletePageMixin(LoginRequiredMixin, ModelNameMixin):
    template_name = "task_manager/confirm_delete.html"


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


class TaskListView(
    LoginRequiredMixin, SearchListMixin, generic.ListView
):
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


class WorkerListView(
    LoginRequiredMixin, SearchListMixin, generic.ListView
):
    model = Worker
    search_lookup = "username__icontains"
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


class PositionListView(
    LoginRequiredMixin, SearchListMixin, generic.ListView
):
    model = Position
    paginate_by = 10


class TaskTypeListView(
    LoginRequiredMixin, SearchListMixin, generic.ListView
):
    model = TaskType
    paginate_by = 10


class TagListView(
    LoginRequiredMixin, SearchListMixin, generic.ListView
):
    model = Tag
    paginate_by = 10


class TaskCreateView(FormPageMixin, generic.CreateView):
    model = Task
    form_class = TaskForm


class TaskUpdateView(FormPageMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm


class TaskDeleteView(DeletePageMixin, generic.DeleteView):
    model = Task
    success_url = reverse_lazy("task_manager:task-list")


class WorkerCreateView(FormPageMixin, generic.CreateView):
    model = Worker
    form_class = WorkerCreationForm


class WorkerUpdateView(FormPageMixin, generic.UpdateView):
    model = Worker
    form_class = WorkerUpdateForm


class WorkerDeleteView(DeletePageMixin, generic.DeleteView):
    model = Worker
    success_url = reverse_lazy("task_manager:worker-list")


class PositionCreateView(FormPageMixin, generic.CreateView):
    model = Position
    fields = "__all__"
    success_url = reverse_lazy("task_manager:position-list")


class PositionUpdateView(FormPageMixin, generic.UpdateView):
    model = Position
    fields = "__all__"
    success_url = reverse_lazy("task_manager:position-list")


class PositionDeleteView(DeletePageMixin, generic.DeleteView):
    model = Position
    success_url = reverse_lazy("task_manager:position-list")


class TaskTypeCreateView(FormPageMixin, generic.CreateView):
    model = TaskType
    fields = "__all__"
    success_url = reverse_lazy("task_manager:task-type-list")


class TaskTypeUpdateView(FormPageMixin, generic.UpdateView):
    model = TaskType
    fields = "__all__"
    success_url = reverse_lazy("task_manager:task-type-list")


class TaskTypeDeleteView(DeletePageMixin, generic.DeleteView):
    model = TaskType
    success_url = reverse_lazy("task_manager:task-type-list")


class TagCreateView(FormPageMixin, generic.CreateView):
    model = Tag
    fields = "__all__"
    success_url = reverse_lazy("task_manager:tag-list")


class TagUpdateView(FormPageMixin, generic.UpdateView):
    model = Tag
    fields = "__all__"
    success_url = reverse_lazy("task_manager:tag-list")


class TagDeleteView(DeletePageMixin, generic.DeleteView):
    model = Tag
    success_url = reverse_lazy("task_manager:tag-list")
