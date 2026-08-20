# coding: utf-8
"""Transcribe downloaded campaign videos with faster-whisper (Icelandic).
Resumable: skips videos that already have a transcript file."""
import io, json, os, sys
from pathlib import Path

os.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')
import imageio_ffmpeg
os.environ['PATH'] = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe()) + os.pathsep + os.environ['PATH']

# CUDA DLLs from the nvidia pip wheels (cublas, cudnn) for ctranslate2 GPU support
import site
for sp in site.getsitepackages() + [site.getusersitepackages()]:
    for sub in ('nvidia/cublas/bin', 'nvidia/cudnn/bin'):
        p = os.path.join(sp, *sub.split('/'))
        if os.path.isdir(p):
            os.add_dll_directory(p)
            os.environ['PATH'] = p + os.pathsep + os.environ['PATH']

from faster_whisper import WhisperModel

ROOT = Path(__file__).parent.parent
RAW = ROOT / 'esb-videos' / 'raw'
OUT = ROOT / 'esb-videos' / 'transcripts'
OUT.mkdir(parents=True, exist_ok=True)

print('loading model...', flush=True)
model = WhisperModel('large-v3', device='cuda', compute_type='float16')

done = fails = 0
for account_dir in sorted(RAW.iterdir()):
    if not account_dir.is_dir():
        continue
    (OUT / account_dir.name).mkdir(exist_ok=True)
    for mp4 in sorted(account_dir.glob('*.mp4')):
        out = OUT / account_dir.name / (mp4.stem + '.json')
        if out.exists():
            done += 1
            continue
        meta = {}
        info = mp4.with_suffix('.info.json')
        if info.exists():
            j = json.load(io.open(info, encoding='utf-8'))
            meta = {'caption': j.get('description') or j.get('title'), 'date': j.get('upload_date'),
                    'views': j.get('view_count'), 'likes': j.get('like_count'),
                    'url': j.get('webpage_url'), 'duration': j.get('duration')}
        try:
            segments, sinfo = model.transcribe(str(mp4), language='is', vad_filter=True)
            text = ' '.join(s.text.strip() for s in segments)
        except Exception as e:
            print(f'FAIL {mp4.name}: {e}', flush=True)
            fails += 1
            continue
        json.dump({'account': account_dir.name, 'id': mp4.stem, 'transcript': text, **meta},
                  io.open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        done += 1
        if done % 10 == 0:
            print(f'{done} transcribed', flush=True)
print(f'TRANSCRIPTION DONE: {done} ok, {fails} failed', flush=True)
