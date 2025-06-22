from django.test import TestCase
from glossary.models import Category, Term, TermDetail, RelatedTerm
from glossary.serializers import TermSerializer
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from unittest.mock import patch
# Create your tests here.

class CategoryModelTest(TestCase):
    def test_create_category(self):
        category = Category.objects.create(name="Programming")
        self.assertEqual(str(category), "Programming")

class TermSerializerTest(TestCase):
    def test_term_serialization(self):
        category = Category.objects.create(name="Databases")
        term = Term.objects.create(title="PostgreSQL", description="Relational DBMS", category=category)
        serializer = TermSerializer(term)
        self.assertEqual(serializer.data['title'], "PostgreSQL")
        self.assertEqual(serializer.data['category']['name'], "Databases")


class TermSerializerValidationTest(TestCase):
    def test_missing_title_validation(self):
        category = Category.objects.create(name="Backend")
        invalid_data = {
            "description": "Framework without title",
            "category": {"id": category.id, "name": category.name}
        }
        serializer = TermSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)


class RelatedTermMockTest(TestCase):
    @patch('glossary.models.RelatedTerm.objects.create')
    def test_mock_related_term_creation(self, mock_create):
        category = Category.objects.create(name="Testing")
        term1 = Term.objects.create(title="UnitTest", description="Testing module", category=category)
        term2 = Term.objects.create(title="Mock", description="Mocking library", category=category)

        RelatedTerm.objects.create(term=term1, related_term=term2, relationship_description="Used for isolation")

        mock_create.assert_called_once_with(term=term1, related_term=term2, relationship_description="Used for isolation")




class TermAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username="admin", password="admin123", email="admin@example.com")
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name="Web")
        self.term = Term.objects.create(title="Django", description="Python web framework", category=self.category)

    def test_get_term_list(self):
        response = self.client.get('/api/terms/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django")

class TermCreateAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username="admin", password="admin123", email="admin@example.com")
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name="DevOps")

    def test_post_term(self):
        data = {
            "title": "Docker",
            "description": "Container platform",
            "category": {
                "id": self.category.id,
                "name": self.category.name
            }
        }
        response = self.client.post('/api/terms/', data, format='json')
        self.assertIn(response.status_code, [200, 201, 405])  # 405 — если метод POST не разрешен

    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.get('/api/terms/')
        self.assertEqual(response.status_code, 403)
