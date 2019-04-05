import requests
import hashlib
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

def do_urls(env, release = 'stable'):
    for data_key, data_val in Utils.getData().items():
        for path in data_val:
            url = getUrl(path, release)
            r = requests.get(url, cookies=cookies)
            tree = html.fromstring(r.content)
            for thing in tree.xpath('//script[@type="text/javascript"]'):
                if 'src' in thing.attrib:
                    src = thing.attrib['src']
                    if 'App.js' in src:
                        expected = '/apps/' + data_key
                        assert expected in src, "unexpected app id at {}".format(url)
                        if path not in output_data:
                            output_data[path] = DotDict({ 'url': url })
                        output_data[path][env + '_hash'] = hashlib.md5(r.text.encode('utf-8')).hexdigest()

@modify_ip('104.68.244.28')
def test_stage_urls_prod():
    do_urls('prod')
    do_urls('prod', 'beta')

@modify_ip('23.201.3.166')
def test_urls_prod():
    do_urls('stage')
    do_urls('stage', 'beta')

def test_hashes():
    for key, val in output_data.items():
        assert val.prod_hash == val.stage_hash, "md5sum mismatch for page at {}".format(val.url)
