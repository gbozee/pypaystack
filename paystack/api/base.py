class BaseClass(object):
    def __init__(self, make_request, async_make_request=None, **kwargs):
        self.make_request = make_request
        self.async_make_request = async_make_request
        for key, value in kwargs.items():
            setattr(self, key, value)

    def build_path(self, path):
        return self.path + path

    def result_format(self, response, callback=None):
        if response.status_code >= 400:
            result = response.json()
            return result["status"], result["message"]

        result = response.json()
        if callback:
            return callback(result)
        return result["status"], result["message"], result["data"], result.get("meta")
