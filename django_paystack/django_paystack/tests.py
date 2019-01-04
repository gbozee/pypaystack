import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.test import TestCase
from django.shortcuts import reverse
from django.template import Context, Template
from paystack.utils import MockRequest


class PaystackTestCase(TestCase):
    def get_mock(self, mock_call, args):
        mock_instance = mock_call.return_value
        mock_instance.verify_payment.return_value = args
        return mock_instance

    @patch('paystack.utils.PaystackAPI')
    def test_when_successful_redirects_to_default_success_url_when_not_set(
            self, mock_call):
        mock_instance = self.get_mock(mock_call,
                                      (True, "verification successful"))
        response = self.client.get("{}?amount=30000&trxref=biola23".format(
            reverse('paystack:verify_payment', args=['1234'])))
        mock_instance.verify_payment.assert_called_once_with(
            "biola23",
            amount=30000,
        )
        self.assertEqual(response.url,
                         reverse(
                             'paystack:successful_verification',
                             args=['1234']))

        response = self.client.get(response.url)
        self.assertEqual(response.url, reverse('paystack:success_page'))

    @patch('paystack.utils.PaystackAPI')
    def test_when_fails_redirects_to_default_fail_url_when_not_set(
            self, mock_call):
        mock_instance = self.get_mock(mock_call, (False, "failed transaction"))
        response = self.client.get("{}?amount=30000&trxref=biola23".format(
            reverse('paystack:verify_payment', args=['1234'])))
        mock_instance.verify_payment.assert_called_once_with(
            "biola23", amount=30000)
        self.assertEqual(response.url,
                         reverse(
                             'paystack:failed_verification', args=['1234']))
        response = self.client.get(response.url)
        self.assertEqual(response.url, reverse('paystack:failed_page'))

    def test_template_tag_renders_correctly(self):
        template_val = Template("""
        {% load paystack %}
        {% paystack_button button_class="red" amount=3000 email="gboze2@example.com" %}
        """)
        context = Context({})
        template_response = template_val.render(context)
        self.assertIn('django-paystack-button', template_response)
        self.assertIn('gboze2@example.com', template_response)
        self.assertIn('300000', template_response)

    def mock_request(self, data, status_code=200):
        return MockRequest(data, status_code=status_code)


class NewTestCase(unittest.TestCase):
    def setUp(self):
        from paystack.utils import load_lib
        self.instance = load_lib('django_paystack.mock_implement')()

    @patch('requests.get')
    def test_can_load_external_module(self, mock_post):
        mock_post.return_value = MockRequest(
            {
                "status": False,
                "message": "Invalid key"
            }, status_code=400)
        response = self.instance.verify_payment("12345", amount=27000)

        self.assertEqual(response, "hello")
