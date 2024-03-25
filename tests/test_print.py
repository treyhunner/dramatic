from io import StringIO

import dramatic

from .utils import assert_write_and_sleep_calls, patch_stdout


def test_print_single_argument(mocks):
    with patch_stdout(mocks):
        dramatic.print("Hiya")
    assert_write_and_sleep_calls(mocks, "Hiya\n")


def test_print_multiple_arguments(mocks):
    with patch_stdout(mocks):
        dramatic.print("Hello", "there")
    assert_write_and_sleep_calls(mocks, "Hello there\n")


def test_print_non_string_arguments(mocks):
    with patch_stdout(mocks):
        dramatic.print(1, 2, 3, 4)
    assert_write_and_sleep_calls(mocks, "1 2 3 4\n")


def test_print_custom_sep(mocks):
    with patch_stdout(mocks):
        dramatic.print("a", "b", sep="-")
    assert_write_and_sleep_calls(mocks, "a-b\n")


def test_print_custom_sep_and_end(mocks):
    with patch_stdout(mocks):
        dramatic.print("hello", "world", sep=",", end="!")
    assert_write_and_sleep_calls(mocks, "hello,world!")


def test_print_non_terminal_file(mocks):
    with patch_stdout(mocks):
        file = StringIO()
        dramatic.print("Hello, file!", file=file)
        assert file.getvalue() == "Hello, file!\n", "Should write to the file at once"
        mocks.stdout_write.assert_not_called()
        assert len(mocks.clock.sleeps) == 0
