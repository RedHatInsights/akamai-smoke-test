import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--data", action="store", default="./data/additions.yml", help="which supplemental data file to use"
    )
    parser.addoption("--app", action="store", help="test only a single app")
