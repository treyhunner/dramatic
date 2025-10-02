"""
Utilities to print text to the screen dramatically.

To print dramatically:

    dramatic.print("This will print character-by-character")

To temporarily change all output to display dramatically:

    with dramatic.output:
        print("ALL output will display dramatically.")
        print("Anything written to sys.stdout or sys.stderr that is.")

To print dramatically whenever a function runs:

    @dramatic.output
    def main():
        print("ALL output will display dramatically.")
        print("Even things printed by other functions we call.")

To print dramatically for the rest of your Python process:

    dramatic.start()
"""

from argparse import ArgumentParser
import code
from contextlib import ContextDecorator, ExitStack, suppress
from fractions import Fraction
from importlib.util import find_spec
from io import TextIOWrapper
from pathlib import Path
import runpy
from site import getsitepackages, getusersitepackages
import sys
from textwrap import dedent
from time import perf_counter, sleep

__version__ = "0.5.0"
__all__ = []  # Disable "from dramatic import *"
_DEFAULT_SPEED = 75


class DramaticTextIOWrapper(TextIOWrapper):
    """
    Text file to "dramatically" write to a buffer.

    This writes to the underlying buffer character-by-character, pausing
    in between each character.

    The speed argument controls how many characters per second to write.
    """

    def __init__(self, *args, speed=None, **kwargs):
        if speed is None:
            speed = _DEFAULT_SPEED
        self.no_sleep_until = perf_counter()
        self.speed = speed
        super().__init__(*args, **kwargs)

    def __del__(self):
        """Detach the buffer so it won't close as we're deleted."""
        with suppress(ValueError):  # In case buffer is already closed
            self.detach()
        super().__del__()

    def write(self, string):
        """
        Write dramatically, but only if this is a terminal device.

        If Ctrl-C is pressed, the remaining text will print immediately.
        """
        if self.isatty():
            for char in string:
                before = perf_counter()
                super().write(char)
                super().flush()
                if before >= self.no_sleep_until:
                    try:
                        elapsed = perf_counter() - before
                        sleep_duration = 1 / self.speed - elapsed
                        if sleep_duration > 0:
                            sleep(sleep_duration)
                    except KeyboardInterrupt:
                        self.no_sleep_until = perf_counter() + 0.5
        else:
            super().write(string)

    def __repr__(self):
        return f"{type(self).__name__}({self.buffer})"


class _DramaticPatcher(ContextDecorator):
    """
    Monkey patch sys.stdout or sys.stderr to print dramatically.

    This replaces stdout/stderr (based on the stream name given) with
    a DramaticTextIOWrapper that wraps around the stream's byte buffer.

    The speed argument controls how many characters per second to write.
    """

    def __init__(self, stream_name, speed=None):
        self.name = stream_name
        self.old = getattr(sys, stream_name)
        self.new = None
        self.speed = speed

    def __enter__(self):
        self.old = getattr(sys, self.name)
        if not isinstance(self.old, DramaticTextIOWrapper):
            self.new = DramaticTextIOWrapper(self.old.buffer, speed=self.speed)
            setattr(sys, self.name, self.new)
        return self.new

    def __exit__(self, *args):
        setattr(sys, self.name, self.old)
        self.new = None


class _CombinedDramaticPatcher(ContextDecorator):
    """
    Monkey patch both sys.stdout and sys.stderr to print dramatically.

    This can be used as a context manager or as a decorator.

    The speed argument controls how many characters per second to write.
    """

    def __init__(self, speed=None):
        self.speed = speed
        self.stack = ExitStack()

    def at_speed(self, speed):
        """Control the characters per second when printing."""
        return type(self)(speed)

    def __enter__(self):
        self.stack.enter_context(_DramaticPatcher("stdout", speed=self.speed))
        self.stack.enter_context(_DramaticPatcher("stderr", speed=self.speed))

    def __exit__(self, *args):
        self.stack.close()


def start(*, speed=None, stdout=True, stderr=True):
    """
    Monkey patch sys.stdout and sys.stderr to print dramatically.

    The speed argument controls how many characters per second to write.
    """
    if stdout:
        global _original_stdout
        _original_stdout = sys.stdout
        sys.stdout = DramaticTextIOWrapper(sys.stdout.buffer, speed=speed)
    if stderr:
        global _original_stderr
        _original_stderr = sys.stderr
        sys.stderr = DramaticTextIOWrapper(sys.stderr.buffer, speed=speed)


def stop():
    """Undo any dramatic monkey patching of sys.stdout or sys.stderr."""
    if isinstance(sys.stdout, DramaticTextIOWrapper):
        sys.stdout = _original_stdout
    if isinstance(sys.stderr, DramaticTextIOWrapper):
        sys.stderr = _original_stderr


def parse_arguments():
    parser = ArgumentParser(description="Run Python, but dramatically", add_help=False)
    parser.add_argument(
        "--max-drama",
        action="store_true",
        help="Monkey patch Python so ALL programs run dramatically",
    )
    parser.add_argument(
        "--min-drama",
        action="store_true",
        help="Undo --max-drama",
    )
    parser.add_argument(
        "-m",
        metavar="mod",
        dest="module",
        help="run library module as a script",
    )
    parser.add_argument(
        "--speed",
        metavar="speed",
        default=_DEFAULT_SPEED,
        type=Fraction,
        help=f"characters per second (default: {_DEFAULT_SPEED})",
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="program read from script file",
    )
    if sys.argv[1:2] in (["--help"], ["-h"]):
        parser.print_help()
        sys.exit()
    return parser.parse_known_args()


def repl_banner():
    version = sys.version.replace("\n", "")
    return dedent(f"""
        Python {version} on {sys.platform}
        Type "help", "copyright", "credits" or "license" for more information.
    """).strip("\n")


def main():
    args, unknown = parse_arguments()
    start(speed=args.speed)

    # Monkey patch Python so all Python programs to print dramatically
    if args.max_drama:
        site_packages = Path(getsitepackages()[0])
        if (Path(sys.prefix) / "pyvenv.cfg").exists():
            print("Virtual environment detected.")
            print("Make all Python scripts in this venv run dramatically?")
        else:
            site_packages = Path(getusersitepackages())
            print("Make all global Python scripts run dramatically?")
        dramatic_py = site_packages / "_dramatic.py"
        dramatic_pth = site_packages / "_dramatic.pth"
        print("Running with --min-drama will undo this operation.")
        try:
            if input("Are you sure? [y/N] ").casefold() != "y":
                sys.exit("Okay. No drama.")
        except KeyboardInterrupt:
            sys.exit("\nOkay. No drama.")
        site_packages.mkdir(parents=True, exist_ok=True)
        dramatic_py.write_text(Path(__file__).read_text())
        print(f"Wrote file {dramatic_py}")
        dramatic_pth.write_text("import _dramatic; _dramatic.start()\n")
        print(f"Wrote file {dramatic_pth}")
        print("To undo run:")
        print(f"{sys.executable} -m _dramatic --min-drama")
        sys.exit(0)

    # Un-monkey patch Python to stop printing dramatically by default
    if args.min_drama:
        site_packages = Path(getsitepackages()[0])
        if (Path(sys.prefix) / "pyvenv.cfg").exists():
            print("Virtual environment detected.")
            print("Removing dramatic.pth from virtual environment.")
        else:
            site_packages = Path(getusersitepackages())
            print("Removing dramatic.pth from global environment.")
        dramatic_py = site_packages / "_dramatic.py"
        dramatic_pth = site_packages / "_dramatic.pth"
        try:
            dramatic_pth.unlink()
        except FileNotFoundError:
            print(f"File not found: {dramatic_pth}")
        else:
            print(f"Deleted file {dramatic_pth}")
        try:
            dramatic_py.unlink()
        except FileNotFoundError:
            print(f"File not found: {dramatic_py}")
        else:
            print(f"Deleted file {dramatic_py}")
        print("No drama.")
        sys.exit(0)

    # Run the given Python module
    if args.module:
        try:
            spec = find_spec(args.module)
        except ModuleNotFoundError as e:
            sys.exit(
                f"Error while finding module specification for {args.module!r}"
                + f" ({type(e).__name__}: {e})"
            )
        if not spec or not spec.origin:
            sys.exit(f"No module named {args.module}")
        index = sys.argv.index(args.module)
        sys.argv = [spec.origin, *sys.argv[index + 1 :]]
        runpy.run_module(args.module, run_name="__main__")

    # Run the given Python file
    elif args.file:
        sys.argv = [args.file, *unknown]
        runpy.run_path(args.file, run_name="__main__")

    # Start a Python REPL
    else:
        code.interact(
            local={"__name__": "__main__", "__builtins__": __builtins__},
            banner=repl_banner(),
            exitmsg="",
        )


output = _CombinedDramaticPatcher()
print = output(print)


if __name__ == "__main__":
    main()
