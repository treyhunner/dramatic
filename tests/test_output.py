import sys

import dramatic

from .utils import (
    patch_stdout,
    patch_stderr,
    assert_write_and_sleep_calls,
    get_mock_args,
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


def test_writing_standard_error_dramatically(mocks):
    with dramatic.output:
        with patch_stderr(mocks):
            sys.stderr.write("Dramatic?\n")
    assert get_mock_args(mocks.stderr_write) == [
        c.encode() for c in "Dramatic?\n"
    ], "Each character was written separately"
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
    assert get_mock_args(mocks.stdout_write) == [
        c.encode() for c in "123\n789\n"
    ], "Standard output characters written separately"
    assert get_mock_args(mocks.stderr_write) == [
        c.encode() for c in "456\n"
    ], "Standard error characters written separately"
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
