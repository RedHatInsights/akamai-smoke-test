import pytest
import globals

def pytest_addoption(parser):
    parser.addoption('--stage', action='store_true', help='run stage tests')
    parser.addoption('--stageip', action='store', help='ip address of stage env')
    parser.addoption('--prod', action='store_true', help='run prod tests')
    parser.addoption('--prodip', action='store', help='ip address of prod env')
    parser.addoption('--data', action='store', default='./data/main.yml', help='which data file to use')
    parser.addoption('--app', action='store', help='test only a single app')

def pytest_runtest_setup(item):
    if 'stage' in item.keywords:
        if not item.config.getvalue('stage'):
            pytest.skip('need --stage option to run')
    if 'prod' in item.keywords:
        if not item.config.getvalue('prod'):
            pytest.skip('need --prod option to run')


def pytest_configure(config):
    if config.getvalue('stage'):
        globals.STAGE_IP = config.getvalue('stageip')
    if config.getvalue('prod'):
        globals.PROD_IP = config.getvalue('prodip')
