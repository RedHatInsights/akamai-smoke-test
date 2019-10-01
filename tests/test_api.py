import pytest
import requests

from utils import getUrl
from utils import headers
from utils import ip_context
from utils import IPS


def do_api(env, path, release="stable", expected_status=200):
    url = getUrl(path, release)
    with ip_context(IPS[env]):
        r = requests.get(url, headers=headers)
    assert r.status_code == expected_status


@pytest.mark.parametrize("data_element", ["/api/v1/static/uploader.json"])
@pytest.mark.parametrize("env", ["stage", "prod"])
def test_api_prod(env, data_element):
    do_api(env, data_element, "stable")


@pytest.mark.parametrize("data_element", ["/api/zomgnotfound"])
@pytest.mark.parametrize("env", ["stage", "prod"])
def test_400_api(env, data_element):
    do_api(env, data_element, "stable", 404)
