import pytest

from unittest import TestCase, mock
from paystack.utils import PaystackAPI, MockRequest

PAYSTACK_API_URL = 'https://api.paystack.co'


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
        response = {
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

    @mock.patch('requests.post')
    def test_create_recipient_success(self, mock_post):
        result = {
            "status": True,
            "message": "Recipient created",
            "data": {
                "type": "nuban",
                "name": "Zombie",
                "description": "Zombier",
                "metadata": {
                    "job": "Flesh Eater"
                },
                "domain": "test",
                "details": {
                    "account_number": "0100000010",
                    "account_name": None,
                    "bank_code": "044",
                    "bank_name": "Access Bank"
                },
                "currency": "NGN",
                "recipient_code": "RCP_1i2k27vk4suemug",
                "active": True,
                "id": 27,
                "createdAt": "2017-02-02T19:35:33.686Z",
                "updatedAt": "2017-02-02T19:35:33.686Z"
            }
        }
        mock_post.return_value = MockRequest(result)
        response = self.api.transfer_api.create_recipient(
            "Jamie Novak", "01000000010", 'Access Bank')
        mock_post.assert_called_once_with(
            "{}/transferrecipient".format(self.api.base_url),
            json={
                "type": "nuban",
                "name": "Jamie Novak",
                "description": "Jamie Novak",
                "account_number": "01000000010",
                "bank_code": "044",
                "currency": "NGN",
            },
            headers=self.headers)
        self.assertTrue(response[0])
        self.assertEqual(response[1], result['message'])
        self.assertEqual(response[2], result['data'])

    @mock.patch('requests.post')
    def test_create_recipient_fail(self, mock_post):
        mock_post.return_value = MockRequest(
            {
                "status": False,
                'message': "Account number is invalid"
            },
            status_code=400)
        result = self.api.transfer_api.create_recipient(
            "Jamie Novak", "01000000010", 'Access Bank')

        self.assertFalse(result[0])
        self.assertEqual(result[1], "Account number is invalid")

    @mock.patch('requests.post')
    def test_initialize_transfer_success(self, mock_post):
        result = {
            "status": True,
            "message": "Transfer requires OTP to continue",
            "data": {
                "integration": 100073,
                "domain": "test",
                "amount": 3794800,
                "currency": "NGN",
                "source": "balance",
                "reason": "Calm down",
                "recipient": 28,
                "status": "otp",
                "transfer_code": "TRF_1ptvuv321ahaa7q",
                "id": 14,
                "createdAt": "2017-02-03T17:21:54.508Z",
                "updatedAt": "2017-02-03T17:21:54.508Z"
            }
        }
        mock_post.return_value = MockRequest(result)
        response = self.api.transfer_api.initialize_transfer(
            37948, "RCP_gx2wn530m0i3w3m", "Calm down")
        mock_post.assert_called_once_with(
            "{}/transfer".format(self.api.base_url),
            json={
                "source": "balance",
                "reason": "Calm down",
                "amount": 3794800,
                "recipient": "RCP_gx2wn530m0i3w3m"
            },
            headers=self.headers)
        self.assertTrue(response[0])
        self.assertEqual(response[1], result['message'])
        self.assertEqual(response[2], result['data'])

    @mock.patch('requests.post')
    def test_initialize_transfer_failed(self, mock_post):
        mock_post.return_value = MockRequest(
            {
                "status": False,
                'message': "The customer specified has no saved authorizations"
            },
            status_code=400)
        result = self.api.transfer_api.initialize_transfer(
            37948, "RCP_gx2wn530m0i3w3m", "Calm down")

        self.assertFalse(result[0])
        self.assertEqual(result[1],
                         "The customer specified has no saved authorizations")

    @mock.patch('requests.post')
    def test_verify_transfer_success(self, mock_post):
        result = {}
        mock_post.return_value = MockRequest(result)
        response = self.api.transfer_api.verify_transfer(
            "TRF_2x5j67tnnw1t98k", "1001")
        mock_post.assert_called_once_with(
            "{}/transfer/finalize_transfer".format(self.api.base_url),
            json={
                "transfer_code": "TRF_2x5j67tnnw1t98k",
                "otp": "1001"
            },
            headers=self.headers)
        self.assertTrue(response[0])

    @mock.patch('requests.post')
    def test_verify_transfer_failed(self, mock_post):
        mock_post.return_value = MockRequest(
            {
                "status": False,
                'message': "Transfer is not currently awaiting OTP"
            },
            status_code=400)
        result = self.api.transfer_api.verify_transfer("TRF_2x5j67tnnw1t98k",
                                                       "1001")

        self.assertFalse(result[0])
        self.assertEqual(result[1], "Transfer is not currently awaiting OTP")

    @mock.patch('requests.get')
    def test_get_transfer_success(self, mock_get):
        result = {
            "status": True,
            "message": "Transfer retrieved",
            "data": {
                "recipient": {
                    "domain": "test",
                    "type": "nuban",
                    "currency": "NGN",
                    "name": "Flesh",
                    "details": {
                        "account_number": "olounje",
                        "account_name": None,
                        "bank_code": "044",
                        "bank_name": "Access Bank"
                    },
                    "metadata": None,
                    "recipient_code": "RCP_2x5j67tnnw1t98k",
                    "active": True,
                    "id": 28,
                    "integration": 100073,
                    "createdAt": "2017-02-02T19:39:04.000Z",
                    "updatedAt": "2017-02-02T19:39:04.000Z"
                },
                "domain": "test",
                "amount": 4400,
                "currency": "NGN",
                "source": "balance",
                "source_details": None,
                "reason": "Redemption",
                "status": "pending",
                "failures": None,
                "transfer_code": "TRF_2x5j67tnnw1t98k",
                "id": 14938,
                "createdAt": "2017-02-03T17:21:54.000Z",
                "updatedAt": "2017-02-03T17:21:54.000Z"
            }
        }
        mock_get.return_value = MockRequest(result)
        response = self.api.transfer_api.get_transfer("TRF_2x5j67tnnw1t98k")
        mock_get.assert_called_once_with(
            "{}/transfer/{}".format(self.api.base_url, "TRF_2x5j67tnnw1t98k"),
            headers=self.headers)
        self.assertTrue(response[0])
        self.assertEqual(response[1], result['message'])
        self.assertEqual(response[2], result['data'])

    @mock.patch('requests.get')
    def test_get_transfer_failed(self, mock_get):
        mock_get.return_value = MockRequest(
            {
                "status": False,
                "message": "Transfer ID/code specified is invalid"
            },
            status_code=400)
        result = self.api.transfer_api.get_transfer("TRF_2x5j67tnnw1t98k")

        self.assertFalse(result[0])
        self.assertEqual(result[1], "Transfer ID/code specified is invalid")

    @mock.patch('requests.post')
    def test_transfer_bulk_success(self, mock_post):
        result = {"status": True, "message": "2 transfers queued."}
        mock_post.return_value = MockRequest(result)
        transfers = [
            {
                "amount": 500,
                "recipient": "RCP_gx2wn530m0i3w3m"
            },
        ]
        transform = [{
            'amount': x['amount'] * 100,
            'recipient': x['recipient']
        } for x in transfers]
        response = self.api.transfer_api.bulk_transfer(transfers)
        json_data = {
            "currency": "NGN",
            "source": "balance",
            "transfers": transform,
        }
        mock_post.assert_called_once_with(
            "{}/transfer/bulk".format(self.api.base_url),
            json=json_data,
            headers=self.headers)
        self.assertTrue(response[0])
        self.assertEqual(response[1], result['message'])

    @mock.patch('requests.post')
    def test_transfer_bulk_failed(self, mock_post):
        mock_post.return_value = MockRequest(
            {
                "status": False,
                "message": "The customer specified has no saved authorizations"
            },
            status_code=400)
        transfers = [
            {
                "amount": 500,
                "recipient": "RCP_gx2wn530m0i3w3m"
            },
        ]

        result = self.api.transfer_api.bulk_transfer(transfers)

        self.assertFalse(result[0])
        self.assertEqual(result[1],
                         "The customer specified has no saved authorizations")

    @mock.patch('requests.get')
    def test_get_balance(self, mock_get):
        mock_get.return_value = MockRequest({
            "status":
            True,
            "message":
            "Balances retrieved",
            "data": [{
                "currency": "NGN",
                "balance": 123120000
            }]
        })
        result = self.api.transfer_api.check_balance()
        self.assertEqual(result, [{"currency": "NGN", "balance": 1231200}])
