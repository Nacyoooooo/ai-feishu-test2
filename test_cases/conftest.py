import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from api.base_api import APIClient
from dotenv import load_dotenv
import os

@pytest.fixture(scope='session', autouse=False)
def before_and_after():
    # before
    yield
    # after
