from urllib3.util import connection
import requests
import hashlib
from dotdict import DotDict
from lxml import html

from utils import Utils



baseurl = 'https://cloud.redhat.com'
cookies = { 'x-rh-insights-alpha': 'flipmodesquadisthegreatest' }

output_data = {}

def t(path):
    return baseurl + path

def do_urls(env):
    for data_key, data_val in Utils.getData().items():
        for path in data_val:
            r = requests.get(t(path), cookies=cookies)
            tree = html.fromstring(r.content)
            things = tree.xpath('//script[@type="text/javascript"]')
            for thing in things:
                if 'src' in thing.attrib:
                    src = thing.attrib['src']
                    if 'App.js' in src:
                        expected = '/apps/' + data_key
                        assert expected in src, "unexpected app id at {}".format(path)
                        if path not in output_data:
                            output_data[path] = DotDict()
                        output_data[path][env + '_hash'] = hashlib.md5(r.text.encode('utf-8')).hexdigest()

def modify_ip(ip):
    def decorator(func):
        def wrapper():
            _orig_create_connection = connection.create_connection
            def my_create_connection(address, *args, **kwargs):
                host, port = address
                return _orig_create_connection((ip, port), *args, **kwargs)
            connection.create_connection = my_create_connection
            func()
            connection.create_connection = _orig_create_connection
        return wrapper
    return decorator

@modify_ip('104.68.244.28')
def test_stage_urls_prod():
    do_urls('prod')

@modify_ip('23.201.3.166')
def test_urls_prod():
    do_urls('stage')

def test_hashes():
    for key, val in output_data.items():
        assert val.prod_hash == val.stage_hash, "md5sum mismatch for page at https://cloud.redhat.com{}".format(key)
