import django

version = django.get_version().split(".")
if int(version[0]) >= 2:
    from django.urls import re_path as url
else:
    from django.conf.urls import url

from django.views.decorators.csrf import csrf_exempt

from . import settings
from . import views

urlpatterns = [
    url(
        r"^verify-payment/(?P<order>[\w.@+-]+)/$",
        views.verify_payment,
        name="verify_payment",
    ),
    url(
        r"^failed-verification/(?P<order_id>[\w.@+-]+)/$",
        views.failure_redirect_view,
        name="failed_verification",
    ),
    url(
        r"^successful-verification/(?P<order_id>[\w.@+-]+)/$",
        views.success_redirect_view,
        name="successful_verification",
    ),
    url(
        r"^failed-page/$",
        views.TemplateView.as_view(template_name="paystack/failed-page.html"),
        name="failed_page",
    ),
    url(
        r"^success-page/$",
        views.TemplateView.as_view(template_name="paystack/success-page.html"),
        name="success_page",
    ),
    url(r"^webhook/$", csrf_exempt(views.webhook_view), name="webhook"),
]
