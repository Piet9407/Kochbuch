#!/usr/bin/env python3
"""Wandelt src/rezepte.md in site/recipes.json um."""
import json, re, sys, pathlib

root = pathlib.Path(sys.argv[1])
md = (root / "src" / "rezepte.md").read_text(encoding="utf-8")

FR = {"½": 0.5, "¼": 0.25, "¾": 0.75, "⅛": 0.125, "⅓": 1/3, "⅔": 2/3}
UNITS = ["kg", "g", "ml", "l", "EL", "TL", "Prisen", "Prise", "Dosen", "Dose", "Packung", "Bund",
         "Handvoll", "Zehen", "Zehe", "Scheiben", "Stängel", "Stangen", "Glas", "Cup"]
NUM = r"(?:\d+(?:[.,]\d+)?[½¼¾⅛⅓⅔]?|[½¼¾⅛⅓⅔])"
QTY_RE = re.compile(rf"^(?P<a>{NUM})(?:\s?[–-]\s?(?P<b>{NUM}))?\s*(?P<unit>{'|'.join(UNITS)})?(?=\s|$)\s*(?P<rest>.*)$")

def num(s):
    s = s.replace(",", ".")
    m = re.match(r"^(\d+(?:\.\d+)?)?([½¼¾⅛⅓⅔])?$", s)
    return (float(m.group(1)) if m.group(1) else 0) + (FR[m.group(2)] if m.group(2) else 0)

def parse_ing(line):
    est = "≈" in line
    line = line.replace("≈", "").strip()
    line = re.sub(r"^ca\.\s*", "", line)
    opt = "(optional)" in line
    m = QTY_RE.match(line)
    q = None; q2 = None; unit = ""; rest = line
    if m:
        q = num(m.group("a"))
        q2 = num(m.group("b")) if m.group("b") else None
        unit = m.group("unit") or ""
        rest = m.group("rest").strip()
        # "1 EL Öl" etc ok; "4 ml Olivenöl(spray)" ok
    return {"raw": line, "qty": q, "qty2": q2, "unit": unit, "name": rest, "est": est, "opt": opt}

recipes = []
blocks = re.split(r"^## ", md, flags=re.M)[1:]
for b in blocks:
    head, *body = b.split("\n", 1)
    body = body[0] if body else ""
    m = re.match(r"(r\d+) · (.+)", head.strip())
    rid, title = m.group(1), m.group(2)
    meta = re.search(r"^Kategorie: (.*)$", body, re.M).group(1)
    cats = [c.strip() for c in meta.split(" · ")[0].replace("Kategorie:", "").split(",")]
    cats = [c.strip() for c in re.sub(r"^Kategorie:\s*", "", meta.split(" · ")[0]).split(",")]
    group = re.search(r"Gruppe: ([^·]+)", meta).group(1).strip()
    group = "" if group == "–" else group
    quelle = re.search(r"Quelle: (.+?)(?: · Original:|$)", meta).group(1).strip()
    link = (re.search(r"https?://[^\s)]+", quelle) or [None])[0] if re.search(r"https?://", quelle) else ""
    creator = re.match(r"(@[\w.]+)", quelle).group(1)
    orig = re.search(r"Original: (.+?)(?: · Original-Idee: (.+))?$", meta)
    original = orig.group(1).strip() if orig else ""
    idea = orig.group(2).strip() if orig and orig.group(2) else ""
    nl = re.search(r"^Nährwerte/Portion: (.*)$", body, re.M).group(1)
    nm = re.match(r"(\d+) kcal · ([\d,]+) g E · ([\d,]+) g KH · ([\d,]+) g F", nl)
    f = lambda s: float(s.replace(",", "."))
    nut = {"kcal": int(nm.group(1)), "e": f(nm.group(2)), "kh": f(nm.group(3)), "f": f(nm.group(4))}
    cm = re.search(r"\(Creator: (.*)\)\s*$", nl)
    nut["creator"] = cm.group(1) if cm else ""
    zut = re.search(r"^Zutaten:\n((?:- .*\n?)+)", body, re.M).group(1)
    ings = [parse_ing(l[2:]) for l in zut.strip().split("\n")]
    sm = re.search(r"^Zubereitung(?: \((.*?)\))?:\n((?:\d+\. .*\n?)+)", body, re.M)
    steps = [re.sub(r"^\d+\. ", "", l) for l in sm.group(2).strip().split("\n")]
    note = (re.search(r"^Anpassungen: (.*)$", body, re.M) or [None, ""])[1]
    recipes.append({
        "id": rid, "title": title, "cats": cats, "group": group, "creator": creator,
        "source": quelle, "link": link, "original": original, "idea": idea,
        "nut": nut, "ings": ings, "steps": steps, "stepsNote": sm.group(1) or "", "note": note,
    })

out = root / "site"
out.mkdir(exist_ok=True)
(out / "recipes.json").write_text(json.dumps(recipes, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(recipes), "Rezepte,", sum(len(r["ings"]) for r in recipes), "Zutaten")
bad = [(r["id"], i["raw"]) for r in recipes for i in r["ings"] if i["qty"] is None and not re.search(r"Salz|Pfeffer|Öl|Gewürz|Kräuter|Oregano|Paprika|Petersilie|Zwiebelpulver|Kreuzk|Knoblauch|Cumin|Basilikum|Schuss|etwas|einige|Schnittlauch|Zitronensaft|Süße|Lorbeer|Salat|Rotwein|Feta|Gewürze|Chiasamen|Kräuter", i["raw"])]
print("Ohne Menge (prüfen):", bad)
