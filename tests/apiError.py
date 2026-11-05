def assert_api_error(res, name, message):
    error = res["error"]
    assert error["name"] == name, f"에러 코드가 다릅니다: 기대 {name}, 실제 {error['name']}"
    assert error["message"] == message, f"에러 메시지가 다릅니다: 기대 {message!r}, 실제 {error['message']!r}"
