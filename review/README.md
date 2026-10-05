# 외부 리뷰 묶음 — Gemini · ChatGPT · 코치에게 줄 것

채팅 AI 는 게임을 직접 해 볼 수 없어요. 그래서 **카드는 글로(`cards.md`), 화면은 그림으로(`screens/`)** 묶어 뒀어요.
아래에서 리뷰 종류를 고르고, **주는 것**을 첨부하거나 링크로 준 뒤 **붙여 넣을 말**을 그대로 쓰면 돼요.

- 게임: <https://myheecheol.github.io/tennis/>
- 저장소: <https://github.com/myheecheol/tennis> (공개)
- 파일을 링크로 줄 때: `https://raw.githubusercontent.com/myheecheol/tennis/HEAD/<경로>` — 예: [`review/cards.md`](https://raw.githubusercontent.com/myheecheol/tennis/HEAD/review/cards.md)
- 화면 그림은 링크로는 잘 안 보이니 **내려받아 첨부**하세요 — <https://github.com/myheecheol/tennis/tree/HEAD/review/screens>

---

## 지금 무엇이 있나 — html 파일 하나?

**배포되는 것**은 `site/index.html` 한 파일(약 450KB)이에요. 그런데 이건 결과물이고, 아래 원본들을 `web/build.py` 가 한 파일로 묶은 거예요.

| 원본 | 무엇 |
|---|---|
| `web/play.template.html` | 게임 화면과 규칙 — 닉네임 · 튜토리얼 · 오늘의 코트 · 복습 · 실전 모드 · 원 포인트 게임 · 기록 · 검증 지표 |
| `web/src/court.js` · `court.css` | 코트 엔진 — 3D 코트 · 공 궤적 · 고르면 공과 사람이 움직이는 결과 재생 · 카드 사이 이어지기 |
| `data/cards/c1~c5.json` | 상황 카드 120장 (5챕터 × 24) — 읽기용은 `review/cards.md` |
| `data/chains.json` · `cards-index.json` · `cameras.json` | 이어지는 카드 짝 · 커리큘럼 목차 · 카메라 규격 |
| `design/*.md` | 기획서(PRD) · 게임 설계 · Phase 1 운영 · 내용 감수 · 배포 점검 |
| `reference/*.md` | 복식 전술 원리(P-01~05) · 코트 좌표 규격 · 카드 예시 |
| `tools/` | 카드 검증기 · 빌드 · 웹 테스트(헤드리스 브라우저로 63가지 흐름) |
| `firebase/firestore.rules` | 기록 권한 — 참여자는 자기 문서만, 만든 사람은 모두 읽기 |

---

## A. 기획 · 화면(UX) 리뷰

**주는 것** — `screens/` 의 그림 12장 첨부 (파일 이름이 화면 이름이에요)

**붙여 넣을 말**

```text
너는 모바일 학습 게임을 많이 만들어 본 UX 디자이너이자 게임 기획자야.
첨부한 화면 12장은 '복식 무브'라는 웹 게임이야. 테니스 복식을 막 시작한 동호인(주로 30~60대, 폰으로 한다)이
"지금 어디로 움직이고, 공을 어디로 보낼지"를 상황 카드로 배운다.

흐름: 닉네임 → 튜토리얼 카드 1장(튜토리얼 1/4~4/4) → 메인 화면.
메인에서 고르는 것: 오늘의 코트(새 카드 5장 + 복습) · 츄어리와 실전(상대 캐릭터와 한 게임, 카드마다 10초, 랠리가 이어지면 저절로 다음 공)
· 원 포인트 게임!(정답이면 다음 수로 이어지는 카드 짝). 카드 한 장: 제목 → 공이 날아와 멈춤 → 상황 글 → 질문과 보기 A·B·C
→ 고르면 공과 사람이 그대로 움직이는 결과(✓ 성공 · △ 아쉬움 · ✕ 실패) → 해설. 마지막 그림(12)은 만든 사람만 보는 검증 지표다.

화면을 보고 찾아 줘:
1) 처음 쓰는 사람이 헷갈리거나 멈출 곳 2) 다시 오고 싶게 만들 장치 3) 글자 크기 · 버튼 · 배치 · 색 문제 4) 말투(해요체)가 어색한 곳.
이미 알고 있는 것은 빼 줘: 안드로이드 뒤로 가기, 10초가 짧은 사람을 위한 옵션, 기록 지우기, 결과 공유 카드, 홈이 길다는 점.

결과는 표로: 우선순위(높음/중간/낮음) · 화면(파일 이름) · 문제 · 왜 문제인지 · 구체적인 수정안. 많아야 15개, 높음부터.
```

## B. 테니스 전술 내용 감수

**주는 것** — `review/cards.md` (첨부하거나 위 링크). 원리를 더 보려면 `reference/doubles-domain-pack.md` 도

**붙여 넣을 말**

```text
너는 생활체육 테니스 복식 코치야. 첨부한 cards.md 는 복식 초보에게 가르치는 상황 카드 120장이다.
카드마다 상황 · 단서 · 질문 · 보기 셋(✓ 정답 · △ 차선 · ✕ 실수)과 이유, 고르면 벌어지는 일, '코치 한 줄'이 있다.
자리 표기(A-RX 같은 것)는 파일 맨 위에 설명이 있다.

카드마다 확인해 줘:
1) 정답이 초보에게 맞는 정석인가 (동호인 복식 기준)
2) 차선과 실수의 구분이 맞는가 — 차선 = 될 때도 있지만 덜 좋은 선택, 실수 = 포인트를 잃기 쉬운 선택
3) 이유와 '코치 한 줄'이 정확하고 초보가 알아듣기 쉬운가
4) 한국 동호인이 실제로 쓰는 말인가 (포치 · 로브 · 넷맨 · 듀스 코트 등)
5) 카드끼리 서로 다른 말을 하는 곳

문제가 있는 카드만 표로: 카드 ID · 어디(정답/차선/실수/해설/코치 한 줄) · 문제 · 근거 · 고칠 문장.
확신이 낮으면 '확인 필요'라고 표시해 줘. 문제없는 카드는 적지 않아도 된다.
```

## C. 코드 리뷰

**주는 것** — 아래 셋을 첨부하거나 링크로

- [`web/play.template.html`](https://raw.githubusercontent.com/myheecheol/tennis/HEAD/web/play.template.html)
- [`web/src/court.js`](https://raw.githubusercontent.com/myheecheol/tennis/HEAD/web/src/court.js)
- [`firebase/firestore.rules`](https://raw.githubusercontent.com/myheecheol/tennis/HEAD/firebase/firestore.rules)

**붙여 넣을 말**

```text
너는 시니어 프런트엔드 엔지니어야. 첨부한 건 프레임워크 없이 바닐라 JS 로 만든 웹 게임이고,
web/build.py 가 카드 데이터 · 엔진 · 그림을 한 HTML 파일로 묶어 GitHub Pages 에 올린다.
play.template.html = 화면과 게임 규칙, court.js = SVG 로 그리는 3D 코트 엔진, firestore.rules = 기록 권한.
기록은 Firebase(익명 로그인 + Firestore, 참여자마다 문서 하나 players/<uid>)로 받고,
만든 사람은 Google 로그인으로 모든 문서를 읽어 검증 지표를 본다.

찾아 줘: 1) 버그 — 특히 화면 상태 꼬임, 10초 타이머, 저장 · 동기화 2) 보안 — XSS, Firestore 규칙의 빈틈, 남용
3) 저사양 안드로이드 성능 — 애니메이션 프레임마다 SVG 를 다시 그린다 4) 접근성 5) iOS 사파리 · 카카오톡 인앱 브라우저 문제.

결과는 표로: 심각도 · 파일과 함수(또는 줄) · 문제 · 재현 방법 · 고칠 코드. 추측이면 추측이라고 써 줘.
```

> GitHub 연결이나 '코드 가져오기' 기능이 있는 AI 라면 저장소 주소를 통째로 주고
> "`design/PRD.md` 와 `review/README.md` 부터 읽고 위 질문에 답해 줘" 라고 해도 돼요.

---

## 받은 결과는

표를 그대로 **이 대화(Claude)** 에 붙여 주세요. 하나씩 실제 코드 · 카드와 대조해 맞는 것만 고치고,
카드를 고치면 검증기(공의 길 · 채점 · 말투)와 웹 테스트를 다시 돌려요.
AI 끼리도 테니스 전술은 틀릴 수 있어요 — 전술의 최종 판단은 **코치 감수**로 해요.

이미 찾아 둔 보완점은 `design/10-launch-review.md` 에 있어요 (같은 걸 또 찾지 않게 리뷰어에게 알려 줘도 좋아요).

---

`cards.md` 는 `bash tools/check.sh` 가 매번 새로 만들어요. 화면 그림은 바뀔 때만 `python3 tools/review_pack.py --screens` 로 다시 찍어요 (지금 그림: 2026-10-05).
