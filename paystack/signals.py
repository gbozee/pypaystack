from django.dispatch import Signal

payment_verified = Signal(providing_args=["ref","amount"])

event_signal = Signal(providing_args=['event', "data"])