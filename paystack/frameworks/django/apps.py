import os
from django.apps import AppConfig

CURRENT_DIRECTOR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class PaystackConfig(AppConfig):
    name = "paystack"
    path = os.path.join(CURRENT_DIRECTOR, "django")

