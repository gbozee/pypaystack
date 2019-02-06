import pytest

from unittest import TestCase, mock
from paystack.utils import PaystackAPI, MockRequest

PAYSTACK_API_URL = 'https://api.paystack.co'


def test_verify_payment_failed(get_request, paystack_api):
    get_request({"status": False, 'message': "Invalid key"}, status_code=400)
    response = paystack_api.verify_payment("1234", amount=20000)
    assert not response[0]
    assert response[1] == "Could not verify transaction"


verify_payment_response = {
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
            "time_spent":
            9,
            "attempts":
            1,
            "authentication":
            None,
            "errors":
            0,
            "success":
            True,
            "mobile":
            False,
            "input": [],
            "channel":
            None,
            "history": [{
                "type":
                "input",
                "message":
                "Filled these fields: card number, card expiry, card cvv",
                "time":
                7
            }, {
                "type": "action",
                "message": "Attempted to pay",
                "time": 7
            }, {
                "type": "success",
                "message": "Successfully paid",
                "time": 8
            }, {
                "type": "close",
                "message": "Page closed",
                "time": 9
            }]
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
}


class TestTransactionTestCase(TestCase):
    def setUp(self):
        self.api = PaystackAPI(
            public_key="public_key",
            secret_key="secret_key",
            django=False,
            base_url=PAYSTACK_API_URL)
        self.headers = {
            'Authorization': "Bearer {}".format(self.api.secret_key),
            'Content-Type': 'application/json'
        }

    @mock.patch('requests.get')
    def test_verify_payment_failed(self, mock_get):
        mock_get.return_value = MockRequest(
            {
                "status": False,
                'message': "Invalid key"
            }, status_code=400)
        response = self.api.transaction_api.verify_payment(
            "1234", amount=20000)
        self.assertFalse(response[0])
        self.assertEqual(response[1], "Could not verify transaction")

    @mock.patch('requests.get')
    def test_verify_payment_success(self, mock_get):
        response = verify_payment_response
        code = "1234"
        mock_get.return_value = MockRequest(response)
        result = self.api.transaction_api.verify_payment(code)
        mock_get.assert_called_once_with(
            "{}/transaction/verify/{}".format(self.api.base_url, code),
            headers=self.headers)
        self.assertTrue(result[0])
        self.assertEqual(result[1], "Verification successful")
        self.assertEqual(
            result[2]['customer'], {
                "id": 84312,
                "customer_code": "CUS_hdhye17yj8qd2tx",
                "first_name": "BoJack",
                "last_name": "Horseman",
                "email": "bojack@horseman.com"
            })
        paystack_details = self.api.transaction_api.get_customer_and_auth_details(
            result[2])
        self.assertEqual(
            paystack_details, {
                'authorization': response['data']['authorization'],
                'customer': response['data']['customer'],
                'plan': response['data']['plan']
            })

    @mock.patch('requests.post')
    def test_recurrent_charge_success_valid(self, mock_post):
        result = {
            "status": True,
            "message": "Charge attempted",
            "data": {
                "amount": 500000,
                "currency": "NGN",
                "transaction_date": "2016-10-01T14:29:53.000Z",
                "status": "success",
                "reference": "0bxco8lyc2aa0fq",
                "domain": "live",
                "metadata": None,
                "gateway_response": "Successful",
                "message": None,
                "channel": "card",
                "ip_address": None,
                "log": None,
                "fees": None,
                "authorization": {
                    "authorization_code": "AUTH_5z72ux0koz",
                    "bin": "408408",
                    "last4": "4081",
                    "exp_month": "12",
                    "exp_year": "2020",
                    "channel": "card",
                    "card_type": "visa DEBIT",
                    "bank": "Test Bank",
                    "country_code": "NG",
                    "brand": "visa",
                    "reusable": True,
                    "signature": "SIG_ZdUx7Z5ujd75rt9OMTN4"
                },
                "customer": {
                    "id": 90831,
                    "customer_code": "CUS_fxg9930u8pqeiu",
                    "first_name": "Bojack",
                    "last_name": "Horseman",
                    "email": "bojack@horsinaround.com"
                },
                "plan": 0
            }
        }
        mock_post.return_value = MockRequest(result)
        json_data = dict(
            authorization_code="AUTH_5z72ux0koz",
            email="bojack@horsinaround.com",
            amount=5000)
        response = self.api.transaction_api.recurrent_charge(**json_data)
        mock_post.assert_called_once_with(
            "{}/transaction/charge_authorization".format(self.api.base_url),
            json={
                "authorization_code": json_data['authorization_code'],
                'email': json_data['email'],
                'amount': json_data['amount'] * 100
            },
            headers=self.headers)
        self.assertTrue(response[0])
        self.assertEqual(response[1], result['message'])
        self.assertEqual(response[2], result['data'])
        self.assertEqual(response[2]['status'], 'success')

    @mock.patch('requests.post')
    def test_recurrent_charge_success_invalid(self, mock_post):
        result = {
            "status": True,
            "message": "Charge Attempted",
            "data": {
                "amount": 27000,
                "currency": "NGN",
                "transaction_date": "2016-10-01T11:03:09.000Z",
                "status": "failed",
                "reference": "DG4uishudoq90LD",
                "domain": "test",
                "metadata": 0,
                "gateway_response": "Insufficient Funds",
                "message": None,
                "channel": "card",
                "ip_address": "41.1.25.1",
                "log": None,
                "fees": None,
                "authorization": {
                    "authorization_code": "AUTH_5z72ux0koz",
                    "bin": "408408",
                    "last4": "4081",
                    "exp_month": "12",
                    "exp_year": "2020",
                    "channel": "card",
                    "card_type": "visa DEBIT",
                    "bank": "Test Bank",
                    "country_code": "NG",
                    "brand": "visa",
                    "reusable": True,
                    "signature": "SIG_ZdUx7Z5ujd75rt9OMTN4"
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
        }
        mock_post.return_value = MockRequest(result)
        json_data = dict(
            authorization_code="AUTH_5z72ux0koz",
            email="bojack@horsinaround.com",
            amount=5000)
        response = self.api.transaction_api.recurrent_charge(**json_data)
        mock_post.assert_called_once_with(
            "{}/transaction/charge_authorization".format(self.api.base_url),
            json={
                "authorization_code": json_data['authorization_code'],
                'email': json_data['email'],
                'amount': json_data['amount'] * 100
            },
            headers=self.headers)
        self.assertTrue(response[0])
        self.assertEqual(response[1], result['message'])
        self.assertEqual(response[2], result['data'])
        self.assertEqual(response[2]['status'], 'failed')

    @mock.patch('requests.post')
    def test_recurrent_charge_success_failed(self, mock_post):
        mock_post.return_value = MockRequest(
            {
                "status": False,
                "message": "Invalid key"
            }, status_code=400)
        json_data = dict(
            authorization_code="AUTH_5z72ux0koz",
            email="bojack@horsinaround.com",
            amount=5000)
        result = self.api.transaction_api.recurrent_charge(**json_data)
        self.assertFalse(result[0])
        self.assertEqual(result[1], "Invalid key")

    @mock.patch('requests.post')
    def test_initialize_transaction_success(self, mock_post):
        result = {
            "status": True,
            "message": "Authorization URL created",
            "data": {
                "authorization_url":
                "https://checkout.paystack.com/0peioxfhpn",
                "access_code": "0peioxfhpn",
                "reference": "7PVGX8MEk85tgeEpVDtD"
            }
        }
        mock_post.return_value = MockRequest(result)
        json_data = {
            'reference': "7PVGX8MEk85tgeEpVDtD",
            'email': 'james@example.com',
            'amount': 20000,
            'callback_url': "http://example.com"
        }
        response = self.api.transaction_api.initialize_transaction(**json_data)
        mock_post.assert_called_once_with(
            "{}/transaction/initialize".format(self.api.base_url),
            json={
                "reference": json_data['reference'],
                'email': json_data['email'],
                'amount': json_data['amount'] * 100,
                'callback_url': json_data['callback_url']
            },
            headers=self.headers)
        self.assertTrue(response[0])
        self.assertEqual(response[1], result['message'])
        self.assertEqual(response[2], result['data'])
