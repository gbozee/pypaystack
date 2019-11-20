import asyncio
import functools
import importlib

from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.config import Config
from starlette.datastructures import URL, Secret
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from paystack.api import signals

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


async def webhook_view(request: Request, background_action=None, **kwargs):
    signature = request.headers.get("x-paystack-signature")
    body = await request.body()
    return JSONResponse(
        {"status": "Success"},
        background=BackgroundTask(background_action, signature, body, **kwargs),
    )


def build_app(
    PaystackAPI,
    root_path="",
    response_callback=None,
    post_webhook_processing=None,
    _app: Starlette = None,
):
    paystack_instance = PaystackAPI(
        public_key=str(PAYSTACK_PUBLIC_KEY),
        secret_key=str(PAYSTACK_SECRET_KEY),
        base_url=str(PAYSTACK_API_URL),
        django=False,
    )
    if _app:
        app = _app
    else:
        app = Starlette()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def background_action(signature, body):
        return paystack_instance.webhook_api.verify(
            signature, body, full_auth=True, full=False, loop=loop
        )

    verify_action = post_webhook_processing or background_action

    async def new_webhook(request):
        return await webhook_view(
            request,
            background_action=verify_action,
            paystack_instance=paystack_instance,
        )

    app.add_route(root_path + "/webhook", new_webhook, methods=["POST"])
    new_verify_payment = lambda request: verify_payment(
        request,
        response_callback=response_callback,
        paystack_instance=paystack_instance,
        PaystackAPI=PaystackAPI,
    )
    app.add_route(
        root_path + "/verify-payment/{order_id}", new_verify_payment, methods=["GET"]
    )
    app.state.paystack = paystack_instance
    return app
