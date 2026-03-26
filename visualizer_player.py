"""
Media player integration
- macOS: uses AppleScript (osascript) to talk to Spotify
- Linux: uses playerctl (MPRIS)
"""
import sys
import subprocess
from pathlib import Path
from typing import Optional, Tuple

_IS_MACOS = sys.platform == 'darwin'


# ---------------------------------------------------------------------------
# macOS — AppleScript helpers
# ---------------------------------------------------------------------------

def _run_applescript(script: str) -> Optional[str]:
    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=1.0
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None


def _macos_get_position() -> Optional[float]:
    out = _run_applescript('tell application "Spotify" to get player position')
    try:
        return float(out) if out else None
    except (ValueError, TypeError):
        return None


def _macos_get_track() -> Optional[Tuple[str, str]]:
    out = _run_applescript(
        'tell application "Spotify"\n'
        '    set a to artist of current track\n'
        '    set t to name of current track\n'
        '    return a & "|||" & t\n'
        'end tell'
    )
    if out:
        parts = out.split('|||')
        return (parts[0], parts[1]) if len(parts) == 2 else None
    return None


def _macos_get_status() -> Optional[str]:
    out = _run_applescript('tell application "Spotify" to get player state')
    if out == 'playing':
        return 'Playing'
    if out == 'paused':
        return 'Paused'
    if out == 'stopped':
        return 'Stopped'
    return None


# ---------------------------------------------------------------------------
# Linux — playerctl helpers
# ---------------------------------------------------------------------------

def _linux_get_position() -> Optional[float]:
    try:
        result = subprocess.run(
            ['playerctl', 'position'],
            capture_output=True,
            text=True,
            timeout=0.5
        )
        return float(result.stdout.strip()) if result.returncode == 0 else None
    except Exception:
        return None


def _linux_get_track() -> Optional[Tuple[str, str]]:
    try:
        result = subprocess.run(
            ['playerctl', 'metadata', '--format', '{{artist}}|||{{title}}'],
            capture_output=True,
            text=True,
            timeout=0.5
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split('|||')
            return (parts[0], parts[1]) if len(parts) == 2 else None
    except Exception:
        return None


def _linux_get_status() -> Optional[str]:
    try:
        result = subprocess.run(
            ['playerctl', 'status'],
            capture_output=True,
            text=True,
            timeout=0.5
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None


def _linux_get_audio_file_info() -> Optional[Path]:
    try:
        result = subprocess.run(
            ['playerctl', 'metadata', '--format', '{{xesam:url}}'],
            capture_output=True,
            text=True,
            timeout=0.5
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            if url.startswith('file://'):
                return Path(url[7:])
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_position() -> Optional[float]:
    """Get current playback position in seconds."""
    return _macos_get_position() if _IS_MACOS else _linux_get_position()


def get_track() -> Optional[Tuple[str, str]]:
    """Get (artist, title) of the currently playing track."""
    return _macos_get_track() if _IS_MACOS else _linux_get_track()


def get_status() -> Optional[str]:
    """Get playback status: 'Playing', 'Paused', or 'Stopped'."""
    return _macos_get_status() if _IS_MACOS else _linux_get_status()


def get_audio_file_info() -> Optional[Path]:
    """Get local audio file path (Linux/MPRIS only; returns None on macOS)."""
    if _IS_MACOS:
        return None  # Spotify on macOS streams; no local file path via AppleScript
    return _linux_get_audio_file_info()


def is_paused() -> bool:
    return get_status() == 'Paused'


def is_playing() -> bool:
    return get_status() == 'Playing'
