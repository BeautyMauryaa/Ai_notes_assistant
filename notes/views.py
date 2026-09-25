import logging

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Note, Task
from .serializers import NoteSerializer, TaskSerializer
from .tasks import generate_ai_summary

logger = logging.getLogger("notes")


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner_id == request.user.id


class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filterset_fields = ["ai_status"]
    search_fields = ["title", "content"]
    ordering_fields = ["created_at", "updated_at", "title"]

    def get_queryset(self):
        return Note.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        note = serializer.save(owner=self.request.user)
        logger.info("Note %s created by user %s, queuing AI summarization", note.id, self.request.user.id)
        # Fire the async GenAI summarization job — request returns immediately.
        generate_ai_summary.delay(note.id)

    def perform_update(self, serializer):
        note = serializer.save()
        logger.info("Note %s updated, re-queuing AI summarization", note.id)
        generate_ai_summary.delay(note.id)

    @action(detail=True, methods=["post"])
    def reprocess(self, request, pk=None):
        """Manually re-trigger the AI summarization job for a note."""
        note = self.get_object()
        logger.info("Manual reprocess requested for note %s", note.id)
        generate_ai_summary.delay(note.id)
        return Response({"detail": "Reprocessing queued."}, status=status.HTTP_202_ACCEPTED)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
