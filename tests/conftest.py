import pytest
from paystack.utils import PaystackAPI, MockRequest
PAYSTACK_API_URL = 'https://api.paystack.co'


@pytest.fixture
def paystack_api():
    return PaystackAPI(
        public_key="public_key",
        secret_key="secret_key",
        django=False,
        base_url=PAYSTACK_API_URL)


@pytest.fixture
def headers(paystack_api):
    return {
        'Authorization': "Bearer {}".format(paystack_api.secret_key),
        'Content-Type': 'application/json'
    }


@pytest.fixture
def get_request(mocker):
    def _get_request(*args, **kwargs):
        mock_get = mocker.patch('requests.get')
        mock_get.return_value = MockRequest(*args, **kwargs)
        return mock_get

    return _get_request


@pytest.fixture
def post_request(mocker):
    def _post_request(*args, **kwargs):
        mock_post = mocker.patch('requests.post')
        mock_post.return_value = MockRequest(*args, **kwargs)
        return mock_post

    return _post_request


@pytest.fixture
def put_request(mocker):
    def _put_request(*args, **kwargs):
        mock_post = mocker.patch('requests.put')
        mock_post.return_value = MockRequest(*args, **kwargs)
        return mock_post

    return _put_request


@pytest.fixture
def mock_assertion(headers, paystack_api):
    def _mock_assertion(mock_call, path, **kwargs):
        url = "{}{}".format(paystack_api.base_url, path)
        mock_call.assert_called_once_with(url, headers=headers, **kwargs)

    return _mock_assertion
