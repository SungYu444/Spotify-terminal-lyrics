# Spotify Terminal Lyrics

Display real-time lyrics for whatever is playing on **Spotify** (or any streaming platform) — right in your terminal, as large ASCII block letters, synced word by word.

```
  ██   ██ ███████ ██      ██       ██████
  ██   ██ ██      ██      ██      ██    ██
  ███████ █████   ██      ██      ██    ██
  ██   ██ ██      ██      ██      ██    ██
  ██   ██ ███████ ███████ ███████  ██████
```

Works with **Spotify, YouTube Music, VLC, and any MPRIS-compatible player** via playerctl. Lyrics are fetched automatically from [LRCLIB](https://lrclib.net) (with syncedlyrics as a fallback — pulling from NetEase, Musixmatch, and more). No local music library required.

> **Note:** Word-level timing accuracy depends on the song — faster lyrics tend to sync better. Less mainstream tracks may not be in LRCLIB.

---

## Dependencies

**System:**
- `python >= 3.12`
- `ffmpeg` (provides ffprobe)
- `playerctl`

**Python (installed automatically by `setup.sh`):**
- `pyyaml` — required
- `mutagen` — reads embedded audio tags for better lyrics matching
- `syncedlyrics` — fallback lyrics source (NetEase, etc.)
- `librosa` — onset detection for more accurate word timing (optional, ~200MB)

---

## Install

```bash
git clone https://github.com/Sungyu444/Spotify-terminal-lyrics
cd Spotify-terminal-lyrics
bash setup.sh
```

`setup.sh` installs Python dependencies, copies the package to `~/.config/lrc-tools/`, creates command stubs in `~/.local/bin/`, and sets up data directories at `~/.local/share/lrc-tools/lyrics/`.

Make sure `~/.local/bin` is in your PATH:
```bash
# fish
fish_add_path ~/.local/bin

# bash/zsh
export PATH="$HOME/.local/bin:$PATH"
```

---

## Usage

### Just run it — works with Spotify out of the box

```bash
lrc-vis
```

No configuration needed. Start playing something on Spotify (or any streaming platform) and run `lrc-vis` — it will detect the current track and fetch lyrics automatically.

### With a pre-processed local library (better timing)

```bash
# 1. Download lyrics for your music library
lrc-fetch --audio-dir ~/music --output-dir ~/.local/share/lrc-tools/lyrics/raw

# 2. Process into word-level timing
lrc-processor --lrc-dir ~/.local/share/lrc-tools/lyrics/raw \
              --audio-dir ~/music \
              --output-dir ~/.local/share/lrc-tools/lyrics/processed \
              --wlrc

# 3. Start the visualizer
lrc-vis --lrc-dir ~/.local/share/lrc-tools/lyrics/processed --wlrc
```

Steps 1 and 2 are one-time setup per library. `lrc-vis` is the daily driver.

---

## How it works

**`lrc-fetch`** scans your music directory, reads embedded tags (or parses filenames), and downloads synced LRC lyrics from LRCLIB with syncedlyrics as a fallback.

**`lrc-processor`** takes standard LRC files (phrase-level timing) and splits long phrases at natural boundaries, then optionally converts to word-level WLRC format using even distribution or librosa onset detection.

**`lrc-vis`** hooks into your media player via playerctl (MPRIS), finds the matching lyrics for the current track (locally or by fetching online), and renders them as large block letters centered in the terminal. Handles seeking, pausing, and track changes automatically.

---

## Configuration

`setup.sh` places a default config at `~/.config/lrc-tools/config.yaml`. Pass it with `--config`:

```bash
lrc-vis --config ~/.config/lrc-tools/config.yaml --lrc-dir ~/.local/share/lrc-tools/lyrics/processed --wlrc
```

Key settings:

```yaml
processor:
  max_phrase_duration: 2.5   # split phrases longer than this (seconds)
  max_words_per_phrase: 8

puller:
  search_threads: 5
  download_threads: 5
  preserve_structure: true   # mirror audio dir layout in lyrics dir

visualizer:
  default_font: block        # block or compact
  refresh_rate: 0.05
```

---

## Custom fonts

Fonts are defined in JSON. See `~/.config/lrc-tools/custom_fonts.json` for the format.

```bash
lrc-vis --lrc-dir ~/.local/share/lrc-tools/lyrics/processed --wlrc \
        --custom-fonts ~/.config/lrc-tools/custom_fonts.json --font mini
```

---

## License

MIT
