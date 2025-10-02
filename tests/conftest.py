from importlib import reload
import sys

import pytest

from .utils import Clock


@pytest.fixture
def mocks(mocker):
    """Monkey patch time.perf_counter and time.sleep."""
    clock = Clock()
    mocker.patch("time.perf_counter", new=clock)
    sleep_mock = mocker.patch("time.sleep", side_effect=clock.increment)

    mocks = mocker.Mock()
    mocks.attach_mock(sleep_mock, "sleep")
    mocks.clock = clock

    yield mocks
    clock.reset()


@pytest.fixture(autouse=True)
def reload_module(mocks):
    """Reload dramatic module after time patches have been applied."""
    import dramatic

    reload(dramatic)


@pytest.fixture(autouse=True)
def isatty_mocks(mocker):
    """Mock isatty to return True for stdout and stderr."""
    mocker.patch.object(sys.stdout.buffer, "isatty", return_value=True)
    mocker.patch.object(sys.stderr.buffer, "isatty", return_value=True)


@pytest.fixture(autouse=True)
def auto_flush():
    """Flush output streams before each test."""
    sys.stdout.flush()
    sys.stderr.flush()
