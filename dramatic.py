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
__version__ = "0.0.0"
