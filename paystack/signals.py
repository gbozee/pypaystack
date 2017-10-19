from django.dispatch import Signal

payment_verified = Signal(providing_args=["ref","amount"])
