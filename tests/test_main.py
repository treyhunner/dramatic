from contextlib import contextmanager, redirect_stdout
from io import StringIO
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile
from textwrap import dedent

import dramatic

from .utils import (
    byte_list,
    patch_stdout,
    patch_stderr,
    assert_write_and_sleep_calls,
    get_mock_args,
)


@contextmanager
def patch_args(args):
    old_argv, sys.argv = sys.argv, [dramatic.__file__, *args]
    try:
        yield
    finally:
        sys.argv = old_argv


@contextmanager
def patch_stdin(text):
    old_stdin, sys.stdin = sys.stdin, StringIO(text)
    try:
        yield sys.stdin
    finally:
        sys.stdin = old_stdin


def test_help(mocks):
    """Check --help output"""
    with patch_args(["--help"]):
        with redirect_stdout(StringIO()) as stdout:
            try:
                dramatic.main()
            except SystemExit as error:
                assert not error.args or not error.args[0]
    # Python 3.8 and below used "optional arguments"
    output = stdout.getvalue().replace("optional arguments", "options")
    assert output == dedent("""
        usage: dramatic.py [-m mod] [--speed speed] [file]

        Run Python, but dramatically

        positional arguments:
          file           program read from script file

        options:
          -m mod         run library module as a script
          --speed speed  characters per second (default: 75)
    """).lstrip("\n")


def test_dramatic_repl(mocks):
    with patch_args([]):
        with patch_stdin("2 + 4\nexit()\n"):
            with patch_stdout(mocks), patch_stderr(mocks):
                try:
                    dramatic.main()
                except SystemExit as error:
                    assert not error.args or not error.args[0]
    assert get_mock_args(mocks.stdout_write) == byte_list(">>> 6\n>>> ")
    stderr_writes = get_mock_args(mocks.stderr_write)
    assert stderr_writes[:9] == byte_list("Python 3.")
    assert stderr_writes[-71:] == byte_list(
        'Type "help", "copyright", "credits" or "license" for more information.\n'
    )
    assert len(mocks.clock.sleeps) > 100


def test_hello_module(mocks):
    """Run the __hello__ dramatically."""
    with patch_args(["-m", "mimetypes", "-e", "text/markdown"]):
        with patch_stdout(mocks):
            dramatic.main()
    assert_write_and_sleep_calls(mocks, ".md\n")


def test_invalid_modules(mocks):
    with patch_args(["-m", "missing"]):
        with patch_stdout(mocks):
            try:
                dramatic.main()
            except SystemExit as error:
                assert str(error) == "No module named missing"

    with patch_args(["-m", "missing.py"]):
        with patch_stdout(mocks):
            try:
                dramatic.main()
            except SystemExit as error:
                assert (
                    str(error)
                    == "Error while finding module specification "
                    + "for 'missing.py' (ModuleNotFoundError: No module named "
                    + "'missing')"
                )


def test_file(mocks):
    with NamedTemporaryFile(mode="wt", delete=False) as file:
        file.write('print("Hiya!")\n')
    path = Path(file.name)
    try:
        with patch_args([str(path)]):
            with patch_stdout(mocks):
                dramatic.main()
        assert_write_and_sleep_calls(mocks, "Hiya!\n")
    finally:
        path.unlink()
