from django.core.management import call_command
from django.core.management.base import SystemCheckError
from django.test import TestCase, override_settings


class SystemChecksTestCase(TestCase):
    def test_system_checks_pass(self):
        call_command("check")

    @override_settings(SOCIAL_AUTH_GOOGLE_OAUTH2_KEY="")
    def test_google_oauth2_key_required(self):
        with self.assertRaises(SystemCheckError):
            call_command("check")

    @override_settings(SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET="")
    def test_google_oauth2_secret_required(self):
        with self.assertRaises(SystemCheckError):
            call_command("check")
