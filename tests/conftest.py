import pytest

def pytest_addoption(parser):
    parser.addoption('--stage', action='store_true', help='run stage tests')
    parser.addoption('--prod', action='store_true', help='run prod tests')

def pytest_runtest_setup(item):
    if 'stage' in item.keywords and not item.config.getvalue('stage'):
        pytest.skip('need --stage option to run')
    if 'prod' in item.keywords and not item.config.getvalue('prod'):
        pytest.skip('need --prod option to run')
