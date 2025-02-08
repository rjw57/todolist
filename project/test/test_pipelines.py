from unittest import mock

from django.test import TestCase
from social_core.exceptions import AuthForbidden

from .. import pipelines

TEST_DOMAINS = ["example.com", "example.invalid"]


class EnforceHostedDomainTestCase(TestCase):
    def setUp(self):
        self.backend = mock.MagicMock()
        self.backend.setting.return_value = TEST_DOMAINS
        self.user = mock.MagicMock()

    def test_no_whitelisted_hosted_domains_ok(self):
        self.backend.setting.return_value = None
        pipelines.enforce_hosted_domain(self.backend, self.user, {})
        self.backend.setting.assert_called_with("WHITELISTED_HOSTED_DOMAINS", None)

    def test_whitelisted_hosted_domains_ok(self):
        for hd in TEST_DOMAINS:
            pipelines.enforce_hosted_domain(self.backend, self.user, {"hd": hd})

    def test_hd_required_for_whitelisted_domains(self):
        with self.assertRaises(AuthForbidden):
            pipelines.enforce_hosted_domain(self.backend, self.user, {})

    def test_correct_hd_required_for_whitelisted_domains(self):
        for hd in TEST_DOMAINS:
            pipelines.enforce_hosted_domain(self.backend, self.user, {"hd": hd})
        with self.assertRaises(AuthForbidden):
            pipelines.enforce_hosted_domain(self.backend, self.user, {"hd": "another.invalid"})
