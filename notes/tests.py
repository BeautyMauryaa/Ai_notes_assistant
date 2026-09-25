from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Note

User = get_user_model()


class NoteAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass12345")
        self.client.force_authenticate(user=self.user)

    @patch("notes.views.generate_ai_summary.delay")
    def test_create_note_triggers_ai_task(self, mock_delay):
        url = "/api/notes/notes/"
        response = self.client.post(url, {"title": "Test", "content": "Some content here."})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Note.objects.count(), 1)
        mock_delay.assert_called_once()

    def test_user_cannot_see_others_notes(self):
        other = User.objects.create_user(username="other", password="pass12345")
        Note.objects.create(owner=other, title="Not mine", content="secret")
        response = self.client.get("/api/notes/notes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Response is paginated: {"count", "next", "previous", "results"}
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(len(response.data["results"]), 0)


class NoteSearchTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester2", password="pass12345")
        self.client.force_authenticate(user=self.user)
        Note.objects.create(owner=self.user, title="Grocery list", content="milk, eggs")
        Note.objects.create(owner=self.user, title="Meeting notes", content="discuss roadmap")

    def test_search_by_title(self):
        response = self.client.get("/api/notes/notes/?search=grocery")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Grocery list")


class HealthCheckTests(APITestCase):
    def test_health_endpoint_is_public(self):
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["status"], "ok")


class GenAIServiceTests(APITestCase):
    def test_fallback_summary_without_api_key(self):
        from .ai_service import GenAIService

        service = GenAIService(api_key="")
        result = service.summarize_and_tag("word " * 40)
        self.assertIn("summary", result)
        self.assertIn("tags", result)
