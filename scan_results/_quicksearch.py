import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import _audit08_helper as h
fn = sys.argv[1]
t = h.text(fn)
for n in sys.argv[2:]:
    i = t.find(n)
    if i>=0:
        print('==', n)
        print(t[i:i+800])
        print()
    else:
        print('==', n, 'NOT FOUND')
