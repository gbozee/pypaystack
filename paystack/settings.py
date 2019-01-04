from django.conf import settings
from django.shortcuts import reverse

PAYSTACK_SECRET_KEY = getattr(settings, "PAYSTACK_SECRET_KEY", None)
PAYSTACK_PUBLIC_KEY = getattr(settings, 'PAYSTACK_PUBLIC_KEY', None)
ALLOWED_HOSTS = getattr(settings, 'ALLOWED_HOSTS', [])
PAYSTACK_WEBHOOK_DOMAIN = getattr(settings, 'PAYSTACK_WEBHOOK_DOMAIN', None)
if PAYSTACK_WEBHOOK_DOMAIN:
    ALLOWED_HOSTS.append(PAYSTACK_WEBHOOK_DOMAIN)
PAYSTACK_FAILED_URL = getattr(settings, 'PAYSTACK_FAILED_URL',
                              'paystack:failed_page')
PAYSTACK_SUCCESS_URL = getattr(settings, 'PAYSTACK_SUCCESS_URL',
                               'paystack:success_page')

PAYSTACK_API_URL = 'https://api.paystack.co'
PAYSTACK_LIB_MODULE = getattr(settings, 'PAYSTACK_LIB_MODULE',
                              'paystack.utils')
