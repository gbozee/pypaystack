from django.db import models
from .utils import generate_code
# Create your models here.


class Paystack(models.Model):
    BEARER_ACCOUNT = 'account'
    BEARER_SUBACCOUNT = 'subaccount'
    CHOICES = (
        (BEARER_ACCOUNT, BEARER_ACCOUNT),
        (BEARER_SUBACCOUNT, BEARER_SUBACCOUNT)
    )
    created = models.DateTimeField(auto_now_add=True)
    ref = models.CharField(
        max_length=12, primary_key=True, db_index=True)
    email = models.EmailField()
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    quantity = models.IntegerField(default=1)
    plan = models.CharField(max_length=40, blank=True)
    transaction_charge = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    subaccount = models.CharField(max_length=40, blank=True)
    currency = models.CharField(max_length=10, default="NGN")
    is_split = models.BooleanField(default=False)
    bearer = models.CharField(
        max_length=30, default=BEARER_ACCOUNT, choices=CHOICES)
    verified = models.BooleanField(default=False)
    date_paid = models.DateTimeField(null=True)

    @classmethod
    def create(cls, **kwargs):
        order = generate_code(cls, 'ref')
        return cls(ref=order, **kwargs)
