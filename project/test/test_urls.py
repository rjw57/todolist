"""
Test basic functionality of project-specific views.

"""
from django.test import TestCase
from django.urls import reverse


class HealthyTest(TestCase):
    def test_healthy(self):
        """GET-ing healthy page should succeed."""
        r = self.client.get(reverse("healthy"))
        self.assertEqual(r.status_code, 200)
