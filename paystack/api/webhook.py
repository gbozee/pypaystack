from . import signals
import json
import hmac
import hashlib


def generate_digest(data, secret):
    return hmac.new(
        secret.encode("utf-8"), msg=data, digestmod=hashlib.sha512
    ).hexdigest()


def charge_data(raw_data, full_auth=False, full=False):
    if full:
        return raw_data
    auth_data = {}
    customer = raw_data["customer"]
    auth = raw_data.get("authorization")
    plan = raw_data.get("plan_object") or raw_data.get("plan") or {}
    for key in ["send_invoices", "send_sms", "description"]:
        plan.pop(key, None)
    if plan.get("amount"):
        plan["amount"] = plan["amount"] / 100
    if auth:
        auth_data["authorization_code"] = auth["authorization_code"]
    if full_auth:
        auth_data = auth
    return {
        "amount": raw_data["amount"] / 100,
        "status": raw_data["status"],
        "currency": raw_data["currency"].lower(),
        "reference": raw_data["reference"],
        "plan_object": plan,
        "authorization": auth_data,
        "customer": {
            "id": customer["id"],
            "email": customer["email"],
            "customer_code": customer["customer_code"],
        },
        "paid_at": raw_data["paid_at"],
    }


def transfer_data(raw_data, full=False):
    if full:
        return raw_data
    result = {
        "amount": raw_data["amount"] / 100,
        "recipient": {"recipient_code": raw_data["recipient"]["recipient_code"]},
        "transfer_code": raw_data["transfer_code"],
        "transferred_at": raw_data["transferred_at"],
        "created_at": raw_data["created_at"],
    }
    return result


class Webhook(object):
    def __init__(self, generate_digest):
        self.secret_key = generate_digest

    def verify(
        self,
        unique_code,
        request_body,
        use_default=False,
        full_auth=False,
        full=False,
        **kwargs
    ):
        digest = generate_digest(request_body, self.secret_key)
        if digest == unique_code:
            payload = json.loads(request_body)
            if payload["event"] == "charge.success":
                kwargs["data"] = charge_data(
                    payload["data"], full_auth=full_auth, full=full
                )
            elif payload["event"] in ["transfer.success", "transfer.failed"]:
                kwargs["data"] = transfer_data(payload["data"], full=full)
                kwargs["transfer_code"] = payload["data"]["transfer_code"]
            else:
                kwargs = {"event": payload["event"], "data": payload["data"]}
            if use_default:
                signal_func = signals.event_signal
            else:
                options = {
                    "charge.success": signals.successful_payment_signal,
                    "transfer.success": signals.successful_transfer_signal,
                    "transfer.failed": signals.failed_transfer_signal,
                }
                try:
                    signal_func = options[payload["event"]]
                except KeyError:
                    signal_func = signals.event_signal
            signal_func.send(sender=self, **kwargs)
            return payload["event"], kwargs
