from contextlib import contextmanager
import sys
from unittest.mock import patch


@contextmanager
def patch_stdout(mocks):
    """Monkey patch sys.stdout.buffer.write and attach to mocks object."""
    with patch.object(sys.stdout.buffer, "write") as write:
        mocks.attach_mock(write, "stdout_write")
        try:
            yield mocks.stdout_write
        finally:
            # Remove all write calls with no written data.
            mocks.stdout_write.mock_calls[:] = [
                c for c in mocks.stdout_write.mock_calls if c.args != (b"",)
            ]


@contextmanager
def patch_stderr(mocks):
    """Monkey patch sys.stderr.buffer.write and attach to mocks object."""
    with patch.object(sys.stderr.buffer, "write") as write:
        mocks.attach_mock(write, "stderr_write")
        try:
            yield mocks.stderr_write
        finally:
            # Remove all write calls with no written data.
            mocks.stderr_write.mock_calls[:] = [
                c for c in mocks.stderr_write.mock_calls if c.args != (b"",)
            ]


def get_mock_args(mock_function):
    r"""Convert \n\r to \n in stdout/stderr mock callse."""
    return [c.args[0].replace(b"\r", b"") for c in mock_function.mock_calls]


def assert_write_and_sleep_calls(mocks, expected_writes):
    n = len(expected_writes)
    assert get_mock_args(mocks.stdout_write) == [
        c.encode() for c in expected_writes
    ], "Each character was written separately"
    assert len(mocks.clock.sleeps) == n, "Sleeps between each letter"
    assert [c[0] for c in mocks.mock_calls][: n * 2 - 1] == (
        ["stdout_write", "sleep"] * n
    )[: n * 2 - 1], f"Wrote to stdout, slept, and repeated {n} times"


class Clock:
    """Fake version of time.perf_counter."""

    def __init__(self):
        self.sleeps = []

    def __call__(self):
        return sum(self.sleeps)

    def reset(self):
        self.sleeps.clear()

    def increment(self, count):
        self.sleeps.append(count)
