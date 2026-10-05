#!/usr/bin/env python3
"""영어판 검사 (PRD #30) — 빠진 번역 · 한글이 섞인 번역 · 너무 긴 보기.

  화면 글: web/play.template.html 의 t('…') · data-t · data-t-aria · data-t-ph · REASONS · RANK_SAY · VERD · LV 를 모아
           web/i18n/en.json 의 ui 에 다 있는지 본다 (열쇠는 한국어 원문).
  카드 글: data/i18n/en/c*.json 에 카드 120장이 다 있고, 칸이 다 차 있는지.
  이름:    역할 · 부수 · 챕터.

  python3 tools/check_i18n.py          검사 (빠지면 실패)
  python3 tools/check_i18n.py --keys   화면 글 열쇠 목록만 찍는다 (번역할 때)"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
HANGUL = re.compile(r"[ᄀ-ᇿ㄰-㆏가-힣]")
TPL = (ROOT / "web" / "play.template.html").read_text(encoding="utf-8")


def js_unescape(s):
    return s.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")


def ui_keys():
    keys = set()
    for m in re.finditer(r"(?<![A-Za-z_.$])t\(\s*'((?:[^'\\\n]|\\.)*)'", TPL):
        keys.add(js_unescape(m.group(1)))
    for m in re.finditer(r'(?<![A-Za-z_.$])t\(\s*"((?:[^"\\\n]|\\.)*)"', TPL):
        keys.add(js_unescape(m.group(1)))
    for m in re.finditer(r"<(\w+)((?:\s[^>]*)?)\sdata-t(?=[\s>])([^>]*)>(.*?)</\1>", TPL):
        keys.add(m.group(4).strip())
    for m in re.finditer(r'data-t-(?:aria|ph)="([^"]+)"', TPL):
        keys.add(m.group(1))
    for name in ("REASONS", "RANK_SAY"):
        m = re.search(name + r"=\[([^\]]*)\]", TPL)
        keys.update(x for x in re.findall(r"'([^']*)'", m.group(1)) if x)
    m = re.search(r"var VERD=\{([^}]*)\}", TPL)
    keys.update(re.findall(r":'([^']*)'", m.group(1)))
    m = re.search(r"var LV=\[(.*?)\];", TPL, re.S)
    keys.update(re.findall(r"(?:name|sub):'([^']*)'", m.group(1)))
    return {k for k in keys if HANGUL.search(k)}


def main():
    keys = ui_keys()
    if "--keys" in sys.argv:
        for k in sorted(keys):
            print(k)
        return 0
    en = json.loads((ROOT / "web" / "i18n" / "en.json").read_text(encoding="utf-8"))
    errs, warns = [], []
    ui = en.get("ui", {})
    miss = sorted(k for k in keys if k not in ui)
    errs += [f"화면 글 번역 없음: {k}" for k in miss]
    warns += [f"쓰지 않는 번역: {k}" for k in sorted(set(ui) - keys)]
    for k, v in ui.items():
        if HANGUL.search(v):
            errs.append(f"화면 글 번역에 한글: {k} → {v}")
        kp = set(re.findall(r"\{(\w+)\}", k))
        ok = kp | {"s"} | ({"opp", "name"} if any(x.startswith("opp") for x in kp) else set())   # 상대 이름은 조사 없이도 늘 같이 넘긴다
        bad = set(re.findall(r"\{(\w+)\}", v)) - ok
        if bad:
            errs.append(f"원문에 없는 자리 {bad}: {k} → {v}")
    cards = [c for f in sorted((ROOT / "data" / "cards").glob("c*.json")) for c in json.loads(f.read_text(encoding="utf-8"))["cards"]]
    tr = {}
    for f in sorted((ROOT / "data" / "i18n" / "en").glob("c*.json")):
        tr.update(json.loads(f.read_text(encoding="utf-8"))["cards"])
    for c in cards:
        e = tr.get(c["id"])
        if not e:
            errs.append(f"{c['id']} 영어 카드 없음")
            continue
        need = ["title", "scene", "cue", "question", "coach", "answer.short", "answer.why", "answer.caption",
                "lo.short", "lo.why", "lo.caption", "hi.short", "hi.why", "hi.caption"] + (["next"] if c.get("next") else [])
        for path in need:
            v = e
            for part in path.split("."):
                v = (v or {}).get(part) if isinstance(v, dict) else None
            if not v or not isinstance(v, str):
                errs.append(f"{c['id']} 빈 칸: {path}")
            elif HANGUL.search(v):
                errs.append(f"{c['id']} 한글이 섞임: {path} → {v}")
        for k in ("answer", "lo", "hi"):
            sh = (e.get(k) or {}).get("short", "")
            if len(sh) > 34:
                warns.append(f"{c['id']} {k}.short 가 길어요 ({len(sh)}자): {sh}")
        if len(e.get("title", "")) > 48:
            warns.append(f"{c['id']} 제목이 길어요 ({len(e['title'])}자)")
    extra = set(tr) - {c["id"] for c in cards}
    errs += [f"없는 카드의 번역: {x}" for x in sorted(extra)]
    roles = {c["myRole"] for c in cards}
    errs += [f"역할 번역 없음: {r}" for r in sorted(roles - set(en.get("roles", {})))]
    ranks = ["신인부", "5부", "4부", "3부", "2부", "1부"]
    errs += [f"부수 번역 없음: {r}" for r in ranks if r not in en.get("ranks", {})]
    idx = json.loads((ROOT / "data" / "cards-index.json").read_text(encoding="utf-8"))
    for ch in idx["chapters"]:
        e = en.get("chapters", {}).get(ch["id"], {})
        if not e.get("title") or not e.get("goal"):
            errs.append(f"챕터 번역 없음: {ch['id']}")
    for w in warns[:40]:
        print("  ⚠️ ", w)
    if errs:
        for x in errs[:80]:
            print("  ❌", x)
        print(f"영어판 검사 실패 {len(errs)}건" + (f" (경고 {len(warns)})" if warns else ""))
        return 1
    print(f"영어판 검사 통과 — 화면 글 {len(keys)}개 · 카드 {len(cards)}장" + (f" · 경고 {len(warns)}" if warns else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
