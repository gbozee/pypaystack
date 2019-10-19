import pytest
from starlette.responses import JSONResponse
from starlette.testclient import TestClient
from starlette.config import environ

environ["PAYSTACK_SECRET_KEY"] = "sample_secret_key"
environ["PAYSTACK_PUBLIC_KEY"] = "sample_public_key"

from paystack.frameworks.starlette import build_app


def response_callback(status, order=None):
    if status:
        return JSONResponse({"status": status, "order": order})
    return JSONResponse({"status": False}, status_code=400)


@pytest.fixture
def client():
    def _init(PaystackAPI):
        app = build_app(PaystackAPI, response_callback=response_callback)
        return TestClient(app=app)

    return _init
