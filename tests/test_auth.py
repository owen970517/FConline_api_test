import pytest
from api_client import FcOnlineClient
from conftest import BASE_URL,TEST_NICKNAME
from tests.apiError import assert_api_error

class TestAuth :
    @pytest.mark.parametrize("api_key, expected_name, expected_message", [
        ("wrong-key", "OPENAPI00005", "The apikey is not valid."),       # TC-11
        (None,        "OPENAPI00004", "Please input valid parameter"),   # TC-12
        ("",          "OPENAPI00004", "Please input valid parameter"),   # TC-13
    ])
    def test_잘못되거나_없는_키는_거부된다(self, api_key, expected_name, expected_message):
        bad_client = FcOnlineClient(BASE_URL, api_key)
        response = bad_client.get_ouid(TEST_NICKNAME)
        assert response.status_code == 400
        assert_api_error(response.json(), expected_name, expected_message)