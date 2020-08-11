from .base import BaseClass


class Customer(BaseClass):
    def create_customer(self, data):
        path = "/customer"
        response = self.make_request("POST", path, json=data)
        # return self.result_format(response)
        if response.status_code >= 400:
            return None
        return response.json()["data"]["customer_code"]

    def n_create_customer(self, data):
        path = "/customer"
        response = self.make_request("POST", path, json=data)
        return self.result_format(response)
        # if response.status_code >= 400:
        #     return None
        # return response.json()['data']['customer_code']

    def list_customer(self, data):
        path = "/customer"
        response = self.make_request("GET", path, params=data)
        return self.result_format(response)

    def get_customer(self, customer_email):
        path = "/customer/{}".format(customer_email)
        response = self.make_request("GET", path)
        return self.result_format(response)

    def update_customer(self, customer_code, data):
        path = "/customer/{}".format(customer_code)
        response = self.make_request("PUT", path, json=data)
        return self.result_format(response)

    def blacklist_customer(self, customer_code, blacklist=True):
        data = {
            "customer": customer_code,
            "risk_action": "deny" if blacklist else "allow",
        }
        path = "/customer/set_risk_action"
        response = self.make_request("POST", path, json=data)
        return self.result_format(response)

    def deactivate_auth(self, authorization_code):
        data = {"authorization_code": authorization_code}
        path = "/customer/deactivate_authorization"
        response = self.make_request("POST", path, json=data)

        def callback(dd):
            return dd["status"], dd["message"]

        return self.result_format(response, callback)


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

    def verify_payment(self, code, amount_only=True, **kwargs):
        path = "/transaction/verify/{}".format(code)
        response = self.make_request("GET", path)
        if amount_only:
            return self.verify_result(response, **kwargs)
        # add test for this scenario
        return self.result_format(response)

    def get_customer_and_auth_details(self, data):
        if data["status"] == "success":
            return {
                "authorization": data["authorization"],
                "customer": data["customer"],
                "plan": data["plan"],
            }
        return {}

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
            "reference": kwargs["reference"],
            "email": kwargs["email"],
            "amount": kwargs["amount"] * 100,
            "callback_url": kwargs["callback_url"],
        }
        response = self.make_request("POST", path, json=json_data)
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
            "authorization_code": kwargs["authorization_code"],
            "email": kwargs["email"],
            "amount": kwargs["amount"] * 100,
        }
        if 'order' in kwargs:
            json_data['reference']  = kwargs['order']
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
            "authorization_code": kwargs["authorization_code"],
            "email": kwargs["email"],
            "amount": kwargs["amount"] * 100,
        }
        response = self.make_request("POST", path, json=json_data)
        return self.result_format(response)

    def get_transactions(
        self,
        perPage=50,
        page=None,
        customer_id=None,
        status=None,
        _from=None,
        _to=None,
        amount=None,
    ):
        params = {"perPage": perPage}
        for key, value in {
            "status": status,
            "customer": customer_id,
            "from": _from,
            "to": _to,
            "page": page,
        }.items():
            if value:
                if key == "amount":
                    params[key] = value * 100
                else:
                    params[key] = value
        path = "/transaction"
        response = self.make_request("GET", path, params=params)
        return self.result_format(response)

    def build_transaction_obj(self, currency="ngn", **kwargs):
        json_data = {
            "key": self.public_key,
            "email": kwargs.get("email"),
            "amount": int(kwargs["amount"]),
            "ref": kwargs.get("reference") or kwargs.get("order"),
            "currency": currency.lower(),
        }
        if kwargs.get("first_name") and kwargs.get("last_name"):
            json_data["label"] = f"{kwargs['first_name']} {kwargs['last_name']}"
        if kwargs.get("items"):
            json_data["metadata"] = kwargs["items"]
        if kwargs.get("subaccount"):
            json_data["subaccount"] = kwargs["subaccount"]
            json_data["bearer"] = kwargs.get("bearer") or "subaccount"
            if kwargs.get("split_code"):
                json_data["split_code"] = kwargs["split_code"]
        if kwargs.get("plan"):
            json_data["plan"] = kwargs["plan"]
        return json_data
