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

To regenerate an image:

```bash
$ agg --theme solarized-light --cols 71 --rows 13 --font-size 16 repl.cast repl.gif
$ agg --theme solarized-light --cols 71 --rows 9 --font-size 16 context.cast context.gif
$ agg --theme solarized-light --cols 71 --rows 13 --font-size 16 decorator.cast decorator.gif
$ agg --theme solarized-light --cols 71 --rows 19 --font-size 16 start.cast start.gif
$ agg --theme solarized-light --cols 71 --rows 24 --font-size 16 module.cast module.gif
```
