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
$ agg --theme solarized-light --cols 71 --rows 20 --font-size 16 file.cast file.gif
```
