"""
detect_eye_positions.py
───────────────────────
Run OpenCV Haar-cascade face/eye detection on every local candidate image,
compute the eye Y position as a fraction of image height,
and write the result to js/data/eye_positions.js.

The frontend (js/municipality.js applySmartCrop) reads this map
to position the modal hero photo so the subject's eyes land at ~1/3
from the top of the visible area.
"""
from pathlib import Path

import cv2

ROOT      = Path(__file__).parent.parent
IMAGE_DIR = ROOT / 'images' / 'candidates'
OUT_FILE  = ROOT / 'js' / 'data' / 'eye_positions.js'
EXTS      = {'.jpg', '.jpeg', '.png', '.webp'}

# Hand-picked overrides for images where Haar-cascade fails (no face
# detected) or fires false positives (typically on V-neck collars,
# shadows, glasses reflections). Applied AFTER auto-detection so the
# manual values always win on subsequent re-runs.
MANUAL_OVERRIDES: dict[str, dict] = {
    # HFJ.B — Framsókn í Hornafirði (May 2026):
    # Sigursteinn — face cascade didn't fire; eyes ~y=75 in 400px
    'images/candidates/13da0275de9d1757.jpg': { 'eyeY': 0.19, 'w': 400, 'h': 400 },
    # Ásgerður — false positive on V-neck collar (auto: 0.47); eyes ~y=55
    'images/candidates/fc2b63efa4146e4d.jpg': { 'eyeY': 0.14, 'w': 400, 'h': 400 },
    # GRN.M — Miðflokkurinn í Grindavík (May 2026):
    # Hajie Flores — safety glasses + cap defeated Haar cascade; eyes ~y=65
    'images/candidates/fa4c670ff3ad7977.jpg': { 'eyeY': 0.16, 'w': 400, 'h': 400 },
    # Andri Hrafn — face on left, false positive too high (auto: 0.0844); eyes ~y=60
    'images/candidates/96b104c7375f2e91.jpg': { 'eyeY': 0.15, 'w': 400, 'h': 400 },
    # AKU.AL — Akureyrarlistinn (May 2026):
    # Ingibjörg Margrét — Haar didn't fire; eyes ~y=130 in 400px portrait
    'images/candidates/8df478d4b15dfae6.jpg': { 'eyeY': 0.32, 'w': 400, 'h': 400 },
    # FJB.H — H-listinn í Fjallabyggð (May 2026):
    # Helgi (with cap + skis prop) — auto put eyes near cap brim; eyes ~y=120
    'images/candidates/41aa691853c69b7a.jpg': { 'eyeY': 0.30, 'w': 400, 'h': 400 },
    # Jón Valgeir — false positive low (auto: 0.4769); eyes ~y=130
    'images/candidates/d77a3d9457f8ddb9.jpg': { 'eyeY': 0.32, 'w': 400, 'h': 400 },
}

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)
eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_eye.xml'
)


def detect_eye_y(image_path: Path) -> dict | None:
    """Return {'eyeY': float, 'w': int, 'h': int} or None on failure."""
    img = cv2.imread(str(image_path))
    if img is None:
        return None
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
    if len(faces) == 0:
        return None

    # Pick the largest face
    fx, fy, fw, fh = max(faces, key=lambda f: f[2] * f[3])

    # Look for eyes within the upper 60% of the face box (skip mouth-area false positives)
    face_roi = gray[fy:fy + int(fh * 0.6), fx:fx + fw]
    eyes = eye_cascade.detectMultiScale(face_roi, scaleFactor=1.1, minNeighbors=5,
                                         minSize=(int(fw * 0.1), int(fw * 0.1)))

    if len(eyes) >= 2:
        # Take the two largest eye candidates, average their centers
        eyes_sorted = sorted(eyes, key=lambda e: e[2] * e[3], reverse=True)[:2]
        ys = [(fy + ey + eh / 2) for (ex, ey, ew, eh) in eyes_sorted]
        eye_y_px = sum(ys) / len(ys)
    elif len(eyes) == 1:
        ex, ey, ew, eh = eyes[0]
        eye_y_px = fy + ey + eh / 2
    else:
        # No eyes detected — fall back to face anthropometric estimate
        # Eyes typically sit at ~38% down the face bounding box from the top
        eye_y_px = fy + fh * 0.38

    eye_y_norm = eye_y_px / h
    if not (0.0 <= eye_y_norm <= 1.0):
        return None

    return {
        'eyeY': round(eye_y_norm, 4),
        'w': w,
        'h': h,
    }


def main():
    images = sorted(p for p in IMAGE_DIR.iterdir()
                    if p.suffix.lower() in EXTS and p.is_file())
    print(f"Scanning {len(images)} images in {IMAGE_DIR}")

    results = {}
    failed  = []
    for i, p in enumerate(images, 1):
        res = detect_eye_y(p)
        rel = f"images/candidates/{p.name}"
        if res:
            results[rel] = res
        else:
            failed.append(rel)
        if i % 100 == 0:
            print(f"  [{i}/{len(images)}] {len(results)} detected, {len(failed)} failed")

    print(f"\nDone: {len(results)} detected, {len(failed)} failed out of {len(images)}")

    # Apply manual overrides (last-write-wins) — for images where Haar
    # cascade fails or fires on collars/shadows. These are listed at the
    # top of this file so the corrections survive subsequent re-runs.
    overridden = 0
    for path, vals in MANUAL_OVERRIDES.items():
        results[path] = vals
        overridden += 1
        if path in failed:
            failed.remove(path)
    if overridden:
        print(f"Applied {overridden} manual overrides")

    # Write ES module
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        '// AUTO-GENERATED — do not edit manually.',
        '// Generated by scripts/detect_eye_positions.py',
        '// Maps candidate image path -> { eyeY: 0..1, w, h }',
        '',
        'export const EYE_POSITIONS = {',
    ]
    for path in sorted(results):
        d = results[path]
        lines.append(f'  "{path}": {{ "eyeY": {d["eyeY"]}, "w": {d["w"]}, "h": {d["h"]} }},')
    lines.append('};')
    lines.append('')
    OUT_FILE.write_text('\n'.join(lines), encoding='utf-8')
    print(f"Wrote {OUT_FILE} ({len(results)} entries)")

    if failed:
        log = ROOT / 'scripts' / 'eye_detection_failed.txt'
        log.write_text('\n'.join(failed) + '\n', encoding='utf-8')
        print(f"Wrote failed list -> {log}")


if __name__ == '__main__':
    main()
