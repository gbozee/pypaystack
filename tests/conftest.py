import pytest
from unittest import mock
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
        side_effect = kwargs.pop('side_effect', None)
        mock_post = mocker.patch('requests.post')
        if side_effect:
            mock_post.side_effect = [MockRequest(x) for x in side_effect]
        else:
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
        side_effect = kwargs.pop('side_effect', None)
        url = "{}{}".format(paystack_api.base_url, path)
        if side_effect:
            mock_calls = [
                mock.call(url, headers=headers, **x) for x in side_effect
            ]
            mock_call.assert_has_calls(mock_calls, any_order=True)
        else:
            mock_call.assert_called_once_with(url, headers=headers, **kwargs)

    return _mock_assertion
