import pytest
import requests
import hashlib
import time

from dotdict import DotDict
from lxml import html
from utils import Utils
from decorators import modify_ip

baseurl = 'https://cloud.redhat.com'
cookies = { 'x-rh-insights-alpha': 'flipmodesquadisthegreatest' }

output_data = {}

def getUrl(path, release='stable'):
    if release == 'beta':
        return baseurl + '/beta' + path
    return baseurl + path

def do_urls(env, data_element, release = 'stable'):
    data_key, data_val = data_element
    for path in data_val:
        url = getUrl(path, release)
        r = requests.get(url, cookies=cookies)

        assert r.status_code == 200, 'Expected status code of GET {} to be 200 got {}'.format(url, r.status_code)

        found = False

        tree = html.fromstring(r.content)
        for thing in tree.xpath('//script[@type="text/javascript"]'):

            if 'src' in thing.attrib:
                src = thing.attrib['src']
                if 'App.js' in src:
                    expected = '/apps/' + data_key
                    assert expected in src, "unexpected app id at {}\n{}\n{}".format(url, r.text, r.headers)

                    if env == 'stage':
                        assert 'X-Akamai-Staging' in r.headers, 'expected to see staging header in {}\n{}'.format(r.headers, url)
                    else:
                        assert 'X-Akamai-Staging' not in r.headers, 'expected to not see staging header in {}\n{}'.format(r.headers, url)

                    if path not in output_data:
                        output_data[path] = DotDict({ 'url': url })
                    output_data[path][env + '_hash'] = hashlib.md5(r.text.encode('utf-8')).hexdigest()
                    found = True

        # if the HTML did not contain a valid JS src!
        assert found, 'did not find a valid app js reference in HTML on GET {}\n{}'.format(url, r.text)


DATA = Utils.getData(path = pytest.config.getoption('data'))
APP = pytest.config.getoption('app')
if APP:
    assert APP in DATA, 'invalid app... you asked for {}'.format(APP)
    DATA = { APP: DATA[APP] }

PROD_IP  = '104.112.254.145'
STAGE_IP = '23.201.3.166'
UHC_ON_CLOUD_URLS = [ getUrl('/'), getUrl('/clusters/') ]

@pytest.mark.prod
@pytest.mark.parametrize('data_element', UHC_ON_CLOUD_URLS)
@modify_ip(PROD_IP)
def test_uhc_unchromed_still_works_prod(data_element):
    r = requests.get(data_element)
    assert '<title>OpenShift Unified Hybrid Cloud</title>' in r.text
    assert ' src="/clusters/bundle.main.js' in r.text

@pytest.mark.prod
@pytest.mark.parametrize('data_element', DATA.items(), ids=list(DATA.keys()))
@modify_ip(PROD_IP)
def test_urls_prod_stable(data_element):
    do_urls('prod', data_element, release = 'beta')

@pytest.mark.prod
@pytest.mark.parametrize('data_element', DATA.items(), ids=list((s + '-beta' for s in DATA.keys())))
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
@pytest.mark.parametrize('data_element', DATA.items(), ids=list(DATA.keys()))
@modify_ip(STAGE_IP)
def test_urls_stage_stable(data_element):
    do_urls('stage', data_element)

@pytest.mark.stage
@pytest.mark.parametrize('data_element', DATA.items(), ids=list((s + '-beta' for s in DATA.keys())))
@modify_ip(STAGE_IP)
def test_urls_stage_beta(data_element):
    do_urls('stage', data_element, release = 'beta')

# cannot use this in parallel without something like
# https://github.com/pytest-dev/pytest-xdist/issues/385
@pytest.mark.skip(reason="cannot use this in parallel mode")
def test_hashes():
    for key, val in output_data.items():
        assert val.prod_hash == val.stage_hash, "md5sum mismatch for page at {}".format(val.url)
