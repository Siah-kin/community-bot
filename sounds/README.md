# Slot lever sound (`casino-coin.mp3`)

The homepage references **`sounds/casino-coin.mp3`** for lever pull feedback. Do **not** commit copyrighted audio you do not license.

Place a short, low-bitrate clip you have rights to use at:

`sounds/casino-coin.mp3`

Until the file exists, the page falls back to a short synthesized tone in script.

## Winamp strip playlist

The footer player uses in-page **`WINAMP_PLAYLIST`** (see `index.html`): ordered tracks with **shown titles** on the LCD, **|<<** / **>>|** for previous/next, wraparound queue, auto-advance on track end.

| File | Shown title |
|------|----------------|
| `sounds/rage-against-the-machine-killing-in-the-name.mp3` | Rage Against the Machine - Killing in the Name |
| `sounds/black-sabbath-children-of-the-grave.mp3` | Black Sabbath - Children of the Grave |
| `sounds/winamp-demo.wav` | Bonzi demo tone (synth WAV) |

`.gitignore` only allows these tracked MP3s by name; add `!sounds/your-file.mp3` when you add another licensed file and extend the playlist in script.

Only ship audio you have the rights to redistribute on a public site.
