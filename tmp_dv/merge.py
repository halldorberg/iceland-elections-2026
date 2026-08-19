import json, sys, pathlib
out = pathlib.Path("scripts/classify_dv.json")
data = {"articles": [], "skipped": [], "possible_new_arguments": []}
if out.exists():
    data = json.loads(out.read_text(encoding="utf-8"))
new = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
known = {a["url"] for a in data["articles"]} | {s["url"] for s in data["skipped"]}
for a in new.get("articles", []):
    if a["url"] not in known:
        data["articles"].append(a); known.add(a["url"])
for s in new.get("skipped", []):
    if s["url"] not in known:
        data["skipped"].append(s); known.add(s["url"])
for p in new.get("possible_new_arguments", []):
    if p not in data["possible_new_arguments"]:
        data["possible_new_arguments"].append(p)
out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
print("articles:", len(data["articles"]), "skipped:", len(data["skipped"]))
