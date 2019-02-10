def test_create_customer(post_request, paystack_api, mock_assertion):
    api_response = {
        "status": True,
        "message": "Customer created",
        "data": {
            "email": "bojack@horsinaround.com",
            "integration": 100032,
            "domain": "test",
            "customer_code": "CUS_xnxdt6s1zg1f4nx",
            "id": 1173,
            "createdAt": "2016-03-29T20:03:09.584Z",
            "updatedAt": "2016-03-29T20:03:09.584Z"
        }
    }
    data = {
        "first_name": "BoJack",
        "last_name": "Horseman",
        "email": "bojack@horsinaround.com",
    }
    mock_post = post_request(api_response)
    result = paystack_api.customer_api.create_customer(data)
    mock_assertion(
        mock_post,
        "/customer",
        json = data
    )
    assert result == api_response['data']['customer_code']

def test_n_create_customer(post_request, paystack_api, mock_assertion):
    api_response = {
        "status": True,
        "message": "Customer created",
        "data": {
            "email": "bojack@horsinaround.com",
            "integration": 100032,
            "domain": "test",
            "customer_code": "CUS_xnxdt6s1zg1f4nx",
            "id": 1173,
            "createdAt": "2016-03-29T20:03:09.584Z",
            "updatedAt": "2016-03-29T20:03:09.584Z"
        }
    }
    data = {
        "first_name": "Bo",
        "last_name": "Jack",
        "email": "bojack@horsinaround.com",
    }
    mock_post = post_request(api_response)
    result = paystack_api.customer_api.n_create_customer(data)
    mock_assertion(
        mock_post,
        "/customer",
        json = data
    )
    assert result[0]
    assert result[1] == "Customer created"
    assert result[2] == api_response['data']

def test_list_customer(get_request, paystack_api, mock_assertion):
    api_response = {
        "status": True,
        "message": "Customers retrieved",
        "data": [
            {
            "integration": 100032,
            "first_name": "Bojack",
            "last_name": "Horseman",
            "email": "bojack@horsinaround.com",
            "phone": None,
            "metadata": {
                "photos": [
                {
                    "type": "twitter",
                    "typeId": "twitter",
                    "typeName": "Twitter",
                    "url": "https://d2ojpxxtu63wzl.cloudfront.net/static/61b1a0a1d4dda2c9fe9e165fed07f812_a722ae7148870cc2e33465d1807dfdc6efca33ad2c4e1f8943a79eead3c21311",
                    "isPrimary": True
                }
                ]
            },
            "domain": "test",
            "customer_code": "CUS_xnxdt6s1zg1f4nx",
            "id": 1173,
            "createdAt": "2016-03-29T20:03:09.000Z",
            "updatedAt": "2016-03-29T20:03:10.000Z"
            },
            {
            "integration": 100032,
            "first_name": "Diane",
            "last_name": "Nguyen",
            "email": "diane@writersclub.com",
            "phone": "16504173147",
            "metadata": None,
            "domain": "test",
            "customer_code": "CUS_1uld4hluw0g2gn0",
            "id": 63,
            "createdAt": "2016-01-13T01:15:47.000Z",
            "updatedAt": "2016-02-24T16:56:48.000Z"
            },
            {
            "integration": 100032,
            "first_name": None,
            "last_name": None,
            "email": "todd@chavez.com",
            "phone": None,
            "metadata": None,
            "domain": "test",
            "customer_code": "CUS_soirsjdqkyjfwcr",
            "id": 65,
            "createdAt": "2016-01-13T01:15:47.000Z",
            "updatedAt": "2016-01-13T01:15:47.000Z"
            }
        ],
        "meta": {
            "total": 3,
            "skipped": 0,
            "perPage": 50,
            "page": 1,
            "pageCount": 1
        }
    }
    mock_get = get_request(api_response)
    data = {'perPage': 50, 'page': 1}
    result = paystack_api.customer_api.list_customer(data)
    mock_assertion(
        mock_get,
        "/customer",
        params={
            'perPage': data['perPage'],
            'page': data['page'],
        }
    )
    assert result[0]
    assert result[1] == "Customers retrieved"
    assert result[2] == api_response['data']

def test_get_customer(get_request, paystack_api, mock_assertion):
    api_response = {
        "status": True,
        "message": "Customer retrieved",
        "data":
            {
            "integration": 100032,
            "first_name": "Bojack",
            "last_name": "Horseman",
            "email": "bojack@horsinaround.com",
            "phone": None,
            "metadata": {
                "photos": [
                {
                    "type": "twitter",
                    "typeId": "twitter",
                    "typeName": "Twitter",
                    "url": "https://d2ojpxxtu63wzl.cloudfront.net/static/61b1a0a1d4dda2c9fe9e165fed07f812_a722ae7148870cc2e33465d1807dfdc6efca33ad2c4e1f8943a79eead3c21311",
                    "isPrimary": True
                }
                ]
            },
            "domain": "test",
            "customer_code": "CUS_xnxdt6s1zg1f4nx",
            "id": 1173,
                    "transactions": [],
            "subscriptions": [],
            "authorizations": [],
            "createdAt": "2016-03-29T20:03:09.000Z",
            "updatedAt": "2016-03-29T20:03:10.000Z"
            }
    }

    mock_get = get_request(api_response)
    data = {'email': 'bojack@horsinaround.com'}
    result = paystack_api.customer_api.get_customer(data['email'])
    mock_assertion(
        mock_get,
        "/customer/{}".format(data['email'])
    )
    assert result[0]
    assert result[1] == "Customer retrieved"
    assert result[2] == api_response['data']

def test_get_customer_failed(get_request, paystack_api, mock_assertion):
    api_response = {
        "status": False,
        "message": "Customer email is invalid for your live domain."
    }
    mock_get = get_request(api_response, status_code=404)
    data = {'email': 'invalid email address'}
    result = paystack_api.customer_api.get_customer(data['email'])
    mock_assertion(
        mock_get,
        "/customer/{}".format(data['email'])
    )
    assert not result[0]
    assert result[1] == api_response['message']

def test_update_customer(put_request, paystack_api, mock_assertion):
    api_response = {
        "status": True,
        "message": "Customer updated",
        "data": {
            "integration": 100032,
            "first_name": "BoJack",
            "last_name": "Horseman",
            "email": "bojack@horsinaround.com",
            "phone": None,
            "metadata": {
                "photos": [
                {
                    "type": "twitter",
                    "typeId": "twitter",
                    "typeName": "Twitter",
                    "url": "https://d2ojpxxtu63wzl.cloudfront.net/static/61b1a0a1d4dda2c9fe9e165fed07f812_a722ae7148870cc2e33465d1807dfdc6efca33ad2c4e1f8943a79eead3c21311",
                    "isPrimary": True
                }
                ]
            },
            "domain": "test",
            "customer_code": "CUS_xnxdt6s1zg1f4nx",
            "id": 1173,
                    "transactions": [],
            "subscriptions": [],
            "authorizations": [],
            "createdAt": "2016-03-29T20:03:09.000Z",
            "updatedAt": "2016-03-29T20:03:10.000Z"
            }
        }

    mock_put = put_request(api_response)
    data = {
        "first_name": "BoJack",
        "last_name": "Horseman",
        'email': 'bojack@horsinaround.com',
        "customer_code": "CUS_xnxdt6s1zg1f4nx"
    }
    result = paystack_api.customer_api.update_customer(data['customer_code'], data)
    mock_assertion(
        mock_put,
        "/customer/{}".format(data['customer_code']),
        json = data,
    )
    assert result[0]
    assert result[1] == "Customer updated"
    assert result[2] == api_response['data']

def test_blacklist_customer(post_request, paystack_api, mock_assertion):
    api_response = {
        "status": True,
        "message": "Customer updated",
        "data": {
            "first_name": "Peter",
            "last_name": "Griffin",
            "email": "peter@familyguy.com",
            "phone": None,
            "metadata": {},
            "domain": "test",
            "customer_code": "CUS_xr58yrr2ujlft9k",
            "risk_action": "deny",
            "id": 2109,
            "integration": 100032,
            "createdAt": "2016-01-26T13:43:38.000Z",
            "updatedAt": "2016-08-23T03:56:43.000Z"
        }
    }
    mock_post = post_request(api_response)
    data = {
        "customer": "CUS_xr58yrr2ujlft9k", 
        "risk_action": "deny", 
    }
    result = paystack_api.customer_api.blacklist_customer(data['customer'], blacklist=True)
    mock_assertion(
        mock_post,
        "/customer/set_risk_action",
        json = data
    )
    assert result[0]
    assert result[1] == api_response['message']
    assert result[2] == api_response['data']

def test_whitelist_customer(post_request, paystack_api, mock_assertion):
    api_response = {
        "status": True,
        "message": "Customer updated",
        "data": {
            "first_name": "Peter",
            "last_name": "Griffin",
            "email": "peter@familyguy.com",
            "phone": None,
            "metadata": {},
            "domain": "test",
            "customer_code": "CUS_xr58yrr2ujlft9k",
            "risk_action": "allow",
            "id": 2109,
            "integration": 100032,
            "createdAt": "2016-01-26T13:43:38.000Z",
            "updatedAt": "2016-08-23T03:56:43.000Z"
        }
    }
    mock_post = post_request(api_response)
    data = {
        "customer": "CUS_xr58yrr2ujlft9k", 
        "risk_action": "allow", 
    }
    result = paystack_api.customer_api.blacklist_customer(data['customer'], blacklist=False)
    mock_assertion(
        mock_post,
        "/customer/set_risk_action",
        json = data
    )
    assert result[0]
    assert result[1] == api_response['message']
    assert result[2] == api_response['data']

def test_deactivate_auth(post_request, paystack_api, mock_assertion):
    api_response = {
        "status": True,
        "message": "Authorization has been deactivated"
    }

    mock_post = post_request(api_response)
    data = {"authorization_code": "AUTH_au6hc0de"}
    result = paystack_api.customer_api.deactivate_auth(data['authorization_code'])
    mock_assertion(
        mock_post,
        "/customer/deactivate_authorization",
        json = data
    )
    assert result[0]
    assert result[1] == api_response['message']
