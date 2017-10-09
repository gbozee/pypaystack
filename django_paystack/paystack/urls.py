from django.conf.urls import url
from . import settings
from .utils import PaystackAPI


def verify_payment(request):
    code = request.GET.get('code')
    paystack_instance = PaystackAPI()
    response = paystack_instance.verify_payment(code)


urlpatterns = [
]
