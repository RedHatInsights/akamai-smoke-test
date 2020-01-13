import dns.resolver
import yaml
import urllib3
from urllib3.util import connection

baseurl = "https://cloud.redhat.com"


_orig_create_connection = connection.create_connection
http = urllib3.PoolManager()


class ip_context(object):
    def __init__(self, ip):
        self.ip = ip

    def __enter__(self):
        def my_create_connection(address, *args, **kwargs):
            host, port = address
            return _orig_create_connection((self.ip, port), *args, **kwargs)

        connection.create_connection = my_create_connection

    def __exit__(self, a, b, c):
        connection.create_connection = _orig_create_connection

def getAdditionalData(path="./data/supplemental.yml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def getMainData(release="stable"):
    apps = {}
    if release in ["stable", "all"]:
        apps = yaml.safe_load(http.request('GET', 'https://cloud.redhat.com/config/main.yml').data.decode('utf-8'))
        for app_key in (x for x in apps.keys() if not hasattr(apps[x], "disabled_on_prod")):
            apps[app_key].update({"releases": ["stable"]})
    if release in ["beta", "all"]:
        beta_apps = yaml.safe_load(http.request('GET', 'https://cloud.redhat.com/beta/config/main.yml').data.decode('utf-8'))
        for app_key in (x for x in beta_apps.keys() if not hasattr(beta_apps[x], "disabled_on_prod")):
            if app_key in apps:
                apps[app_key]["releases"].append("test")
            else:
                apps[app_key] = beta_apps[app_key]
                apps[app_key].update({"releases": ["test"]})
    return apps

def getStageIp():
    cname = "cloud.redhat.com"
    for i in range(0, 10):
        try:
            answers = dns.resolver.query(cname, "CNAME")
            cname = str(answers[0])
        except Exception as e:
            print(e)
            break
        if i == 10:
            raise Exception("Too many loops looking for last cname")
    cname = cname.replace(".net", "-staging.net")
    return str(dns.resolver.query(cname)[0])


def getProdIP():
    return str(dns.resolver.query("cloud.redhat.com")[0])


def getFlatData(main_data, supplemental_data):
    ret = []
    # For every app that has frontend paths
    for key in (
        x
        for x in main_data.keys()
        if (
            "frontend" in main_data[x]
            and "paths" in main_data[x]["frontend"]
            and "app_base" not in main_data[x]["frontend"]
        )
    ):
        app = main_data[key]
        # For every frontend path listed in the main data
        for fe_path in app["frontend"]["paths"]:
            skip_test = False
            # If defined in supplemental file...
            # For every defined supplemental path, append to the end of the basic frontend paths
            if key in supplemental_data:
                if 'skip' in supplemental_data[key] and supplemental_data[key]['skip']:
                    skip_test = True
                elif 'additions' in supplemental_data[key]:
                    for val in supplemental_data[key]['additions']:
                        ret.append((key, fe_path + val, main_data[key]["releases"]))

            # Add the basic path, with and without the trailing slash
            if skip_test == False:
                for release in main_data[key]["releases"]:
                    ret.append((key, fe_path, release))
                    ret.append((key, fe_path + "/", release))
    return ret


def getUrl(path, release="stable"):
    if release == "beta":
        return baseurl + "/beta" + path
    return baseurl + path


def getNetStoragePath(appname, release="stable", expected_status=200):
    filename = "index.html" if expected_status == 200 else "404.html"
    if release == "beta":
        return "/822386/beta/apps/{}/{}".format(appname, filename)
    return "/822386/apps/{}/{}".format(appname, filename)


def extractNamedInfoHeaderValue(string, name):
    name_str = "name={}".format(name)
    for i in string.split(","):
        if name_str in i:
            name, value = tuple(i.split(";"))
            n, k, v = tuple(i.split("="))
            return v
    return True


IPS = {"prod": getProdIP(), "stage": "184.31.98.175"}

headers = {"Pragma": "akamai-x-get-extracted-values"}

if __name__ == "__main__":
    header_str = (
        "name=AKA_PM_BASEDIR; value=, name=AKA_PM_CACHEABLE_OBJECT; value=true, ",
        "name=AKA_PM_FWD_URL; value=/822386/beta/apps/insights/index.html, ",
        "name=AKA_PM_NETSTORAGE_ROOT; value=/822386, name=AKA_PM_PREFETCH_ON; value=true, ",
        "name=AKA_PM_SR_ENABLED; value=false, name=AKA_PM_TD_ENABLED; value=false, ",
        "name=AKA_PM_TD_MAP_PREFIX; value=ch2, name=ANS_PEARL_VERSION; value=0.9.0, ",
        "name=ENABLE_SD_POC; value=yes, name=FASTTCP_RENO_FALLBACK_DISABLE_OPTOUT; value=on, ",
        "name=NL_16801_REDHATCOMWAFBYPASS_NAME; value=RedHat.com WAF Bypass, ",
        "name=NL_16802_REDHATCOMWHITELIST_NAME; value=RedHat.com Whitelist, ",
        "name=NL_2580_BLACKLIST_NAME; value=Black List, ",
        "name=NL_27979_REDHATNETWORKADDRESSLIS_NAME; value=Red Hat Network Address List, ",
        "name=OVERRIDE_HTTPS_IE_CACHE_BUST; value=all, ",
        "name=SEC_CLIENT_IP_ASNUM_MASK_SIZE; value=64, name=SEC_XFF_ASNUM_MASK_SIZE; value=64, ",
        "name=TAP_GUID; value=, name=TAP_KEY_ID; value=, name=TCP_OPT_APPLIED; value=low, ",
        "name=UA_IDENTIFIER; value=python-requests%2f2.21.0; full_location_id=User-Agent",
    )

    extracted_str = extractNamedInfoHeaderValue(header_str, "AKA_PM_FWD_URL")
    assert extracted_str == "/822386/beta/apps/insights/index.html"
