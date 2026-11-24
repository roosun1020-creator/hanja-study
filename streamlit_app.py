"""한자 탐험대 v1.2.2 | 키즈 판타지 UI · 카드 선택 · 드래곤 가디언즈."""

import json
import random
from datetime import datetime, timedelta
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="한자 탐험대 v1.2.2",
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


# 판타지 게임 설정: 한자 진화 계보와 포켓몬 기술에서 영감받은 독창적인 기술 이름.
# 해금 숫자는 '신규 한자 5자짜리 단원'의 완료 횟수입니다.
DRAGONS = {
    "fire": {"name": "화루", "kind": "불", "color": "#DF7443", "icon": "🔥",
             "hanja": ["火", "炎", "焱"],
             "forms": ["꼬마 불꽃룡", "붉은 날개룡", "화염 수호룡"]},
    "water": {"name": "수루", "kind": "물", "color": "#327FBF", "icon": "💧",
              "hanja": ["水", "江", "海"],
              "forms": ["물방울룡", "강물날개룡", "대해 수호룡"]},
    "forest": {"name": "그루", "kind": "숲", "color": "#3A9565", "icon": "🌿",
               "hanja": ["木", "林", "森"],
               "forms": ["새싹룡", "숲날개룡", "고대 숲 수호룡"]},
}
# (완료 단원 수, 필요한 진화 단계, 기술명, 참고 기술)
SKILL_TREE = {
    "fire": [
        (0,1,"불씨탄","불꽃세례"),(2,1,"화염송곳니","불꽃엄니"),
        (4,1,"불꽃소용돌이","회오리불꽃"),(8,2,"화염숨결","화염방사"),
        (11,2,"용의열풍","열풍"),(14,2,"폭염날개","강화 불꽃 공격"),
        (17,3,"대화염진","불대문자"),(20,3,"태양폭발","최종 필살기"),
    ],
    "water": [
        (0,1,"물방울탄","거품"),(2,1,"물대포","물대포"),
        (4,1,"거품파동","거품광선"),(8,2,"강물파동","물의파동"),
        (11,2,"파도꼬리","아쿠아테일"),(14,2,"급류돌진","아쿠아제트"),
        (17,3,"대해분출","하이드로펌프"),(20,3,"해룡의격류","최종 필살기"),
    ],
    "forest": [
        (0,1,"새싹채찍","덩굴채찍"),(2,1,"씨앗탄","씨기관총"),
        (4,1,"잎날검","잎날가르기"),(8,2,"덩굴회오리","덩굴채찍"),
        (11,2,"꽃잎폭풍","꽃잎댄스"),(14,2,"대지의뿌리","씨뿌리기"),
        (17,3,"숲의광선","에너지볼"),(20,3,"태양의숨결","솔라빔"),
    ],
}

# 배틀에서 선택할 기술마다 고유 아이콘을 보여 줍니다.
SKILL_ICONS = {
    "fire": ["🔥", "🦷", "🌀", "🐲", "🌪️", "🪽", "☄️", "☀️"],
    "water": ["🫧", "💦", "🌊", "💠", "🐉", "⚡", "🌊", "🔱"],
    "forest": ["🌱", "🌰", "🍃", "🌿", "🌸", "🌳", "✨", "☀️"],
}


def fresh_game():
    return {"starter": None, "active": None, "owned": [],
            "xp": 0, "won_battles": []}


def completed_unit_count(progress):
    learned = set(progress.get("learned", []))
    return sum(all(item["char"] in learned for item in NEW[i*5:(i+1)*5])
               for i in range(20))


def evolution_stage(unit_count, unique_wins):
    if unit_count >= 15 and unique_wins >= 3:
        return 3
    if unit_count >= 5 and unique_wins >= 1:
        return 2
    return 1


def unlocked_skills(dragon_key, unit_count, stage):
    return [(minimum, required, skill, source)
            for minimum, required, skill, source in SKILL_TREE[dragon_key]
            if unit_count >= minimum and stage >= required]


def update_dragon_ownership(game, unit_count):
    # 선택한 첫 드래곤 외의 두 마리는 10·20개 단원 보상으로 열립니다.
    starter = game.get("starter")
    if starter not in DRAGONS:
        return
    others = [key for key in DRAGONS if key != starter]
    game["owned"] = list(dict.fromkeys(
        [starter] + ([others[0]] if unit_count >= 10 else []) +
        ([others[1]] if unit_count >= 20 else [])
    ))
    if game.get("active") not in game["owned"]:
        game["active"] = starter


def new_dragon_question(target):
    # 문제 한자를 크게 표시하므로 정답 한자가 그대로 노출되는 '한자 찾기' 유형은 제외.
    kind = random.choice(["훈음", "뜻"])
    if kind == "훈음":
        answer, values = label(target), [label(x) for x in ALL]
        title = "이 한자의 뜻과 음을 고르세요."
    else:
        answer, values = target["meaning"], [x["meaning"] for x in ALL]
        title = "이 한자의 뜻은 무엇일까요?"
    wrong = list(dict.fromkeys(v for v in values if v != answer))
    choices = random.sample(wrong, 3) + [answer]
    random.shuffle(choices)
    return {"char": target["char"], "title": title,
            "answer": answer, "choices": choices, "kind": kind}


def battle_scope_pool(progress, selection):
    if selection == "8급 복습":
        return GROUPS["8급"]
    if selection == "학습 완료 한자":
        learned = set(progress.get("learned", []))
        return [item for item in ALL if item["char"] in learned]
    if selection.startswith("신규 ") and selection.endswith("단원"):
        unit = int(selection.split()[1].removesuffix("단원"))
        if 1 <= unit <= 20:
            return NEW[(unit-1)*5:unit*5]
    return []


def fresh_battle(pool, scope, serial):
    if len(pool) < 5:
        raise ValueError("한자 배틀은 서로 다른 5자가 있어야 시작할 수 있습니다.")
    return {"scope":scope, "serial": serial,
            "questions":[new_dragon_question(x) for x in random.sample(pool,5)],
            "index":0, "correct":0, "selected":None, "answered":False,
            "last_correct":False, "last_skill":"", "rewarded":False}


def award_first_win(game, scope):
    # 같은 배틀의 무한 반복으로 드래곤 경험치를 쌓는 것을 방지.
    if scope in game["won_battles"]:
        return False
    game["won_battles"].append(scope)
    game["xp"] += 30
    return True


def fresh_progress():
    return {"learned": [], "cards": {}, "xp": 0, "active_days": [], "game": fresh_game()}


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
    with st.container(key="quiz_problem_area"):
        if question["kind"] in ("훈음", "뜻"):
            st.markdown(
                f'<div class="hanja-card quiz-symbol">{escape(question["char"])}</div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            f'<div class="quiz-prompt">{escape(question["title"])}</div>',
            unsafe_allow_html=True,
        )
    # 기본 라디오 버튼 대신 큰 선택 버튼을 사용합니다.
    # Streamlit의 버전별 라디오 내부 HTML 구조와 무관하게 크기를 유지합니다.
    with st.container(key="quiz_choice_area"):
        for option_index, option in enumerate(question["choices"]):
            active = quiz.get("selected") == option
            if st.button(
                f"{option_index + 1}.  {option}",
                key=f"quiz_option_{quiz['serial']}_{quiz['index']}_{option_index}",
                type="primary" if active else "secondary",
                disabled=quiz["answered"],
                use_container_width=True,
            ):
                quiz["selected"] = option
                st.rerun()
    choice = quiz.get("selected")

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
            quiz["selected"] = None  # 이전 문제의 선택이 새 문제에 남지 않도록 초기화
            st.rerun()
    if st.button("이 퀴즈 종료"):
        st.session_state.quiz = None
        st.rerun()



# ----- v1.2.2 Kid-friendly UI primitives: no selectbox, radio or checkbox -----
# These helpers change only presentation state. Study, grading, reward, backup
# and Hanzi Writer logic is intentionally kept from v1.2.1.

def kid_heading(icon, title, subtitle=""):
    subtitle_html = f'<p>{escape(subtitle)}</p>' if subtitle else ''
    st.markdown(f'<div class="kid-heading"><div class="kid-heading-icon">{icon}</div>'
                f'<div><h2>{escape(title)}</h2>{subtitle_html}</div></div>',
                unsafe_allow_html=True)


def game_stats(items):
    """Lightweight responsive stats, not native Streamlit dashboard metrics."""
    body = ''.join(
        '<div class="kid-stat">'
        f'<div class="kid-stat-icon">{icon}</div>'
        f'<span class="kid-stat-value">{escape(str(value))}</span>'
        f'<span class="kid-stat-label">{escape(label_)}</span>'
        '</div>' for icon, label_, value in items
    )
    st.markdown(f'<div class="kid-stats">{body}</div>', unsafe_allow_html=True)


def kid_notice(message, icon="✨"):
    st.markdown(f'<div class="kid-notice"><span>{icon}</span>'
                f'<span>{escape(message)}</span></div>', unsafe_allow_html=True)


def tile_picker(options, key, cols=2, title=None):
    """A persistent single-select tile grid, returning the selected option value.

    options: [(value, label), ...]; updates immediately when a big card is touched.
    """
    choices = [value for value, _ in options]
    if not choices:
        raise ValueError('선택 옵션이 없습니다.')
    if st.session_state.get(key) not in choices:
        st.session_state[key] = choices[0]
    if title:
        st.markdown(f'<div class="kid-small-title">{escape(title)}</div>', unsafe_allow_html=True)
    with st.container(key='tiles_' + key):
        for start in range(0, len(options), cols):
            row = options[start:start + cols]
            widgets = st.columns(len(row), gap="small")
            for col, (value, label_) in zip(widgets, row):
                with col:
                    selected = st.session_state[key] == value
                    if st.button(label_ + ('  ✓' if selected else ''),
                                 key=f'{key}_pick_{choices.index(value)}',
                                 type='primary' if selected else 'secondary',
                                 use_container_width=True):
                        st.session_state[key] = value
                        st.rerun()
    return st.session_state[key]


def unit_picker(key, count, label_prefix="", complete_func=None):
    """Five-unit pages and 3+2 large unit cards instead of a dense selectbox."""
    unit_key = key + '_unit'
    group_key = key + '_group'
    if not 1 <= st.session_state.get(unit_key, 0) <= count:
        st.session_state[unit_key] = 1
    num_groups = (count + 4)//5
    if not 0 <= st.session_state.get(group_key, -1) < num_groups:
        st.session_state[group_key] = (st.session_state[unit_key]-1)//5
    with st.container(key='unit_groups_' + key):
        group_columns = st.columns(num_groups, gap='small')
        for g in range(num_groups):
            start = g*5 + 1
            end = min(count, start+4)
            with group_columns[g]:
                selected = g == st.session_state[group_key]
                if st.button(f'{start}~{end}', key=f'{key}_group_{g}',
                             type='primary' if selected else 'secondary',
                             use_container_width=True):
                    st.session_state[group_key] = g
                    st.session_state[unit_key] = start
                    st.rerun()
    start = st.session_state[group_key]*5 + 1
    options = list(range(start, min(count, start+4)+1))
    st.markdown('<div class="kid-small-title">📖 모험할 단원을 골라요</div>',unsafe_allow_html=True)
    with st.container(key='units_' + key):
        for group in (options[:3],options[3:]):
            if not group:
                continue
            cols = st.columns(len(group), gap='small')
            for unit, col in zip(group,cols):
                complete = bool(complete_func and complete_func(unit))
                prefix = '⭐ ' if complete else ''
                label_ = f'{prefix}{unit}단원'
                if label_prefix:
                    label_ = f'{prefix}{label_prefix} {unit}'
                selected = st.session_state[unit_key] == unit
                with col:
                    if st.button(label_ + (' ✓' if selected else ''),
                                 key=f'{key}_unit_{unit}',
                                 type='primary' if selected else 'secondary',
                                 use_container_width=True):
                        st.session_state[unit_key] = unit
                        st.rerun()
    return st.session_state[unit_key]


def select_stroke_char(cards, key, limit=12):
    """Searchable large hanja tile gallery; safe for 150 symbols and mobile."""
    available = {c['char'] for c in cards}
    if not available:
        return None
    search_term = st.text_input('🔎 연습할 한자 찾기', placeholder='한자 또는 뜻·음을 적어 보세요',
                                key=key+'_search').strip().lower()
    filtered = [c for c in cards if search_term in c['char'].lower()
                or search_term in label(c).lower()]
    if not filtered:
        kid_notice('찾는 한자가 없어요. 다른 글자를 입력해 보세요.', '🔎')
        return None
    chosen_key, page_key = key+'_char',key+'_page'
    visible_chars = {c['char'] for c in filtered}
    if st.session_state.get(chosen_key) not in visible_chars:
        st.session_state[chosen_key] = filtered[0]['char']
        st.session_state[key+'_page'] = 0
    pages = (len(filtered)+limit-1)//limit
    if not 0 <= st.session_state.get(page_key, -1) < pages:
        st.session_state[page_key] = 0
    p = st.session_state[page_key]
    st.caption(f'한자를 누르면 바로 쓰기 연습으로 연결돼요 · {len(filtered)}자 중 {p+1}/{pages}쪽')
    with st.container(key='hanja_gallery_'+key):
        subset=filtered[p*limit:(p+1)*limit]
        for i in range(0,len(subset),3):
            row=subset[i:i+3]
            cols=st.columns(len(row),gap='small')
            for c,col in zip(row,cols):
                with col:
                    selected=st.session_state[chosen_key]==c['char']
                    if st.button(f"{c['char']}\n{label(c)}"+(' ✓' if selected else ''),
                                 key=f'{key}_char_{c["char"]}',
                                 type='primary' if selected else 'secondary',
                                 use_container_width=True):
                        st.session_state[chosen_key]=c['char']
                        st.rerun()
    if pages>1:
        prev,mid,nxt=st.columns([1,2,1],gap='small')
        with prev:
            if st.button('◀ 이전',key=key+'_prev',disabled=p==0,use_container_width=True):
                st.session_state[page_key]=p-1
                st.rerun()
        with mid:
            st.markdown(f'<div class="kid-pages">{p+1} / {pages} 페이지</div>',unsafe_allow_html=True)
        with nxt:
            if st.button('다음 ▶',key=key+'_next',disabled=p>=pages-1,use_container_width=True):
                st.session_state[page_key]=p+1
                st.rerun()
    return st.session_state[chosen_key] if st.session_state[chosen_key] in {c['char'] for c in filtered} else filtered[0]['char']


def page_home():
    progress=st.session_state.progress
    learned=len(NEW_SET.intersection(progress['learned']))
    mastered=sum(is_mastered(c) for c in NEW_SET)
    kid_heading('🏰','오늘의 한자 모험','하루에 5자씩 배우면 드래곤도 쑥쑥 자라요!')
    game_stats([('📖','배운 새 한자',f'{learned}/100'),('🏅','완전히 익힌 한자',f'{mastered}/100'),
                ('⭐','모은 별',f'{progress["xp"]//50}개'),('🔥','연속 공부',f'{study_streak()}일')])
    st.progress(learned/100)
    st.caption('새로 배우는 7급 100자 기준이에요. 8급 50자는 별도로 복습할 수 있어요.')
    pending=review_chars()
    if pending:
        kid_notice(f'오늘 복습을 기다리는 한자가 {len(pending)}자 있어요!','🔔')
        if st.button('🧠 복습 모험 시작',type='primary',key='home_review',use_container_width=True):
            st.session_state.main_nav='복습'
            st.rerun()
    else:
        kid_notice('오늘도 새로운 한자 다섯 글자를 배워 볼까요?','🌈')
    for i in range(20):
        block=NEW[i*5:(i+1)*5]
        if any(item['char'] not in progress['learned'] for item in block):
            grade='7급Ⅱ' if i<10 else '7급'
            st.markdown(f'<div class="kid-mission"><div class="kid-mission-tag">✨ 오늘의 추천 모험</div>'
                        f'<h3>{i+1}단원 · {grade}</h3>'
                        f'<div class="kid-mission-hanja">{" · ".join(x["char"] for x in block)}</div></div>',
                        unsafe_allow_html=True)
            if st.button('📖 이 단원 배우러 가기',type='primary',use_container_width=True,key='home_start_unit'):
                st.session_state['learn_section']='7급 신규 100자'
                st.session_state['learn_new_unit']=i+1
                st.session_state['learn_new_group']=i//5
                st.session_state.main_nav='한자 학습'
                st.rerun()
            break
    else:
        st.success('🎉 100자 모험 완료! 복습으로 마스터를 노려 보세요.')
    cols=st.columns(2,gap='small')
    with cols[0]:
        if st.button('🐉 드래곤 만나기',key='home_dragon',use_container_width=True):
            st.session_state.main_nav='드래곤 게임'
            st.rerun()
    with cols[1]:
        if st.button('✍️ 획순 쓰기',key='home_write',use_container_width=True):
            st.session_state.main_nav='획순 쓰기'
            st.rerun()
    st.caption('개인 학습 보조 앱이며 한국어문회 공식 시험 서비스가 아닙니다.')


def page_learning():
    kid_heading('📚','한자 배우기','원하는 단원 카드를 눌러 모험을 시작해요.')
    section=tile_picker([('7급 신규 100자','🌟 7급 새 한자 100자'),
                         ('8급 50자 복습','🏅 8급 복습 50자')],
                        'learn_section',cols=2,title='어떤 한자를 배울까요?')
    learned=set(st.session_state.progress['learned'])
    if section=='7급 신규 100자':
        def complete(i):
            return all(c['char'] in learned for c in NEW[(i-1)*5:i*5])
        unit=unit_picker('learn_new',20,complete_func=complete)
        cards=NEW[(unit-1)*5:unit*5]
    else:
        def complete(i):
            return all(c['char'] in learned for c in GROUPS['8급'][(i-1)*5:i*5])
        unit=unit_picker('learn_old',10,complete_func=complete)
        cards=GROUPS['8급'][(unit-1)*5:unit*5]
    idx=st.session_state.card_cursor%len(cards)
    card=cards[idx]
    st.markdown(f'<div class="kid-lesson-label">✨ {escape(card["grade"])} · {unit}단원 · {idx+1}/5</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="hanja-card">{escape(card["char"])}</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="card-reading">{escape(label(card))}</div>',unsafe_allow_html=True)
    if card['char'] in ALT:
        st.caption(f'다른 읽기/뜻: {ALT[card["char"]]}')
    if is_mastered(card['char']):
        kid_notice('이 한자는 이미 마스터했어요!','🏆')
    elif card['char'] in learned:
        kid_notice('배운 한자예요. 퀴즈로 기억해 볼까요?','🌟')
    if st.button('🌟 이 한자 배웠어요! +2점',type='primary',
                 disabled=card['char'] in learned,use_container_width=True):
        mark_learned(card['char'])
        st.rerun()
    left,right=st.columns(2,gap='small')
    with left:
        if st.button('⬅️ 이전 글자',use_container_width=True):
            st.session_state.card_cursor=(idx-1)%len(cards)
            st.rerun()
    with right:
        if st.button('다음 글자 ➡️',use_container_width=True):
            st.session_state.card_cursor=(idx+1)%len(cards)
            st.rerun()
    st.caption('✍️ 획순은 상단 ‘획순 쓰기’에서 연습해요.')


def page_quiz():
    if st.session_state.quiz is not None:
        quiz_panel()
        return
    kid_heading('🎯','한자 퀴즈','문제를 풀고 별을 모아 보세요!')
    scopes={
        '7급 전체 (150자)':ALL,
        '신규 7급 (100자)':NEW,
        '7급Ⅱ 신규 (50자)':GROUPS['7급Ⅱ'],
        '7급 신규 (50자)':GROUPS['7급'],
        '8급 복습 (50자)':GROUPS['8급'],
        '내가 학습 표시한 한자':[INDEX[h] for h in st.session_state.progress['learned'] if h in INDEX],
    }
    labels=[('7급 전체 (150자)','🏰 전체 모험 · 150자'),
            ('신규 7급 (100자)','⭐ 새로운 도전 · 100자'),
            ('7급Ⅱ 신규 (50자)','🌱 7급Ⅱ · 50자'),
            ('7급 신규 (50자)','🌿 7급 · 50자'),
            ('8급 복습 (50자)','🏅 8급 다시보기 · 50자'),
            ('내가 학습 표시한 한자',f'📚 내가 배운 글자 · {len(scopes["내가 학습 표시한 한자"])}자')]
    scope=tile_picker(labels,'quiz_scope_tiles',cols=2,title='어떤 모험에 도전할까요?')
    kid_notice('뜻·음·한자 찾기 문제가 섞여 나와요. 최대 10문제!','🧩')
    if st.button('🚀 퀴즈 출발!',type='primary',disabled=not scopes[scope],use_container_width=True):
        start_quiz(scopes[scope],scope)
        st.rerun()
    if not scopes[scope]:
        st.info('아직 배운 한자가 없어요. 한자 배우기에서 시작해 주세요.')


def page_review():
    if st.session_state.quiz is not None and st.session_state.quiz['title']=='오늘의 복습':
        quiz_panel()
        return
    kid_heading('🧠','기억력 훈련소','한 번 더 만나면 더 오래 기억할 수 있어요!')
    due=review_chars()
    game_stats([('🔔','오늘의 복습',f'{len(due)}자'),('🌟','완전히 익힌 글자',f'{sum(is_mastered(c) for c in INDEX)}자')])
    st.caption('틀린 한자는 당일, 맞힌 한자는 1·3·7일 뒤 다시 만나요.')
    if due:
        st.markdown('<div class="kid-notice">📜 오늘 만날 한자 친구들</div>',unsafe_allow_html=True)
        st.markdown('<div class="review-characters">' + ''.join(
            f'<span>{escape(c)}</span>' for c in due[:30])+'</div>',unsafe_allow_html=True)
        if st.button('🧠 복습 퀴즈 시작!',type='primary',use_container_width=True):
            start_quiz([INDEX[h] for h in due],'오늘의 복습')
            st.rerun()
    else:
        kid_notice('오늘의 복습 완료! 새로운 한자를 배워 볼까요?','🎉')
    st.caption('복습 일정은 퀴즈 풀이 기록부터 계산돼요.')


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
    # v1.0~v1.1.6 백업에는 game이 없어도 정상 복원합니다.
    original_game = data.get("game", {})
    if isinstance(original_game, dict):
        starter = original_game.get("starter")
        if starter in DRAGONS:
            cleaned["game"]["starter"] = starter
            cleaned["game"]["active"] = original_game.get("active", starter)
        cleaned["game"]["xp"] = max(0, int(original_game.get("xp", 0)))
        battles = original_game.get("won_battles", [])
        if isinstance(battles, list):
            cleaned["game"]["won_battles"] = list(dict.fromkeys(
                x for x in battles if isinstance(x,str) and len(x) <= 50
            ))[:25]
        update_dragon_ownership(cleaned["game"], completed_unit_count(cleaned))
    return cleaned


def page_records():
    kid_heading('🏆','나의 모험 기록','배운 한자와 모은 별을 한눈에 확인해요.')
    progress=st.session_state.progress
    history=progress['cards']
    attempts=sum(item['attempts'] for item in history.values())
    rights=sum(item['correct'] for item in history.values())
    game_stats([('🎯','푼 문제',f'{attempts}개'),('🥇','정답률',f'{rights/attempts:.0%}' if attempts else '—'),
                ('⭐','모은 점수',f'{progress["xp"]:,}점')])
    grade=tile_picker([('8급','🏅 8급'),('7급Ⅱ','🌱 7급Ⅱ'),('7급','🌿 7급')],
                      'record_grade',cols=3,title='한자 도감을 펼쳐 봐요')
    cards=GROUPS[grade]
    learned=set(progress['learned'])
    st.caption('👑 마스터 · ⭐ 배웠어요 · 🔒 아직 만나지 않았어요')
    for start in range(0,50,10):
        subset=cards[start:start+10]
        html='<div class="record-gallery">'
        for card in subset:
            char=card['char']
            state='master' if is_mastered(char) else 'learned' if char in learned else 'locked'
            tag='👑' if state=='master' else '⭐' if state=='learned' else '🔒'
            html+=(f'<div class="record-item {state}"><div class="record-char">{escape(char)}</div>'
                   f'<div class="record-reading">{escape(label(card))}</div>'
                   f'<div class="record-status">{tag}</div></div>')
        st.markdown(html+'</div>',unsafe_allow_html=True)
    # Preserve the original detailed record and backup features for parents.
    rows=[]
    for g in ('8급','7급Ⅱ','7급'):
        for card in GROUPS[g]:
            char=card['char']
            item=history.get(char,{})
            if char in learned or item:
                rows.append({'급수':g,'한자':char,'훈음':label(card),
                             '학습 표시':'완료' if char in learned else '-',
                             '풀이 횟수':item.get('attempts',0),
                             '정답 횟수':item.get('correct',0),
                             '숙달':'완료' if is_mastered(char) else '진행 중',
                             '다음 복습일':item.get('due','-')})
    with st.expander('👨‍👩‍👧 학부모용 자세한 학습 기록 · 백업',expanded=False):
        if rows:
            st.dataframe(rows,use_container_width=True,hide_index=True)
        else:
            st.info('아직 학습 기록이 없습니다.')
        st.markdown('**학습기록 저장과 복원**')
        st.warning('무료 Streamlit 서버의 세션 데이터는 영구 저장이 아닙니다. 공부한 뒤 JSON 백업을 보관하세요.')
        backup=json.dumps({'version':'1.2.2','progress':progress},ensure_ascii=False,indent=2)
        st.download_button('💾 학습기록 파일 저장하기',data=backup,
                           file_name=f'hanja_progress_{today().isoformat()}.json',
                           mime='application/json',type='primary')
        upload=st.file_uploader('이전에 저장한 JSON 파일 선택',type=['json'])
        if st.button('🔄 저장한 기록 불러오기',disabled=upload is None):
            try:
                payload=json.loads(upload.getvalue().decode('utf-8-sig'))
                st.session_state.progress=restore_progress(payload['progress'])
                st.session_state.quiz=None
                st.session_state.dragon_battle=None
                st.success('학습 기록을 불러왔습니다.')
            except (ValueError,TypeError,KeyError,AttributeError) as error:
                st.error(f'파일을 복원하지 못했습니다: {error}')
        st.markdown('**기록 관리**')
        if not st.session_state.get('reset_confirm_mode',False):
            if st.button('🔐 전체 기록 초기화 메뉴 열기'):
                st.session_state.reset_confirm_mode=True
                st.rerun()
        else:
            st.error('학습 기록과 드래곤 성장 정보가 모두 초기화됩니다. 되돌릴 수 없습니다.')
            cancel,confirm=st.columns(2)
            with cancel:
                if st.button('↩️ 취소',use_container_width=True):
                    st.session_state.reset_confirm_mode=False
                    st.rerun()
            with confirm:
                if st.button('🗑️ 정말 모두 삭제',type='primary',use_container_width=True):
                    st.session_state.progress=fresh_progress()
                    st.session_state.quiz=None
                    st.session_state.dragon_battle=None
                    st.session_state.reset_confirm_mode=False
                    st.rerun()


def dragon_image(key, stage):
    """캐릭터 이미지의 절대경로. 파일이 없으면 이모지로 대체합니다."""
    if key not in DRAGONS or stage not in (1, 2, 3):
        return None
    path = Path(__file__).resolve().parent / "assets" / "dragons" / f"{key}_{stage}.webp"
    return str(path) if path.is_file() else None


def dragon_art(key, stage, caption=None):
    """이미지와 텍스트를 분리하여 Streamlit 재실행에서도 안전하게 표시."""
    img = dragon_image(key, stage)
    if img:
        st.image(img, use_container_width=True)
    else:
        st.markdown(f'<div class="dragon-fallback">{DRAGONS[key]["icon"]} 🐉</div>',
                    unsafe_allow_html=True)
    if caption:
        st.markdown(f'<div class="dragon-art-caption">{escape(caption)}</div>',
                    unsafe_allow_html=True)


def page_dragons():
    """기존 v1.2.0 배틀 로직을 유지한 카드형 캐릭터 및 스킬 인터페이스."""
    kid_heading('🐉', '드래곤 가디언즈', '한자를 익히고, 기술을 배우고, 멋진 수호룡으로 성장해요!')
    progress = st.session_state.progress
    game = progress.setdefault("game", fresh_game())
    units = completed_unit_count(progress)
    update_dragon_ownership(game, units)
    battle = st.session_state.get("dragon_battle")

    if game["starter"] not in DRAGONS:
        st.markdown("### 함께 모험할 드래곤을 선택하세요")
        st.info("첫 번째 드래곤을 선택하세요. 나머지 두 드래곤은 10·20단원 완료 시 얻을 수 있어요.")
        cols = st.columns(3, gap="medium")
        for idx, (key, dragon) in enumerate(DRAGONS.items()):
            with cols[idx]:
                with st.container(key=f"dragon_starter_card_{key}"):
                    dragon_art(key, 1)
                    st.markdown(f'<div class="dragon-card-symbol">{dragon["hanja"][0]}</div>'
                                f'<div class="dragon-card-name">{dragon["name"]}</div>'
                                f'<div class="dragon-card-caption">{dragon["kind"]} · {dragon["forms"][0]}</div>',
                                unsafe_allow_html=True)
                    if st.button(f"{dragon['name']} 선택", key=f"dragon_starter_{key}",
                                 type="primary", use_container_width=True):
                        game["starter"] = key
                        game["active"] = key
                        update_dragon_ownership(game, units)
                        st.rerun()
        return

    # 소유 캐릭터는 카드로 전환. 전투 중에는 변경을 막아 배틀 보상/연출 상태를 보존.
    st.markdown("### 내 드래곤 선택")
    if battle is not None:
        st.caption("배틀 진행 중에는 드래곤을 바꿀 수 없어요. 배틀 종료 후 선택할 수 있습니다.")
    cols = st.columns(3, gap="medium")
    wins = len(game["won_battles"])
    stage = evolution_stage(units, wins)
    for idx, (key, character) in enumerate(DRAGONS.items()):
        owned = key in game["owned"]
        active = key == game["active"]
        with cols[idx]:
            with st.container(key=f"dragon_select_card_{key}"):
                dragon_art(key, stage if owned else 1)
                st.markdown(f'<div class="dragon-card-symbol">{character["hanja"][stage-1] if owned else character["hanja"][0]}</div>'
                            f'<div class="dragon-card-name">{character["name"]}</div>',
                            unsafe_allow_html=True)
                if owned:
                    msg = "선택 중 ✓" if active else f"{character['name']} 선택"
                else:
                    others = [x for x in DRAGONS if x != game["starter"]]
                    needed = 10 if key == others[0] else 20
                    msg = f"🔒 {needed}단원 해금"
                if st.button(msg, key=f"dragon_switch_{key}",
                             type="primary" if active and owned else "secondary",
                             use_container_width=True,
                             disabled=(not owned) or active or (battle is not None)):
                    game["active"] = key
                    st.rerun()

    chosen = game["active"]
    dragon = DRAGONS[chosen]
    skills = unlocked_skills(chosen, units, stage)
    with st.container(key="dragon_feature_hero"):
        colpic, colinfo = st.columns([1, 1.7], gap="medium", vertical_alignment="center")
        with colpic:
            dragon_art(chosen, stage)
        with colinfo:
            st.caption(f"{dragon['kind']} 속성 · {stage}단계 진화")
            st.markdown(f'<div class="dragon-hero-name">{escape(dragon["name"])} · '
                        f'{escape(dragon["forms"][stage-1])}</div>'
                        f'<div class="dragon-hero-hanja" style="color:{dragon["color"]}">'
                        f'{dragon["hanja"][stage-1]}</div>', unsafe_allow_html=True)
            st.caption("한자의 힘으로 성장하는 나의 드래곤")

    game_stats([('📚','학습 단원',f'{units}/20'),('⚡','배운 기술',f'{len(skills)}/8'),
                ('💎','드래곤 XP',f'{game["xp"]:,}'),('🏆','승리한 배틀',f'{wins}개')])
    st.progress(units / 20)
    st.caption(f"드래곤 레벨 {1 + game['xp'] // 60} · 다음 레벨까지 {60 - game['xp'] % 60} XP")
    if stage == 1:
        st.caption("1차 진화: 신규 단원 5개 학습 완료 + 서로 다른 배틀 1회 승리")
    elif stage == 2:
        st.caption("최종 진화: 신규 단원 15개 학습 완료 + 서로 다른 배틀 3회 승리")
    else:
        st.success("최종 진화 달성! 전설의 수호 드래곤과 함께하세요.")

    with st.expander("기술 도감 · 해금 조건", expanded=False):
        skills_html='<div class="skill-gallery">'
        for i,(requirement, min_stage, move, reference) in enumerate(SKILL_TREE[chosen]):
            available=units>=requirement and stage>=min_stage
            icon=SKILL_ICONS[chosen][i] if available else '🔒'
            detail='배운 기술!' if available else f'{requirement}단원 · 진화 {min_stage}단계'
            skills_html+=(f'<div class="skill-entry {"unlocked" if available else "locked"}">'
                          f'<span>{icon}</span><strong>{escape(move)}</strong>'
                          f'<small>{escape(detail)}</small></div>')
        st.markdown(skills_html+'</div>',unsafe_allow_html=True)
        st.caption("기술은 속성별로 총 8개입니다. 해금 조건을 달성하면 배틀에서 선택할 수 있어요.")

    if battle is None:
        st.divider()
        st.markdown("### 한자 배틀 시작")
        scopes = ["8급 복습"] + [f"신규 {n}단원" for n in range(1, 21)]
        if len(progress.get("learned", [])) >= 5:
            scopes.insert(1, "학습 완료 한자")
        general=[(s, '🏅 '+s if s=='8급 복습' else '📚 '+s) for s in scopes if not s.startswith('신규 ')]
        mode=tile_picker([('basic','🛡️ 기본 모험'),('unit','📖 단원별 모험')],
                         'battle_scope_mode',cols=2,title='전투할 모험의 종류')
        if mode=='basic':
            scope=tile_picker(general,'battle_scope_basic',cols=2)
        else:
            selected_unit=unit_picker('battle_new_unit',20,
                                      complete_func=lambda n: all(c['char'] in progress['learned'] for c in NEW[(n-1)*5:n*5]))
            scope=f'신규 {selected_unit}단원'
            kid_notice(f'{selected_unit}단원 한자로 전투해요!','⚔️')
        pool=battle_scope_pool(progress,scope)
        st.caption("5문제 중 4문제 이상 정답이면 승리! 처음 승리한 범위마다 경험치 30점을 받습니다.")
        if st.button("드래곤 배틀 시작", type="primary", use_container_width=True,
                     disabled=len(pool) < 5):
            st.session_state.dragon_battle_serial = st.session_state.get("dragon_battle_serial", 0) + 1
            st.session_state.dragon_battle = fresh_battle(
                pool, scope, st.session_state.dragon_battle_serial)
            st.rerun()
        return

    st.divider()
    st.markdown(f"### {battle['scope']} · 한자 배틀")
    n = len(battle["questions"])
    index = battle["index"]
    if index >= n:
        won = battle["correct"] >= 4
        if not battle["rewarded"]:
            battle["new_reward"] = award_first_win(game, battle["scope"]) if won else False
            battle["rewarded"] = True
        if won:
            st.success(f"배틀 승리! {n}문제 중 {battle['correct']}문제 정답")
        else:
            st.warning(f"배틀 종료 · {n}문제 중 {battle['correct']}문제 정답. 복습하고 다시 도전해요!")
        if battle.get("new_reward"):
            st.info("처음 승리한 범위! 드래곤 경험치 +30 XP")
        elif won:
            st.caption("이 범위의 첫 승리 보상은 이미 받았어요. 재도전은 언제든 가능합니다.")
        if st.button("다른 배틀 선택", type="primary", use_container_width=True):
            st.session_state.dragon_battle = None
            st.rerun()
        return

    st.progress(index / n)
    st.caption(f"문제 {index+1} / {n} · 현재 정답 {battle['correct']}개")
    q = battle["questions"][index]
    col1, col2 = st.columns([1, 1], gap="medium")
    with col1:
        with st.container(key="dragon_battle_fighter"):
            dragon_art(chosen, stage)
            st.markdown(f'<div class="dragon-art-caption">{escape(dragon["name"])} · 내 드래곤</div>',
                        unsafe_allow_html=True)
    with col2:
        enemy_hp = max(0, 100 - 25 * battle["correct"])
        with st.container(key="dragon_battle_enemy"):
            st.markdown('<div class="dragon-enemy-icon">👾</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="dragon-art-caption">상대 몬스터 · HP {enemy_hp}/100</div>',
                        unsafe_allow_html=True)
            st.progress(enemy_hp / 100)
    st.markdown(f'<div class="battle-char">{escape(q["char"])}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="battle-prompt">{escape(q["title"])}</div>', unsafe_allow_html=True)

    if not battle["answered"]:
        # 최신 습득 기술을 처음 선택하되, 버튼으로 바꾼 뒤에도 선택 상태가 유지됩니다.
        skill_names = [entry[2] for entry in skills]
        if battle.get("move") not in skill_names:
            battle["move"] = skill_names[-1]
        st.markdown("#### 사용할 기술 선택")
        with st.container(key="dragon_skill_grid"):
            for i in range(0, len(skill_names), 2):
                cs = st.columns(2, gap="small")
                for j, name in enumerate(skill_names[i:i+2]):
                    with cs[j]:
                        selected_move = battle["move"] == name
                        icon = SKILL_ICONS[chosen][i+j]
                        if st.button(f"{icon}  {name}" + ("  ✓" if selected_move else ""),
                                     key=f"dragon_skill_{battle['serial']}_{index}_{i+j}",
                                     type="primary" if selected_move else "secondary",
                                     use_container_width=True):
                            battle["move"] = name
                            st.rerun()
        st.markdown("#### 정답 선택")
        with st.container(key="dragon_answers"):
            for i, option in enumerate(q["choices"]):
                if st.button(f"{i+1}.  {option}",
                             key=f"dragon_answer_{battle['serial']}_{index}_{i}",
                             type="primary" if battle["selected"] == option else "secondary",
                             use_container_width=True):
                    battle["selected"] = option
                    st.rerun()
        if st.button(f"{battle['move']} 사용하기!", type="primary",
                     disabled=battle["selected"] is None, use_container_width=True):
            correct = battle["selected"] == q["answer"]
            register_answer(q["char"], correct)
            battle["answered"] = True
            battle["last_correct"] = correct
            battle["last_skill"] = battle["move"]
            if correct:
                battle["correct"] += 1
            st.rerun()
    else:
        if battle["last_correct"]:
            st.markdown(f'<div class="dragon-attack-result dragon-attack-{chosen}">'
                        f'✨ {escape(battle["last_skill"])} 성공! 상대 몬스터에게 피해를 주었어요!'
                        '</div>', unsafe_allow_html=True)
        else:
            st.error(f"이번엔 빗나갔어요. 정답은 '{q['answer']}'입니다.")
        if st.button("다음 문제" if index+1 < n else "배틀 결과 보기",
                     type="primary", use_container_width=True):
            battle["index"] += 1
            battle["selected"] = None
            battle["answered"] = False
            st.rerun()
    if st.button("현재 배틀 종료", type="secondary"):
        st.session_state.dragon_battle = None
        st.rerun()
    st.caption("캐릭터는 직접 제작한 드래곤 이미지입니다. 한국식 획순 검증은 별도 진행 중입니다.")



def page_writing():
    # HanziWriter/Chinese stroke ordering notice unchanged; UI only.
    kid_heading('✍️','마법 한자 쓰기','한자 카드를 고르고, 획순을 보며 직접 써 보세요!')
    view=tile_picker([('단원별','📖 단원별 쓰기'),('학습 완료','⭐ 배운 글자'),
                      ('전체 한자','🗺️ 전체 한자')],
                     'stroke_view_tiles',cols=3,title='어떻게 연습할까요?')
    if view=='단원별':
        grade=tile_picker([('7급Ⅱ','🌱 7급Ⅱ'),('7급','🌿 7급'),('8급','🏅 8급')],
                          'stroke_grade_tiles',cols=3,title='급수를 골라요')
        unit=unit_picker('stroke_units_'+grade,10)
        cards=GROUPS[grade][(unit-1)*5:unit*5]
        st.caption('이 단원의 다섯 글자를 모두 연습해 볼 수 있어요.')
    elif view=='학습 완료':
        learned=set(st.session_state.progress['learned'])
        cards=[c for c in ALL if c['char'] in learned]
        if not cards:
            kid_notice('아직 배운 한자가 없어요. 한자 배우기에서 별을 눌러 주세요.','🌱')
            return
    else:
        grade=tile_picker([('전체 150자','🗺️ 전체'),('8급','🏅 8급'),
                           ('7급Ⅱ','🌱 7급Ⅱ'),('7급','🌿 7급')],
                          'stroke_all_grade_tiles',cols=2,title='한자 모험 범위')
        cards=ALL if grade=='전체 150자' else GROUPS[grade]
    if view=='단원별':
        selection_id=f'stroke_unit_pick_{grade}_{unit}'
        if st.session_state.get(selection_id) not in [c['char'] for c in cards]:
            st.session_state[selection_id]=cards[0]['char']
        st.markdown('<div class="kid-small-title">한자를 하나 골라 보세요</div>',unsafe_allow_html=True)
        with st.container(key='stroke_unit_buttons'):
            for row in (cards[:3],cards[3:]):
                cols=st.columns(len(row),gap='small')
                for card,col in zip(row,cols):
                    with col:
                        selected=st.session_state[selection_id]==card['char']
                        if st.button(card['char']+(' ✓' if selected else ''),
                                     use_container_width=True,
                                     type='primary' if selected else 'secondary',
                                     key=f'stroke_pick_{grade}_{unit}_{card["char"]}'):
                            st.session_state[selection_id]=card['char']
                            st.rerun()
        char=st.session_state[selection_id]
    else:
        selection_key=f'stroke_gallery_{view}_{grade if view=="전체 한자" else "learned"}'
        char=select_stroke_char(cards,selection_key,limit=12)
        if char is None:
            return

    # 작게 표시되던 '선택한 한자' 설명을 별도 큰 카드로 개선.
    selected_card = INDEX[char]
    st.markdown(
        '<div class="selected-hanja-banner">'
        f'<span class="selected-hanja-symbol">{escape(char)}</span>'
        '<div class="selected-hanja-info">'
        '<span class="selected-hanja-caption">지금 연습할 한자</span>'
        f'<strong>{escape(label(selected_card))}</strong>'
        f'<span class="selected-hanja-grade">{escape(selected_card["grade"])}</span>'
        '</div></div>',
        unsafe_allow_html=True,
    )
    st.caption("※ 현재 쓰기 판정은 중국식 데이터 기준이며 한국식 획순 검증은 진행 전입니다.")
    with st.expander("학부모 안내 · 획순 데이터 검증 상태"):
        st.info(
            "획순 애니메이션과 자동 판정은 Hanzi Writer의 중국식 데이터 기준입니다. "
            "배정한자 150자를 선택할 수 있지만 한국식 획순 전체 검증은 아직 완료되지 않았습니다."
        )

    # 수동으로 획수를 먼저 확인했던 5자만 별도 개수 검사합니다.
    # 나머지는 라이브러리의 실제 획 데이터 개수로 숫자를 생성합니다.
    checked_counts = {"山": 3, "木": 4, "人": 2, "日": 4, "水": 4}
    char_js = json.dumps(char, ensure_ascii=False)
    expected_js = json.dumps(checked_counts.get(char))
    html = r'''
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<script src="https://cdn.jsdelivr.net/npm/hanzi-writer@3.5/dist/hanzi-writer.min.js"></script>
<style>
  * { box-sizing: border-box; }
  body { margin:0; font-family:"Malgun Gothic","Apple SD Gothic Neo",system-ui,sans-serif;
    color:#20364A; background:#F7FAFD; }
  .wrap { display:flex; flex-direction:column; align-items:center; gap:12px;
    padding:10px 6px 14px; max-width:520px; margin:auto; }
  .board { width:min(100%,360px); aspect-ratio:1/1; border:2px solid #B9D6E8;
    border-radius:20px; background:#fff; position:relative; overflow:hidden;
    box-shadow:0 12px 26px rgba(40,73,100,.10); }
  .board::before { content:""; position:absolute; inset:0;pointer-events:none;
    background:linear-gradient(to right,transparent calc(50% - .5px),#E6EDF5 50%,transparent calc(50% + .5px)),
               linear-gradient(to bottom,transparent calc(50% - .5px),#E6EDF5 50%,transparent calc(50% + .5px)); }
  #target {width:100%;height:100%;touch-action:none;position:relative;z-index:1;}
  #target svg {touch-action:none;width:100%;height:100%;display:block;}
  #numbers { position:absolute;inset:0;width:100%;height:100%;
    pointer-events:none; overflow:visible;z-index:2; }
  .toolbar { display:grid; grid-template-columns:repeat(2,minmax(0,1fr));
    width:min(100%,470px);gap:10px; }
  button { font:700 17px/1.35 "Malgun Gothic",system-ui,sans-serif;
    cursor:pointer; border:1.5px solid #C9DBE7;
    border-radius:14px; min-height:57px; padding:10px 12px;
    background:#fff; color:#213B52;box-shadow:0 3px 8px rgba(36,77,111,.06); }
  button:disabled {cursor:not-allowed;opacity:.5;}
  button.primary {background:#127F91;color:white;border-color:#127F91;}
  .settings {font-size:17px;font-weight:600;display:flex;align-items:center;gap:10px;}
  input[type=checkbox] {width:23px;height:23px;accent-color:#127F91;}
  #status {font-size:16px;text-align:center;max-width:470px;min-height:54px;
    line-height:1.6;padding:6px 10px;background:#EDF5FA;border-radius:12px;width:100%;}
  #counter {font-size:21px;font-weight:800;color:#203B55;}
  @media(max-width:380px) {
    .toolbar {gap:7px;}button {font-size:14px;min-height:56px;padding:9px 6px;}
    #counter {font-size:18px;}#status {font-size:14px;}
  }
</style>
</head>
<body>
<div class="wrap">
  <div id="counter">획순 데이터를 읽는 중...</div>
  <div class="board">
    <div id="target" aria-label="한자 쓰기 영역"></div>
    <svg id="numbers" xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 360 360" aria-hidden="true"></svg>
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
const SIZE = 360;
const PAD = 22;
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
      if (!Number.isInteger(strokeCount) || strokeCount<1 ||
          !Array.isArray(data.medians) || data.medians.length!==strokeCount ||
          (expectedCount!==null && strokeCount!==expectedCount)) {
        validNumberData=false;
        status('획 데이터가 불완전하거나 확인한 획수와 다릅니다. 번호 표시를 중지했습니다.');
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
    components.html(html, height=724, scrolling=False)
    st.caption(
        "학습 범위: 8급부터 7급까지 150자 선택 지원. 숫자는 각 획 옆의 시작점 근처에 표시됩니다. "
        "한국식 획순 검증 전 시범 적용이며 쓰기 성공 여부는 아직 별·점수·학습기록에 연결되지 않습니다."
    )

st.markdown("""
<style>
/* 한자 탐험대 v1.1.6: 학습 프로그램형 테마. 기능 로직과 분리된 UI 전용 CSS */
:root { --study-navy:#253B54; --study-teal:#168A94;
        --study-bg:#F5F9FC; --study-border:#DAE6EE; }
.stApp {background:linear-gradient(180deg,#EAF5FA 0,#F6F9FC 280px,#FBFCFE 100%);}
.block-container {max-width:1080px;padding-top:1.15rem;padding-bottom:3rem;}
.study-hero {padding:26px 32px;border-radius:24px;background:linear-gradient(115deg,#176B84,#239A9D);
  color:white;box-shadow:0 12px 30px rgba(12,91,111,.17);margin-bottom:20px;}
.study-hero-kicker {font-size:13px;font-weight:800;letter-spacing:1.6px;opacity:.85;margin-bottom:7px;}
.study-hero h1 {font-size:clamp(29px,4vw,43px);letter-spacing:-.045em;
  margin:0 0 5px;line-height:1.3;color:#fff;}
.study-hero p {font-size:clamp(15px,1.8vw,18px);font-weight:500;line-height:1.65;
  margin:0;color:#EDFAFE;}
/* 일관된 여백·카드·큰 터치 타깃 */
[data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stMetric"]) {border-radius:18px;}
[data-testid="stMetric"] {border:1px solid var(--study-border);border-radius:18px;
  padding:18px 14px;background:white;box-shadow:0 4px 13px rgba(47,77,104,.04);}
[data-testid="stMetricValue"] {font-size:clamp(22px,3vw,31px);color:var(--study-navy);}
[data-testid="stMetricLabel"] {font-size:15px;font-weight:700;}
h2,h3 {color:var(--study-navy);letter-spacing:-.035em;}
div.stButton > button, div.stDownloadButton > button {min-height:54px;border-radius:14px;
  padding:10px 20px;font-size:17px;font-weight:750;}
[data-testid="stSelectbox"] [data-baseweb="select"] {min-height:50px;}
[data-testid="stSelectbox"] [data-baseweb="select"] div {font-size:17px;}
/* 상단 메뉴를 누르기 편한 학습 탭으로 구성 */
.st-key-main_nav [role="radiogroup"] {padding:11px 12px;border:1px solid var(--study-border);
  border-radius:16px;background:#FFF;gap:10px;flex-wrap:wrap;}
.st-key-main_nav [role="radiogroup"] label {padding:8px 7px;border-radius:12px;}
.st-key-main_nav [role="radiogroup"] label p {font-size:16px;font-weight:750;}
/* 한자 학습 카드 */
.hanja-card {font-size:clamp(130px,18vw,190px);font-weight:650;
  text-align:center;padding:20px 12px;border:2px solid #D5E4ED;
  border-radius:23px;background:#FFF;color:#192F49;line-height:1.45;
  box-shadow:0 7px 19px rgba(55,95,123,.06);font-family:"Noto Serif CJK KR","Batang",serif;}
.card-reading {font-size:clamp(28px,3.9vw,38px);font-weight:800;text-align:center;
  padding:13px;color:#213B55;}
/* 퀴즈 문제와 객관식 보기: 화면의 주인공이 되도록 확대 */
.st-key-quiz_problem_area {padding:8px 0 12px;}
.quiz-symbol {font-size:clamp(155px,23vw,215px);padding:16px 10px;}
.quiz-prompt {font-size:clamp(25px,3.3vw,34px);font-weight:800;line-height:1.6;
  color:#213953;text-align:center;padding:20px 10px 12px;word-break:keep-all;}
/* 보기 4개는 Streamlit 기본 라디오 대신 크기 확실한 큰 버튼으로 표시 */
.st-key-quiz_choice_area {display:flex;flex-direction:column;gap:10px;}
.st-key-quiz_choice_area div.stButton > button {
  width:100%!important;min-height:103px!important;
  padding:18px 30px!important;border-radius:20px!important;
  border:3px solid #C5DFE9!important;background:#FFFFFF!important;
  color:#1D3852!important;text-align:left!important;
  justify-content:flex-start!important;white-space:normal!important;
  font-size:clamp(30px,3.6vw,40px)!important;line-height:1.4!important;
  font-weight:850!important;box-shadow:0 5px 16px rgba(37,67,90,.06)!important;
  transition:background-color .15s,border-color .15s;
}
.st-key-quiz_choice_area div.stButton > button p,
.st-key-quiz_choice_area div.stButton > button span,
.st-key-quiz_choice_area div.stButton > button div {
  font-size:inherit!important;font-weight:inherit!important;
  line-height:inherit!important;white-space:normal!important;text-align:left!important;
}
.st-key-quiz_choice_area div.stButton > button:hover:not(:disabled) {
  border-color:#168A94!important;background:#F1FAFC!important;
}
.st-key-quiz_choice_area div.stButton > button[data-testid="stBaseButton-primary"] {
  border-color:#168A94!important;background:#DEF6F2!important;
  color:#075C65!important;box-shadow:0 0 0 2px #B7E8E3!important;
}
.st-key-quiz_choice_area div.stButton > button:disabled {
  opacity:.9!important;cursor:default!important;
}
/* 획순 쓰기: 선택 버튼과 선택한 글자를 크게 표시 */
.st-key-stroke_unit_buttons div.stButton > button {font-size:clamp(37px,5.1vw,49px);
  min-height:92px;font-family:"Noto Serif CJK KR","Batang",serif;
  font-weight:700;border:2px solid #CCDFE9;border-radius:18px;}
.st-key-stroke_unit_buttons div.stButton > button[kind="primary"] {
  background:#157E91;border-color:#157E91;color:#fff;}
.selected-hanja-banner {display:flex;gap:20px;align-items:center;background:#FFF;
  padding:16px 23px;border:2px solid #D4E8EB;border-radius:20px;
  margin:17px 0 14px;box-shadow:0 6px 15px rgba(39,82,108,.05);}
.selected-hanja-symbol {font-family:"Noto Serif CJK KR","Batang",serif;
  font-size:clamp(60px,8vw,92px);color:#116E83;font-weight:700;
  min-width:clamp(65px,10vw,105px);line-height:1.3;text-align:center;}
.selected-hanja-info {display:flex;flex-direction:column;gap:4px;}
.selected-hanja-info strong {font-size:clamp(25px,3.3vw,35px);
  color:#213953;font-weight:800;}
.selected-hanja-caption,.selected-hanja-grade {font-size:14px;color:#597184;font-weight:700;}
@media(max-width:680px) {
  .block-container {padding-top:.7rem;}
  .study-hero {padding:19px 20px;border-radius:19px;margin-bottom:13px;}
  .st-key-quiz_choice_area div.stButton > button {
    min-height:91px!important;padding:13px 19px!important;
    font-size:32px!important;border-radius:16px!important;
  }
  .st-key-stroke_unit_buttons div.stButton > button {min-height:78px;font-size:37px;}
  .selected-hanja-banner {padding:12px 15px;gap:14px;}
}

/* 드래곤 가디언즈: v1.1.6 퀴즈·획순 스타일은 변경하지 않습니다. */
.dragon-pick-card{background:#fff;min-height:213px;border:2px solid #D8E8EE;
  border-radius:20px;padding:18px 12px;text-align:center;display:flex;
  flex-direction:column;align-items:center;gap:8px;margin-bottom:10px;}
.dragon-pick-card strong{font-size:25px;color:#243D52;}
.dragon-pick-card small{font-size:14px;color:#597386;}
.dragon-icon{font-size:48px;}.dragon-big-hanja{font-size:49px;font-weight:800;color:#237D86;}
.dragon-hero-card{display:flex;align-items:center;gap:26px;padding:22px 26px;
  border-radius:24px;background:#fff;border:2px solid var(--dragon-accent);
  margin-bottom:15px;box-shadow:0 8px 18px rgba(30,70,95,.07);}
.dragon-avatar{font-size:76px;white-space:nowrap;}
.dragon-subtitle{font-size:15px;color:#5A788B;font-weight:800;}
.dragon-hero-name{font-size:clamp(24px,3.3vw,37px);font-weight:900;color:#223952;}
.dragon-hero-hanja{font-size:clamp(50px,7vw,77px);font-weight:800;color:var(--dragon-accent);}
.battle-fighter{border:2px solid #D7E6EE;border-radius:20px;background:#fff;
  padding:16px 8px;text-align:center;font-size:55px;min-height:138px;}
.battle-fighter span{font-size:17px;color:#38586D;font-weight:800;}
.battle-enemy{background:#FFF8F4;}
.battle-char{background:white;border:2px solid #CFE4EB;border-radius:22px;
  font-size:clamp(135px,20vw,185px);font-family:serif;text-align:center;
  line-height:1.35;margin:16px 0 5px;color:#253A54;}
.battle-prompt{text-align:center;font-size:clamp(23px,3vw,32px);
  font-weight:900;margin:11px 0 18px;color:#243F58;}
.st-key-dragon_answers div.stButton>button{width:100%!important;min-height:77px!important;
  font-size:clamp(24px,3vw,34px)!important;border:2px solid #BFD9E5!important;
  border-radius:16px!important;text-align:left!important;justify-content:flex-start!important;}
.st-key-dragon_answers div.stButton>button p{font-size:inherit!important;font-weight:800!important;}
@media(max-width:680px){
  .dragon-hero-card{padding:12px;gap:10px;}
  .dragon-avatar{font-size:45px;}
  .battle-fighter{font-size:38px;min-height:105px;}
  .battle-fighter span{font-size:12px;}
  .dragon-pick-card{padding:10px 6px;min-height:174px;}
  .dragon-icon{font-size:30px;}.dragon-big-hanja{font-size:35px;}
  .dragon-pick-card strong{font-size:18px;}
  .dragon-pick-card small{font-size:11px;}
  .st-key-dragon_answers div.stButton>button{min-height:85px!important;font-size:28px!important;}
}

/* v1.2.1 드래곤 이미지 카드: 기존 퀴즈·획순 UI와 분리 */
[class*="st-key-dragon_starter_card_"],
[class*="st-key-dragon_select_card_"] {
  background: #fff;
  border: 2px solid #D7E6EF;
  border-radius: 22px;
  padding: 14px 10px 16px;
  text-align: center;
  box-shadow: 0 5px 16px rgba(36, 79, 106, .07);
}
[class*="st-key-dragon_select_card_"]:has(button[kind="primary"]) {
  border-color:#27A9AD;
  box-shadow: 0 6px 20px rgba(22, 122, 135, .16);
}
[class*="st-key-dragon_starter_card_"] img,
[class*="st-key-dragon_select_card_"] img{
  max-height: 205px;
  object-fit: contain;
}
.dragon-card-symbol {font-size:clamp(33px,4vw,50px);font-weight:900;color:#216C83;}
.dragon-card-name{font-size:clamp(20px,2.5vw,28px);font-weight:900;color:#243B51;}
.dragon-card-caption{font-size:13px;font-weight:700;color:#627D91;margin-bottom:8px;}
.dragon-fallback{text-align:center;font-size:82px;min-height:170px;}
.dragon-art-caption {font-size:16px;font-weight:850;text-align:center;color:#34506A;margin-top:3px;}
.st-key-dragon_feature_hero {
  border:2px solid #D4E6EC;border-radius:24px;background:linear-gradient(135deg,#FFFFFF 0%,#EAF8F8 100%);
  padding:15px 24px;margin:18px 0 16px;
}
.st-key-dragon_feature_hero img{max-height:255px;object-fit:contain;}
.st-key-dragon_battle_fighter,.st-key-dragon_battle_enemy{
  min-height:250px;border:2px solid #D4E6EC;border-radius:20px;
  padding:10px 16px;background:#fff;
}
.st-key-dragon_battle_fighter img{max-height:210px;object-fit:contain;}
.st-key-dragon_battle_enemy{background:linear-gradient(135deg,#FFF8F0,#F5F3FF);}
.dragon-enemy-icon{font-size:122px;text-align:center;line-height:1.75;}
.st-key-dragon_skill_grid div.stButton > button{
  min-height:71px!important;border-radius:17px!important;
  padding:10px 14px!important;font-size:clamp(18px,2.25vw,25px)!important;
  font-weight:850!important;border:2px solid #B5D8E4!important;
}
.st-key-dragon_skill_grid div.stButton > button[kind="primary"]{
  border-color:#147A8C!important; box-shadow:0 0 0 3px rgba(28,131,155,.15);
}
.st-key-dragon_skill_grid div.stButton > button p{font-size:inherit!important;font-weight:850!important;}
.dragon-attack-result{border-radius:16px;padding:20px 14px;font-size:clamp(20px,3vw,28px);
 font-weight:900;text-align:center;animation:dragonAttackPulse .8s ease-in-out 1;
 border:2px solid #C2DCEC;background:#ECF9FF;color:#205580;}
.dragon-attack-fire{background:#FFF2E9;border-color:#F5B684;color:#A34D1B;}
.dragon-attack-water{background:#EAF6FF;border-color:#99CEF8;color:#2069A6;}
.dragon-attack-forest{background:#EDF9EF;border-color:#9CD5B3;color:#237749;}
@keyframes dragonAttackPulse{0%{transform:scale(.96);opacity:.6}65%{transform:scale(1.015);opacity:1}100%{transform:scale(1)}}
@media(max-width:680px){
 [class*="st-key-dragon_starter_card_"], [class*="st-key-dragon_select_card_"]{padding:8px 4px;}
 [class*="st-key-dragon_starter_card_"] img,[class*="st-key-dragon_select_card_"] img{max-height:120px;}
 .dragon-card-symbol{font-size:29px;}.dragon-card-name{font-size:18px;}
 .dragon-card-caption{font-size:11px;}
 .st-key-dragon_feature_hero{padding:11px 14px;}
 .st-key-dragon_feature_hero img{max-height:160px;}
 .st-key-dragon_battle_fighter,.st-key-dragon_battle_enemy{min-height:180px;padding:6px;}
 .st-key-dragon_battle_fighter img{max-height:150px;}
 .dragon-enemy-icon{font-size:83px;}
 .st-key-dragon_skill_grid div.stButton > button{min-height:79px!important;font-size:22px!important;}
}

</style>
""", unsafe_allow_html=True)


# v1.2.2 playground theme. The HanziWriter iframe and grading logic are untouched.
st.markdown(r"""
<style>
:root { --kid-ink:#303753; --kid-berry:#7452B5; --kid-cream:#FFFDF7;
        --kid-peach:#FFE3CA; --kid-mint:#D9F7EB; --kid-lilac:#EEE7FE; }
.stApp {background:radial-gradient(ellipse 80% 430px at 50% 0%,#E8E6FF 0%,transparent 75%),
                 linear-gradient(180deg,#FFF9F0 0%,#FAF8FF 54%,#F2FAFF 100%);}
.block-container {max-width:1060px;padding-top:1rem;padding-bottom:3rem;}
h1,h2,h3,[data-testid="stMarkdownContainer"] h2,[data-testid="stMarkdownContainer"] h3{color:#373558;}
/* Grand fantasy banner, not a productivity dashboard */
.study-hero{position:relative;overflow:hidden;border:3px solid rgba(255,255,255,.85);
  padding:24px 32px 27px;background:linear-gradient(115deg,#7353BD 0%,#A572CE 47%,#E89EAF 100%);
  box-shadow:0 12px 27px rgba(108,70,155,.16);border-radius:28px;margin-bottom:13px;}
.study-hero:after{content:'✦   ✨   ✦';font-size:38px;letter-spacing:25px;color:rgba(255,255,255,.55);
  position:absolute;top:8px;right:-35px;transform:rotate(-12deg);pointer-events:none;}
.study-hero-kicker{color:#FFF6C9;font-size:12px;letter-spacing:2px;}
.study-hero h1 {font-size:clamp(29px,4.6vw,46px);font-weight:950;text-shadow:0 3px 0 rgba(61,37,101,.16);}
.study-hero p {color:#fff;font-weight:750;font-size:clamp(13px,2vw,17px);}
/* Easy-to-press candy-like buttons */
div.stButton>button,div.stDownloadButton>button{
  min-height:57px;border-radius:18px;border:2px solid #DCD8F0;color:#3A3D61;
  background:linear-gradient(#FFFFFF,#FBF8FF);box-shadow:0 4px 0 #E5E1F0;
  font-weight:850;transition:transform .1s ease,box-shadow .1s ease,border-color .12s;}
div.stButton>button:hover:not(:disabled),div.stDownloadButton>button:hover:not(:disabled){
  border-color:#B79BEA;color:#5B469F;background:#F5F0FF;transform:translateY(-1px);}
div.stButton>button:active:not(:disabled){transform:translateY(2px);box-shadow:0 1px 0 #D3CAEA;}
div.stButton>button[kind="primary"],div.stDownloadButton>button[kind="primary"],
div.stButton>button[data-testid="stBaseButton-primary"]{
  color:white;border-color:#8065CA;background:linear-gradient(135deg,#9071D6,#7255BF);
  box-shadow:0 4px 0 #6043A9;}
div.stButton>button[kind="primary"]:hover:not(:disabled),
div.stButton>button[data-testid="stBaseButton-primary"]:hover:not(:disabled){
  color:white;background:linear-gradient(135deg,#9F80E4,#7B5BCB);border-color:#7153BC;}
div.stButton>button:focus-visible{outline:4px solid #E5BEFF!important;outline-offset:2px;}
/* Touch-friendly top navigation, 4+3 buttons */
.st-key-kid_top_nav {background:#FFFFFFD9;border:2px solid #EAE0F7;border-radius:22px;
  padding:12px 14px 8px;margin-bottom:14px;box-shadow:0 6px 14px rgba(73,60,120,.06);}
.st-key-kid_top_nav div.stButton>button{padding:8px 3px;min-height:60px;border-radius:17px;
  font-size:clamp(12px,1.7vw,16px);line-height:1.2;white-space:normal;}
.st-key-kid_top_nav div.stButton>button p {font-size:inherit!important;font-weight:900;}
/* Page titles and game-like stats */
.kid-heading {display:flex;align-items:center;gap:14px;margin:14px 0 19px;}
.kid-heading-icon{display:flex;align-items:center;justify-content:center;font-size:31px;
  flex:0 0 63px;width:63px;height:63px;border-radius:22px;background:#FFF4DB;
  border:3px solid #FFE3AE;box-shadow:0 4px 0 #F5DBA8;}
.kid-heading h2{margin:0;font-size:clamp(23px,3.5vw,33px);font-weight:950;color:#44376B;line-height:1.25;}
.kid-heading p{margin:4px 0 0;font-size:clamp(13px,1.7vw,16px);color:#6D6885;font-weight:720;}
.kid-stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:12px 0 16px;}
.kid-stat{display:flex;align-items:center;flex-direction:column;justify-content:center;
  text-align:center;padding:16px 8px 14px;min-height:130px;border:2px solid #F2E1CF;
  border-radius:22px;background:linear-gradient(160deg,#FFFEFD,#FFF3E7);
  box-shadow:0 5px 0 #F1E4D8;}
.kid-stat:nth-child(2n){background:linear-gradient(155deg,#FFFFFF,#EFF7FF);border-color:#DFEBF5;box-shadow:0 5px 0 #E4EDF5;}
.kid-stat-icon{font-size:28px;}.kid-stat-value{font-size:clamp(19px,2.6vw,30px);font-weight:950;color:#4A4170;}
.kid-stat-label{font-size:13px;font-weight:850;color:#706887;}
.kid-notice{display:flex;align-items:center;gap:12px;padding:13px 17px;border:2px solid #F3DFC0;
  border-radius:19px;background:#FFFAEC;color:#645170;font-size:16px;font-weight:850;margin:13px 0;}
.kid-notice>span:first-child{font-size:22px;}
.kid-small-title{font-size:17px;color:#5E497C;font-weight:950;margin:17px 0 9px;}
.kid-pages{text-align:center;padding:14px;color:#695880;font-weight:850;}
.kid-mission{background:linear-gradient(125deg,#FFFAE8,#FFF2DA);border:3px solid #FCE1AF;
  border-radius:24px;padding:20px 24px;margin:17px 0 10px;}
.kid-mission-tag{font-weight:950;color:#BE793B;font-size:15px;}
.kid-mission h3{margin:3px 0 6px;font-weight:950;font-size:25px;color:#59426D;}
.kid-mission-hanja{font-family:'Noto Serif CJK KR','Batang',serif;font-size:clamp(28px,5vw,46px);
  letter-spacing:5px;font-weight:800;color:#463768;}
.kid-lesson-label{background:#EEE9FF;color:#6753A1;border-radius:20px;
  font-weight:950;font-size:15px;padding:8px 16px;text-align:center;margin:12px 0 10px;}
/* Selected tile cards and page groups */
[class*="st-key-tiles_"] div.stButton>button,[class*="st-key-units_"] div.stButton>button{
  min-height:75px;border-radius:20px;border-width:2px;
  padding:11px 7px;white-space:normal;line-height:1.4;}
[class*="st-key-tiles_"] div.stButton>button p,[class*="st-key-units_"] div.stButton>button p{
  font-size:clamp(14px,2vw,19px);font-weight:900;}
[class*="st-key-unit_groups_"] div.stButton>button{min-height:48px;border-radius:16px;padding:5px 2px;}
[class*="st-key-hanja_gallery_"] div.stButton>button{
  min-height:95px;padding:10px 4px;border-radius:18px;white-space:pre-line;}
[class*="st-key-hanja_gallery_"] div.stButton>button p{white-space:pre-line;font-size:clamp(17px,2.5vw,24px);font-weight:900;line-height:1.55;}
/* Comfortable reading cards and quiz options */
.hanja-card,.battle-char{background:linear-gradient(150deg,#FFFFFF,#FFF9EE);border:3px solid #E8D6EC;
  color:#393358;border-radius:30px;box-shadow:0 6px 0 #EDE5F5;}
.card-reading,.quiz-prompt,.battle-prompt{color:#45345C;}
.st-key-quiz_choice_area div.stButton>button {border-color:#E4D5F3!important;background:#FFFEFF!important;
  color:#3D3761!important;box-shadow:0 5px 0 #E8E2F3!important;}
.st-key-quiz_choice_area div.stButton>button[data-testid="stBaseButton-primary"]{
  background:#F2E9FF!important;color:#5F4298!important;border-color:#916CCC!important;}
.st-key-dragon_answers div.stButton>button {background:#fff;border-color:#DFD6F2!important;color:#423D65;}
.st-key-dragon_answers div.stButton>button[kind="primary"] {background:#E8DEFF;color:#4F408C;border-color:#9476D6!important;}
/* Dragon cards and special abilities */
[class*="st-key-dragon_starter_card_"],[class*="st-key-dragon_select_card_"]{
  border:3px solid #E4D8F0;border-radius:24px;background:linear-gradient(#FFFFFF,#FFF8F0);
  box-shadow:0 6px 0 #EAE0F0;}
.st-key-dragon_feature_hero {background:linear-gradient(120deg,#FFFCF7,#F3EBFF);
  border:3px solid #E6D9FF;border-radius:27px;box-shadow:0 5px 0 #EDE7F7;}
.st-key-dragon_battle_fighter,.st-key-dragon_battle_enemy {border:3px solid #E6D9F5;
  background:linear-gradient(145deg,#F5FCFF,#FFF9F0);}
.st-key-dragon_skill_grid div.stButton>button{border-color:#DDD0F6!important;border-radius:19px!important;
  background:linear-gradient(#FFFFFF,#F7F2FF);color:#514379;}
.st-key-dragon_skill_grid div.stButton>button[kind="primary"]{background:#EEE3FF;color:#6740A7;
  border-color:#9972D7!important;}
.skill-gallery{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;}
.skill-entry{display:flex;align-items:center;flex-direction:column;text-align:center;gap:5px;
  padding:13px 4px;min-width:0;border:2px solid #DACDEF;border-radius:16px;background:#FFFCFF;}
.skill-entry>span{font-size:30px;}.skill-entry strong{font-size:14px;color:#50406F;}
.skill-entry small{font-size:11px;color:#786989;}.skill-entry.locked{background:#F1EFF3;opacity:.67;}
/* Record book replaces visible spreadsheet with collectible cards */
.record-gallery{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin:10px 0;}
.record-item{border-radius:17px;padding:10px 3px 8px;text-align:center;border:2px solid #E7D9E4;
  min-width:0;background:#FFFAF5;}
.record-item.learned{background:#FFF9E4;border-color:#F5D89B;}
.record-item.master{background:#E9FBEF;border-color:#B4E8BE;}
.record-item.locked{background:#F3F1F6;border-color:#E7E3EC;opacity:.7;}
.record-char{font-family:'Noto Serif CJK KR','Batang',serif;font-size:clamp(27px,4vw,38px);
  font-weight:800;color:#40385E;}.record-reading{font-size:12px;font-weight:750;color:#736A85;white-space:nowrap;}
.record-status{font-size:17px;}.review-characters{display:flex;gap:7px;flex-wrap:wrap;margin:13px 0;}
.review-characters span{background:#FFFFFF;border:2px solid #E7D9F7;padding:9px 15px;border-radius:15px;
  font-size:25px;font-weight:800;color:#4B3B70;}
/* Parent tools remain functional but not visually central */
[data-testid="stExpander"]{border-radius:18px;border-color:#E8DEEE;}
[data-testid="stFileUploader"]{border-radius:18px;}
.st-key-stroke_unit_buttons div.stButton>button {background:#FFFDF9;border:3px solid #E0D4F3;border-radius:18px;color:#4C3A6C;}
.st-key-stroke_unit_buttons div.stButton>button[kind="primary"] {background:#9A7ADA;color:white;border-color:#8464BE;}
.selected-hanja-banner {background:#FFFCF6;border:3px solid #E6D5F6;box-shadow:0 5px 0 #EFE8F8;}
/* Streamlit native controls still used for file upload/search are rounded */
[data-testid="stTextInput"] input{background:white;border-radius:15px;border:2px solid #DED5EC;min-height:53px;}
/* Small screens: intentionally roomy 4+3 nav and 2-column stats */
@media(max-width:700px){
  .block-container{padding:0.7rem 0.8rem 2.5rem;}
  .study-hero{padding:19px 18px;border-radius:21px;margin-bottom:10px;}
  .study-hero:after{display:none;}
  .st-key-kid_top_nav{padding:8px 7px 6px;}
  .st-key-kid_top_nav div.stButton>button{font-size:12px;min-height:57px;padding:8px 1px;border-radius:12px;}
  .kid-heading{gap:11px;}.kid-heading-icon{flex-basis:49px;width:49px;height:49px;font-size:25px;border-radius:17px;}
  .kid-stats{grid-template-columns:repeat(2,minmax(0,1fr));gap:9px;}
  .kid-stat{min-height:110px;}.kid-mission{padding:14px 15px;}
  [class*="st-key-tiles_"] div.stButton>button,[class*="st-key-units_"] div.stButton>button{
    min-height:70px;padding:8px 3px;}
  [class*="st-key-tiles_"] div.stButton>button p,[class*="st-key-units_"] div.stButton>button p{
    font-size:14px;}
  .record-gallery{gap:5px;}.record-item{padding:8px 0;}
  .record-reading{font-size:10px;letter-spacing:-.05em;}
  .skill-gallery{grid-template-columns:repeat(2,minmax(0,1fr));}
  .kid-notice{font-size:14px;}
}
@media (prefers-reduced-motion:reduce){div.stButton>button,.dragon-attack-result{animation:none!important;transition:none!important;}}
</style>
""",unsafe_allow_html=True)


st.markdown("""
<section class="study-hero" aria-label="한자 탐험대 소개">
  <div class="study-hero-kicker">✦ HANJA DRAGON ADVENTURE ✦</div>
  <h1>🐉 한자 탐험대</h1>
  <p>한자를 배우면 드래곤이 성장해요! · 하루 5자씩 떠나는 판타지 모험</p>
</section>
""",unsafe_allow_html=True)
NAV_ITEMS=[('홈','🏠 홈'),('한자 학습','📚 배우기'),('획순 쓰기','✍️ 쓰기'),
           ('퀴즈','🎯 퀴즈'),('복습','🧠 복습'),('드래곤 게임','🐉 드래곤'),('학습 기록','🏆 기록')]
if st.session_state.get('main_nav') not in {item[0] for item in NAV_ITEMS}:
    st.session_state.main_nav='홈'
with st.container(key='kid_top_nav'):
    for group in (NAV_ITEMS[:4],NAV_ITEMS[4:]):
        navcols=st.columns(len(group),gap='small')
        for col,(page,title) in zip(navcols,group):
            with col:
                active=st.session_state.main_nav==page
                if st.button(title,key='menu_'+page,
                             type='primary' if active else 'secondary',
                             use_container_width=True):
                    st.session_state.main_nav=page
                    st.rerun()
menu=st.session_state.main_nav
if menu=='홈':
    page_home()
elif menu=='한자 학습':
    page_learning()
elif menu=='획순 쓰기':
    page_writing()
elif menu=='퀴즈':
    page_quiz()
elif menu=='복습':
    page_review()
elif menu=='드래곤 게임':
    page_dragons()
else:
    page_records()
st.divider()
st.caption('한자 탐험대 v1.2.2 · 개인 학습용 · 시험 공식 모의고사는 아닙니다.')
