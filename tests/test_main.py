from contextlib import contextmanager, redirect_stdout
from io import StringIO
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile
from textwrap import dedent

import dramatic

from .utils import (
    assert_write_and_sleep_calls,
    byte_list,
    get_mock_args,
    patch_stderr,
    patch_stdout,
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
        usage: dramatic.py [--max-drama] [--min-drama] [-m mod] [--speed speed] [file]

        Run Python, but dramatically

        positional arguments:
          file           program read from script file

        options:
          --max-drama    Monkey patch Python so ALL programs run dramatically
          --min-drama    Undo --max-drama
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


def test_max_drama(mocks, mocker, tmp_path):
    mocker.patch("dramatic.getusersitepackages", return_value=str(tmp_path))
    mocker.patch("sys.prefix", return_value=str(tmp_path))

    dramatic_py = tmp_path / "_dramatic.py"
    dramatic_pth = tmp_path / "_dramatic.pth"

    with patch_args(["--max-drama"]):
        with patch_stdin("y\n"):
            with patch_stdout(mocks), patch_stderr(mocks):
                try:
                    dramatic.main()
                except SystemExit as error:
                    assert error.args == (0,)

    assert dramatic_py.exists()
    assert dramatic_pth.exists()

    dramatic_py_text = dramatic_py.read_text()
    assert "def start(" in dramatic_py_text

    dramatic_pth_text = dramatic_pth.read_text()
    assert dramatic_pth_text == "import _dramatic; _dramatic.start()\n"

    expected = dedent(
        f"""
        Make all global Python scripts run dramatically?
        Running with --min-drama will undo this operation.
        Are you sure? [y/N] Wrote file {dramatic_py}
        Wrote file {dramatic_pth}
        To undo run:
        {sys.executable} -m _dramatic --min-drama
        """
    ).lstrip("\n")
    assert b"".join(get_mock_args(mocks.stdout_write)) == expected.encode()
    assert_write_and_sleep_calls(mocks, expected)


def test_max_drama_no(mocks, mocker, tmp_path):
    mocker.patch("dramatic.getusersitepackages", return_value=str(tmp_path))
    mocker.patch("sys.prefix", return_value=str(tmp_path))

    dramatic_py = tmp_path / "_dramatic.py"
    dramatic_pth = tmp_path / "_dramatic.pth"

    with patch_args(["--max-drama"]):
        with patch_stdin("n\n"):
            with patch_stdout(mocks), patch_stderr(mocks):
                try:
                    dramatic.main()
                except SystemExit as error:
                    assert str(error) == "Okay. No drama."

    assert not dramatic_py.exists()
    assert not dramatic_pth.exists()

    expected = dedent(
        """
            Make all global Python scripts run dramatically?
            Running with --min-drama will undo this operation.
            Are you sure? [y/N] """
    ).lstrip("\n")
    assert b"".join(get_mock_args(mocks.stdout_write)) == expected.encode()
    assert_write_and_sleep_calls(mocks, expected)


def test_max_keyboard_interrupt(mocks, mocker, tmp_path):
    mocker.patch("dramatic.getusersitepackages", return_value=str(tmp_path))
    mocker.patch("sys.prefix", return_value=str(tmp_path))
    mocker.patch("builtins.input", side_effect=KeyboardInterrupt)

    dramatic_py = tmp_path / "_dramatic.py"
    dramatic_pth = tmp_path / "_dramatic.pth"

    with patch_args(["--max-drama"]):
        with patch_stdout(mocks), patch_stderr(mocks):
            try:
                dramatic.main()
            except SystemExit as error:
                assert str(error) == "\nOkay. No drama."

    assert not dramatic_py.exists()
    assert not dramatic_pth.exists()

    expected = dedent(
        """
            Make all global Python scripts run dramatically?
            Running with --min-drama will undo this operation.
            """
    ).lstrip("\n")
    assert b"".join(get_mock_args(mocks.stdout_write)) == expected.encode()
    assert_write_and_sleep_calls(mocks, expected)


def test_max_drama_virtual_environment(mocks, mocker, tmp_path):
    mocker.patch("dramatic.getsitepackages", return_value=[str(tmp_path)])

    dramatic_py = tmp_path / "_dramatic.py"
    dramatic_pth = tmp_path / "_dramatic.pth"

    with patch_args(["--max-drama"]):
        with patch_stdin("y\n"):
            with patch_stdout(mocks), patch_stderr(mocks):
                try:
                    dramatic.main()
                except SystemExit as error:
                    assert error.args == (0,)

    assert dramatic_py.exists()
    assert dramatic_pth.exists()

    dramatic_py_text = dramatic_py.read_text()
    assert "def start(" in dramatic_py_text

    dramatic_pth_text = dramatic_pth.read_text()
    assert dramatic_pth_text == "import _dramatic; _dramatic.start()\n"

    expected = dedent(
        f"""
        Virtual environment detected.
        Make all Python scripts in this venv run dramatically?
        Running with --min-drama will undo this operation.
        Are you sure? [y/N] Wrote file {dramatic_py}
        Wrote file {dramatic_pth}
        To undo run:
        {sys.executable} -m _dramatic --min-drama
        """
    ).lstrip("\n")
    assert b"".join(get_mock_args(mocks.stdout_write)) == expected.encode()
    assert_write_and_sleep_calls(mocks, expected)


def test_min_drama(mocks, mocker, tmp_path):
    mocker.patch("dramatic.getusersitepackages", return_value=str(tmp_path))
    mocker.patch("sys.prefix", return_value=str(tmp_path))

    dramatic_py = tmp_path / "_dramatic.py"
    dramatic_pth = tmp_path / "_dramatic.pth"
    dramatic_py.write_text("import _dramatic; _dramatic.start()\n")
    dramatic_pth.write_text("import _dramatic; _dramatic.start()\n")

    with patch_args(["--min-drama"]):
        with patch_stdout(mocks), patch_stderr(mocks):
            try:
                dramatic.main()
            except SystemExit as error:
                assert error.args == (0,)

    assert not dramatic_py.exists()
    assert not dramatic_pth.exists()

    expected = dedent(
        f"""
        Removing dramatic.pth from global environment.
        Deleted file {dramatic_pth}
        Deleted file {dramatic_py}
        No drama.
        """
    ).lstrip("\n")
    assert b"".join(get_mock_args(mocks.stdout_write)) == expected.encode()
    assert_write_and_sleep_calls(mocks, expected)


def test_min_drama_no_files(mocks, mocker, tmp_path):
    mocker.patch("dramatic.getusersitepackages", return_value=str(tmp_path))
    mocker.patch("sys.prefix", return_value=str(tmp_path))

    dramatic_py = tmp_path / "_dramatic.py"
    dramatic_pth = tmp_path / "_dramatic.pth"

    with patch_args(["--min-drama"]):
        with patch_stdout(mocks), patch_stderr(mocks):
            try:
                dramatic.main()
            except SystemExit as error:
                assert error.args == (0,)

    assert not dramatic_py.exists()
    assert not dramatic_pth.exists()

    expected = dedent(
        f"""
        Removing dramatic.pth from global environment.
        File not found: {dramatic_pth}
        File not found: {dramatic_py}
        No drama.
        """
    ).lstrip("\n")
    assert b"".join(get_mock_args(mocks.stdout_write)) == expected.encode()
    assert_write_and_sleep_calls(mocks, expected)


def test_min_drama_virtual_environment(mocks, mocker, tmp_path):
    mocker.patch("dramatic.getsitepackages", return_value=[str(tmp_path)])

    dramatic_py = tmp_path / "_dramatic.py"
    dramatic_pth = tmp_path / "_dramatic.pth"
    dramatic_py.write_text("import _dramatic; _dramatic.start()\n")
    dramatic_pth.write_text("import _dramatic; _dramatic.start()\n")

    with patch_args(["--min-drama"]):
        with patch_stdout(mocks), patch_stderr(mocks):
            try:
                dramatic.main()
            except SystemExit as error:
                assert error.args == (0,)

    assert not dramatic_py.exists()
    assert not dramatic_pth.exists()

    expected = dedent(
        f"""
        Virtual environment detected.
        Removing dramatic.pth from virtual environment.
        Deleted file {dramatic_pth}
        Deleted file {dramatic_py}
        No drama.
        """
    ).lstrip("\n")
    assert b"".join(get_mock_args(mocks.stdout_write)) == expected.encode()
    assert_write_and_sleep_calls(mocks, expected)
