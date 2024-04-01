Make your Python output dramatic 🎭
==================================

[![PyPI - Version](https://img.shields.io/pypi/v/dramatic.svg?label=PyPI)](https://pypi.org/project/dramatic/)
[![License](https://img.shields.io/pypi/l/dramatic?label=License)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/treyhunner/dramatic/actions/workflows/test.yml/badge.svg "Tests")](https://github.com/treyhunner/dramatic/actions?workflow=test)
[![Codecov](https://codecov.io/gh/treyhunner/dramatic/graph/badge.svg?token=e2Ah1TKt3g&label=Codecov "Coverage")](https://codecov.io/gh/treyhunner/dramatic)

The `dramatic` module includes utilities which cause all text output to display character-by-character (it prints *dramatically*).


![dramatic printing within a terminal](https://raw.githubusercontent.com/treyhunner/dramatic/main/screenshots/main.gif)

**Note**: This project is based on a [Python Morsels](https://www.pythonmorsels.com) exercise.
If you're working on that exercise right now, please don't look at the source code for this! 😉

<a href="https://www.pythonmorsels.com">
    <img src="https://raw.githubusercontent.com/treyhunner/dramatic/main/screenshots/python-morsels-logo.png" alt="an adorable snake taking a bite out of a cookie with the words Python Morsels next to it (Python Morsels logo)" width="250">
</a>


Usage 🥁
-------

The `dramatic` module is available on [PyPI][].
You can install it with `pip`:

```bash
$ python3 -m pip install dramatic
```

There are four primary ways to use the utilities in the `dramatic` module:

1. As a **context manager** that temporarily makes output display dramatically
2. As a **decorator** that temporarily makes output display dramatically
3. Using a `dramatic.start()` function that makes output display dramatically
4. Using a `dramatic.print` function to display specific text dramatically


Dramatic Context Manager 🚪
--------------------------

The `dramatic.output` [context manager][] will temporarily cause all standard output and standard error to display dramatically:

```python
import dramatic

def main():
    print("This function prints")

with dramatic.output:
    main()
```

To change the printing speed from the default of 75 characters per second to another value (30 characters per second in this case) use the `at_speed` method:


```python
import dramatic

def main():
    print("This function prints")

with dramatic.output.at_speed(30):
    main()
```

Example context manager usage:

![dramatic.output context manager demo](https://raw.githubusercontent.com/treyhunner/dramatic/main/screenshots/context.gif)


Dramatic Decorator 🎀
--------------------

The `dramatic.output` [decorator][] will cause all standard output and standard error to display dramatically while the decorated function is running:

```python
import dramatic

@dramatic.output
def main():
    print("This function prints")

main()
```

The `at_speed` method works as a decorator as well:


```python
import dramatic

@dramatic.output.at_speed(30)
def main():
    print("This function prints")

main()
```

Example decorator usage:

![dramatic.output decorator demo](https://raw.githubusercontent.com/treyhunner/dramatic/main/screenshots/decorator.gif)


Manually Starting and Stopping 🔧
--------------------------------

Instead of enabling dramatic printing temporarily with a context manager or decorator, the `dramatic.start` function may be used to enable dramatic printing:

```python
import dramatic

def main():
    print("This function prints")

dramatic.start()
main()
```

The `speed` keyword argument may be used to change the printing speed (in characters per second):

```python
import dramatic

def main():
    print("This function prints")

dramatic.start(speed=30)
main()
```

To make *only* standard output dramatic (but not standard error) pass `stderr=False` to `start`:

```python
import dramatic

def main():
    print("This function prints")

dramatic.start(stderr=False)
main()
```

To disable dramatic printing, the `dramatic.stop` function may be used.
Here's an example [context manager][] that uses both `dramatic.start` and `dramatic.stop`:

```python
import dramatic


class CustomContextManager:
    def __enter__(self):
        print("Printing will become dramatic now")
        dramatic.start()
    def __exit__(self):
        dramatic.stop()
        print("Dramatic printing has stopped")
```

Example `start` and `stop` usage:

![dramatic.start decorator demo](https://raw.githubusercontent.com/treyhunner/dramatic/main/screenshots/start.gif)


Dramatic Print 🖨️
----------------

The `dramatic.print` function acts just like the built-in `print` function, but it prints dramatically:

```python
import dramatic
dramatic.print("This will print some text dramatically")
```


Dramatic Interpreter ⌨️
----------------------

To start a dramatic [Python REPL][]:

```bash
$ python3 -m dramatic
>>>
```

![dramatic printing within a terminal](https://raw.githubusercontent.com/treyhunner/dramatic/main/screenshots/repl.gif)

To dramatically run a Python module:

```bash
$ python3 -m dramatic -m this
```

To dramatically run a Python file:

```bash
$ python3 -m dramatic hello_world.py
```

The `dramatic` module also accepts a `--speed` argument to set the characters printed per second.
In this example we're increasing the speed from 75 characters-per-second to 120:

![dramatic module running demo](https://raw.githubusercontent.com/treyhunner/dramatic/main/screenshots/module.gif)


Maximum Drama (Use With Caution ⚠️)
----------------------------------

Want to make your Python interpreter dramatic *by default*?

Run the `dramatic` module as a script with the `--max-drama` argument to modify Python so that *all* your Python programs will print dramatically:

```bash
$ python3 -m dramatic --max-drama
This will cause all Python programs to run dramatically.
Running --min-drama will undo this operation.
Are you sure? [y/N]
```

Example:

![python3 -m dramatic --max-drama](https://raw.githubusercontent.com/treyhunner/dramatic/main/screenshots/max.gif)

If the drama is too much, run the module again with the argument `--min-drama` to undo:

```bash
$ python3 -m dramatic --min-drama
Deleted file /home/trey/.local/lib/python3.12/site-packages/dramatic.pth
Deleted file /home/trey/.local/lib/python3.12/site-packages/_dramatic.py
No drama.
```

Example:

![python3 -m dramatic --min-drama](https://raw.githubusercontent.com/treyhunner/dramatic/main/screenshots/min.gif)

This even works if you don't have the `dramatic` module installed.
Just download [dramatic.py](https://github.com/treyhunner/dramatic/blob/main/dramatic.py) and run it with `--max-drama`!
To disable the drama, you'll need to run `python3 -m _dramatic --min-drama` (note the `_` before `dramatic`).

**Warning**: using `--max-drama` is *probably a bad idea*.
Use with caution.


Other Features ✨
----------------

Other features of note:

- Pressing `Ctrl-C` while text is printing dramatically will cause the remaining text to print immediately.
- Dramatic printing is automatically disabled when the output stream is piped to a file (e.g. `python3 my_script.py > output.txt`)


Credits 💖
---------

This package was inspired by [the **dramatic print** Python Morsels exercise][dramatic print], which was partially inspired by Brandon Rhodes' [adventure][] Python port (which displays its text at 1200 baud).


[pypi]: https://pypi.org/project/dramatic/
[context manager]: https://www.pythonmorsels.com/what-is-a-context-manager/
[decorator]: https://www.pythonmorsels.com/what-is-a-decorator/
[python repl]: https://www.pythonmorsels.com/using-the-python-repl/
[dramatic print]: https://www.pythonmorsels.com/exercises/57338fa2ecc342e3bad18afdbf12aacd/
[adventure]: https://pypi.org/project/adventure/
