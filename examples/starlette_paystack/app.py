from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from paystack.frameworks.starlette import build_app
from paystack.utils import PaystackAPI, get_js_script


async def post_webhook_processing(
    signature, body, paystack_instance: PaystackAPI = None, **kwargs
):
    event, data = paystack_instance.webhook_api.verify(
        signature, body, full_auth=True, full=True
    )
    import ipdb

    ipdb.set_trace()
    pass


app = build_app(
    PaystackAPI, root_path="/paystack", post_webhook_processing=post_webhook_processing
)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.route("/", methods=["GET"])
def payment_page(request: Request):
    paystack_instance: PaystackAPI = app.state.paystack
    # client_secret = stripe_instance.initialize_payment(amount=20, currency="eur")
    # params = {"amount": 2000, "currency": "eur"}
    # redirect_url = f"/verify-payment/ABCD?{urllib.parse.urlencode(params)}"
    redirect_url = f"/make-payment/ABCD"
    payment_info = {
        **paystack_instance.processor_info(30),
        "currency": "ngn",
        "ref": "13ABCDJJUU",
    }
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "paystack_instance": paystack_instance,
            "payment_info": payment_info,
        },
    )
