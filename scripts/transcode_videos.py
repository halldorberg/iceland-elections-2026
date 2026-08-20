# coding: utf-8
"""Transcode campaign videos to compact 720p H.264 for self-hosting (NVENC).
Resumable: skips existing outputs."""
import io, json, os, subprocess, sys
from pathlib import Path
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = Path(__file__).parent.parent
RAW = ROOT / 'esb-videos' / 'raw'
OUT = ROOT / 'esb-videos' / 'media'
OUT.mkdir(parents=True, exist_ok=True)

wanted = set()
for f in ('video_classify_ja', 'video_classify_nei'):
    d = json.load(io.open(ROOT / 'scripts' / f'{f}.json', encoding='utf-8'))
    for v in d['videos']:
        wanted.add(v['id'])

done = fails = 0
for account_dir in sorted(RAW.iterdir()):
    if not account_dir.is_dir():
        continue
    for mp4 in sorted(account_dir.glob('*.mp4')):
        if mp4.stem not in wanted:
            continue
        out = OUT / (mp4.stem + '.mp4')
        if out.exists():
            done += 1
            continue
        r = subprocess.run([
            FF, '-y', '-i', str(mp4),
            '-vf', "scale='min(720,iw)':-2",
            '-c:v', 'h264_nvenc', '-preset', 'p5', '-cq', '30', '-maxrate', '2M', '-bufsize', '4M',
            '-c:a', 'aac', '-b:a', '96k',
            '-movflags', '+faststart',
            str(out),
        ], capture_output=True, text=True)
        if r.returncode != 0:
            # CPU fallback if nvenc unavailable for this input
            r = subprocess.run([
                FF, '-y', '-i', str(mp4),
                '-vf', "scale='min(720,iw)':-2",
                '-c:v', 'libx264', '-preset', 'fast', '-crf', '26',
                '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart',
                str(out),
            ], capture_output=True, text=True)
        if r.returncode != 0:
            print(f'FAIL {mp4.stem}: {r.stderr[-200:]}', flush=True)
            fails += 1
            continue
        done += 1
        if done % 20 == 0:
            print(f'{done} transcoded', flush=True)

total_mb = sum(f.stat().st_size for f in OUT.glob('*.mp4')) / 1e6
print(f'TRANSCODE DONE: {done} ok, {fails} failed, {total_mb:.0f} MB total', flush=True)
