from _pytest.config import argparsing


def pytest_addoption(parser: argparsing.Parser) -> None:
    parser.addoption("--mongodb-host", default=None)
    parser.addoption("--mongodb-image", default="mongo:4.2")
