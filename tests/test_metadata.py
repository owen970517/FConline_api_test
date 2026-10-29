from api_client import FcOnlineClient
from conftest import BASE_URL

def test_매치타입_메타데이터_조회():
    no_key_client = FcOnlineClient(BASE_URL, None)
    response = no_key_client.get_meta_data()
    assert response.status_code == 200
    meta = response.json()
    assert len(meta) > 0
    assert type(meta[0]['matchtype']) is int
    assert type(meta[0]['desc']) is str