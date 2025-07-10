import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))


@pytest.fixture(scope='session', autouse=False)
def before_and_after():
    # before
    yield
    # after
