from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils import timezone
from django.views.generic import RedirectView, TemplateView
# Create your views here.
from . import settings
from .signals import payment_verified
from .utils import PaystackAPI
from django.contrib import messages


def verify_payment(request, order):
    amount = request.GET.get('amount')
    txrf = request.GET.get('trxref')
    paystack_instance = PaystackAPI()
    response = paystack_instance.verify_payment(txrf, int(amount))
    if response[0]:
        payment_verified.send(
            sender=PaystackAPI,
            ref=txrf, amount=int(amount) / 100)
        return redirect(reverse('paystack:successful_verification', args=[order]))
    return redirect(reverse('paystack:failed_verification', args=[order]))


class FailedView(RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        if settings.PAYSTACK_FAILED_URL == 'paystack:failed_page':
            return reverse(settings.PAYSTACK_FAILED_URL)
        return settings.PAYSTACK_FAILED_URL


class SuccessView(RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        if settings.PAYSTACK_SUCCESS_URL == 'paystack:failed_page':
            return reverse(settings.PAYSTACK_SUCCESS_URL)
        return settings.PAYSTACK_SUCCESS_URL
