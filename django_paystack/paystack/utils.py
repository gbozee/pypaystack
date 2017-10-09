import requests
import random
from . import settings


def generate_code(referral_class, key='order'):
    def _generate_code():
        t = "ABCDEFGHIJKLOMNOPQRSTUVWXYZ1234567890"
        return "".join([random.choice(t) for i in range(12)])

    code = _generate_code()
    if key == 'slug':
        kwargs = {'slug': code}
    else:
        kwargs = {'order': code}
    while referral_class.objects.filter(**kwargs).exists():
        code = _generate_code()
    return code


class PaystackAPI(object):

    def __init__(self):
        self.public_key = settings.PAYSTACK_PUBLIC_KEY
        self.secret_key = settings.PAYSTACK_SECRET_KEY
