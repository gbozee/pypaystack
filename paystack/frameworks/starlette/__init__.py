import asyncio
import functools
import importlib

from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.background import BackgroundTask
from starlette.responses import JSONResponse, RedirectResponse

from paystack.api import signals

from starlette.config import Config
from starlette.datastructures import URL, Secret

config = Config(".env")

PAYSTACK_SECRET_KEY = config("PAYSTACK_SECRET_KEY", cast=Secret)
PAYSTACK_PUBLIC_KEY = config("PAYSTACK_PUBLIC_KEY", cast=Secret)

PAYSTACK_API_URL = config("PAYSTACK_API_URL", default="https://api.paystack.co")


def verify_payment(
    request: Request, response_callback=None, paystack_instance=None, PaystackAPI=None
):
    amount = request.query_params.get("amount")
    order = request.path_params.get("order_id")
    txrf = request.query_params.get("trxref")
    response = paystack_instance.verify_payment(txrf, amount=int(amount))
    if response[0]:
        signals.payment_verified.send(
            sender=PaystackAPI, ref=txrf, amount=int(amount) / 100, order=order
        )
    return response_callback(response[0], order=order)


async def webhook_view(request: Request, paystack_instance=None, full=True):
    signature = request.headers.get("x-paystack-signature")
    body = await request.body()
    return JSONResponse(
        {"status": "Success"},
        background=BackgroundTask(
            paystack_instance.webhook_api.verify,
            signature,
            body,
            full_auth=True,
            full=full,
        ),
    )


def build_app(PaystackAPI, response_callback=None, full_event=False):
    app = Starlette()
    paystack_instance = PaystackAPI(
        public_key=str(PAYSTACK_PUBLIC_KEY),
        secret_key=str(PAYSTACK_SECRET_KEY),
        base_url=str(PAYSTACK_API_URL),
    )
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
    )

    async def new_webhook(request):
        return await webhook_view(
            request, paystack_instance=paystack_instance, full=full_event
        )

    # new_webhook = lambda request: expression asyncio.coroutine(
    #     functools.partial(webhook_view, paystack_instance=paystack_instance)
    # )
    app.add_route("/webhook", new_webhook, methods=["POST"])
    new_verify_payment = lambda request: verify_payment(
        request,
        response_callback=response_callback,
        paystack_instance=paystack_instance,
        PaystackAPI=PaystackAPI,
    )
    app.add_route("/verify-payment/{order_id}", new_verify_payment, methods=["GET"])
    return app
