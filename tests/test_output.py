from contextlib import redirect_stdout
import sys
from tempfile import NamedTemporaryFile

import pytest

import dramatic

from .utils import (
    assert_write_and_sleep_calls,
    byte_list,
    get_mock_args,
    patch_stderr,
    patch_stdout,
)


def test_output_with_print(mocks):
    with dramatic.output:
        with patch_stdout(mocks):
            print("This", "is", "dramatic", sep="---", end="!\n")
        assert_write_and_sleep_calls(mocks, "This---is---dramatic!\n")

    mocks.clock.reset()

    with patch_stdout(mocks):
        print("This", "is", "boring", flush=False)
        sys.stdout.flush()
    assert b"".join(get_mock_args(mocks.stdout_write)) == b"This is boring\n"
    assert len(mocks.stdout_write.mock_calls) < 7
    assert len(mocks.clock.sleeps) == 0


def test_writing_standard_output_dramatically(mocks):
    with dramatic.output:
        with patch_stdout(mocks):
            sys.stdout.write("Dramatic?\n")
    assert_write_and_sleep_calls(mocks, "Dramatic?\n")


def test_writing_to_file(mocks):
    """No sleeping when stdout points to a real file."""
    with NamedTemporaryFile(mode="wt") as file:
        with redirect_stdout(file):
            with patch_stdout(mocks):
                with dramatic.output:
                    sys.stdout.write("Dramatic?\n")
                    sys.stdout.flush()
        assert get_mock_args(mocks.stdout_write) == [b"Dramatic?\n"]
        assert [c[0] for c in mocks.mock_calls] == ["stdout_write"]


def test_string_representation(mocks):
    with patch_stdout(mocks):
        with dramatic.output:
            print(sys.stdout)
    output = b"".join(get_mock_args(mocks.stdout_write)).decode()
    # File descriptor number can vary, so check the pattern instead
    assert output.startswith("DramaticTextIOWrapper(<_io.FileIO name=")
    assert " mode='rb+' closefd=True>)\n" in output
    assert [c[0] for c in mocks.mock_calls] == ["stdout_write", "sleep"] * 67


def test_default_speed(mocks):
    with dramatic.output:
        with patch_stdout(mocks):
            sys.stdout.write("Dramatic?\n")
    assert mocks.clock.sleeps == [1 / 75] * 10


def test_custom_speed(mocks):
    with dramatic.output.at_speed(30):
        with patch_stdout(mocks):
            sys.stdout.write("Dramatic?\n")
    assert mocks.clock.sleeps == [1 / 30] * 10


def test_control_c(mocks):
    with dramatic.output.at_speed(100):
        with patch_stdout(mocks):
            # Hit Ctrl-C (raise KeyboardInterrupt) after 5 characters
            mocks.clock.error_after = 5
            sys.stdout.write("Dramatic?\n")
            sys.stdout.write("Still undramatic\n")

            mocks.clock.reset()
            # No sleep until 1/100 * 5 + 500ms
            assert sys.stdout.no_sleep_until == pytest.approx(0.55, 0.001)
            sys.stdout.no_sleep_until = mocks.clock()

            # Hit Ctrl-C (raise KeyboardInterrupt) after 4 characters
            mocks.clock.error_after = 4
            sys.stdout.write("Hello!\n")

    assert [c[0] for c in mocks.mock_calls] == (
        ["stdout_write", "sleep"] * 5  # Slept 5 times successfully
        + ["stdout_write"] * 5  # No sleeps after Control-C
        + ["stdout_write"] * 17  # No sleeps after Control-C
        + ["stdout_write", "sleep"] * 4  # Slept 4 times successfully
        + ["stdout_write"] * 3  # No sleeps after Control-C
    )
    assert (
        b"".join(get_mock_args(mocks.stdout_write))
        == b"Dramatic?\nStill undramatic\nHello!\n"
    )


def test_writing_standard_error_dramatically(mocks):
    with dramatic.output:
        with patch_stderr(mocks):
            sys.stderr.write("Dramatic?\n")
    assert get_mock_args(mocks.stderr_write) == byte_list("Dramatic?\n")
    assert len(mocks.clock.sleeps) == 10, "Sleeps between each letter"
    assert [c[0] for c in mocks.mock_calls] == (
        ["stderr_write", "sleep"] * 10
    ), "Wrote to stderr, slept, and repeated 10 times"


def test_stdout_and_stderr_are_separate(mocks):
    with dramatic.output:
        with patch_stdout(mocks), patch_stderr(mocks):
            sys.stdout.write("123\n")
            sys.stderr.write("456\n")
            print("789")
    assert get_mock_args(mocks.stdout_write) == byte_list("123\n789\n")
    assert get_mock_args(mocks.stderr_write) == byte_list("456\n")
    assert [c[0] for c in mocks.mock_calls] == (
        ["stdout_write", "sleep"] * 4
        + ["stderr_write", "sleep"] * 4
        + ["stdout_write", "sleep"] * 4
    ), "Wrote to stdout, then stderr, then stdout"


def test_exiting_stops_monkey_patching(mocks):
    with dramatic.output:
        with patch_stdout(mocks), patch_stderr(mocks):
            sys.stdout.write("123\n")
            sys.stderr.write("456\n")
            print("789")

    mocks.clock.reset()

    with patch_stdout(mocks), patch_stderr(mocks):
        print("Output", flush=True)
        sys.stderr.write("Error\n")
        sys.stderr.flush()
    assert b"".join(get_mock_args(mocks.stdout_write)) == b"Output\n"
    assert len(mocks.stdout_write.mock_calls) < 3
    assert get_mock_args(mocks.stderr_write) == [b"Error\n"]
    assert len(mocks.clock.sleeps) == 0


@pytest.mark.filterwarnings("error::pytest.PytestUnraisableExceptionWarning")
def test_cleanup_with_closed_buffer(mocker):
    """Test that __del__ doesn't raise error when buffer is already closed."""
    import gc
    from tempfile import TemporaryFile

    import dramatic

    # Create a real temporary file buffer
    temp_file = TemporaryFile(mode="w+b")

    # Create a DramaticTextIOWrapper with the temp buffer
    wrapper = dramatic.DramaticTextIOWrapper(temp_file, speed=75)

    # Close the underlying buffer to simulate cleanup race condition
    temp_file.close()

    # Mock the detach method to raise ValueError instead of actually detaching
    # This simulates what happens during cleanup when buffer is already closed
    wrapper.detach = mocker.Mock(side_effect=ValueError("I/O operation on closed file"))

    # Delete the wrapper and force garbage collection
    # If __del__ doesn't catch the ValueError, pytest will raise PytestUnraisableExceptionWarning as error
    del wrapper
    gc.collect()


def test_slow_write_does_not_raise_error(mocker):
    """Test that slow write operations don't cause negative sleep ValueError."""
    from .utils import Clock

    class SlowClock(Clock):
        """Clock that simulates slow write operations."""

        def __init__(self):
            super().__init__()
            self.call_count = 0
            self.time_per_write = 0.02  # 20ms per write operation

        def __call__(self):
            # Alternate between returning base time and base time + write overhead
            result = sum(self.sleeps)
            if self.call_count % 2 == 1:
                # Second call in a pair (after write) - add write overhead
                result += self.time_per_write
            self.call_count += 1
            return result

    slow_clock = SlowClock()
    mocker.patch("time.perf_counter", new=slow_clock)
    mocker.patch("time.sleep", side_effect=slow_clock.increment)

    # Reload module to pick up new patches
    from importlib import reload

    reload(dramatic)

    # With default speed of 75 chars/sec, target time is ~13.3ms per char
    # Our slow write takes 20ms, which would cause negative sleep without the fix
    with dramatic.output:
        with patch_stdout(mocker.Mock()):
            # This should not raise ValueError
            sys.stdout.write("Hi")

    # Verify that sleep was called only when duration was positive
    # With 20ms writes and 13.3ms target, no sleeps should occur
    assert len(slow_clock.sleeps) == 0
