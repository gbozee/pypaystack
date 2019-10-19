import json
from paystack.api import signals
from dispatch import receiver


def test_successful_order_verification(client, mocker):
    module = mocker.patch("paystack.utils.PaystackAPI")
    mock_instance = module.return_value
    mock_instance.verify_payment.return_value = (True, "verification successful")
    client_instance = client(module)
    response = client_instance.get(
        "/verify-payment/1234", params={"amount": 30000, "trxref": "biola23"}
    )
    assert response.status_code == 200
    mock_instance.verify_payment.assert_called_once_with("biola23", amount=30000)
    assert response.json() == {"status": True, "order": "1234"}


def test_webhook_notification(client, mocker):
    module = mocker.patch("paystack.utils.PaystackAPI")
    mock_instance = module.return_value
    client_instance = client(module)

    @receiver(signals.successful_payment_signal)
    def payment_signal(sender, **kwargs):
        pass

    body = {
        "event": "charge.success",
        "data": {
            "id": 302961,
            "domain": "live",
            "status": "success",
            "reference": "qTPrJoy9Bx",
            "amount": 10000,
        },
    }
    response = client_instance.post(
        "/webhook", json=body, headers={"X-PAYSTACK-SIGNATURE": "encoded signature"}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "Success"}
    mock_instance.webhook_api.verify.assert_called_once_with(
        "encoded signature", json.dumps(body).encode('utf-8'), full_auth=True
    )

