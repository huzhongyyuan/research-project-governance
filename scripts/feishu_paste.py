#!/usr/bin/env python3
"""Convert a report's Markdown subset to HTML and put it on the macOS clipboard for Feishu paste.

Feishu turns pasted HTML tables, headings and lists into native blocks; raw Markdown tables stay
as pipe text. Python 3 standard library only; reads the file, writes nothing but the clipboard.
"""
import argparse
import html
from pathlib import Path
import re
import subprocess
import sys

TABLE_STYLE = 'border-collapse:collapse'
CELL_STYLE = 'border:1px solid #d0d3d6;padding:4px 8px'


def inline(text):
    parts = re.split(r'(`[^`]+`)', text)
    out = []
    for part in parts:
        if part.startswith('`') and part.endswith('`') and len(part) > 1:
            out.append('<code>' + html.escape(part[1:-1]) + '</code>')
            continue
        part = html.escape(part, quote=False)
        part = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', part)
        part = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)',
                      lambda m: '<a href="' + html.escape(m[2]) + '">' + m[1] + '</a>', part)
        out.append(part)
    return ''.join(out)


def cells(line):
    line = line.strip()
    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|'):
        line = line[:-1]
    return [c.strip() for c in line.split('|')]


def is_separator(line):
    return bool(re.fullmatch(r'\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*', line))


def to_html(markdown):
    text = re.sub(r'<!--.*?-->', '', markdown, flags=re.S)
    lines = text.splitlines()
    out, i, para = [], 0, []

    def flush():
        if para:
            out.append('<p>' + '<br>'.join(inline(p) for p in para) + '</p>')
            para.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        fence = re.match(r'^(`{3,}|~{3,})', stripped)
        if fence:
            flush()
            body, i = [], i + 1
            while i < len(lines) and not lines[i].strip().startswith(fence[1]):
                body.append(lines[i])
                i += 1
            out.append('<pre>' + html.escape('\n'.join(body)) + '</pre>')
            i += 1
            continue
        if not stripped:
            flush()
            i += 1
            continue
        heading = re.match(r'^(#{1,6})\s+(.*)', stripped)
        if heading:
            flush()
            level = len(heading[1])
            out.append('<h%d>%s</h%d>' % (level, inline(heading[2]), level))
            i += 1
            continue
        if '|' in stripped and i + 1 < len(lines) and is_separator(lines[i + 1]):
            flush()
            rows = ['<tr>' + ''.join('<th style="%s">%s</th>' % (CELL_STYLE, inline(c))
                                     for c in cells(stripped)) + '</tr>']
            i += 2
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append('<tr>' + ''.join('<td style="%s">%s</td>' % (CELL_STYLE, inline(c))
                                             for c in cells(lines[i])) + '</tr>')
                i += 1
            out.append('<table style="%s">%s</table>' % (TABLE_STYLE, ''.join(rows)))
            continue
        if stripped.startswith('>'):
            flush()
            quote = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                quote.append(inline(lines[i].strip()[1:].strip()))
                i += 1
            out.append('<blockquote>' + '<br>'.join(quote) + '</blockquote>')
            continue
        item = re.match(r'^([-*]|\d+\.)\s+(.*)', stripped)
        if item:
            flush()
            tag = 'ol' if item[1][0].isdigit() else 'ul'
            items = []
            while i < len(lines):
                m = re.match(r'^([-*]|\d+\.)\s+(.*)', lines[i].strip())
                if not m or ('ol' if m[1][0].isdigit() else 'ul') != tag:
                    break
                items.append('<li>' + inline(m[2]) + '</li>')
                i += 1
            out.append('<%s>%s</%s>' % (tag, ''.join(items), tag))
            continue
        para.append(stripped)
        i += 1
    flush()
    return '<html><body>' + '\n'.join(out) + '</body></html>'


def copy_to_clipboard(html_text, plain_text):
    """Set HTML and plain-text flavors on the macOS pasteboard."""
    if sys.platform != 'darwin':
        raise OSError('clipboard copy is only implemented for macOS; use --output instead')
    # AppleScript cannot receive raw bytes via argv, so the HTML goes in as a hex data literal.
    hex_html = html_text.encode('utf-8').hex()
    script = ('on run argv\n'
              'set the clipboard to {«class HTML»:«data HTML' + hex_html + '», '
              'string:(item 1 of argv)}\n'
              'end run')
    subprocess.run(['osascript', '-', plain_text], input=script, text=True, check=True,
                   capture_output=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('markdown', help='report file (Markdown subset)')
    parser.add_argument('--output', help='write HTML to this file instead of the clipboard')
    args = parser.parse_args(argv)
    source = Path(args.markdown).read_text(encoding='utf-8')
    result = to_html(source)
    if args.output:
        Path(args.output).write_text(result, encoding='utf-8')
        print('HTML written to ' + args.output)
    else:
        copy_to_clipboard(result, re.sub(r'<!--.*?-->', '', source, flags=re.S))
        print('Copied as rich text; paste into Feishu with Cmd+V.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
