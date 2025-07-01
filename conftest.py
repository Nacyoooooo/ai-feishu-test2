import pytest
from api.base_api import APIClient
from dotenv import load_dotenv
import os

@pytest.fixture(scope='session', autouse=True)
def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()

from common.common_api import CommonAPI

@pytest.fixture(scope='module')
def common_api():
    """Fixture to provide common API instance"""
    base_url = os.getenv('API_BASE_URL', 'https://api.example.com')
    return CommonAPI(base_url)

@pytest.fixture(scope='function')
def clean_test_data():
    """Fixture to clean up test data after each test"""
    yield
    # Add cleanup logic here if needed