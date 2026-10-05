#!/usr/bin/env python3
"""외부 리뷰 묶음(review/) — Gemini · ChatGPT · 코치에게 줄 자료를 만든다.

  python3 tools/review_pack.py            review/cards.md — 카드 120장을 읽기 쉬운 글로 (check.sh 가 매번 갱신)
  python3 tools/review_pack.py --screens  review/screens/*.png — 폰 화면 12장 (헤드리스 Chromium, 필요할 때만)

채팅 AI 는 게임을 직접 해 볼 수 없으니, 카드는 글로 · 화면은 그림으로 준다. 쓰는 법은 review/README.md."""
import glob, json, pathlib, re, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "review"

QTYPE = {"move": "어디로 움직일까", "target": "어디로 보낼까", "both": "움직이며 보내기", "readNext": "다음 공 읽기"}


def principles():
    txt = (ROOT / "reference" / "doubles-domain-pack.md").read_text(encoding="utf-8")
    return {k: v.split(" — ")[0] for k, v in re.findall(r"\*\*(P-\d+)\. ([^*]+?)\*\*", txt)}


def render_cards():
    P = principles()
    files = sorted((ROOT / "data" / "cards").glob("c*.json"))
    total = sum(len(json.loads(f.read_text(encoding="utf-8"))["cards"]) for f in files)
    L = [f"# 복식 무브 — 상황 카드 {total}장 (읽기용)", "",
         "> 자동 생성 — `python3 tools/review_pack.py` (원본 `data/cards/*.json`). 코치 · Gemini · ChatGPT 가 읽기 쉽게 풀었다.",
         "> 카드마다: 상황 → 질문 → 보기 셋(✓ 정답 · △ 차선 · ✕ 실수)과 이유 · 고르면 코트에서 벌어지는 일 한 줄 → 코치 한 줄.",
         "> 게임에서는 보기 순서가 섞이고, 고르면 공과 사람이 그대로 움직여 결과가 보인다. 여기서는 정답을 먼저 적었다.",
         "> 대상: 복식을 막 시작한 동호인(초보). 앱 안의 말투는 해요체.", "",
         "**자리 표기** — `A` 우리 코트 · `E` 상대 코트 / `L` 왼쪽 · `C` 가운데 · `R` 오른쪽 (늘 **우리 베이스라인에서 네트를 볼 때** 기준, 상대 코트도 같은 방향) /",
         "`N` 네트 가까이 · `M` 서비스 박스 부근 · `B` 베이스라인 가까이 · `X` 베이스라인 뒤. 예: `A-RX` 우리 오른쪽 베이스라인 뒤(듀스 코트 서브 자리), `E-LN` 상대 왼쪽 네트 앞.", "",
         "**원리** — " + " · ".join(f"{k} {v}" for k, v in sorted(P.items())) + " (자세히: `reference/doubles-domain-pack.md`)", ""]
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        L += ["", f"## {d['chapter'][1:]}챕터 · {d['title']} ({len(d['cards'])}장)", ""]
        for c in d["cards"]:
            st, a = c["setup"], c["answer"]
            who = f"나 `{st['me']['zone']}` · 짝 `{st['partner']['zone']}` · 상대1 `{st['opp1']['zone']}` · 상대2 `{st['opp2']['zone']}` · 공: {st['ball'].get('kind', '')}"
            L += [f"### {c['id']} · {c['title']}",
                  f"역할 **{c['myRole']}** · 단계 {c['phase']} · 난이도 {c.get('difficulty', '')} · 질문 종류: {QTYPE.get(c['question']['type'], c['question']['type'])}"
                  + (f" · 먼저 볼 카드 {', '.join(c['prereq'])}" if c.get("prereq") else ""), "",
                  f"- **자리** {who}",
                  f"- **상황** {c['scene']}"]
            if c.get("cue"):
                L.append(f"- **단서** {c['cue']}")
            L.append(f"- **질문** {c['question']['text']}")
            pr = a.get("principle", "")
            L.append(f"- ✓ **정답 — {a['short']}** (`{a['zone']}`) {a['why']}" + (f" _[{pr} {P.get(pr, '')}]_" if pr else "")
                     + (f" → 고르면: {a['caption']}" if a.get("caption") else ""))
            for x in sorted(c["distractors"], key=lambda x: x["severity"] != "차선"):
                mk = "△" if x["severity"] == "차선" else "✕"
                L.append(f"- {mk} **{x['severity']} — {x['short']}** (`{x['zone']}`) {x['why']}" + (f" → 고르면: {x['caption']}" if x.get("caption") else ""))
            L.append(f"- **코치 한 줄** “{c['coachLine']}”")
            if c.get("next"):
                L.append(f"- **다음 수** {c['next']['text']} → {c['next']['id']}")
            L.append("")
    OUT.mkdir(exist_ok=True)
    text = "\n".join(L).rstrip() + "\n"
    (OUT / "cards.md").write_text(text, encoding="utf-8")
    print(f"review/cards.md  {len(text):,} chars · 카드 {total}장")


# ── 화면 — 폰 폭 375px · 2배 해상도. 움직임 줄이기로 장면을 끝 모습에 세운다 ──
def find_chrome():
    import os
    cands = [os.environ.get("CHROME_BIN", "")] + sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"))
    cands += [shutil.which(n) or "" for n in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable")]
    return next((c for c in cands if c and os.path.exists(c)), None)


def render_screens():
    sys.path.insert(0, str(ROOT / "tools"))
    import web_smoke as W   # 같은 저장 상태 · 가짜 저장소를 쓴다
    chrome = find_chrome()
    if not chrome:
        print("⏭  브라우저가 없어 화면을 건너뜁니다")
        return
    page = (ROOT / "web" / "play.html").read_text(encoding="utf-8")
    m = re.search(r'<script id="config-data" type="application/json">(.*?)</script>', page, re.S)
    cfg = json.loads(m.group(1)); cfg.update(W.FB_OFF)
    page = page[:m.start(1)] + json.dumps(cfg, ensure_ascii=False) + page[m.end(1):]
    played = W.state([(cid, "정답", None) for cid in W.IDS[:5]]); played["nick"] = "희철"
    newbie = {"v": 1, "uid": "p_shot", "nick": "희철", "cards": {}}
    ask = "for(var k=0;k<4&&q('#gs').getAttribute('data-phase')!=='ask';k++)click('#gs-court');"
    pick = ("function pick(w){var id=q('#p-id').textContent,c=JSON.parse(q('#card-data').textContent).filter(function(x){return x.id===id;})[0],i=0;"
            "Court.optsOf(c).forEach(function(x,j){if(x.v===w)i=j;});click('#p-opts [data-opt=\"'+i+'\"]');}")
    lose = "for(var k=0;k<30;k++){if(!q('#s-done').hidden)break;pick('실수');if(q('[data-act=match-next]'))click('[data-act=match-next]');}"
    shots = [  # 이름, 저장 상태, 차례대로 할 일(ms 뒤, 코드), 가짜 저장소, 높이 (, 찍는 때 ms — 저절로 넘어가기 전에 찍을 때)
        ("01-닉네임", None, [], "", 812),
        ("02-튜토리얼-제목", newbie, [], "", 812),
        ("03-튜토리얼-질문", newbie, [[150, ask]], "", 812),
        ("04-튜토리얼-결과", newbie, [[150, ask], [150, "pick('정답')"]], "", 812),
        ("05-튜토리얼-해설", newbie, [[150, ask], [150, "pick('정답')"], [150, "click('#gs-court')"]], "", 812),
        ("06-메인", played, [], "", 1500),
        ("07-실전-로비", played, [[150, "click('[data-act=match-open]')"]], "", 1200),
        ("08-실전-질문", played, [[150, "click('[data-act=match-open]')"], [150, "click('[data-act=match-start]')"]], "", 812, 1500),
        ("09-실전-랠리계속", played, [[150, "click('[data-act=match-open]')"], [150, "click('[data-act=match-start]')"], [150, "pick('차선')"]], "", 812, 1600),
        ("10-실전-결과", played, [[150, "click('[data-act=match-open]')"], [150, "click('[data-act=match-start]')"], [150, lose]], "", 1300),
        ("11-원포인트-두번째수", W.state([(cid, "정답", None) for cid in ("C2-08", "C3-09")]),
         [[150, "click('[data-act=chain-start]')"], [150, ask], [150, "pick('정답')"], [150, "click('[data-act=explain]')"],
          [150, "click('[data-act=chain-next]')"]], "", 812),
        ("12-검증지표", played, [[400, "click('[data-act=stats]')"]], W.DB_MOCK, 1700),
    ]
    out = OUT / "screens"
    out.mkdir(parents=True, exist_ok=True)
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="dmb-shots-"))
    for name, st, steps, mock, h, *at in shots:
        stj = ('try{localStorage.setItem("dmb-game-v1",' + json.dumps(json.dumps(st, ensure_ascii=False)) + ')}catch(e){}'
               if st else 'try{localStorage.removeItem("dmb-game-v1")}catch(e){}')
        probe = ("<script>(function(){function q(s){return document.querySelector(s);}function click(s){var e=q(s);if(e)e.dispatchEvent(new MouseEvent('click',{bubbles:true}));}"
                 + pick + "var S=" + json.dumps(steps, ensure_ascii=False) + ",i=0;"
                 "setTimeout(function n(){if(i>=S.length)return;var s=S[i++];setTimeout(function(){try{(new Function('q','click','pick',s[1]))(q,click,pick);}catch(e){}n();},s[0]);},500);})();</script>")
        (tmp / "p.html").write_text(W.PRE.replace("{REDUCED}", "true").replace("{STATE}", stj).replace("{MOCK}", mock) + page + probe, encoding="utf-8")
        # 헤드리스 창은 500px 보다 좁아지지 않는다 — 375px 틀(iframe) 안에 띄우고 그 폭만 잘라 낸다
        (tmp / "w.html").write_text('<!doctype html><html><head><meta charset="utf-8"><style>body{margin:0;background:#fff}iframe{border:0;width:375px;'
                                    f'height:{h}px;display:block}}</style></head><body><iframe src="p.html"></iframe></body></html>', encoding="utf-8")
        png = out / (name + ".png")
        subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                        f"--window-size=500,{h}", f"--virtual-time-budget={at[0] if at else 6000}", f"--screenshot={png}", (tmp / "w.html").as_uri()],
                       capture_output=True, timeout=120)
        try:   # 틀 폭만 남기고, 크기를 줄인다 (PIL 이 있으면)
            from PIL import Image
            im = Image.open(png).convert("RGB")
            im = im.crop((0, 0, min(im.width, 750), im.height))
            px, bottom = im.load(), im.height   # 아래쪽 빈 흰 줄(창 밖)을 잘라 낸다 — 게임 바탕은 연두라 흰 줄이 없다
            while bottom > 200 and all(px[x, bottom - 1] == (255, 255, 255) for x in range(0, im.width, 7)):
                bottom -= 1
            im.crop((0, 0, im.width, bottom)).save(png, optimize=True)
        except Exception:
            pass
        print(f"review/screens/{png.name}  {png.stat().st_size // 1024} KB")
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    render_cards()
    if "--screens" in sys.argv:
        render_screens()
