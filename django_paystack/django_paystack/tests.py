import os
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.test import TestCase, override_settings
from django.shortcuts import reverse
from django.template import Context, Template
from paystack.utils import PaystackAPI, load_lib
from django.conf import settings


class PaystackTestCase(TestCase):

    def get_mock(self, mock_call, args):
        mock_instance = mock_call.return_value
        mock_instance.verify_payment.return_value = args
        return mock_instance

    @patch('paystack.utils.PaystackAPI')
    def test_when_successful_redirects_to_default_success_url_when_not_set(self, mock_call):
        mock_instance = self.get_mock(
            mock_call, (
                True, "verification successful"))
        response = self.client.get(
            "{}?amount=30000&trxref=biola23".format(reverse('paystack:verify_payment', args=['1234'])))
        mock_instance.verify_payment.assert_called_once_with("biola23", amount=30000)
        self.assertEqual(response.url, reverse(
            'paystack:successful_verification', args=['1234']))
        response = self.client.get(response.url)
        self.assertEqual(response.url, reverse('paystack:success_page'))

    @patch('paystack.utils.PaystackAPI')
    def test_when_fails_redirects_to_default_fail_url_when_not_set(self, mock_call):
        mock_instance = self.get_mock(
            mock_call, (
                False, "failed transaction"))
        response = self.client.get(
            "{}?amount=30000&trxref=biola23".format(reverse('paystack:verify_payment', args=['1234'])))
        mock_instance.verify_payment.assert_called_once_with("biola23", amount=30000)
        self.assertEqual(response.url, reverse(
            'paystack:failed_verification', args=['1234']))
        response = self.client.get(response.url)
        self.assertEqual(response.url, reverse('paystack:failed_page'))

    def test_template_tag_renders_correctly(self):
        template_val = Template(
            """
        {% load paystack %}
        {% paystack_button button_class="red" amount=3000 email="gboze2@example.com" %}
        """)
        context = Context({})
        template_response = template_val.render(context)
        self.assertIn('django-paystack-button', template_response)
        self.assertIn('gboze2@example.com', template_response)
        self.assertIn('300000', template_response)

    @patch('requests.get')
    def test_verify_payment_function_on_success(self, mock_post):
        mock_post.return_value = self.mock_request({
            "status": True,
            "message": "Verification successful",
            "data": {
                "amount": 27000,
                "currency": "NGN",
                "transaction_date": "2016-10-01T11:03:09.000Z",
                "status": "success",
                "reference": "DG4uishudoq90LD",
                "domain": "test",
                "metadata": 0,
                "gateway_response": "Successful",
                "message": None,
                "channel": "card",
                "ip_address": "41.1.25.1",
                "log": {
                    "time_spent": 9,
                    "attempts": 1,
                    "authentication": None,
                    "errors": 0,
                    "success": True,
                    "mobile": False,
                    "input": [],
                    "channel": None,
                    "history": [
                        {
                            "type": "input",
                            "message": "Filled these fields: card number, card expiry, card cvv",
                            "time": 7
                        },
                        {
                            "type": "action",
                            "message": "Attempted to pay",
                            "time": 7
                        },
                        {
                            "type": "success",
                            "message": "Successfully paid",
                            "time": 8
                        },
                        {
                            "type": "close",
                            "message": "Page closed",
                            "time": 9
                        }
                    ]
                },
                "fees": None,
                "authorization": {
                    "authorization_code": "AUTH_8dfhjjdt",
                    "card_type": "visa",
                    "last4": "1381",
                    "exp_month": "08",
                    "exp_year": "2018",
                    "bin": "412345",
                    "bank": "TEST BANK",
                    "channel": "card",
                    "signature": "SIG_idyuhgd87dUYSHO92D",
                    "reusable": True,
                    "country_code": "NG"
                },
                "customer": {
                    "id": 84312,
                    "customer_code": "CUS_hdhye17yj8qd2tx",
                    "first_name": "BoJack",
                    "last_name": "Horseman",
                    "email": "bojack@horseman.com"
                },
                "plan": "PLN_0as2m9n02cl0kp6"
            }
        })
        instance = PaystackAPI()
        response = instance.verify_payment("12345", amount=27000)
        mock_post.assert_called_once_with(
            "{}/transaction/verify/12345".format(instance.base_url),
            headers={
                'Authorization': "Bearer {}".format(instance.secret_key)
            })
        self.assertTrue(response[0])
        self.assertEqual(response[1], "Verification successful")

    @patch('requests.get')
    def test_verify_payment_function_on_fail(self, mock_post):
        mock_post.return_value = self.mock_request({
            "status": False,
            "message": "Invalid key"
        }, status_code=400)
        instance = PaystackAPI()
        response = instance.verify_payment("12345", amount=27000)

        self.assertFalse(response[0])
        self.assertEqual(response[1], "Could not verify transaction")

    def mock_request(self, data, status_code=200):
        return MockRequst(data, status_code=status_code)


class NewTestCase(TestCase):

    @patch('requests.get')
    def test_can_load_external_module(self, mock_post):
        mock_post.return_value = MockRequst({
            "status": False,
            "message": "Invalid key"
        }, status_code=400)
        instance = load_lib('django_paystack.mock_implement')()
        response = instance.verify_payment("12345", amount=27000)

        self.assertEqual(response, "hello")


class MockRequst(object):
    def __init__(self, response, **kwargs):
        self.response = response
        self.overwrite = True
        if kwargs.get('overwrite'):
            self.overwrite = True
        self.status_code = kwargs.get('status_code', 200)

    @classmethod
    def raise_for_status(cls):
        pass

    def json(self):
        if self.overwrite:
            return self.response
        return {'data': self.response}
