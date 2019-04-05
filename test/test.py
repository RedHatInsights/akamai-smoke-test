from urllib3.util import connection
import requests
import hashlib
from dotdict import DotDict
from lxml import html

baseurl = 'https://cloud.redhat.com'
cookies = { 'x-rh-insights-alpha': 'flipmodesquadisthegreatest' }

data = [

    # dashboard
    DotDict({ 'url': '/rhel/dashboard/', 'app': 'dashboard' }),
    DotDict({ 'url': '/rhel/dashboard',  'app': 'dashboard' }),

    # rhel inventory
    DotDict({ 'url': '/rhel/inventory/7d5b12fd-a45f-48c6-8921-5da2423b6be8/vulnerabilities', 'app': 'inventory' }),
    DotDict({ 'url': '/rhel/inventory', 'app': 'inventory' }),

    # insights inventory
    DotDict({ 'url': '/insights/inventory/7d5b12fd-a45f-48c6-8921-5da2423b6be8/vulnerabilities', 'app': 'inventory' }),
    DotDict({ 'url': '/insights/inventory', 'app': 'inventory' }),

    # insights
    DotDict({ 'url': '/insights/rules/', 'app': 'insights' }),
    DotDict({ 'url': '/insights/rules', 'app': 'insights' }),
    DotDict({ 'url': '/insights/actions/', 'app': 'insights' }),
    DotDict({ 'url': '/insights/actions', 'app': 'insights' }),
    DotDict({ 'url': '/insights/', 'app': 'insights' }),
    DotDict({ 'url': '/insights/', 'app': 'insights' }),

    # landing
    DotDict({ 'url': '/', 'app': 'landing' })
]

output_data = {}

def t(path):
    return baseurl + path

def do_urls(env):
    for e in data:
        r = requests.get(t(e.url), cookies=cookies)
        tree = html.fromstring(r.content)
        things = tree.xpath('//script[@type="text/javascript"]')

        for thing in things:
            if 'src' in thing.attrib:
                src = thing.attrib['src']
                if 'App.js' in src:
                    expected = '/apps/' + e.app
                    assert expected in src, "unexpected app id at {}".format(e.url)
                    if e.url not in output_data:
                        output_data[e.url] = DotDict({ 'url': e.url, })
                    output_data[e.url][env] = hashlib.md5(r.text.encode('utf-8')).hexdigest()



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
        assert val.prod == val.stage, "md5sum mismatch for page at https://cloud.redhat.com{}".format(key)
