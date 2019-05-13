import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--data", action="store", default="./data/main.yml", help="which data file to use"
    )
    parser.addoption("--app", action="store", help="test only a single app")
