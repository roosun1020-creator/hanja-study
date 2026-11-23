"""한자 탐험대 v1.1.3 | 한국어문회 8급 복습 + 7급 학습."""

import json
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="한자 탐험대 v1.1.3",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 형식: 한자,대표훈,대표음. 8급/7급Ⅱ/7급 각 50자.
RAW = {
    "8급": """
一,한,일|二,두,이|三,석,삼|四,넉,사|五,다섯,오|六,여섯,륙|七,일곱,칠|八,여덟,팔|九,아홉,구|十,열,십
山,메,산|水,물,수|火,불,화|木,나무,목|金,쇠,금|土,흙,토|日,날,일|月,달,월|年,해,년|東,동녘,동
西,서녘,서|南,남녘,남|北,북녘,북|中,가운데,중|白,흰,백|靑,푸를,청|人,사람,인|大,큰,대|小,작을,소|女,계집,녀
父,아비,부|母,어미,모|兄,형,형|弟,아우,제|生,날,생|敎,가르칠,교|校,학교,교|先,먼저,선|學,배울,학|國,나라,국
軍,군사,군|民,백성,민|韓,한국,한|門,문,문|室,집,실|王,임금,왕|外,바깥,외|長,긴,장|寸,마디,촌|萬,일만,만
""",
    "7급Ⅱ": """
家,집,가|間,사이,간|江,강,강|車,수레,거|工,장인,공|空,빌,공|氣,기운,기|記,기록할,기|男,사내,남|內,안,내
農,농사,농|答,대답,답|道,길,도|動,움직일,동|力,힘,력|立,설,립|每,매양,매|名,이름,명|物,물건,물|方,모,방
不,아닐,불|事,일,사|上,윗,상|姓,성,성|世,인간,세|手,손,수|時,때,시|市,저자,시|食,밥,식|安,편안,안
午,낮,오|右,오른,우|子,아들,자|自,스스로,자|場,마당,장|電,번개,전|前,앞,전|全,온전,전|正,바를,정|足,발,족
左,왼,좌|直,곧을,직|平,평평할,평|下,아래,하|漢,한나라,한|海,바다,해|話,말씀,화|活,살,활|孝,효도,효|後,뒤,후
""",
    "7급": """
歌,노래,가|口,입,구|旗,기,기|同,한가지,동|洞,골,동|冬,겨울,동|登,오를,등|來,올,래|老,늙을,로|里,마을,리
林,수풀,림|面,낯,면|命,목숨,명|文,글월,문|問,물을,문|百,일백,백|夫,지아비,부|算,셈,산|色,빛,색|夕,저녁,석
少,적을,소|所,바,소|數,셈,수|植,심을,식|心,마음,심|語,말씀,어|然,그럴,연|有,있을,유|育,기를,육|邑,고을,읍
入,들,입|字,글자,자|祖,할아비,조|住,살,주|主,주인,주|重,무거울,중|紙,종이,지|地,땅,지|千,일천,천|天,하늘,천
川,내,천|草,풀,초|村,마을,촌|秋,가을,추|春,봄,춘|出,날,출|便,편할,편|夏,여름,하|花,꽃,화|休,쉴,휴
""",
}


def load_cards():
    groups = {}
    seen = set()
    for grade, block in RAW.items():
        cards = []
        for text in block.replace("\n", "|").split("|"):
            if not text.strip():
                continue
            char, meaning, sound = [item.strip() for item in text.split(",")]
            if char in seen:
                raise ValueError(f"한자 중복: {char}")
            seen.add(char)
            cards.append({"char": char, "meaning": meaning, "sound": sound, "grade": grade})
        if len(cards) != 50:
            raise ValueError(f"{grade} 데이터가 50자가 아닙니다: {len(cards)}")
        groups[grade] = cards
    if len(seen) != 150:
        raise ValueError("총 배정한자는 150자여야 합니다.")
    return groups


GROUPS = load_cards()
ALL = sum(GROUPS.values(), [])
INDEX = {item["char"]: item for item in ALL}
NEW = GROUPS["7급Ⅱ"] + GROUPS["7급"]
NEW_SET = {item["char"] for item in NEW}
# 같은 한자에 다른 훈음이 존재하는 예시 (문제 채점은 대표훈음 기준)
ALT = {"金": "성 김", "車": "수레 차", "洞": "밝을 통",
       "便": "똥오줌 변", "食": "먹을 식", "韓": "나라 한", "漢": "한수 한"}


def today():
    return datetime.now(ZoneInfo("Asia/Seoul")).date()


def fresh_progress():
    return {"learned": [], "cards": {}, "xp": 0, "active_days": []}


if "progress" not in st.session_state:
    st.session_state.progress = fresh_progress()
if "quiz" not in st.session_state:
    st.session_state.quiz = None
if "quiz_serial" not in st.session_state:
    st.session_state.quiz_serial = 0
if "card_cursor" not in st.session_state:
    st.session_state.card_cursor = 0


def record_activity():
    days = st.session_state.progress["active_days"]
    date = today().isoformat()
    if date not in days:
        days.append(date)


def mark_learned(char):
    progress = st.session_state.progress
    if char not in progress["learned"]:
        progress["learned"].append(char)
        progress["xp"] += 2
        record_activity()


def is_mastered(char):
    entry = st.session_state.progress["cards"].get(char, {})
    return entry.get("streak", 0) >= 3 and len(set(entry.get("correct_dates", []))) >= 2


def review_chars():
    cutoff = today().isoformat()
    history = st.session_state.progress["cards"]
    return [char for char, entry in history.items()
            if char in INDEX and entry.get("attempts", 0) > 0
            and entry.get("due", "9999-12-31") <= cutoff]


def study_streak():
    marked = set(st.session_state.progress["active_days"])
    cursor = today()
    if cursor.isoformat() not in marked:
        cursor -= timedelta(days=1)
    count = 0
    while cursor.isoformat() in marked:
        count += 1
        cursor -= timedelta(days=1)
    return count


def register_answer(char, correct):
    progress = st.session_state.progress
    entry = progress["cards"].setdefault(
        char, {"attempts": 0, "correct": 0, "streak": 0,
               "correct_dates": [], "due": today().isoformat()}
    )
    entry["attempts"] += 1
    record_activity()
    if correct:
        entry["correct"] += 1
        entry["streak"] += 1
        date = today().isoformat()
        if date not in entry["correct_dates"]:
            entry["correct_dates"].append(date)
        interval = 1 if entry["streak"] == 1 else 3 if entry["streak"] == 2 else 7
        entry["due"] = (today() + timedelta(days=interval)).isoformat()
        progress["xp"] += 10
    else:
        entry["streak"] = 0
        entry["due"] = today().isoformat()


def label(card):
    return f"{card['meaning']} {card['sound']}"


def make_question(target):
    kind = random.choice(["훈음", "한자", "뜻"])
    if kind == "훈음":
        title = f"{target['char']} 의 뜻과 음을 골라보세요."
        answer = label(target)
        value = label
    elif kind == "한자":
        title = f"'{label(target)}' 에 해당하는 한자는?"
        answer = target["char"]
        value = lambda c: c["char"]
    else:
        title = f"{target['char']} 의 뜻은 무엇일까요?"
        answer = target["meaning"]
        value = lambda c: c["meaning"]
    distractors = list(dict.fromkeys(value(c) for c in ALL if value(c) != answer))
    choices = random.sample(distractors, 3) + [answer]
    random.shuffle(choices)
    return {"char": target["char"], "title": title,
            "answer": answer, "choices": choices, "kind": kind}


def start_quiz(pool, title):
    if not pool:
        return
    selected = random.sample(pool, min(10, len(pool)))
    st.session_state.quiz_serial += 1
    st.session_state.quiz = {
        "title": title, "questions": [make_question(item) for item in selected],
        "index": 0, "answered": False, "selected": None, "correct_count": 0,
        "serial": st.session_state.quiz_serial,
    }


def quiz_panel():
    quiz = st.session_state.quiz
    if quiz is None:
        return
    count = len(quiz["questions"])
    st.subheader(quiz["title"])
    if quiz["index"] >= count:
        score = quiz["correct_count"]
        st.success(f"문제풀이 완료! {count}문제 중 {score}문제 정답")
        st.metric("정답률", f"{score / count:.0%}")
        st.caption("퀴즈 기록이 현재 세션의 학습 현황에 반영되었습니다.")
        if st.button("다른 문제 풀기", type="primary"):
            st.session_state.quiz = None
            st.rerun()
        return

    question = quiz["questions"][quiz["index"]]
    st.progress(quiz["index"] / count)
    st.caption(f"문제 {quiz['index'] + 1} / {count}")
    if question["kind"] in ("훈음", "뜻"):
        st.markdown(f'<div class="hanja-card">{question["char"]}</div>', unsafe_allow_html=True)
    st.markdown(f"**{question['title']}**")
    key = f"answer_{quiz['serial']}_{quiz['index']}"
    choice = st.radio("정답 선택", question["choices"], index=None,
                      label_visibility="collapsed", key=key, disabled=quiz["answered"])

    if not quiz["answered"]:
        if st.button("정답 확인", type="primary", disabled=choice is None):
            correct = choice == question["answer"]
            register_answer(question["char"], correct)
            quiz["selected"] = choice
            quiz["answered"] = True
            if correct:
                quiz["correct_count"] += 1
            st.rerun()
    else:
        if quiz["selected"] == question["answer"]:
            st.success("정답이에요! +10점")
        else:
            st.error(f"아쉬워요. 정답: {question['answer']}")
        if st.button("다음 문제" if quiz["index"] + 1 < count else "결과 보기", type="primary"):
            quiz["index"] += 1
            quiz["answered"] = False
            st.rerun()
    if st.button("이 퀴즈 종료"):
        st.session_state.quiz = None
        st.rerun()


def page_home():
    progress = st.session_state.progress
    learned = len(NEW_SET.intersection(progress["learned"]))
    mastered = sum(is_mastered(char) for char in NEW_SET)
    a, b, c, d = st.columns(4)
    a.metric("신규 한자 학습", f"{learned}/100")
    b.metric("숙달한 신규 한자", f"{mastered}/100")
    c.metric("모은 별", f"{progress['xp'] // 50}개")
    d.metric("연속 공부", f"{study_streak()}일")
    st.progress(learned / 100)
    st.caption("8급 50자는 합격 범위로 따로 복습하며, 위 진도는 새로 배울 100자 기준입니다.")
    pending = review_chars()
    if pending:
        st.warning(f"오늘 복습할 한자가 {len(pending)}자 있어요. '복습' 메뉴에서 풀어보세요.")
    else:
        st.info("오늘은 7급 신규 한자를 5자 배우고 퀴즈 10문제를 풀어보세요.")
    for unit in range(20):
        block = NEW[unit * 5:(unit + 1) * 5]
        if any(item["char"] not in progress["learned"] for item in block):
            grade = "7급Ⅱ" if unit < 10 else "7급"
            st.subheader(f"추천 단원: {unit + 1}단원 ({grade})")
            st.write("  ".join(item["char"] for item in block))
            break
    else:
        st.success("100자 신규 학습을 모두 완료했어요! 반복 복습으로 실력을 다져보세요.")
    st.caption("이 앱은 개인 학습 보조 도구이며, 한국어문회의 공식 시험 서비스가 아닙니다.")


def page_learning():
    st.subheader("한자 배우기")
    section = st.radio("학습 범위", ["7급 신규 100자", "8급 50자 복습"], horizontal=True)
    if section == "7급 신규 100자":
        unit = st.selectbox("단원 선택", list(range(1, 21)),
                            format_func=lambda n: f"{n}단원 · {'7급Ⅱ' if n <= 10 else '7급'}")
        cards = NEW[(unit - 1) * 5:unit * 5]
    else:
        unit = st.selectbox("복습 단원", list(range(1, 11)), key="old_unit",
                            format_func=lambda n: f"8급 복습 {n}단원")
        cards = GROUPS["8급"][(unit - 1) * 5:unit * 5]

    idx = st.session_state.card_cursor % len(cards)
    card = cards[idx]
    st.caption(f"{card['grade']} · 단원 {unit} · {idx + 1} / 5")
    st.markdown(f'<div class="hanja-card">{card["char"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="card-reading">{label(card)}</div>', unsafe_allow_html=True)
    if card["char"] in ALT:
        st.caption(f"다른 읽기/뜻: {ALT[card['char']]}")
    if is_mastered(card["char"]):
        st.success("숙달한 한자예요!")
    elif card["char"] in st.session_state.progress["learned"]:
        st.info("학습 표시 완료 · 퀴즈로 기억력을 확인해 보세요.")
    if st.button("이 한자 익혔어요 (+2점)", type="primary",
                 disabled=card["char"] in st.session_state.progress["learned"]):
        mark_learned(card["char"])
        st.rerun()
    left, right = st.columns(2)
    with left:
        if st.button("이전 한자", use_container_width=True):
            st.session_state.card_cursor = (idx - 1) % len(cards)
            st.rerun()
    with right:
        if st.button("다음 한자", use_container_width=True):
            st.session_state.card_cursor = (idx + 1) % len(cards)
            st.rerun()
    st.caption("획순·음성·어휘 예문은 이후 버전에서 검증된 자료를 연계할 예정입니다.")


def page_quiz():
    if st.session_state.quiz is not None:
        quiz_panel()
        return
    st.subheader("한자 퀴즈")
    scopes = {
        "7급 전체 (150자)": ALL,
        "신규 7급 (100자)": NEW,
        "7급Ⅱ 신규 (50자)": GROUPS["7급Ⅱ"],
        "7급 신규 (50자)": GROUPS["7급"],
        "8급 복습 (50자)": GROUPS["8급"],
        "내가 학습 표시한 한자": [INDEX[h] for h in st.session_state.progress["learned"] if h in INDEX],
    }
    scope = st.selectbox("출제 범위 선택", list(scopes))
    st.caption("훈음 맞히기 · 한자 찾기 · 뜻 맞히기가 섞여 나옵니다. 최대 10문제입니다.")
    if st.button("퀴즈 시작", type="primary", disabled=not scopes[scope]):
        start_quiz(scopes[scope], scope)
        st.rerun()
    if not scopes[scope]:
        st.info("아직 학습 표시한 한자가 없습니다. '한자 학습'에서 한자를 먼저 배워보세요.")


def page_review():
    if st.session_state.quiz is not None and st.session_state.quiz["title"] == "오늘의 복습":
        quiz_panel()
        return
    st.subheader("자동 복습")
    due = review_chars()
    st.metric("오늘 복습 예정", f"{len(due)}자")
    st.caption("틀린 한자는 당일, 맞힌 한자는 정답 연속 횟수에 따라 1·3·7일 뒤 다시 출제됩니다.")
    if due:
        st.write("복습할 한자: " + " · ".join(due[:30]))
        if st.button("복습 퀴즈 시작", type="primary"):
            start_quiz([INDEX[h] for h in due], "오늘의 복습")
            st.rerun()
    else:
        st.success("현재 복습 예정인 한자가 없어요. 새로운 한자를 배워보세요!")
    st.caption("복습 일정은 퀴즈 풀이 기록이 생긴 한자부터 계산합니다.")


def restore_progress(data):
    if not isinstance(data, dict):
        raise ValueError("학습기록 형식이 올바르지 않습니다.")
    cleaned = fresh_progress()
    cleaned["learned"] = list(dict.fromkeys(c for c in data.get("learned", []) if c in INDEX))
    cleaned["xp"] = max(0, int(data.get("xp", 0)))
    cleaned["active_days"] = list(dict.fromkeys(str(d) for d in data.get("active_days", [])))
    for char, item in data.get("cards", {}).items():
        if char not in INDEX or not isinstance(item, dict):
            continue
        attempts = max(0, int(item.get("attempts", 0)))
        correct = min(attempts, max(0, int(item.get("correct", 0))))
        cleaned["cards"][char] = {
            "attempts": attempts, "correct": correct,
            "streak": min(correct, max(0, int(item.get("streak", 0)))),
            "correct_dates": [str(d) for d in item.get("correct_dates", [])],
            "due": str(item.get("due", today().isoformat())),
        }
    return cleaned


def page_records():
    st.subheader("학습 기록 · 백업")
    progress = st.session_state.progress
    history = progress["cards"]
    attempts = sum(item["attempts"] for item in history.values())
    rights = sum(item["correct"] for item in history.values())
    a, b, c = st.columns(3)
    a.metric("퀴즈 총 응답", f"{attempts}문제")
    b.metric("누적 정답률", f"{rights / attempts:.0%}" if attempts else "-")
    c.metric("획득 점수", f"{progress['xp']:,}점")

    rows = []
    for grade in ("8급", "7급Ⅱ", "7급"):
        for card in GROUPS[grade]:
            char = card["char"]
            item = history.get(char, {})
            if char in progress["learned"] or item:
                rows.append({"급수": grade, "한자": char, "훈음": label(card),
                             "학습 표시": "완료" if char in progress["learned"] else "-",
                             "풀이 횟수": item.get("attempts", 0),
                             "정답 횟수": item.get("correct", 0),
                             "숙달": "완료" if is_mastered(char) else "진행 중",
                             "다음 복습일": item.get("due", "-")})
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("아직 학습 기록이 없어요.")

    st.divider()
    st.markdown("**학습기록 백업 및 복원**")
    st.warning("무료 Streamlit 서버의 세션 데이터는 영구 저장이 아닙니다. 학습 후 반드시 백업 파일을 내려받아 보관하세요.")
    backup = json.dumps({"version": "1.0", "progress": progress},
                        ensure_ascii=False, indent=2)
    st.download_button("학습기록 JSON 다운로드", data=backup,
                       file_name=f"hanja_progress_{today().isoformat()}.json",
                       mime="application/json", type="primary")
    upload = st.file_uploader("이전에 내려받은 JSON 파일로 복원", type=["json"])
    if st.button("백업 파일 불러오기", disabled=upload is None):
        try:
            payload = json.loads(upload.getvalue().decode("utf-8-sig"))
            st.session_state.progress = restore_progress(payload["progress"])
            st.session_state.quiz = None
            st.success("학습기록 복원을 완료했습니다.")
        except (ValueError, TypeError, KeyError, AttributeError) as error:
            st.error(f"파일을 복원하지 못했습니다: {error}")

    with st.expander("모든 학습기록 초기화"):
        confirm = st.checkbox("모든 기록을 지우겠습니다.")
        if st.button("기록 삭제", disabled=not confirm):
            st.session_state.progress = fresh_progress()
            st.session_state.quiz = None
            st.rerun()


def page_writing():
    # 한자 획순 안내와 획 번호 오버레이 (기존 5자 시범).
    st.subheader("획순 쓰기")
    st.write("한 획씩 재생되는 순서에 맞춰 숫자를 확인하고, 직접 써보세요.")

    # 공식 한국식 획순 검수를 마치기 전까지 시범 글자 5개만 사용.
    stroke_count = {"山": 3, "木": 4, "人": 2, "日": 4, "水": 4}
    char = st.selectbox(
        "연습할 한자", list(stroke_count),
        format_func=lambda c: f"{c} · {label(INDEX[c])}",
        key="stroke_char",
    )
    st.info(
        "시험 기능: 숫자는 Hanzi Writer의 획순 데이터와 정확히 같은 순서를 사용합니다. "
        "해당 자료는 중국 한자 기반이므로 한국식 획순과의 완전한 일치 검증은 아직 끝나지 않았습니다."
    )

    # json.dumps로 입력을 JS 문자열 값으로 안전하게 전달.
    char_js = json.dumps(char, ensure_ascii=False)
    expected_js = json.dumps(stroke_count[char])
    html = r'''
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<script src="https://cdn.jsdelivr.net/npm/hanzi-writer@3.5/dist/hanzi-writer.min.js"></script>
<style>
  * { box-sizing: border-box; }
  body { margin:0; font-family:system-ui,-apple-system,sans-serif; color:#17283e; }
  .wrap { display:flex; flex-direction:column; align-items:center; gap:10px; }
  .board { width:280px; height:280px; border:1px solid #cbd5e1;
    border-radius:12px; background:#fff; position:relative; overflow:hidden; }
  #target {width:280px;height:280px;touch-action:none;}
  #target svg {touch-action:none;}
  #numbers { position:absolute;top:0;left:0;width:280px;height:280px;
    pointer-events:none; overflow:visible; }
  .toolbar { display:flex; flex-wrap:wrap; justify-content:center; gap:7px; }
  button { font:inherit; cursor:pointer; border:1px solid #cbd5e1;
    border-radius:9px; min-height:43px; padding:8px 13px;
    background:#f8fafc; color:#17283e; }
  button:disabled {cursor:not-allowed;opacity:.5;}
  button.primary {background:#1668a5;color:white;border-color:#1668a5;}
  .settings {font-size:14px;display:flex;align-items:center;gap:8px;}
  input[type=checkbox] {width:18px;height:18px;accent-color:#1668a5;}
  #status {font-size:14px;text-align:center;max-width:420px;min-height:42px;
    line-height:1.5;padding:0 4px;}
  #counter {font-size:14px;font-weight:600;color:#334155;}
</style>
</head>
<body>
<div class="wrap">
  <div id="counter">획순 데이터를 읽는 중...</div>
  <div class="board">
    <div id="target" aria-label="한자 쓰기 영역"></div>
    <svg id="numbers" xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 280 280" aria-hidden="true"></svg>
  </div>
  <label class="settings">
    <input id="showNumbers" type="checkbox" checked /> 획순 숫자 표시
  </label>
  <div class="toolbar">
    <button id="animate" disabled>① 번호와 함께 보기</button>
    <button id="all" disabled>② 전체 번호 보기</button>
    <button id="quiz" class="primary" disabled>③ 직접 써보기</button>
    <button id="retry" disabled>다시 쓰기</button>
  </div>
  <div id="status" role="status" aria-live="polite">데이터를 불러오는 중입니다…</div>
</div>
<script>
'use strict';
const char = __CHAR_JSON__;
const expectedCount = __EXPECTED_COUNT__;
const SIZE = 280;
const PAD = 18;
const svgNS = 'http://www.w3.org/2000/svg';
const overlay = document.getElementById('numbers');
const counter = document.getElementById('counter');
const numberToggle = document.getElementById('showNumbers');
const statusEl = document.getElementById('status');
const buttons = ['animate','all','quiz','retry'].map(id => document.getElementById(id));
const status = text => {statusEl.textContent = text;};
let writer;
let strokeCount = 0;
let numberLocations = [];
let visibleCount = 0;
let mode = 'idle';
let busy = false;
let validNumberData = false;

function setBusy(value) {
  busy = value;
  buttons.forEach(b => b.disabled = value || !strokeCount);
}
function clamp(n, lo, hi) {return Math.max(lo,Math.min(hi,n));}
function positionLabels(medians) {
  // Hanzi Writer 반환값 t.y는 SVG에 적용할 translateY가 아니라 yOffset입니다.
  // 실제 SVG transform은 translate(t.x, SIZE - t.y) scale(t.scale, -t.scale).
  // 따라서 화면 좌표로 변환할 때 Y축은 SIZE - t.y - rawY * t.scale로 계산합니다.
  const t = HanziWriter.getScalingTransform(SIZE,SIZE,PAD);
  const centers = [];
  return medians.map((points, index) => {
    if (!Array.isArray(points) || !Array.isArray(points[0]) || points[0].length < 2)
      throw new Error('획의 중심선 좌표가 없습니다: ' + (index+1));
    const first = points[0];
    const second = (points.length > 1 ? points[1] : first);
    const sx = t.x + first[0]*t.scale;
    const sy = SIZE - t.y - first[1]*t.scale;
    const vx = (second[0]-first[0])*t.scale;
    const vy = -(second[1]-first[1])*t.scale;
    const mag = Math.hypot(vx,vy) || 1;
    const tx = vx/mag, ty=vy/mag;
    // 각 획의 실제 시작점 옆에 배치하고, 앞서 배치한 숫자와 겹침을 줄입니다.
    const nx=-ty, ny=tx;
    const shifts = [[-12,13],[-12,-13],[-23,0],[0,19],[0,-19],[-22,22],[13,23],[23,-15]];
    let best = null;
    shifts.forEach(([along,side]) => {
      const x=clamp(sx + tx*along + nx*side,14,SIZE-14);
      const y=clamp(sy + ty*along + ny*side,14,SIZE-14);
      const collision=centers.reduce((sum,c)=>sum+Math.max(0,26-Math.hypot(x-c.x,y-c.y))**2,0);
      const penalty=collision + Math.hypot(x-sx,y-sy)*0.15;
      if (!best || penalty<best.penalty) best={x,y,penalty};
    });
    centers.push(best);
    return {x:best.x, y:best.y, number:index+1};
  });
}
function paintNumbers() {
  overlay.replaceChildren();
  if (!numberToggle.checked || mode === 'quiz' || !validNumberData) return;
  numberLocations.slice(0,visibleCount).forEach(item => {
    const g=document.createElementNS(svgNS,'g');
    const circle=document.createElementNS(svgNS,'circle');
    circle.setAttribute('cx',String(item.x));
    circle.setAttribute('cy',String(item.y));
    circle.setAttribute('r','12');
    circle.setAttribute('fill','#fff');
    circle.setAttribute('stroke','#12699d');
    circle.setAttribute('stroke-width','1.8');
    const text=document.createElementNS(svgNS,'text');
    text.setAttribute('x',String(item.x));
    text.setAttribute('y',String(item.y+4.5));
    text.setAttribute('font-size',item.number<10?'12':'10');
    text.setAttribute('font-weight','700');
    text.setAttribute('text-anchor','middle');
    text.setAttribute('fill','#12699d');
    text.textContent=String(item.number);
    g.append(circle,text);
    overlay.appendChild(g);
  });
}
function setVisible(count) {
  visibleCount=clamp(count,0,strokeCount);
  paintNumbers();
}
async function playWithNumbers() {
  if(busy || !writer) return;
  mode='animation';
  setBusy(true);
  setVisible(0);
  try {
    writer.cancelQuiz();
    await writer.hideCharacter({duration:0});
    for (let i=0; i<strokeCount; i++) {
      counter.textContent='현재 '+(i+1)+' / '+strokeCount+'획';
      // 애니메이션과 번호의 인덱스를 동일하게 유지합니다.
      setVisible(i+1); // 다음 획의 번호를 먼저 표시한 뒤 획을 그립니다.
      await writer.animateStroke(i);
    }
    counter.textContent='총 '+strokeCount+'획';
    status('모든 획을 순서대로 확인했어요. 이제 직접 써보세요!');
  } catch(error) {
    status('획순 재생 중 오류가 발생했습니다: '+String(error));
  } finally {
    setBusy(false);
  }
}
async function showAll() {
  if(busy || !writer) return;
  mode='all';
  setBusy(true);
  try {
    writer.cancelQuiz();
    await writer.showCharacter({duration:0});
    setVisible(strokeCount);
    counter.textContent='총 '+strokeCount+'획';
    status('한자 전체와 각 획의 시작 위치를 숫자로 표시했습니다.');
  } finally {
    setBusy(false);
  }
}
function beginQuiz() {
  if(busy || !writer) return;
  mode='quiz';
  setVisible(0);   // 쓰기 판정 중에는 숫자가 입력을 가리지 않도록 숨김
  counter.textContent='손가락 또는 터치펜으로 써보세요.';
  status('첫 획부터 직접 써보세요. 틀린 획은 두 번 실수하면 힌트가 나타납니다.');
  writer.cancelQuiz();
  writer.quiz({
    showHintAfterMisses:2,
    leniency:1.2,
    onCorrectStroke: data => {
      counter.textContent=(data.strokeNum+1)+' / '+strokeCount+'획 완료';
      status('좋아요! 남은 획: '+data.strokesRemaining);
    },
    onMistake: data => {
      status((data.strokeNum+1)+'획의 순서나 방향을 다시 확인해 보세요.');
    },
    onComplete: data => {
      counter.textContent='총 '+strokeCount+'획 완성';
      status(data.totalMistakes===0
        ? '완성! 한 번에 성공했어요!'
        : '완성! 틀린 획 '+data.totalMistakes+'회 · 다시 도전해 보세요.');
    },
  });
}
numberToggle.addEventListener('change',paintNumbers);
if (typeof HanziWriter === 'undefined') {
  status('획순 프로그램을 불러오지 못했습니다. 인터넷 연결을 확인하세요.');
} else {
  writer=HanziWriter.create('target',char,{
    width:SIZE,height:SIZE,padding:PAD,
    showCharacter:false,showOutline:true,
    strokeColor:'#1d4ed8',outlineColor:'#d1d5db',
    drawingColor:'#2563eb',highlightColor:'#10b981',
    strokeAnimationSpeed:0.5,delayBetweenStrokes:250, // 획 재생 속도를 기존의 절반으로
    drawingWidth:40, // 직접 쓰기 펜 굵기를 기본값(4)의 10배로
    onLoadCharDataSuccess: data => {
      strokeCount=data.strokes.length;
      counter.textContent='총 '+strokeCount+'획';
      if (strokeCount!==expectedCount || !Array.isArray(data.medians) || data.medians.length!==strokeCount) {
        validNumberData=false;
        status('획수 또는 획순 데이터가 기준값과 일치하지 않아 번호 표시를 중지했습니다.');
      } else {
        try {
          numberLocations=positionLabels(data.medians);
          validNumberData=true;
          status('① 번호와 함께 보기 → ② 전체 번호 보기 → ③ 직접 써보기');
        } catch(error) {
          validNumberData=false;
          status('숫자 좌표를 생성할 수 없어 획순만 표시합니다.');
        }
      }
      setBusy(false);
    },
    onLoadCharDataError: () => status('획순 데이터를 불러오지 못했습니다. 인터넷 연결을 확인하세요.'),
  });
  document.getElementById('animate').addEventListener('click',playWithNumbers);
  document.getElementById('all').addEventListener('click',showAll);
  document.getElementById('quiz').addEventListener('click',beginQuiz);
  document.getElementById('retry').addEventListener('click',beginQuiz);
}
</script>
</body>
</html>
'''.replace("__CHAR_JSON__", char_js).replace("__EXPECTED_COUNT__", expected_js)
    components.html(html, height=492, scrolling=False)
    st.caption(
        "학습 범위: 山·木·人·日·水 5자 시범. 숫자는 각 획 옆의 시작점 근처에 표시됩니다. "
        "쓰기 성공 여부는 아직 별·점수·학습기록에 연결되지 않습니다."
    )

st.markdown("""
<style>
.block-container {max-width: 980px; padding-top: 1.25rem;}
.hanja-card {font-size: clamp(90px, 13vw, 150px); font-weight: 650;
  text-align: center; padding: 18px 0; border: 1px solid #e5e7eb;
  border-radius: 16px; background: #fff; color: #182532;}
.card-reading {font-size: 30px; font-weight: 700; text-align:center;
  padding: 12px; color: #25354d;}
div.stButton > button {min-height: 46px;}
</style>
""", unsafe_allow_html=True)

st.title("📚 한자 탐험대")
st.caption("한국어문회 8급 합격 → 7급 도전 · 신규 100자 + 8급 복습 50자")
menu = st.radio("메뉴", ["홈", "한자 학습", "획순 쓰기", "퀴즈", "복습", "학습 기록"],
                horizontal=True, label_visibility="collapsed")
st.divider()
if menu == "홈":
    page_home()
elif menu == "한자 학습":
    page_learning()
elif menu == "획순 쓰기":
    page_writing()
elif menu == "퀴즈":
    page_quiz()
elif menu == "복습":
    page_review()
else:
    page_records()

st.divider()
st.caption("한자 탐험대 v1.1.3 · 개인 학습용 · 실제 시험 문항을 재현한 공식 모의고사는 아닙니다.")
