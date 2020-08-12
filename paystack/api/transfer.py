from .base import BaseClass
from dateutil import parser
import requests as  requests_async
import asyncio


class PaystackException(Exception):
    pass


def filter_status(field, status):
    return field["status"] == status


def filter_recipient_code(field, recipient, recipient_field="recipient_code"):
    nested = recipient_field.split(".")
    if len(nested) == 2:
        return recipient in field["recipient"][nested[0]][nested[1]]
    return recipient in field["recipient"][recipient_field]


def filter_date_range(field, _from, to, date_field="createdAt"):
    field_date = parser.parse(field[date_field])
    from_date = parser.parse(_from).replace(tzinfo=field_date.tzinfo)
    to_date = parser.parse(to).replace(tzinfo=field_date.tzinfo)
    # print("\n")
    # print(f"from: {from_date}")
    # print(f"date: {field_date}")
    # print(f"to: {to_date}")
    return from_date <= field_date <= to_date


def filter_result(data, filters):
    filter_functions = {
        "status": lambda x: filter_status(x, filters["status"]),
        "recipient_code": lambda x: filter_recipient_code(x, filters["recipient"]),
        "recipient_name": lambda x: filter_recipient_code(
            x, filters["recipient"], "name"
        ),
        "recipient_account": lambda x: filter_recipient_code(
            x, filters["recipient"], "details.account_number"
        ),
        "date_created": lambda x: filter_date_range(x, filters["_from"], filters["to"]),
        "date_updated": lambda x: filter_date_range(
            x, filters["_from"], filters["to"], date_field="updatedAt"
        ),
    }
    conditions = {}
    for key, value in filters.items():
        if key == "status":
            conditions["status"] = filter_functions["status"]
        if key == "r_kind":
            if value in ["recipient_code", "recipient_name", "recipient_account"]:
                conditions[value] = filter_functions[value]
        if key == "date_kind":
            if value == "created":
                conditions["date_created"] = filter_functions["date_created"]
            else:
                conditions["date_updated"] = filter_functions["date_updated"]

    return [x for x in data if all([b(x) for a, b in conditions.items()])]


class Transfer(BaseClass):
    def get_banks(self):
        path = "/bank"
        response = self.make_request("GET", path)
        return self.result_format(response)

    def create_recipient(self, account_name, account_id, bank):
        path = "/transferrecipient"
        json = {
            "type": "nuban",
            "name": account_name,
            "description": account_name,
            "account_number": account_id,
            "bank_code": self.get_bank_code(bank),
            "currency": "NGN",
        }
        response = self.make_request("POST", path, json=json)
        return self.result_format(response)

    def initialize_transfer(self, amount, recipient, reason):
        path = "/transfer"
        json = {
            "source": "balance",
            "reason": reason,
            "amount": float(amount * 100),
            "recipient": recipient,
        }
        req = self.make_request("POST", path, json=json)
        return self.result_format(req)

    def create_transfer_code(self, recipient_code, amount, reason=""):
        data = self.initialize_transfer(amount, recipient_code, reason)
        return self._transfer_response(data)

    def _transfer_response(self, result):
        if len(result) == 3:
            transfer_code = result[2]["transfer_code"]
            msg = result[1]
            return transfer_code, msg
        return None, None

    def bulk_transfer(self, array_of_recipient_with_amount):
        transform = [
            {"amount": x["amount"] * 100, "recipient": x["recipient"]}
            for x in array_of_recipient_with_amount
        ]
        path = "/transfer/bulk"
        json_data = {"currency": "NGN", "source": "balance", "transfers": transform}
        req = self.make_request("POST", path, json=json_data)
        return self.result_format(req, lambda x: (x["status"], x["message"]))

    def verify_transfer(self, transfer_recipient, code):
        """verify transaction"""
        path = "/transfer/finalize_transfer"
        json = {"transfer_code": transfer_recipient, "otp": code}
        req = self.make_request("POST", path, json=json)
        return self.result_format(req, lambda x: (True, x))

    def enable_otp(self, status=True, code=None):
        url = "/transfer/enable_otp"
        if not status:
            url = "/transfer/disable_otp"
        if code:
            url = "/transfer/disable_otp_finalize"
        json = {}
        if code:
            json = {"otp": code}
        req = self.make_request("POST", url, json=json)
        if req.status_code >= 400:
            req.raise_for_status()
        return req.json()["data"]

    def resend_otp(self, transfer_recipient):
        req = self.make_request(
            "POST", "/transfer/resend_otp", json={"transfer_code": transfer_recipient}
        )
        if req.status_code >= 400:
            req.raise_for_status()
        return req.json()["data"]

    def get_transfer(self, transfer_recipient):
        """Fetch the transfer for a given recipient"""
        req = self.make_request("GET", "/transfer/" + transfer_recipient)
        return self.result_format(req)

    def get_banks(self):
        """Fetch the list of banks supported by paystack"""
        req = self.make_request("GET", "/bank")
        return self.result_format(req)

    def get_bank(self, bank_name):
        result = self.get_banks()
        if len(result) > 2:
            instance = [x for x in result[2] if bank_name.lower() in x["name"].lower()]
            if instance:
                return instance[0]

    def get_bank_code(self, bank_name):
        options = {
            "Citibank": "023",
            "Access Bank": "044",
            "Diamond Bank": "063",
            "Ecobank Nigeria": "050",
            "Enterprise Bank": "084",
            "Fidelity Bank Nigeria": "070",
            "First Bank of Nigeria": "011",
            "First City Monument Bank": "214",
            "Guaranty Trust Bank": "058",
            "Heritage Bank": "030",
            "Keystone Bank Limited": "082",
            "Mainstreet Bank": "014",
            "Skye Bank": "076",
            "Stanbic IBTC Bank": "221",
            "Standard Chartered Bank": "068",
            "Sterling Bank": "232",
            "Union Bank of Nigeria": "032",
            "United Bank for Africa": "033",
            "Unity Bank": "215",
            "Wema Bank": "035",
            "Zenith Bank": "057",
            "Jaiz Bank": "301",
            "Suntrust Bank": "100",
            "Providus Bank": "101",
            "Parallex Bank": "526",
        }
        return options.get(bank_name)

    def check_balance(self):
        path = "/balance"
        result = self.make_request("GET", path)
        data = result.json()
        if not data["status"]:
            raise PaystackException("Invalid Key sent.")
        return [
            {"currency": x["currency"], "balance": x["balance"] / 100}
            for x in data.get("data")
        ]

    async def get_transfers(self, perPage=50, page=1, session=requests_async):
        params = {"perPage": perPage, "page": page}
        path = "/transfer"
        response = await self.async_make_request("GET", path, session, params=params)
        return self.result_format(response)

    async def get_transfer_and_filter(self, perPage, page, session, filters):
        result = await self.get_transfers(perPage=perPage, page=page, session=session)
        if result[0]:
            return filter_result(result[2], filters)
        return []

    async def get_transfers_with_filters(
        self,
        perPage=100,
        recipient=None,
        r_kind=None,
        date_kind=None,
        status=None,
        _from=None,
        _to=None,
    ):
        result = await self.get_transfers(perPage=perPage)
        if result[0]:

            filter_params = {}
            for key, value in {
                "recipient": recipient,
                "r_kind": r_kind,
                "_from": _from,
                "to": _to,
                "date_kind": date_kind,
                "status": status,
            }.items():
                if value:
                    filter_params[key] = value
            meta = result[3]

            tasks = []
            async with requests_async.Session() as session:
                for i in range(1, meta["pageCount"] + 1):
                    task = asyncio.ensure_future(
                        self.get_transfer_and_filter(perPage, i, session, filter_params)
                    )
                    tasks.append(task)
                responses = await asyncio.gather(*tasks)
                return responses

    def sync_get_transfers_with_filters(self, **kwargs):
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(self.get_transfers_with_filters(**kwargs))
        result = loop.run_until_complete(future)
        empty_list = [x for x in result if len(x) > 0]
        return [a for b in empty_list for a in b]


filters = {"r_kind": "recipient_name", "recipient": "Abiola Oyeniyi"}

