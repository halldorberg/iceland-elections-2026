# coding: utf-8
"""Download all TikTok videos of the four ESB campaign accounts via yt-dlp.
Resumable: yt-dlp --download-archive skips already-downloaded ids."""
import subprocess, sys, io, json
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUT = ROOT / 'esb-videos' / 'raw'
OUT.mkdir(parents=True, exist_ok=True)

ACCOUNTS = {
    'aframisland': ('nei', 'https://www.tiktok.com/@afram.island'),
    'sja': ('ja', 'https://www.tiktok.com/@jatiladsja'),
    'evropuhreyfingin': ('ja', 'https://www.tiktok.com/@evropuhreyfingin'),
    'heimssyn': ('nei', 'https://www.tiktok.com/@heimssyn'),
}

for name, (side, url) in ACCOUNTS.items():
    dest = OUT / name
    dest.mkdir(exist_ok=True)
    print(f'=== {name} ({side}) ===', flush=True)
    r = subprocess.run([
        sys.executable, '-m', 'yt_dlp',
        '--download-archive', str(dest / 'archive.txt'),
        '--write-info-json',
        '--no-write-comments',
        '-o', str(dest / '%(id)s.%(ext)s'),
        '-f', 'mp4/bv*+ba/b',
        '--sleep-interval', '2', '--max-sleep-interval', '5',
        '--ignore-errors',
        url,
    ])
    print(f'{name} exit {r.returncode}', flush=True)
print('ALL DOWNLOADS DONE', flush=True)
