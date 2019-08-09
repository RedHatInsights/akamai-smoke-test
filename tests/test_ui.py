import hashlib

import pytest
import requests
from dotdict import DotDict
from lxml import html

from utils import extractNamedInfoHeaderValue
from utils import getMainData
from utils import getAdditionalData
from utils import getFlatData
from utils import getNetStoragePath
from utils import getUrl
from utils import headers
from utils import ip_context
from utils import IPS

output_data = {}
sessions = {}
sessions['stage'] = requests.Session()
sessions['prod'] = requests.Session()

def do_urls(env, appname, path, release, expected_status=200):
    url = getUrl(path, release)
    with ip_context(IPS[env]):
        r = requests.get(url, headers=headers, timeout=6)

    assert (
        r.status_code == expected_status
    ), "Expected status code of GET {} to be {} but got {}".format(
        url, expected_status, r.status_code
    )

    found = False
    tree = html.fromstring(r.content)

    if "App.js" in r.text:
        for thing in tree.xpath('//script[@type="text/javascript"]'):
            if "src" in thing.attrib:
                src = thing.attrib["src"]
                if "App.js" in src:
                    expected = f"/apps/{appname}"
                    assert expected in src, f"unexpected app id at {url}\n{r.text}\n{r.headers}"
                    found = True
    else:
        # catches apps that are not the starter app
        if release == "beta":
            assert '<script type="text/javascript" src="/beta/apps/{}'.format(appname) in r.text
        else:
            assert '<script type="text/javascript" src="/apps/{}'.format(appname) in r.text
        found = True

    assert found, "did not find a valid app js reference in HTML on GET {}\n{}".format(url, r.text)

    if env == "stage":
        assert "X-Akamai-Staging" in r.headers, "expected to see staging header in {}\n{}".format(
            r.headers, url
        )
    else:
        assert (
            "X-Akamai-Staging" not in r.headers
        ), "expected to not see staging header in {}\n{}".format(r.headers, url)

    assert "X-Akamai-Session-Info" in r.headers

    AKA_PM_FWD_URL = extractNamedInfoHeaderValue(
        r.headers["X-Akamai-Session-Info"], "AKA_PM_FWD_URL"
    )
    net_storage_path = getNetStoragePath(appname, release, expected_status)

    assert (
        AKA_PM_FWD_URL == net_storage_path
    ), "expected AKA_PM_FWD_URL ({}) to match the netstorage path ({}) for the GET {}".format(
        AKA_PM_FWD_URL, net_storage_path, url
    )

    if path not in output_data:
        output_data[path] = DotDict({"url": url})
    output_data[path][env + "_hash"] = hashlib.md5(r.text.encode("utf-8")).hexdigest()

    # if the HTML did not contain a valid JS src!

MAIN_DATA = getMainData(release=pytest.config.getoption("release"))
SUPPLEMENTAL_DATA = getAdditionalData(path=pytest.config.getoption("data"))
DATA = getFlatData(MAIN_DATA, SUPPLEMENTAL_DATA)
APP = pytest.config.getoption("app")

if APP:
    assert APP in DATA, "invalid app... you asked for {}".format(APP)
    DATA = getFlatData({APP: DATA[APP]})

UHC_ON_CLOUD_URLS = [getUrl("/"), getUrl("/clusters/")]


@pytest.mark.parametrize("appname,path,releaselist", DATA)
@pytest.mark.parametrize("env", ["stage", "prod"])
@pytest.mark.parametrize("release", ["stable", "beta"])
def test_urls(appname, path, releaselist, env, release):
    if release in releaselist:
        do_urls(env, appname, path, release=release)


@pytest.mark.parametrize("data_element", [("landing", "/zomgnotfound")])
@pytest.mark.parametrize("env", ["stage", "prod"])
def test_400_url(env, data_element):
    do_urls(env, data_element, "stable", 404)


# cannot use this in parallel without something like
# https://github.com/pytest-dev/pytest-xdist/issues/385
@pytest.mark.parametrize("data_element", DATA, ids=list(d[1] for d in DATA))
def test_hashes_prod_and_stage(data_element):
    for env in ['prod', 'stage']:
        hash = []
        with ip_context(IPS[env]):
            appname, path, release = data_element
            url = getUrl(path, 'stable')
            r = sessions[env].get(url, headers=headers, timeout=6)
            hash.append(hashlib.md5(r.text.encode("utf-8")).hexdigest())
    assert all(hash[0] == h_obj for h_obj in hash)
