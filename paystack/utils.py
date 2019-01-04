import hmac
import hashlib
import requests
import importlib
from . import api


class PaystackAPI(object):
    def __init__(self, django=True, **kwargs):
        if django:
            from . import settings
            self.public_key = kwargs.get('public_key',
                                         settings.PAYSTACK_PUBLIC_KEY)
            self.secret_key = kwargs.get('secret_key',
                                         settings.PAYSTACK_SECRET_KEY)
            self.base_url = kwargs.get('base_url', settings.PAYSTACK_API_URL)
        else:
            for key, value in kwargs.items():
                setattr(self, key, value)
        self.transaction_api = api.Transaction(self.make_request)
        self.customer_api = api.Customer(self.make_request)
        self.transfer_api = api.Transfer(self.make_request)


    def make_request(self, method, path, **kwargs):
        options = {
            "GET": requests.get,
            "POST": requests.post,
            "PUT": requests.put,
            "DELETE": requests.delete,
        }
        url = "{}{}".format(self.base_url, path)
        headers = {
            "Authorization": "Bearer {}".format(self.secret_key),
            "Content-Type": "application/json"
        }
        return options[method](url, headers=headers, **kwargs)

    def verify_result(self, response, **kwargs):
        return self.transaction_api.verify_result(response, **kwargs)

    def verify_payment(self, code, **kwargs):
        return self.transaction_api.verify_payment(code, **kwargs)


def load_lib(config=None):
    """
    dynamically import the paystack module to use
    """
    from . import settings
    config_lib = config or settings.PAYSTACK_LIB_MODULE
    module = importlib.import_module(config_lib)
    return module.PaystackAPI


def generate_digest(data):
    from . import settings
    return hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode("utf-8"),
        msg=data,
        digestmod=hashlib.sha512).hexdigest()  # request body hash digest



def get_js_script():
    return "https://js.paystack.co/v1/inline.js"


class MockRequest(object):
    def __init__(self, response, **kwargs):
        self.response = response
        self.overwrite = True
        if kwargs.get('overwrite'):
            self.overwrite = True
        self.status_code = kwargs.get('status_code', 200)

    @classmethod
    def raise_for_status(cls):
        pass

    def json(self):
        if self.overwrite:
            return self.response
        return {'data': self.response}

