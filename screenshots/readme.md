Screenshots
-----------

Screenshots were generated using `asciinema`.

```bash
$ pipx install asciinema
```

The images are generated from `.cast` files using `agg`:

```bash
$ snap install asciinema-agg
```

To rerecord:

```bash
$ asciinema rec -c python3 output.cast
```

To regenerate an image:

```bash
$ agg --theme solarized-light --cols 71 --rows 16 --font-size 16 main.cast main.gif
$ agg --theme solarized-light --cols 71 --rows 13 --font-size 16 repl.cast repl.gif
$ agg --theme solarized-light --cols 71 --rows 9 --font-size 16 context.cast context.gif
$ agg --theme solarized-light --cols 71 --rows 13 --font-size 16 decorator.cast decorator.gif
$ agg --theme solarized-light --cols 71 --rows 19 --font-size 16 start.cast start.gif
$ agg --theme solarized-light --cols 71 --rows 24 --font-size 16 module.cast module.gif
$ agg --theme solarized-light --cols 71 --rows 10 --font-size 16 max.cast max.gif
$ agg --theme solarized-light --cols 72 --rows 6 --font-size 16 min.cast min.gif
```
