import pytest
from dotenv import load_dotenv

# Load environment variables from .env.test file
load_dotenv(dotenv_path=".env.test")


@pytest.fixture(scope='session', autouse=True)
def load_env():
    # This fixture ensures the environment variables are loaded for all tests
    load_dotenv(dotenv_path=".env.test")
