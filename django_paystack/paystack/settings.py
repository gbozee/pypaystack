from django.conf import settings

PAYSTACK_SECRET_KEY = getattr(settings, "PAYSTACK_SECRET_KEY", None)
PAYSTACK_PUBLIC_KEY = getattr(settings, 'PAYSTACK_PUBLIC_KEY', None)
ALLOWED_HOSTS = getattr(settings, 'ALLOWED_HOSTS', [])
PAYSTACK_WEBHOOK_DOMAIN = getattr(settings, 'PAYSTACK_WEBHOOK_DOMAIN', None)
if PAYSTACK_WEBHOOK_DOMAIN:
    ALLOWED_HOSTS.append(PAYSTACK_WEBHOOK_DOMAIN)
