# Slot lever sound (`casino-coin.mp3`)

The homepage references **`sounds/casino-coin.mp3`** for lever pull feedback. Do **not** commit copyrighted audio you do not license.

Place a short, low-bitrate clip you have rights to use at:

`sounds/casino-coin.mp3`

Until the file exists, the page falls back to a short synthesized tone in script.

## Winamp strip (`rage-against-the-machine-killing-in-the-name.mp3`)

The homepage `<audio id="winamp-player">` loads **`sounds/rage-against-the-machine-killing-in-the-name.mp3`** first, then falls back to **`sounds/winamp-demo.wav`**.

Only ship audio you have the rights to redistribute on a public site. Source of truth on the operator machine may live under the Bonzi_v5 tree; this repo keeps a copy under `sounds/` for GitHub Pages.

## Winamp fallback (`winamp-demo.wav`)

Short in-repo sine tone used if the MP3 source is missing or unsupported.
