"""
Tests for views.

"""
from django.test import TestCase
from django.urls import reverse


class IndexTests(TestCase):
    def test_home(self):
        r = self.client.get(reverse("ui:home"))
        self.assertEqual(r.status_code, 200)
