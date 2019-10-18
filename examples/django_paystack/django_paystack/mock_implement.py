from paystack.utils import PaystackAPI as MPaystackAPI
from paystack.api import Transaction


class TestTransaction(Transaction):
    def verify_result(self, response, **kwargs):
        if response.status_code == 200:
            result = response.json()
            data = result['data']
            return data['amount']
        return "hello"


class PaystackAPI(MPaystackAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transaction_api = TestTransaction(self.make_request)
