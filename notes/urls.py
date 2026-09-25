from rest_framework.routers import DefaultRouter
from .views import NoteViewSet, TaskViewSet

router = DefaultRouter()
router.register("notes", NoteViewSet, basename="note")
router.register("tasks", TaskViewSet, basename="task")

urlpatterns = router.urls
