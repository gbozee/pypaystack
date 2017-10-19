from paystack.utils import PaystackAPI as MPaystackAPI

class PaystackAPI(MPaystackAPI):
    def verify_result(self, response, **kwargs):
        if response.status_code == 200:
            result = response.json()
            data = result['data']
            return data['amount']
        return "hello"