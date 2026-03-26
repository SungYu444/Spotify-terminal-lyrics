"""
Display utilities for LRC visualizer
Handles rendering text in various styles to terminal
"""
import sys
import os
import re
from pathlib import Path
from typing import List, Optional, Tuple


def _read_hyprland_colors() -> Optional[dict]:
    """
    Read matugen-generated colors from ~/.config/hypr/colors.conf.
    Parses lines like: $primary = rgba(a6c8ffff)
    Returns dict mapping color name -> (r, g, b).
    """
    conf = Path.home() / '.config' / 'hypr' / 'colors.conf'
    if not conf.exists():
        return None
    palette = {}
    pattern = re.compile(r'^\$(\w+)\s*=\s*rgba\(([0-9a-fA-F]{8})\)')
    try:
        for line in conf.read_text().splitlines():
            m = pattern.match(line.strip())
            if m:
                name = m.group(1)
                hex8 = m.group(2)
                r, g, b = int(hex8[0:2], 16), int(hex8[2:4], 16), int(hex8[4:6], 16)
                palette[name] = (r, g, b)
        return palette if palette else None
    except Exception:
        return None


def load_palette() -> List[Tuple[int, int, int]]:
    """
    Load the primary color from matugen colors.
    Returns a list with one (r, g, b) tuple, falling back to white.
    """
    palette = _read_hyprland_colors()
    if palette and 'primary' in palette:
        return [palette['primary']]
    return [(255, 255, 255)]


def get_terminal_size() -> tuple:
    """
    Get terminal dimensions.
    
    Returns:
        Tuple of (columns, rows)
    """
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except Exception:
        return 80, 24  # Default fallback


def clear_screen():
    """Clear the terminal screen"""
    sys.stdout.write('\033[2J\033[H')
    sys.stdout.flush()


def hide_cursor():
    """Hide terminal cursor"""
    sys.stdout.write('\033[?25l')
    sys.stdout.flush()


def show_cursor():
    """Show terminal cursor"""
    sys.stdout.write('\033[?25h')
    sys.stdout.flush()


def render_block_text(text: str, font_data: dict, color: Optional[Tuple[int, int, int]] = None) -> str:
    """
    Render text using block letters.

    Args:
        text: Text to render
        font_data: Font dictionary mapping characters to line arrays

    Returns:
        Rendered text as string
    """
    text = text.upper()

    # Get height from first available character
    height = len(font_data.get('A', ['']))
    cols, rows = get_terminal_size()

    def char_render_width(c: str) -> int:
        if c in font_data:
            return len(font_data[c][0]) + 1  # +1 for spacing between chars
        return len(font_data.get(' ', ['    '])[0]) + 1

    # Word-wrap text so each wrapped line fits within terminal width
    words = text.split(' ')
    wrapped_words: List[str] = []
    current = ''
    for word in words:
        candidate = (current + ' ' + word).strip() if current else word
        if sum(char_render_width(c) for c in candidate) <= cols:
            current = candidate
        else:
            if current:
                wrapped_words.append(current)
            # If a single word is wider than the terminal, truncate it
            if sum(char_render_width(c) for c in word) > cols:
                truncated = ''
                for c in word:
                    if sum(char_render_width(ch) for ch in truncated + c) <= cols:
                        truncated += c
                    else:
                        break
                current = truncated
            else:
                current = word
    if current:
        wrapped_words.append(current)

    if not wrapped_words:
        wrapped_words = ['']

    # Render each wrapped line as block letters
    all_block_lines: List[str] = []
    for wline in wrapped_words:
        block_lines = ['' for _ in range(height)]
        for char in wline:
            if char in font_data:
                char_lines = font_data[char]
                for i in range(height):
                    if i < len(char_lines):
                        block_lines[i] += char_lines[i] + ' '
                    else:
                        block_lines[i] += ' ' * (len(char_lines[0]) + 1)
            else:
                space_width = len(font_data.get(' ', ['    '])[0])
                for i in range(height):
                    block_lines[i] += ' ' * (space_width + 1)
        all_block_lines.extend(block_lines)

    # Center vertically
    pad_top = max(0, (rows - len(all_block_lines)) // 2)

    output = []
    for i in range(rows):
        if pad_top <= i < pad_top + len(all_block_lines):
            line = all_block_lines[i - pad_top]
            pad_left = max(0, (cols - len(line)) // 2)
            centered = ' ' * pad_left + line
            output.append(centered.ljust(cols))
        else:
            output.append(' ' * cols)

    result = '\n'.join(output)
    if color:
        r, g, b = color
        result = f'\033[38;2;{r};{g};{b}m{result}\033[0m'
    return result


def render_simple_text(text: str, centered: bool = True) -> str:
    """
    Render text in simple format (no block letters).
    
    Args:
        text: Text to render
        centered: Whether to center the text
        
    Returns:
        Rendered text as string
    """
    cols, rows = get_terminal_size()
    
    if centered:
        pad_top = rows // 2
        pad_left = max(0, (cols - len(text)) // 2)
        
        output = []
        for i in range(rows):
            if i == pad_top:
                output.append(' ' * pad_left + text)
            else:
                output.append(' ' * cols)
        
        return '\n'.join(output)
    else:
        return text


def render_waiting() -> str:
    """
    Render waiting/loading indicator.
    
    Returns:
        Rendered waiting text
    """
    return render_simple_text("•••", centered=True)


def display_text(text: str, use_block_letters: bool = True, font_data: dict = None, clear: bool = True,
                 color: Optional[Tuple[int, int, int]] = None):
    """
    Display text in the terminal.

    Args:
        text: Text to display
        use_block_letters: Whether to use block letter rendering
        font_data: Font to use for block letters
        clear: Whether to clear screen first
        color: Optional (r, g, b) tuple for true-color ANSI coloring
    """
    if clear:
        sys.stdout.write('\033[2J\033[H')

    if use_block_letters and font_data:
        output = render_block_text(text, font_data, color=color)
    else:
        output = render_simple_text(text)

    sys.stdout.write(output)
    sys.stdout.flush()


def display_waiting(clear: bool = True):
    """
    Display waiting indicator.
    
    Args:
        clear: Whether to clear screen first
    """
    if clear:
        sys.stdout.write('\033[2J\033[H')
    
    output = render_waiting()
    sys.stdout.write(output)
    sys.stdout.flush()
