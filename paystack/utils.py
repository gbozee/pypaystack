import hmac
import hashlib
import requests
from . import settings
import importlib


class PaystackAPI(object):

    def __init__(self):
        self.public_key = settings.PAYSTACK_PUBLIC_KEY
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.base_url = settings.PAYSTACK_API_URL

    def make_request(self, method, path, **kwargs):
        options = {
            'GET': requests.get,
            'POST': requests.post,
            'PUT': requests.put,
            'DELETE': requests.delete
        }
        url = "{}{}".format(self.base_url, path)
        headers = {
            'Authorization': "Bearer {}".format(self.secret_key)
        }
        return options[method](url, headers=headers, **kwargs)

    def verify_result(self, response, **kwargs):
        if response.status_code == 200:
            result = response.json()
            data = result['data']
            amount = kwargs.get('amount')
            if amount:
                if data['amount'] == int(amount):
                    return True, result["message"]
                return False, data['amount']
            return True, result["message"]

        if response.status_code >= 400:
            return False, "Could not verify transaction"

    def verify_payment(self, code, **kwargs):
        path = "/transaction/verify/{}".format(code)
        response = self.make_request('GET', path)
        return self.verify_result(response, **kwargs)


def load_lib(config=settings.PAYSTACK_LIB_MODULE):
    module = importlib.import_module(config)
    return module.PaystackAPI


def generate_digest(data):
    return hmac.new(settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
                    msg=data,
                    digestmod=hashlib.sha512).hexdigest()  # request body hash digest
