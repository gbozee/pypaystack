class BaseClass(object):
    def __init__(self, make_request):
        self.make_request = make_request

    def result_format(self, response, callback=None):
        if response.status_code >= 400:
            result = response.json()
            return result["status"], result["message"]

        result = response.json()
        if callback:
            return callback(result)
        return result["status"], result["message"], result["data"], request.get("meta")
