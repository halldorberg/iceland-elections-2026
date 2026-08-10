#!/usr/bin/env python3
"""Local election-night results entry backend (NOT deployed).

A single-file, dependency-free web app (Python stdlib http.server) for
entering counted results per municipality on election night. One row per
contested muni, a % box per ballot letter + a votes-counted box, live
D'Hondt seat preview, and Σ% sanity. Saving writes
`data/live-results.draft.json` — exactly the shape
`scripts/publish_live_results.py` consumes.

It NEVER pushes, NEVER touches git, NEVER writes the micro-repo. Bind is
127.0.0.1 only. Workflow:

  1. python scripts/results_backend.py        # opens http://127.0.0.1:5050
  2. Enter (or let Claude prepopulate) results; Save rows.
  3. Tell Claude "approved" → Claude runs publish_live_results.py + pushes
     the iceland-results-live micro-repo (the fast path).

Claude can prepopulate by writing data/live-results.draft.json directly
(same schema); hit "Reload from disk" in the UI to pull those values in,
edit anything, then Save.

Usage:
  python scripts/results_backend.py [--port 5050]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

for _s in (sys.stdout, sys.stderr):  # Windows cp1252 chokes on → ⚠ Σ
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "data" / "muni_config.json"
PARTIES_JS = ROOT / "js" / "data" / "parties.js"
DRAFT = ROOT / "data" / "live-results.draft.json"
PUBLISHED = Path(
    __import__("os").environ.get(
        "ICELAND_RESULTS_REPO", ROOT.parent / "iceland-results-live"
    )
) / "results.json"


def now_iso() -> str:
    return (datetime.now(timezone.utc)
            .isoformat(timespec="seconds").replace("+00:00", "Z"))


def dhondt(pct: dict, total_seats: int) -> dict:
    seats = {c: 0 for c in pct}
    for _ in range(total_seats):
        best_c, best_q = None, -1.0
        for c, v in pct.items():
            q = v / (seats[c] + 1)
            if q > best_q:
                best_q, best_c = q, c
        if best_c is None:
            break
        seats[best_c] += 1
    return seats


def party_names() -> dict:
    src = PARTIES_JS.read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"^\s{2}([A-Za-z0-9ÁÉÍÓÚÝÐÞÆÖ]+):\s*\{", src, re.M):
        blk = src[m.end(): src.find("\n  }", m.end())]
        nm = re.search(r"name:\s*'([^']*)'", blk)
        if nm:
            out[m.group(1)] = nm.group(1)
    return out


def load_json(p: Path, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default


# Icelandic alphabetical collation: á after a, ð after d, þ/æ/ö at the end,
# so Árborg sorts by 'A', Ísafjörður by 'I', Þingeyjarsveit/Ölfus last.
_IS_ALPHABET = "a á b c d ð e é f g h i í j k l m n o ó p q r s t u ú v w x y ý z þ æ ö".split()
_IS_RANK = {ch: i for i, ch in enumerate(_IS_ALPHABET)}


def is_sort_key(name: str):
    return [_IS_RANK.get(ch, 99 + ord(ch)) for ch in (name or "").lower()]


def build_state() -> dict:
    cfg = load_json(CONFIG, {"munis": {}})["munis"]
    names = party_names()
    draft = load_json(DRAFT, {"munis": {}}).get("munis", {})
    pub = load_json(PUBLISHED, {"munis": {}}).get("munis", {})
    pub_last = {}
    for mid, m in pub.items():
        snaps = m.get("snapshots") or []
        if snaps:
            pub_last[mid] = {
                "votesCounted": snaps[-1].get("votesCounted"),
                "at": snaps[-1].get("at"),
            }
    munis = []
    for mid, c in sorted(cfg.items(),
                         key=lambda kv: is_sort_key(kv[1]["name"])):
        dr = draft.get(mid)
        pb = pub_last.get(mid)
        # "Needs confirm" = the draft holds info not yet on the live
        # channel: a muni never published, or a draft vote-count that
        # differs from what was last published. Clears once published
        # (published==draft) on the next reload.
        needs_confirm = bool(dr) and (
            pb is None or dr.get("votesCounted") != pb.get("votesCounted"))
        munis.append({
            "id": mid,
            "name": c["name"],
            "region": c["region"],
            "totalSeats": c["totalSeats"],
            "seatsUnverified": c.get("seatsUnverified", False),
            "parties": [{"code": L, "name": names.get(L, L)}
                        for L in c["partyIds"]],
            "draft": dr,
            "published": pb,
            "needsConfirm": needs_confirm,
        })
    return {"munis": munis, "generatedAt": now_iso()}


def validate_and_norm(mid, cfg, body):
    """Return (entry|None, warnings[]). entry is the draft muni object."""
    warn = []
    c = cfg.get(mid)
    if not c:
        return None, [f"{mid}: unknown muni"]
    valid = set(c["partyIds"])
    raw = body.get("parties") or {}
    pct = {}
    for k, v in raw.items():
        if k not in valid:
            warn.append(f"unknown party '{k}' ignored")
            continue
        if v is None or v == "":
            continue
        try:
            f = float(v)
        except (TypeError, ValueError):
            warn.append(f"{k}: '{v}' is not a number — ignored")
            continue
        if f < 0 or f > 100:
            warn.append(f"{k}: {f} out of 0–100")
        pct[k] = f
    votes = body.get("votesCounted")
    try:
        votes = int(votes)
    except (TypeError, ValueError):
        votes = None
    if not pct and votes in (None, 0):
        return "DELETE", warn       # empty row → clear from draft
    s = sum(pct.values())
    if pct and not (90.0 <= s <= 110.0):
        warn.append(f"party % sum = {s:.1f} (expected ≈100)")
    if votes is None:
        warn.append("votes counted missing → recorded as 0")
        votes = 0
    return {"votesCounted": votes, "at": now_iso(), "parties": pct}, warn


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):           # quiet
        pass

    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj, ensure_ascii=False))

    def do_GET(self):
        if self.path.split("?")[0] == "/":
            self._send(200, PAGE.replace("__STATE__",
                       json.dumps(build_state(), ensure_ascii=False)),
                       "text/html")
        elif self.path.split("?")[0] == "/api/state":
            self._json(200, build_state())
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        ln = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(ln) or b"{}")
        except Exception:
            return self._json(400, {"error": "bad json"})
        route = self.path.split("?")[0]
        cfg = load_json(CONFIG, {"munis": {}})["munis"]

        if route in ("/api/save", "/api/save-all"):
            rows = body.get("rows") if route == "/api/save-all" else [body]
            draft = load_json(DRAFT, {"munis": {}})
            draft.setdefault("munis", {})
            results = []
            for r in rows:
                mid = r.get("muniId")
                entry, warn = validate_and_norm(mid, cfg, r)
                if entry == "DELETE":
                    draft["munis"].pop(mid, None)
                    results.append({"muniId": mid, "ok": True,
                                    "cleared": True, "warnings": warn})
                    continue
                if entry is None:
                    results.append({"muniId": mid, "ok": False,
                                    "warnings": warn})
                    continue
                draft["munis"][mid] = entry
                seats = dhondt(entry["parties"],
                               cfg[mid]["totalSeats"]) if entry["parties"] else {}
                results.append({
                    "muniId": mid, "ok": True, "warnings": warn,
                    "at": entry["at"],
                    "sumPct": round(sum(entry["parties"].values()), 1),
                    "seats": {k: v for k, v in seats.items() if v},
                })
            DRAFT.parent.mkdir(parents=True, exist_ok=True)
            DRAFT.write_text(
                json.dumps(draft, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8")
            return self._json(200, {"results": results,
                                    "draftMunis": len(draft["munis"])})

        return self._json(404, {"error": "not found"})


PAGE = r"""<!DOCTYPE html><html lang="is"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kosninganiðurstöður — innsláttur</title>
<style>
:root{color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:#0c1422;color:#e7eef7;font:13px/1.4 Inter,system-ui,sans-serif}
header{position:sticky;top:0;z-index:5;background:#0f1a2e;border-bottom:1px solid #24344f;
  padding:10px 16px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
header h1{font-size:15px;margin:0;font-weight:700}
header .sp{flex:1}
input,button,select{font:inherit;color:#e7eef7}
input[type=text],input[type=number]{background:#0c1422;border:1px solid #2c3f5e;
  border-radius:5px;padding:5px 7px}
input.pct{width:58px;text-align:right}
input.votes{width:88px;text-align:right}
button{background:#1a56db;border:0;border-radius:6px;padding:7px 13px;font-weight:600;cursor:pointer}
button.sec{background:#26344d}
button.row{padding:5px 10px;font-size:12px}
#q{width:220px}
.region{color:#7d92b3;font-size:11px;margin-left:6px}
.muni{font-weight:600}
.seatsbadge{color:#8fe3b5;font-size:11px;font-variant-numeric:tabular-nums}
.sum{font-variant-numeric:tabular-nums;font-weight:600}
.sum.bad{color:#ff8a8a}.sum.ok{color:#8fe3b5}
.pub{color:#7d92b3;font-size:11px}
.st{font-size:11px}
.st.ok{color:#8fe3b5}.st.warn{color:#ffcf6b}.st.err{color:#ff8a8a}
small.note{color:#7d92b3}
</style></head><body>
<header>
  <h1>🗳️ Kosninganiðurstöður — innsláttur</h1>
  <input type="text" id="q" placeholder="Leita að sveitarfélagi…">
  <select id="reg"></select>
  <label style="font-size:12px;color:#cfe0f5;display:flex;align-items:center;gap:5px;cursor:pointer">
    <input type="checkbox" id="ncOnly"> aðeins óstaðfest</label>
  <select id="sort" title="Röðun sveitarfélaga">
    <option value="name">Röð: stafrófsröð</option>
    <option value="recent">Röð: nýjustu tölur efst</option>
  </select>
  <span class="sp"></span>
  <small class="note" id="meta"></small>
  <button class="sec" id="reload">↻ Endurhlaða af diski</button>
  <button id="saveall">💾 Vista allt breytt</button>
</header>
<div id="wrap"></div>
<script>
const STATE = __STATE__;
const $ = s => document.querySelector(s);

function dhondt(pct, total){
  const s={}; for(const c in pct) s[c]=0;
  for(let i=0;i<total;i++){let bc=null,bq=-1;
    for(const c in pct){const q=pct[c]/(s[c]+1); if(q>bq){bq=q;bc=c;}}
    if(bc===null)break; s[bc]++;}
  return s;
}
function seatStr(pct,total){
  const ps=Object.fromEntries(Object.entries(pct).filter(([k,v])=>v>0));
  if(!Object.keys(ps).length) return '';
  const s=dhondt(ps,total);
  return Object.entries(s).filter(([k,v])=>v).sort((a,b)=>b[1]-a[1])
    .map(([k,v])=>k+' '+v).join(' · ');
}

const regions=[...new Set(STATE.munis.map(m=>m.region))].sort();
const regSel=$('#reg');
regSel.innerHTML='<option value="">Öll svæði</option>'+
  regions.map(r=>`<option>${r}</option>`).join('');

// Party columns differ per muni (each has its own ballot letters), so each
// muni is rendered as its own flex row with inline letter-tagged inputs
// rather than one rigid table.
function render(){
  const blocks=STATE.munis.map(m=>{
    const d=m.draft||{}; const dp=d.parties||{};
    const inputs=m.parties.map(p=>{
      const v=dp[p.code]!=null?dp[p.code]:'';
      return `<label class="pcell" title="${p.name}">
        <span class="plet">${p.code}</span>
        <input class="pct" data-c="${p.code}" value="${v}" inputmode="decimal">
      </label>`;
    }).join('');
    const pub=m.published?`<span class="pub">síðast birt: ${Number(m.published.votesCounted||0).toLocaleString('is-IS')} atkv · kl. ${(m.published.at||'').slice(11,16)}</span>`:'<span class="pub">engin birt tala enn</span>';
    const nc=m.needsConfirm
      ?'<span class="nc-badge" title="Nýjar tölur úr skrapi sem á eftir að staðfesta/birta">● óstaðfest</span>':'';
    return `<div class="mrow${m.needsConfirm?' needs-confirm':''}" data-id="${m.id}" data-name="${m.name.toLowerCase()}" data-region="${m.region}" data-nc="${m.needsConfirm?1:0}">
      <div class="mhead">
        <div><span class="muni">${m.name}</span>${m.seatsUnverified?' <span title="Staðfesta sætafjölda fyrir kvöldið">⚠</span>':''}${nc}
          <span class="region">${m.region} · ${m.totalSeats} sæti</span></div>
        <div>${pub}</div>
      </div>
      <div class="mbody">
        <label class="pcell vc"><span class="plet">Atkv. talin</span>
          <input class="votes" data-votes value="${d.votesCounted!=null?d.votesCounted:''}" inputmode="numeric"></label>
        ${inputs}
        <span class="sum" data-sum>Σ –</span>
        <span class="seatsbadge" data-seats></span>
        <button class="row sec" data-save>Vista</button>
        <span class="st" data-st></span>
      </div>
    </div>`;
  }).join('');
  $('#wrap').innerHTML=blocks;
  document.querySelectorAll('.mrow').forEach(recalc);
  const ncN=STATE.munis.filter(m=>m.needsConfirm).length;
  $('#meta').textContent=`${STATE.munis.length} sveitarfélög`+
    (ncN?` · ${ncN} óstaðfest`:` · ekkert óstaðfest`)+
    ` · uppfært ${STATE.generatedAt.slice(11,16)}`;
  applySort();
}

function collect(row){
  const parties={};
  row.querySelectorAll('input.pct').forEach(i=>{
    if(i.value.trim()!=='') parties[i.dataset.c]=parseFloat(i.value);
  });
  const vraw=row.querySelector('input.votes').value.trim();
  return {muniId:row.dataset.id,
    votesCounted: vraw===''?null:parseInt(vraw,10),
    parties};
}
function recalc(row){
  const m=STATE.munis.find(x=>x.id===row.dataset.id);
  const {parties}=collect(row);
  const sum=Object.values(parties).reduce((a,b)=>a+(+b||0),0);
  const se=row.querySelector('[data-sum]');
  se.textContent='Σ '+(sum?sum.toFixed(1):'–');
  se.className='sum '+(!sum?'':(sum>=95&&sum<=105?'ok':'bad'));
  row.querySelector('[data-seats]').textContent=seatStr(parties,m.totalSeats);
}
async function save(rows){
  const payload=rows.length===1
    ? rows[0] : {rows};
  const url=rows.length===1?'/api/save':'/api/save-all';
  const res=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify(payload)}).then(r=>r.json());
  const arr=res.results||[];
  arr.forEach(r=>{
    const row=document.querySelector(`.mrow[data-id="${r.muniId}"]`);
    if(!row)return;
    const st=row.querySelector('[data-st]');
    if(r.cleared){st.textContent='hreinsað';st.className='st warn';return;}
    if(!r.ok){st.textContent='✗ '+(r.warnings||[]).join('; ');st.className='st err';return;}
    st.textContent='✓ '+ (r.at||'').slice(11,16) +
      ((r.warnings&&r.warnings.length)?' ⚠ '+r.warnings.join('; '):'');
    st.className='st '+((r.warnings&&r.warnings.length)?'warn':'ok');
  });
  $('#meta').textContent=`vistað · ${res.draftMunis} sveitarfélög í drögum`;
}

$('#wrap').addEventListener('input',e=>{
  const row=e.target.closest('.mrow'); if(row)recalc(row);
});
$('#wrap').addEventListener('click',e=>{
  if(e.target.matches('[data-save]')){
    const row=e.target.closest('.mrow'); save([collect(row)]);
  }
});
$('#saveall').addEventListener('click',()=>{
  const rows=[...document.querySelectorAll('.mrow')]
    .map(collect).filter(r=>Object.keys(r.parties).length||r.votesCounted!=null);
  if(rows.length) save(rows); else $('#meta').textContent='ekkert til að vista';
});
$('#reload').addEventListener('click',async()=>{
  const s=await fetch('/api/state').then(r=>r.json());
  STATE.munis=s.munis; STATE.generatedAt=s.generatedAt; render();
});
function applyFilter(){
  const q=$('#q').value.toLowerCase().trim();
  const r=$('#reg').value;
  const ncOnly=$('#ncOnly').checked;
  document.querySelectorAll('.mrow').forEach(row=>{
    const ok=(!q||row.dataset.name.includes(q))
      &&(!r||row.dataset.region===r)
      &&(!ncOnly||row.dataset.nc==='1');
    row.style.display=ok?'':'none';
  });
}
// Sort the rendered rows in place (moves existing nodes, so any unsaved
// input + the per-row status are preserved). "name" = the server's
// Icelandic-alphabetical order; "recent" = newest RÚV figure first
// (draft.at, which is RÚV's per-muni update time), munis with no draft
// data last in their original alphabetical order.
function applySort(){
  const mode=$('#sort').value;
  const wrap=$('#wrap');
  const idx=new Map(STATE.munis.map((m,i)=>[m.id,i]));
  const atOf=id=>{const m=STATE.munis[idx.get(id)];
    return (m&&m.draft&&m.draft.at)||'';};
  const rows=[...wrap.children];
  rows.sort((a,b)=>{
    const ia=idx.get(a.dataset.id), ib=idx.get(b.dataset.id);
    if(mode==='recent'){
      const ta=atOf(a.dataset.id), tb=atOf(b.dataset.id);
      if(ta&&tb&&ta!==tb) return tb<ta?-1:1;   // newest first
      if(ta&&!tb) return -1;                    // has data → above no-data
      if(!ta&&tb) return 1;
    }
    return ia-ib;                               // tie / name → server order
  });
  rows.forEach(r=>wrap.appendChild(r));
}
$('#q').addEventListener('input',applyFilter);
$('#reg').addEventListener('change',applyFilter);
$('#ncOnly').addEventListener('change',applyFilter);
$('#sort').addEventListener('change',applySort);
render();
</script>
<style>
.mrow{border-bottom:1px solid #16233c;padding:8px 16px;border-left:3px solid transparent}
.mrow:hover{background:#0f1c33}
.mrow.needs-confirm{border-left-color:#ffb02e;background:rgba(255,176,46,.06)}
.nc-badge{margin-left:8px;font-size:10px;font-weight:700;letter-spacing:.03em;
  color:#ffb02e;border:1px solid rgba(255,176,46,.5);border-radius:5px;
  padding:1px 6px;vertical-align:1px}
.mhead{display:flex;justify-content:space-between;gap:12px;align-items:baseline;margin-bottom:5px}
.mbody{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.pcell{display:flex;flex-direction:column;align-items:center;gap:2px}
.pcell .plet{font-size:10px;color:#9fb2cc}
.pcell.vc .plet{color:#cfe0f5}
.pcell input.pct{width:56px;text-align:right;padding:4px 5px}
.pcell input.votes{width:92px;text-align:right;padding:4px 5px}
.sum{margin-left:6px}
.seatsbadge{min-width:120px}
.st{min-width:120px}
</style>
</body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=5050)
    args = ap.parse_args()
    if not CONFIG.exists():
        print("ERROR: data/muni_config.json missing — run "
              "scripts/build_muni_config.py first.", file=sys.stderr)
        return 2
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    n = len(load_json(CONFIG, {"munis": {}})["munis"])
    print(f"Results backend — {n} contested munis")
    print(f"  → http://127.0.0.1:{args.port}")
    print(f"  draft file: {DRAFT}")
    print("  (local only · never pushes · Ctrl+C to stop)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
