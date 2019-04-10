import pytest
import requests
import hashlib
import time
import itertools

from dotdict import DotDict
from lxml import html
from utils import Utils
from decorators import modify_ip

headers = {
    'Cookie': 'x-rh-insights-alpha=flipmodesquadisthegreatest',
    'Pragma': 'akamai-x-get-extracted-values'
}

output_data = {}

def do_urls(env, data_element, release = 'stable'):
    appname, path = data_element
    url = Utils.getUrl(path, release)
    r = requests.get(url, headers=headers)

    assert r.status_code == 200, 'Expected status code of GET {} to be 200 got {}'.format(url, r.status_code)

    found = False
    tree = html.fromstring(r.content)

    if 'App.js' in r.text:
        for thing in tree.xpath('//script[@type="text/javascript"]'):
            if 'src' in thing.attrib:
                src = thing.attrib['src']
                if 'App.js' in src:
                    expected = '/apps/' + appname
                    assert expected in src, "unexpected app id at {}\n{}\n{}".format(url, r.text, r.headers)
                    found = True
    else:
        # catches apps that are not the starter app
        if release == 'beta':
            assert '<script type="text/javascript" src="/beta/apps/{}'.format(appname) in r.text
        else:
            assert '<script type="text/javascript" src="/apps/{}'.format(appname) in r.text
        found = True

    assert found, 'did not find a valid app js reference in HTML on GET {}\n{}'.format(url, r.text)

    if env == 'stage':
        assert 'X-Akamai-Staging' in r.headers, 'expected to see staging header in {}\n{}'.format(r.headers, url)
    else:
        assert 'X-Akamai-Staging' not in r.headers, 'expected to not see staging header in {}\n{}'.format(r.headers, url)

    assert 'X-Akamai-Session-Info' in r.headers

    AKA_PM_FWD_URL = Utils.extractNamedInfoHeaderValue(r.headers['X-Akamai-Session-Info'], 'AKA_PM_FWD_URL')
    net_storage_path = Utils.getNetStoragePath(appname, release)
    # TODO disabled while we hack
    # assert AKA_PM_FWD_URL == net_storage_path, 'expected AKA_PM_FWD_URL ({}) to match the netstorage path ({}) for the GET {}'.format(AKA_PM_FWD_URL, net_storage_path, url)

    if path not in output_data:
        output_data[path] = DotDict({ 'url': url })
    output_data[path][env + '_hash'] = hashlib.md5(r.text.encode('utf-8')).hexdigest()

    # if the HTML did not contain a valid JS src!

RAW_DATA = Utils.getData(path = pytest.config.getoption('data'))
DATA = Utils.getFlatData(RAW_DATA)
APP = pytest.config.getoption('app')

if APP:
    assert APP in RAW_DATA, 'invalid app... you asked for {}'.format(APP)
    DATA = Utils.getFlatData({ APP: RAW_DATA[APP] })

PROD_IP  = '104.112.254.145'
STAGE_IP = '23.201.3.166'
UHC_ON_CLOUD_URLS = [ Utils.getUrl('/'), Utils.getUrl('/clusters/') ]

@pytest.mark.prod
@pytest.mark.parametrize('data_element', UHC_ON_CLOUD_URLS)
@modify_ip(PROD_IP)
def test_uhc_unchromed_still_works_prod(data_element):
    r = requests.get(data_element)
    assert '<title>OpenShift Unified Hybrid Cloud</title>' in r.text
    assert ' src="/clusters/bundle.main.js' in r.text

@pytest.mark.prod
@pytest.mark.parametrize('data_element', DATA, ids=list((d[1] for d in DATA)))
@modify_ip(PROD_IP)
def test_urls_prod_stable(data_element):
    do_urls('prod', data_element, release = 'beta')

@pytest.mark.prod
@pytest.mark.parametrize('data_element', DATA, ids=list(('/beta' + d[1] for d in DATA)))
@modify_ip(PROD_IP)
def test_urls_prod_beta(data_element):
    do_urls('prod', data_element, release = 'beta')

@pytest.mark.stage
@pytest.mark.parametrize('data_element', UHC_ON_CLOUD_URLS)
@modify_ip(STAGE_IP)
def test_uhc_unchromed_still_works_stage(data_element):
    r = requests.get(data_element)
    assert '<title>OpenShift Unified Hybrid Cloud</title>' in r.text
    assert ' src="/clusters/bundle.main.js' in r.text

@pytest.mark.stage
@pytest.mark.parametrize('data_element', DATA, ids=list((d[1] for d in DATA)))
@modify_ip(STAGE_IP)
def test_urls_stage_stable(data_element):
    do_urls('stage', data_element)

@pytest.mark.stage
@pytest.mark.parametrize('data_element', DATA, ids=list(('/beta' + d[1] for d in DATA)))
@modify_ip(STAGE_IP)
def test_urls_stage_beta(data_element):
    do_urls('stage', data_element, release = 'beta')

# cannot use this in parallel without something like
# https://github.com/pytest-dev/pytest-xdist/issues/385
@pytest.mark.skip(reason="cannot use this in parallel mode")
def test_hashes():
    for key, val in output_data.items():
        assert val.prod_hash == val.stage_hash, "md5sum mismatch for page at {}".format(val.url)
