import sys, pathlib
for stem in sys.argv[1:]:
    p = pathlib.Path("tmp_dv/text") / (stem + ".txt")
    t = p.read_text(encoding="utf-8")
    lines = t.split("\n", 2)
    body = lines[2] if len(lines) > 2 else ""
    print("=" * 20, stem)
    print("TITLE:", lines[0]); print("DATE:", lines[1]); print("LEN:", len(body))
    print("HEAD:", body[:1300])
    if len(body) > 1900:
        print("TAIL:", body[-500:])
    print()
