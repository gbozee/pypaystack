from dispatch import Signal

payment_verified = Signal(providing_args=["ref", "amount", "order"])

event_signal = Signal(providing_args=['event', "data"])

successful_payment_signal = Signal(providing_args=['data'])

successful_transfer_signal = Signal(providing_args=['transfer_code', 'data'])

failed_transfer_signal = Signal(providing_args=['transfer_code', 'data'])
