"""Probe find_close on RVK.C's list."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def find_close(s, op, oc, cc, log=False, log_until=None):
    depth, i, in_str = 0, op, None
    while i < len(s):
        c = s[i]
        if in_str:
            if c == "\\": i += 2; continue
            if c == in_str: in_str = None
            i += 1; continue
        if c in ("'", '"'): in_str = c; i += 1; continue
        if c == oc:
            depth += 1
        elif c == cc:
            depth -= 1
            if depth == 0: return i + 1
        if log and (log_until is None or i <= log_until) and (depth <= 1 or i < op + 10000):
            if c in (oc, cc):
                line = s[:i].count("\n") + 1
                print(f"  d{depth} L{line} {c!r}: ...{s[max(0,i-30):i+20]!r}")
        i += 1
    return -1

src = open('js/data/candidates.js', encoding='utf-8').read()

# RVK.C list `[` at line 1022
i = src.find("  C: {", 30000)
list_start = src.find("list: [", i)
list_open = list_start + len("list: ")  # position of `[`
print(f"list_open offset: {list_open}, char: {src[list_open]!r}, line: {src[:list_open].count(chr(10))+1}")

close = find_close(src, list_open, "[", "]", log=True, log_until=160000)
print(f"find_close returned: {close}, line: {src[:close].count(chr(10))+1}")
print(f"  context @ close: {src[max(0,close-30):close+30]!r}")
