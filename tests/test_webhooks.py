from paystack import signals
from dispatch import receiver
import pytest


@receiver(signals.successful_payment_signal)
def signal_called(sender, **kwargs):
    kwargs.pop('signal', None)
    generic_function(**kwargs)


def generic_function(**params):
    print(params)


@receiver(signals.successful_transfer_signal)
def signal_called_2(sender, **kwargs):
    kwargs.pop('signal', None)
    generic_function(**kwargs)


@receiver(signals.failed_transfer_signal)
def signal_called_3(sender, **kwargs):
    kwargs.pop('signal', None)
    generic_function(**kwargs)


@pytest.fixture
def mock_generic_fuc(mocker):
    mock_successful_transer = mocker.patch('test_webhooks.generic_function')
    mock_digest = mocker.patch('paystack.api.webhook.generate_digest')
    mock_digest.return_value = "1001"
    return mock_successful_transer


def test_successful_webhook_signals(mock_generic_fuc, paystack_api):
    body = """{  
   "event":"charge.success",
   "data":{  
      "id":302961,
      "domain":"live",
      "status":"success",
      "reference":"qTPrJoy9Bx",
      "amount":10000,
      "message":null,
      "gateway_response":"Approved by Financial Institution",
      "paid_at":"2016-09-30T21:10:19.000Z",
      "created_at":"2016-09-30T21:09:56.000Z",
      "channel":"card",
      "currency":"NGN",
      "ip_address":"41.242.49.37",
      "metadata":0,
      "log":{  
         "time_spent":16,
         "attempts":1,
         "authentication":"pin",
         "errors":0,
         "success":false,
         "mobile":false,
         "input":[  

         ],
         "channel":null,
         "history":[  
            {  
               "type":"input",
               "message":"Filled these fields: card number, card expiry, card cvv",
               "time":15
            },
            {  
               "type":"action",
               "message":"Attempted to pay",
               "time":15
            },
            {  
               "type":"auth",
               "message":"Authentication Required: pin",
               "time":16
            }
         ]
      },
      "fees":null,
      "customer":{  
         "id":68324,
         "first_name":"BoJack",
         "last_name":"Horseman",
         "email":"bojack@horseman.com",
         "customer_code":"CUS_qo38as2hpsgk2r0",
         "phone":null,
         "metadata":null,
         "risk_action":"default"
      },
      "authorization":{  
         "authorization_code":"AUTH_f5rnfq9p",
         "bin":"539999",
         "last4":"8877",
         "exp_month":"08",
         "exp_year":"2020",
         "card_type":"mastercard DEBIT",
         "bank":"Guaranty Trust Bank",
         "country_code":"NG",
         "brand":"mastercard"
      },
     "plan_object": {
                "id": 6743,
                "name": "Test Plans",
                "plan_code": "PLN_tq8ur7pqz80fbpi",
                "description": "This is to test listing plans, etc etc",
                "amount": 200000,
                "interval": "hourly",
                "send_invoices": true,
                "send_sms": true,
                "currency": "NGN"
            }
            }

}"""
    paystack_api.webhook_api.verify("1001", body)
    mock_generic_fuc.assert_called_once_with(
        data={
            'amount': 100.0,
            'plan_object': {
                "id": 6743,
                "name": "Test Plans",
                "plan_code": "PLN_tq8ur7pqz80fbpi",
                "amount": 2000.0,
                "interval": "hourly",
                "currency": "NGN"
            },
            'currency': 'ngn',
            # 'interval': 'hourly',
            'status': 'success',
            "authorization": {
                "authorization_code": "AUTH_f5rnfq9p",
            },
            'reference': 'qTPrJoy9Bx',
            "customer": {
                "id": 68324,
                "email": "bojack@horseman.com",
                "customer_code": "CUS_qo38as2hpsgk2r0",
            },
            "paid_at": "2016-09-30T21:10:19.000Z",
        })


def test_successful_transfer(mock_generic_fuc, paystack_api):
    body = """
    {
      "event": "transfer.success",
      "data": {
        "domain": "live",
        "amount": 10000,
        "currency": "NGN",
        "source": "balance",
        "source_details": null,
        "reason": "Bless you",
        "reference": "JDJDJ",
        "recipient": {
          "domain": "live",
          "type": "nuban",
          "currency": "NGN",
          "name": "Someone",
          "details": {
            "account_number": "0123456789",
            "account_name": null,
            "bank_code": "058",
            "bank_name": "Guaranty Trust Bank"
          },
          "description": null,
          "metadata": null,
          "recipient_code": "RCP_xoosxcjojnvronx",
          "active": true
        },
        "status": "success",
        "transfer_code": "TRF_zy6w214r4aw9971",
        "transferred_at": "2017-03-25T17:51:24.000Z",
        "created_at": "2017-03-25T17:48:54.000Z"
      }
    }
    """
    paystack_api.webhook_api.verify("1001", body)
    mock_generic_fuc.assert_called_once_with(
        transfer_code="TRF_zy6w214r4aw9971",
        data={
            "amount": 100.0,
            "recipient": {
                "recipient_code": "RCP_xoosxcjojnvronx",
            },
            "transfer_code": "TRF_zy6w214r4aw9971",
            "transferred_at": "2017-03-25T17:51:24.000Z",
            "created_at": "2017-03-25T17:48:54.000Z"
        })


def test_failed_transfer(mock_generic_fuc, paystack_api):
    body = """
    {
  "event": "transfer.failed",
  "data": {
    "domain": "test",
    "amount": 10000,
    "currency": "NGN",
    "source": "balance",
    "source_details": null,
    "reason": "Test",
    "reference": "XJKSKS",
    "recipient": {
      "domain": "live",
      "type": "nuban",
      "currency": "NGN",
      "name": "Test account",
      "details": {
        "account_number": "0000000000",
        "account_name": null,
        "bank_code": "058",
        "bank_name": "Zenith Bank"
      },
      "description": null,
      "metadata": null,
      "recipient_code": "RCP_7um8q67gj0v4n1c",
      "active": true
    },
    "status": "failed",
    "transfer_code": "TRF_3g8pc1cfmn00x6u",
    "transferred_at": null,
    "created_at": "2017-12-01T08:51:37.000Z"
  }
}
    """
    paystack_api.webhook_api.verify("1001", body)
    mock_generic_fuc.assert_called_once_with(
        transfer_code='TRF_3g8pc1cfmn00x6u',
        data={
            "amount": 100.0,
            "recipient": {
                "recipient_code": "RCP_7um8q67gj0v4n1c",
            },
            "transfer_code": "TRF_3g8pc1cfmn00x6u",
            "transferred_at": None,
            "created_at": "2017-12-01T08:51:37.000Z"
        })


def test_webhook_not_called(mock_generic_fuc, paystack_api):
    body = """
    {
  "event": "transfer.failed",
  "data": {
    "domain": "test",
    "amount": 10000,
    "currency": "NGN",
    "source": "balance",
    "source_details": null,
    "reason": "Test",
    "reference": "XJKSKS",
    "recipient": {
      "domain": "live",
      "type": "nuban",
      "currency": "NGN",
      "name": "Test account",
      "details": {
        "account_number": "0000000000",
        "account_name": null,
        "bank_code": "058",
        "bank_name": "Zenith Bank"
      },
      "description": null,
      "metadata": null,
      "recipient_code": "RCP_7um8q67gj0v4n1c",
      "active": true
    },
    "status": "failed",
    "transfer_code": "TRF_3g8pc1cfmn00x6u",
    "transferred_at": null,
    "created_at": "2017-12-01T08:51:37.000Z"
  }
}
    """
    paystack_api.webhook_api.verify("1101", body)
    mock_generic_fuc.assert_not_called()
