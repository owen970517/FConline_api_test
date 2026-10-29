def assert_api_error(res, name, message):
    assert res['error']['name'] == name
    assert res['error']['message'] == message