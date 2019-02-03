def test_create_plan_multiple_currency(post_request, paystack_api,
                                       mock_assertion):
    api_repsonse1 = {
        "status": True,
        "message": "Plan created",
        "data": {
            "name": "Monthly retainer",
            "amount": 500000,
            "interval": "monthly",
            "integration": 100032,
            "domain": "test",
            "plan_code": "PLN_gx2wn530m0i3w3m",
            "send_invoices": True,
            "send_sms": True,
            "hosted_page": False,
            "currency": "NGN",
            "id": 28,
            "createdAt": "2016-03-29T22:42:50.811Z",
            "updatedAt": "2016-03-29T22:42:50.811Z"
        }
    }
    api_response2 = {
        "status": True,
        "message": "Plan created",
        "data": {
            "name": "Monthly retainer",
            "amount": 32500,
            "interval": "monthly",
            "integration": 100032,
            "domain": "test",
            "plan_code": "PLN_gx2wn530m0i3w3e",
            "send_invoices": True,
            "send_sms": True,
            "hosted_page": False,
            "currency": "USD",
            "id": 29,
            "createdAt": "2016-03-29T22:42:50.811Z",
            "updatedAt": "2016-03-29T22:42:50.811Z"
        }
    }
    mock_post = post_request(side_effect=[api_repsonse1, api_response2])
    data = {
        "name": "Monthly retainer",
        "interval": "monthly",
        "amount": {
            'ngn': 5000,
            'usd': 325
        },
    }
    result = paystack_api.subscription_api.create_plans(data)
    mock_assertion(
        mock_post,
        "/plan",
        side_effect=[
            dict(
                json={
                    'name': data['name'],
                    'interval': data['interval'],
                    'amount': data['amount']['ngn'] * 100,
                    'currency': 'NGN'
                }),
            dict(
                json={
                    'name': data['name'],
                    'interval': data['interval'],
                    'amount': data['amount']['usd'] * 100,
                    'currency': 'USD'
                })
        ])
    assert result[0]
    assert result[1] == {
        'name': "Monthly retainer",
        'interval': 'monthly',
        'plan': {
            'ngn': "PLN_gx2wn530m0i3w3m",
            'usd': "PLN_gx2wn530m0i3w3e"
        }
    }
