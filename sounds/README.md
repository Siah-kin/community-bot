# Slot lever sound (`casino-coin.mp3`)

The homepage references **`sounds/casino-coin.mp3`** for lever pull feedback. Do **not** commit copyrighted audio you do not license.

Place a short, low-bitrate clip you have rights to use at:

`sounds/casino-coin.mp3`

Until the file exists, the page falls back to a short synthesized tone in script.

## Winamp strip demo (`winamp-demo.wav`)

The footer **Winamp**-homage stripe plays **`sounds/winamp-demo.wav`**: a short in-repo sine tone (no rights issue).

To use **MP3** instead, add a licensed file and change the homepage `<audio id="winamp-player">` to a single `<source src="sounds/your-track.mp3" type="audio/mpeg">`.
