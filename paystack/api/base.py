class BaseClass(object):
    def __init__(self, make_request, async_make_request=None):
        self.make_request = make_request
        self.async_make_request = async_make_request

    def result_format(self, response, callback=None):
        if response.status_code >= 400:
            result = response.json()
            return result["status"], result["message"]

        result = response.json()
        if callback:
            return callback(result)
        return result["status"], result["message"], result["data"], result.get("meta")
