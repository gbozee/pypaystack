import datetime


def test_create_plan_success(post_request, paystack_api, mock_assertion):
    api_response = {
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
    mock_post = post_request(api_response)
    data = {
        "name": "Monthly retainer",
        "interval": "monthly",
        "amount": 50000,
        "currency": "ngn",
    }
    result = paystack_api.subscription_api.create_plan(data)
    mock_assertion(
        mock_post,
        "/plan",
        json={
            'name': data['name'],
            'interval': data['interval'],
            'amount': data['amount'] * 100,
            'currency': 'NGN'
        })
    assert result[0]
    assert result[1] == 'Plan created'
    assert result[2] == api_response['data']


def test_list_plan(get_request, paystack_api, mock_assertion):
    api_response = {
        "status":
        True,
        "message":
        "Plans retrieved",
        "data": [{
            "subscriptions": [{
                "customer": 63,
                "plan": 27,
                "integration": 100032,
                "domain": "test",
                "start": 1458505748,
                "status": "complete",
                "quantity": 1,
                "amount": 100000,
                "subscription_code": "SUB_birvokwpp0sftun",
                "email_token": "9y62mxp4uh25das",
                "authorization": 79,
                "easy_cron_id": None,
                "cron_expression": "0 0 * * 0",
                "next_payment_date": "2016-03-27T07:00:00.000Z",
                "open_invoice": None,
                "id": 8,
                "createdAt": "2016-03-20T20:29:08.000Z",
                "updatedAt": "2016-03-22T16:23:52.000Z"
            }],
            "integration":
            100032,
            "domain":
            "test",
            "name":
            "Satin Flower",
            "plan_code":
            "PLN_lkozbpsoyd4je9t",
            "description":
            None,
            "amount":
            100000,
            "interval":
            "weekly",
            "send_invoices":
            True,
            "send_sms":
            True,
            "hosted_page":
            False,
            "hosted_page_url":
            None,
            "hosted_page_summary":
            None,
            "currency":
            "NGN",
            "id":
            27,
            "createdAt":
            "2016-03-21T02:44:14.000Z",
            "updatedAt":
            "2016-03-21T02:44:14.000Z"
        }, {
            "subscriptions": [],
            "integration": 100032,
            "domain": "test",
            "name": "Monthly retainer",
            "plan_code": "PLN_gx2wn530m0i3w3m",
            "description": None,
            "amount": 50000,
            "interval": "monthly",
            "send_invoices": True,
            "send_sms": True,
            "hosted_page": False,
            "hosted_page_url": None,
            "hosted_page_summary": None,
            "currency": "NGN",
            "id": 28,
            "createdAt": "2016-03-29T22:42:50.000Z",
            "updatedAt": "2016-03-29T22:42:50.000Z"
        }],
        "meta": {
            "total": 2,
            "skipped": 0,
            "perPage": 50,
            "page": 1,
            "pageCount": 1
        }
    }
    mock_get = get_request(api_response)
    data = {'perPage': 50, 'page': 1, 'interval': "monthly", 'amount': 20000}
    result = paystack_api.subscription_api.list_plans(data)
    mock_assertion(
        mock_get,
        "/plan",
        params={
            'perPage': data['perPage'],
            'page': data['page'],
            'interval': data['interval'],
            'amount': data['amount'] * 100
        })
    assert result[0]
    assert result[1] == "Plans retrieved"
    assert result[2] == api_response['data']


def test_fetch_plan(get_request, paystack_api, mock_assertion):
    api_response = {
        "status": True,
        "message": "Plan retrieved",
        "data": {
            "subscriptions": [],
            "integration": 100032,
            "domain": "test",
            "name": "Monthly retainer",
            "plan_code": "PLN_gx2wn530m0i3w3m",
            "description": None,
            "amount": 50000,
            "interval": "monthly",
            "send_invoices": True,
            "send_sms": True,
            "hosted_page": False,
            "hosted_page_url": None,
            "hosted_page_summary": None,
            "currency": "NGN",
            "id": 28,
            "createdAt": "2016-03-29T22:42:50.000Z",
            "updatedAt": "2016-03-29T22:42:50.000Z"
        }
    }
    mock_get = get_request(api_response)
    result = paystack_api.subscription_api.get_plan("PLN_gx2wn530m0i3w3m")
    mock_assertion(mock_get, "/plan/PLN_gx2wn530m0i3w3m")
    assert result[0]
    assert result[1] == "Plan retrieved"
    assert result[2] == api_response['data']


def test_update_plan(put_request, paystack_api, mock_assertion):
    api_response = {
        "status": True,
        "message": "Plan updated. 1 subscription(s) affected"
    }
    mock_put = put_request(api_response)
    data = {
        "name": "Montly Plan",
        "amount": 30000,
        "plan": "PLN_gx2wn530m0i3w3m"
    }
    result = paystack_api.subscription_api.update_plan(data)
    mock_assertion(
        mock_put,
        "/plan/PLN_gx2wn530m0i3w3m",
        json={
            "name": data['name'],
            'amount': data['amount'] * 100
        })
    assert result[0]
    assert result[1] == api_response['message']


def test_create_subscription_success(post_request, paystack_api,
                                     mock_assertion):
    api_response = {
        "status": True,
        "message": "Subscription successfully created",
        "data": {
            "customer": 1173,
            "plan": 28,
            "integration": 100032,
            "domain": "test",
            "start": 1459296064,
            "status": "active",
            "quantity": 1,
            "amount": 50000,
            "authorization": 79,
            "subscription_code": "SUB_vsyqdmlzble3uii",
            "email_token": "d7gofp6yppn3qz7",
            "id": 9,
            "createdAt": "2016-03-30T00:01:04.687Z",
            "updatedAt": "2016-03-30T00:01:04.687Z"
        }
    }
    mock_post = post_request(api_response)
    data = {
        'customer': "customer email or code",
        'plan': "plan code",
        'authorization': 'customer authorization code',
        'start_date': "2017-10-16"
    }
    result = paystack_api.subscription_api.create_subscription(data)
    mock_assertion(
        mock_post,
        "/subscription",
        json={
            'customer': data['customer'],
            'plan': data['plan'],
            'authorization': data['authorization'],
            'start_date': data['start_date'],
        })
    assert result[0]
    assert result[1] == api_response["message"]
    assert result[2] == api_response["data"]


def test_create_subscription_failed(post_request, paystack_api,
                                    mock_assertion):
    api_response = {
        "status": False,
        "message": "The customer specified has no saved authorizations"
    }
    mock_post = post_request(api_response, status_code=400)
    data = {
        'customer': "customer email or code",
        'plan': "plan code",
        'authorization': 'customer authorization code',
        'start_date': "2017-10-16"
    }
    result = paystack_api.subscription_api.create_subscription(data)
    mock_assertion(
        mock_post,
        "/subscription",
        json={
            'customer': data['customer'],
            'plan': data['plan'],
            'authorization': data['authorization'],
            'start_date': data['start_date']
        })
    assert not result[0]
    assert result[1] == api_response['message']


def test_list_subscriptions(get_request, paystack_api, mock_assertion):
    api_response = {
        "status":
        True,
        "message":
        "Subscriptions retrieved",
        "data": [{
            "customer": {
                "first_name": "BoJack",
                "last_name": "Horseman",
                "email": "bojack@horseman.com",
                "phone": "",
                "metadata": None,
                "domain": "test",
                "customer_code": "CUS_hdhye17yj8qd2tx",
                "risk_action": "default",
                "id": 84312,
                "integration": 100073,
                "createdAt": "2016-10-01T10:59:52.000Z",
                "updatedAt": "2016-10-01T10:59:52.000Z"
            },
            "plan": {
                "domain": "test",
                "name": "Weekly small chops",
                "plan_code": "PLN_0as2m9n02cl0kp6",
                "description": "Small chops delivered every week",
                "amount": 27000,
                "interval": "weekly",
                "send_invoices": True,
                "send_sms": True,
                "hosted_page": False,
                "hosted_page_url": None,
                "hosted_page_summary": None,
                "currency": "NGN",
                "migrate": None,
                "id": 1716,
                "integration": 100073,
                "createdAt": "2016-10-01T10:59:11.000Z",
                "updatedAt": "2016-10-01T10:59:11.000Z"
            },
            "integration": 123456,
            "authorization": 161811,
            "domain": "test",
            "start": 1475319599,
            "status": "active",
            "quantity": 1,
            "amount": 27000,
            "subscription_code": "SUB_6phdx225bavuwtb",
            "email_token": "ore84lyuwcv2esu",
            "easy_cron_id": "275226",
            "cron_expression": "0 0 * * 6",
            "next_payment_date": "2016-10-15T00:00:00.000Z",
            "open_invoice": "INV_qc875pkxpxuyodf",
            "id": 4192,
            "createdAt": "2016-10-01T10:59:59.000Z",
            "updatedAt": "2016-10-12T07:45:14.000Z"
        }],
        "meta": {
            "total": 1,
            "skipped": 0,
            "perPage": 50,
            "page": 1,
            "pageCount": 1
        }
    }
    mock_get = get_request(api_response)
    mock_get = get_request(api_response)
    data = {
        'perPage': 50,
        'plan': "planID",
        'customer': "customerID",
        'page': 1
    }
    result = paystack_api.subscription_api.get_all_subscriptions(data)
    mock_assertion(mock_get, "/subscription", params=data)
    assert result[0]
    assert result[1] == api_response['message']
    assert result[2] == api_response['data']


def test_enable_subscription(post_request, paystack_api, mock_assertion):
    api_response_enable = {
        "status": True,
        "message": "Subscription enabled successfully"
    }
    mock_post_enable = post_request(api_response_enable)
    data = {'code': "SUB_vsyqdmlzble3uii", "token": "d7gofp6yppn3qz7"}
    result_enable = paystack_api.subscription_api.activate_subscription(data)
    mock_assertion(mock_post_enable, "/subscription/enable", json=data)
    assert result_enable[0]
    assert result_enable[1] == api_response_enable['message']


def test_disable_subscription(post_request, paystack_api, mock_assertion):
    api_response_disable = {
        "status": True,
        "message": "Subscription disabled successfully"
    }
    mock_post_disable = post_request(api_response_disable)
    data = {'code': "SUB_vsyqdmlzble3uii", "token": "d7gofp6yppn3qz7"}
    result_disable = paystack_api.subscription_api.activate_subscription(
        data, False)
    mock_assertion(mock_post_disable, "/subscription/disable", json=data)
    assert result_disable[0]
    assert result_disable[1] == api_response_disable['message']


def test_fetch_subscription(get_request, paystack_api, mock_assertion):
    api_response = {
        "status": True,
        "message": "Subscription retrieved successfully",
        "data": {
            "invoices": [],
            "customer": {
                "first_name": "BoJack",
                "last_name": "Horseman",
                "email": "bojack@horsinaround.com",
                "phone": None,
                "metadata": {
                    "photos": [{
                        "type":
                        "twitter",
                        "typeId":
                        "twitter",
                        "typeName":
                        "Twitter",
                        "url":
                        "https://d2ojpxxtu63wzl.cloudfront.net/static/61b1a0a1d4dda2c9fe9e165fed07f812_a722ae7148870cc2e33465d1807dfdc6efca33ad2c4e1f8943a79eead3c21311",
                        "isPrimary":
                        False
                    }]
                },
                "domain": "test",
                "customer_code": "CUS_xnxdt6s1zg1f4nx",
                "id": 1173,
                "integration": 100032,
                "createdAt": "2016-03-29T20:03:09.000Z",
                "updatedAt": "2016-03-29T20:53:05.000Z"
            },
            "plan": {
                "domain": "test",
                "name": "Monthly retainer (renamed)",
                "plan_code": "PLN_gx2wn530m0i3w3m",
                "description": None,
                "amount": 50000,
                "interval": "monthly",
                "send_invoices": True,
                "send_sms": True,
                "hosted_page": False,
                "hosted_page_url": None,
                "hosted_page_summary": None,
                "currency": "NGN",
                "id": 28,
                "integration": 100032,
                "createdAt": "2016-03-29T22:42:50.000Z",
                "updatedAt": "2016-03-29T23:51:41.000Z"
            },
            "integration": 100032,
            "authorization": {
                "domain": "test",
                "authorization_code": "AUTH_5u1q4898",
                "bin": None,
                "brand": None,
                "card_type": "Visa",
                "last4": "1381",
                "bank": None,
                "country_code": None,
                "country_name": None,
                "description": "Visa ending with 1381",
                "mobile": False,
                "id": 79,
                "integration": 100032,
                "customer": 1173,
                "card": 392,
                "createdAt": "2016-01-13T01:15:52.000Z",
                "updatedAt": "2016-01-13T01:15:52.000Z"
            },
            "domain": "test",
            "start": 1459296064,
            "status": "active",
            "quantity": 1,
            "amount": 50000,
            "subscription_code": "SUB_vsyqdmlzble3uii",
            "email_token": "d7gofp6yppn3qz7",
            "easy_cron_id": None,
            "cron_expression": "0 0 28 * *",
            "next_payment_date": "2016-04-28T07:00:00.000Z",
            "open_invoice": None,
            "id": 9,
            "createdAt": "2016-03-30T00:01:04.000Z",
            "updatedAt": "2016-03-30T00:22:58.000Z"
        }
    }
    mock_get = get_request(api_response)
    result = paystack_api.subscription_api.get_subscription(
        "SUB_vsyqdmlzble3uii")
    mock_assertion(mock_get, "/subscription/SUB_vsyqdmlzble3uii")
    assert result[0]
    assert result[1] == api_response['message']
    assert result[2] == api_response['data']
