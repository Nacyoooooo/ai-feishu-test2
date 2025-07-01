import pytest
from api.base_api import APIClient
from dotenv import load_dotenv
import os

@pytest.fixture(scope='session', autouse=True)
def before_and_after():
    # before
    yield
    # after
