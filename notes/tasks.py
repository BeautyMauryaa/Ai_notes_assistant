from celery import shared_task

from .models import Note
from .ai_service import GenAIService


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def generate_ai_summary(self, note_id: int):
    """
    Background job triggered after a Note is created/updated.
    Calls the GenAI service and persists the summary + tags.
    This is the Celery + Redis + GenAI piece requested in the JD.
    """
    try:
        note = Note.objects.get(id=note_id)
    except Note.DoesNotExist:
        return

    note.ai_status = Note.Status.PROCESSING
    note.save(update_fields=["ai_status"])

    try:
        service = GenAIService()
        result = service.summarize_and_tag(note.content)
        note.ai_summary = result["summary"]
        note.ai_tags = result["tags"]
        note.ai_status = Note.Status.DONE
        note.save(update_fields=["ai_summary", "ai_tags", "ai_status"])
    except Exception as exc:
        note.ai_status = Note.Status.FAILED
        note.save(update_fields=["ai_status"])
        raise self.retry(exc=exc)
