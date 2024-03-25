import sys

import dramatic

from .utils import (
    assert_write_and_sleep_calls,
    byte_list,
    get_mock_args,
    patch_stderr,
    patch_stdout,
)


def test_start_and_stop_with_print(mocks):
    dramatic.start()
    with patch_stdout(mocks):
        print("This", "is", "dramatic", sep="---", end="!\n")
    assert_write_and_sleep_calls(mocks, "This---is---dramatic!\n")

    mocks.clock.reset()

    dramatic.stop()
    with patch_stdout(mocks):
        print("This", "is", "boring", flush=False)
        sys.stdout.flush()
    assert b"".join(get_mock_args(mocks.stdout_write)) == b"This is boring\n"
    assert len(mocks.stdout_write.mock_calls) < 7
    assert len(mocks.clock.sleeps) == 0


def test_writing_standard_output_dramatically(mocks):
    dramatic.start()
    with patch_stdout(mocks):
        sys.stdout.write("Dramatic?\n")
    dramatic.stop()
    assert_write_and_sleep_calls(mocks, "Dramatic?\n")


def test_default_speed(mocks):
    dramatic.start()
    with patch_stdout(mocks):
        sys.stdout.write("Dramatic?\n")
    dramatic.stop()
    assert mocks.clock.sleeps == [1 / 75] * 10


def test_custom_speed(mocks):
    dramatic.start(speed=30)
    with patch_stdout(mocks):
        sys.stdout.write("Dramatic?\n")
    dramatic.stop()
    assert mocks.clock.sleeps == [1 / 30] * 10


def test_writing_standard_error_dramatically(mocks):
    dramatic.start()
    with patch_stderr(mocks):
        sys.stderr.write("Dramatic?\n")
    dramatic.stop()
    assert get_mock_args(mocks.stderr_write) == byte_list("Dramatic?\n")
    assert len(mocks.clock.sleeps) == 10, "Sleeps between each letter"
    assert [c[0] for c in mocks.mock_calls] == (
        ["stderr_write", "sleep"] * 10
    ), "Wrote to stderr, slept, and repeated 10 times"


def test_stdout_and_stderr_are_separate(mocks):
    dramatic.start()
    with patch_stdout(mocks), patch_stderr(mocks):
        sys.stdout.write("123\n")
        sys.stderr.write("456\n")
        print("789")
    dramatic.stop()
    assert get_mock_args(mocks.stdout_write) == byte_list("123\n789\n")
    assert get_mock_args(mocks.stderr_write) == byte_list("456\n")
    assert [c[0] for c in mocks.mock_calls] == (
        ["stdout_write", "sleep"] * 4
        + ["stderr_write", "sleep"] * 4
        + ["stdout_write", "sleep"] * 4
    ), "Wrote to stdout, then stderr, then stdout"


def test_start_just_stdout(mocks):
    dramatic.start(stderr=False)
    with patch_stdout(mocks), patch_stderr(mocks):
        sys.stdout.write("123\n")
        sys.stderr.write("456\n")
        print("789")
    dramatic.stop()
    assert get_mock_args(mocks.stdout_write) == byte_list("123\n789\n")
    assert get_mock_args(mocks.stderr_write) == [
        b"456\n"
    ], "Standard error characters not written separately"
    assert [c[0] for c in mocks.mock_calls] == (
        ["stdout_write", "sleep"] * 4 + ["stderr_write"] + ["stdout_write", "sleep"] * 4
    ), "Wrote to stdout, then stderr, then stdout"


def test_start_just_stderr(mocks):
    dramatic.start(stdout=False)
    with patch_stdout(mocks), patch_stderr(mocks):
        sys.stdout.write("123\n")
        sys.stderr.write("456\n")
        print("789")
    dramatic.stop()
    assert get_mock_args(mocks.stdout_write) == [
        b"123\n",
        b"789",
        b"\n",
    ], "Standard output characters not written separately"
    assert get_mock_args(mocks.stderr_write) == byte_list("456\n")
    assert [c[0] for c in mocks.mock_calls] == (
        ["stdout_write"] + ["stderr_write", "sleep"] * 4 + ["stdout_write"] * 2
    ), "Wrote to stdout, then stderr, then stdout"


def test_stop_works_properly(mocks):
    dramatic.start()
    with patch_stdout(mocks), patch_stderr(mocks):
        sys.stdout.write("123\n")
        sys.stderr.write("456\n")
        print("789")
    dramatic.stop()

    mocks.clock.reset()

    with patch_stdout(mocks), patch_stderr(mocks):
        print("Output", flush=True)
        sys.stderr.write("Error\n")
        sys.stderr.flush()
    assert b"".join(get_mock_args(mocks.stdout_write)) == b"Output\n"
    assert len(mocks.stdout_write.mock_calls) < 3
    assert get_mock_args(mocks.stderr_write) == [b"Error\n"]
    assert len(mocks.clock.sleeps) == 0
