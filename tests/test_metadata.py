import pytest

from api_client import FcOnlineClient
from conftest import BASE_URL

@pytest.mark.parametrize("meta_name, id_field, name_field", [
    ("matchtype", "matchtype", "desc"),
    ("division", "divisionId", "divisionName"),
])
def test_키없이_메타데이터_조회(meta_name, id_field, name_field):
    no_key_client = FcOnlineClient(BASE_URL, None)
    response = no_key_client.get_meta(meta_name)
    assert response.status_code == 200
    meta = response.json()
    assert len(meta) > 0
    assert all(type(m[id_field]) is int for m in meta)
    assert all(type(m[name_field]) is str for m in meta)
    
    ids = [m[id_field] for m in meta]
    assert len(ids) == len(set(ids)), f"{meta_name} 메타데이터에 중복된 {id_field}가 있습니다"