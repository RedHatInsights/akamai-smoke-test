import yaml

baseurl = 'https://cloud.redhat.com'

class Utils():
    def getData(path = './data/main.yml'):
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def getFlatData(data):
        ret = []
        for key in data:
            for val in data[key]:
                ret.append((key, val))
        return ret

    def getUrl(path, release='stable'):
        if release == 'beta':
            return baseurl + '/beta' + path
        return baseurl + path

    def getNetStoragePath(appname, release='stable'):
        if release == 'beta':
            return '/822386/beta/apps/{}/index.html'.format(appname)
        return  '/822386/apps/{}/index.html'.format(appname)

    def extractNamedInfoHeaderValue(string, name):
        name_str = 'name={}'.format(name)
        for i in string.split(','):
            if name_str in i:
                name, value = tuple(i.split(';'))
                n, k, v = tuple(i.split('='))
                return v
        return True

if __name__ == '__main__':
    header_str = 'name=AKA_PM_BASEDIR; value=, name=AKA_PM_CACHEABLE_OBJECT; value=true, name=AKA_PM_FWD_URL; value=/822386/beta/apps/insights/index.html, name=AKA_PM_NETSTORAGE_ROOT; value=/822386, name=AKA_PM_PREFETCH_ON; value=true, name=AKA_PM_SR_ENABLED; value=false, name=AKA_PM_TD_ENABLED; value=false, name=AKA_PM_TD_MAP_PREFIX; value=ch2, name=ANS_PEARL_VERSION; value=0.9.0, name=ENABLE_SD_POC; value=yes, name=FASTTCP_RENO_FALLBACK_DISABLE_OPTOUT; value=on, name=NL_16801_REDHATCOMWAFBYPASS_NAME; value=RedHat.com WAF Bypass, name=NL_16802_REDHATCOMWHITELIST_NAME; value=RedHat.com Whitelist, name=NL_2580_BLACKLIST_NAME; value=Black List, name=NL_27979_REDHATNETWORKADDRESSLIS_NAME; value=Red Hat Network Address List, name=OVERRIDE_HTTPS_IE_CACHE_BUST; value=all, name=SEC_CLIENT_IP_ASNUM_MASK_SIZE; value=64, name=SEC_XFF_ASNUM_MASK_SIZE; value=64, name=TAP_GUID; value=, name=TAP_KEY_ID; value=, name=TCP_OPT_APPLIED; value=low, name=UA_IDENTIFIER; value=python-requests%2f2.21.0; full_location_id=User-Agent'

    extracted_str = Utils.extractNamedInfoHeaderValue(header_str, 'AKA_PM_FWD_URL')
    assert extracted_str == '/822386/beta/apps/insights/index.html'
