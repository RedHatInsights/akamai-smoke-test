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

def getUrl(path, release):
    if release == 'beta':
        return baseurl + '/beta' + path
    return baseurl + path

def do_urls(env, data_element, release = 'stable'):
    data_key, data_val = data_element
    for path in data_val:
        url = getUrl(path, release)
        r = requests.get(url, cookies=cookies)
        tree = html.fromstring(r.content)
        for thing in tree.xpath('//script[@type="text/javascript"]'):
            if 'src' in thing.attrib:
                src = thing.attrib['src']
                if 'App.js' in src:
                    expected = '/apps/' + data_key
                    assert expected in src, "unexpected app id at {}\n{}\n{}".format(url, r.text, r.headers)

                    if env == 'stage':
                        assert 'X-Akamai-Staging' in r.headers, 'expected to see staging header in {}'.format(r.headers)
                    else:
                        assert 'X-Akamai-Staging' not in r.headers, 'expected to not see staging header in {}'.format(r.headers)

                    if path not in output_data:
                        output_data[path] = DotDict({ 'url': url })
                    output_data[path][env + '_hash'] = hashlib.md5(r.text.encode('utf-8')).hexdigest()

DATA = Utils.getData()

@pytest.mark.parametrize('data_element', DATA.items(), ids=list(DATA.keys()))
@modify_ip('104.112.254.145')
def test_urls_prod_stable(data_element):
    do_urls('prod', data_element, release = 'beta')

@pytest.mark.parametrize('data_element', DATA.items(), ids=list(DATA.keys()))
@modify_ip('104.112.254.145')
def test_urls_prod_beta(data_element):
    do_urls('prod', data_element, release = 'beta')

@pytest.mark.parametrize('data_element', DATA.items(), ids=list(DATA.keys()))
@modify_ip('23.201.3.166')
def test_urls_stage_stable(data_element):
    do_urls('stage', data_element)

@pytest.mark.parametrize('data_element', DATA.items(), ids=list((s + '-beta' for s in DATA.keys())))
@modify_ip('23.201.3.166')
def test_urls_stage_beta(data_element):
    do_urls('stage', data_element, release = 'beta')

# cannot use this in parallel without something like
# https://github.com/pytest-dev/pytest-xdist/issues/385
# def test_hashes():
#     for key, val in output_data.items():
#         assert val.prod_hash == val.stage_hash, "md5sum mismatch for page at {}".format(val.url)
