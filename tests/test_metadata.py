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
    assert response.status_code == 200, f"{meta_name} 메타데이터 조회 실패: {response.status_code} {response.text}"
    meta = response.json()
    assert len(meta) > 0, f"{meta_name} 메타데이터가 비어 있습니다"

    invalid_ids = [m[id_field] for m in meta if type(m[id_field]) is not int]
    assert not invalid_ids, f"{meta_name} 메타데이터의 {id_field} 중 정수가 아닌 값: {invalid_ids}"
    invalid_names = [m[name_field] for m in meta if type(m[name_field]) is not str]
    assert not invalid_names, f"{meta_name} 메타데이터의 {name_field} 중 문자열이 아닌 값: {invalid_names}"

    ids = [m[id_field] for m in meta]
    assert len(ids) == len(set(ids)), f"{meta_name} 메타데이터에 중복된 {id_field}가 있습니다"
