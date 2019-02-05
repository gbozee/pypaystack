from unittest.mock import call


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


def get_plan(plan_code, amount, currency):
    return {
        "status": True,
        "message": "Plan retrieved",
        "data": {
            "subscriptions": [],
            "integration": 100032,
            "domain": "test",
            "name": "New monthly retainer",
            "plan_code": plan_code,
            "description": None,
            "amount": amount * 100,
            "interval": "monthly",
            "send_invoices": True,
            "send_sms": True,
            "hosted_page": False,
            "hosted_page_url": None,
            "hosted_page_summary": None,
            "currency": currency.upper(),
            "id": 28,
            "createdAt": "2016-03-29T22:42:50.000Z",
            "updatedAt": "2016-03-29T22:42:50.000Z"
        }
    }


def test_update_existing_multiple_plans(put_request, get_request, paystack_api,
                                        mock_assertion, headers):
    api_response = {
        "status": True,
        "message": "Plan updated. 1 subscription(s) affected"
    }
    mock_put = put_request(api_response)
    data = {
        'name': "Monthly retainer",
        'interval': 'monthly',
        'plan': {
            'ngn': "PLN_gx2wn530m0i3w3m",
            'usd': "PLN_gx2wn530m0i3w3e"
        }
    }
    new_data = {
        'name': "New monthly retainer",
        'amount': {
            'ngn': 3000,
            'usd': 25
        }
    }
    mock_get = get_request(side_effect=[
        get_plan(data['plan']['ngn'], new_data['amount']['ngn'], 'ngn'),
        get_plan(data['plan']['usd'], new_data['amount']['usd'], 'usd')
    ])
    result = paystack_api.subscription_api.update_plans(data, new_data)
    mock_put.assert_has_calls(
        [
            call(
                "{}/plan/{data['plan']['ngn']}".format(paystack_api.base_url),
                json={
                    'name': new_data['name'],
                    'amount': new_data['amount']['ngn'] * 100
                },
                headers=headers),
            call(
                "{}/plan/{data['plan']['usd']}".format(paystack_api.base_url),
                json={
                    'name': new_data['name'],
                    'amount': new_data['amount']['usd'] * 100
                },
                headers=headers)
        ],
        any_order=True)
    mock_get.assert_has_calls(
        [
            call(
                "{}/plan/{data['plan']['ngn']}".format(paystack_api.base_url),
                headers=headers),
            call(
                "{}/plan/{data['plan']['usd']}".format(paystack_api.base_url),
                headers=headers)
        ],
        any_order=True)
    assert result[0]
    assert result[1] == {
        'name': "New monthly retainer",
        'interval': 'monthly',
        'plan': {
            'ngn': "PLN_gx2wn530m0i3w3m",
            'usd': "PLN_gx2wn530m0i3w3e"
        }
    }
