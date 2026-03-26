# lrc-tools

Terminal lyrics visualizer with word-level sync. Hooks into any MPRIS-compatible media player via playerctl and displays the current lyric as large ASCII block letters in your terminal, one word at a time.

```
  ██   ██ ███████ ██      ██       ██████
  ██   ██ ██      ██      ██      ██    ██
  ███████ █████   ██      ██      ██    ██
  ██   ██ ██      ██      ██      ██    ██
  ██   ██ ███████ ███████ ███████  ██████
```

Lyrics are fetched automatically from [LRCLIB](https://lrclib.net) (with syncedlyrics as a fallback). You can also pre-download and process your library for better word-level timing.

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
git clone https://github.com/tacoproz1/tacos-terminal-lyrics
cd tacos-terminal-lyrics
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

### Just run it (lyrics fetched online automatically)

```bash
lrc-vis
```

No setup needed — it will look up lyrics for whatever is playing.

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
