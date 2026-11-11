from django.urls import path

from task_manager.views import (
    PositionListView,
    TagListView,
    TaskDetailView,
    TaskListView,
    TaskTypeListView,
    WorkerDetailView,
    WorkerListView,
    index,
)

urlpatterns = [
    path("", index, name="index"),
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("workers/", WorkerListView.as_view(), name="worker-list"),
    path(
        "workers/<int:pk>/",
        WorkerDetailView.as_view(),
        name="worker-detail",
    ),
    path("positions/", PositionListView.as_view(), name="position-list"),
    path("task-types/", TaskTypeListView.as_view(), name="task-type-list"),
    path("tags/", TagListView.as_view(), name="tag-list"),
]

app_name = "task_manager"
