class BaseClass(object):
    def __init__(self, make_request):
        self.make_request = make_request

    def result_format(self, response, callback=None):
        if response.status_code >= 400:
            result = response.json()
            return result['status'], result['message']

        result = response.json()
        if callback:
            return callback(result)
        return result['status'], result['message'], result['data']


class Customer(BaseClass):
    def create_customer(self, data):
        path = "/customer"
        response = self.make_request('POST', path, json=data)
        if response.status_code >= 400:
            return None
        return response.json()['data']['customer_code']


class Transfer(BaseClass):
    def get_banks(self):
        path = "/bank"
        response = self.make_request('GET', path)
        return self.result_format(response)

    def create_recipient(self, account_name, account_id, bank):
        path = "/transferrecipient"
        json = {
            "type": "nuban",
            "name": account_name,
            "description": account_name,
            "account_number": account_id,
            "bank_code": self.get_bank_code(bank),
            "currency": "NGN",
        }
        response = self.make_request('POST', path, json=json)
        return self.result_format(response)

    def initialize_transfer(self, amount, recipient, reason):
        path = "/transfer"
        json = {
            "source": "balance",
            "reason": reason,
            "amount": float(amount * 100),
            "recipient": recipient,
        }
        req = self.make_request('POST', path, json=json)
        return self.result_format(req)

    def bulk_transfer(self, array_of_recipient_with_amount):
        transform = [{
            'amount': x['amount'] * 100,
            'recipient': x['recipient']
        } for x in array_of_recipient_with_amount]
        path = "/transfer/bulk"
        json_data = {
            "currency": "NGN",
            "source": "balance",
            "transfers": transform,
        }
        req = self.make_request('POST', path, json=json_data)
        return self.result_format(req, lambda x: (x['status'], x['message']))

    def verify_transfer(self, transfer_recipient, code):
        """verify transaction"""
        path = "/transfer/finalize_transfer"
        json = {"transfer_code": transfer_recipient, "otp": code}
        req = self.make_request('POST', path, json=json)
        return self.result_format(req, lambda x: (True, x))

    def enable_otp(self, status=True, code=None):
        url = "/transfer/enable_otp"
        if not status:
            url = "/transfer/disable_otp"
        if code:
            url = "/transfer/disable_otp_finalize"
        json = {}
        if code:
            json = {"otp": code}
        req = self.make_request('POST', url, json=json)
        if req.status_code >= 400:
            req.raise_for_status()
        return req.json()["data"]

    def resend_otp(self, transfer_recipient):
        req = self.make_request(
            'POST',
            "/transfer/resend_otp",
            json={"transfer_code": transfer_recipient})
        if req.status_code >= 400:
            req.raise_for_status()
        return req.json()["data"]

    def get_transfer(self, transfer_recipient):
        """Fetch the transfer for a given recipient"""
        req = self.make_request('GET', "/transfer/" + transfer_recipient)
        return self.result_format(req)

    def get_bank_code(self, bank_name):
        options = {
            "Citibank": "023",
            "Access Bank": "044",
            "Diamond Bank": "063",
            "Ecobank Nigeria": "050",
            "Enterprise Bank": "084",
            "Fidelity Bank Nigeria": "070",
            "First Bank of Nigeria": "011",
            "First City Monument Bank": "214",
            "Guaranty Trust Bank": "058",
            "Heritage Bank": "030",
            "Keystone Bank Limited": "082",
            "Mainstreet Bank": "014",
            "Skye Bank": "076",
            "Stanbic IBTC Bank": "221",
            "Standard Chartered Bank": "068",
            "Sterling Bank": "232",
            "Union Bank of Nigeria": "032",
            "United Bank for Africa": "033",
            "Unity Bank": "215",
            "Wema Bank": "035",
            "Zenith Bank": "057",
            "Jaiz Bank": "301",
            "Suntrust Bank": "100",
            "Providus Bank": "101",
            "Parallex Bank": "526",
        }
        return options.get(bank_name)

    def check_balance(self):
        path = "/balance"
        result = self.make_request('GET', path)
        data = result.json()
        if not data['status']:
            raise Exception("Invalid Key sent.")
        return [{
            'currency': x['currency'],
            'balance': x['balance'] / 100
        } for x in data.get('data')]


class Transaction(BaseClass):
    def verify_result(self, response, **kwargs):
        if response.status_code == 200:
            result = response.json()
            data = result["data"]
            amount = kwargs.get("amount")
            if amount:
                if data["amount"] == int(amount):
                    return True, result["message"]
                return False, data["amount"]
            return True, result["message"], data

        if response.status_code >= 400:
            return False, "Could not verify transaction"

    def verify_payment(self, code, **kwargs):
        path = "/transaction/verify/{}".format(code)
        response = self.make_request("GET", path)
        return self.verify_result(response, **kwargs)

    def initialize_transaction(self, **kwargs):
        """When we expect paystack to respond back to us once
        the payment is successful but not processing it
        from our end
        :params: kwargs{
            reference,
            email,
            amount, in naira.
            callback_url
        }
        """
        path = "/transaction/initialize"
        json_data = {
            'reference': kwargs['reference'],
            'email': kwargs['email'],
            'amount': kwargs['amount'] * 100,
            'callback_url': kwargs['callback_url']
        }
        response = self.make_request('POST', path, json=json_data)
        return self.result_format(response)

    def recurrent_charge(self, **kwargs):
        """
        When attempting to bill an existing customers that has already paid
         through us
        :data : {
            'authorization_code','email','amount'
        }
        """
        path = "/transaction/charge_authorization"
        json_data = {
            'authorization_code': kwargs['authorization_code'],
            'email': kwargs['email'],
            'amount': kwargs['amount'] * 100
        }
        response = self.make_request('POST', path, json=json_data)
        return self.result_format(response)

    def check_authorization(self, **kwargs):
        """
        :data:{
            authorization_code,
            email,
            amount
        }"""
        path = "/transaction/check_authorization"
        json_data = {
            'authorization_code': kwargs['authorization_code'],
            'email': kwargs['email'],
            'amount': kwargs['amount'] * 100
        }
        response = self.make_request('POST', path, json=json_data)
        return self.result_format(response)

    def get_transactions(self,
                         perPage=50,
                         customer_id=None,
                         status=None,
                         _from=None,
                         _to=None,
                         amount=None):
        params = {'perPage': perPage}
        for key, value in {
                'status': status,
                'customer': customer_id,
                'from': _from,
                'to': _to
        }.items():
            if value:
                if key == 'amount':
                    params[key] = value * 100
                else:
                    params[key] = value
        path = "/transaction"
        response = self.make_request('GET', path, params=params)
        return self.result_format(response)
