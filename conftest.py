import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--data", action="store", default="./data/supplemental.yml", help="which supplemental data file to use"
    )
    parser.addoption(
        "--release", action="store", default="stable", help="which release to test ('stable', 'beta', or 'all')"
    )
    parser.addoption("--app", action="store", help="test only a single app")
