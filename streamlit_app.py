"""한자 탐험대 v1.2.3.8 | 모바일 최적화 점검 및 한자 카드 맞추기."""

import json
import random
import base64
from datetime import datetime, timedelta
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="한자 탐험대 v1.2.3.8",
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
# 완료 단원 수 / 필요한 진화 단계 / 기술명 / 모티브 기술
# v1.2.3의 8개 기술을 5개로 축소: 기존 학습기록·승리 기록은 그대로 보존.
SKILL_TREE = {
    "fire": [
        (0, 1, "불꽃탄", "불꽃세례"),
        (5, 2, "화염꼬리", "불꽃엄니"),
        (10, 2, "불꽃회오리", "회오리불꽃"),
        (15, 3, "화염방사", "화염방사"),
        (20, 3, "대화염", "불대문자"),
    ],
    "water": [
        (0, 1, "물방울탄", "거품"),
        (5, 2, "물대포", "물대포"),
        (10, 2, "물의파동", "물의파동"),
        (15, 3, "강물베기", "아쿠아테일"),
        (20, 3, "대해의파도", "하이드로펌프"),
    ],
    "forest": [
        (0, 1, "새싹탄", "씨기관총"),
        (5, 2, "덩굴채찍", "덩굴채찍"),
        (10, 2, "잎날베기", "잎날가르기"),
        (15, 3, "숲의뿌리", "씨뿌리기"),
        (20, 3, "고대숲의힘", "솔라빔"),
    ],
}
SKILL_ICONS = {
    "fire": ["🔥", "🐲", "🌀", "🌋", "☄️"],
    "water": ["🫧", "💦", "🌊", "💠", "🌊"],
    "forest": ["🌱", "🌿", "🍃", "🌳", "✨"],
}

# 일반 6종 + 중간 보스 2종 + 최종 보스 1종 = 총 9종.
MONSTERS = {
    "slime": {"name":"보라 말랑이", "class":"일반", "emoji":"👾"},
    "sprout_imp": {"name":"새싹 도깨비", "class":"일반", "emoji":"🌱"},
    "mushroom": {"name":"버섯 요정", "class":"일반", "emoji":"🍄"},
    "stone_guardian": {"name":"바위 골렘", "class":"중간 보스", "emoji":"🪨"},
    "crystal_bat": {"name":"수정 박쥐", "class":"일반", "emoji":"🦇"},
    "storm_fox": {"name":"번개 여우", "class":"일반", "emoji":"⚡"},
    "ancient_ent": {"name":"고대 나무 정령", "class":"중간 보스", "emoji":"🌳"},
    "flame_wisp": {"name":"불꽃 도깨비", "class":"일반", "emoji":"🔥"},
    "shadow_dragon": {"name":"그림자 용왕", "class":"최종 보스", "emoji":"🐉"},
}


def monster_for_scope(scope, completed_units=0):
    """학습 단원에 따른 몬스터 결정. 기본 모험은 학습 진도에 대응."""
    if scope.startswith("신규 ") and scope.endswith("단원"):
        try:
            unit = int(scope.split()[1].removesuffix("단원"))
        except (ValueError, IndexError):
            unit = 1
    elif scope == "학습 완료 한자":
        unit = max(1, min(20, completed_units))
    else:
        unit = 1  # 8급 복습은 첫 번째 몬스터
    if unit == 20:
        return "shadow_dragon"
    if unit == 15:
        return "ancient_ent"
    if unit == 10:
        return "stone_guardian"
    if unit <= 3:
        return "slime"
    if unit <= 6:
        return "sprout_imp"
    if unit <= 9:
        return "mushroom"
    if unit <= 12:
        return "crystal_bat"
    if unit <= 14:
        return "storm_fox"
    if unit <= 17:
        return "flame_wisp"
    return "storm_fox" if unit == 18 else "flame_wisp"


def effect_image(dragon_key, move):
    """기술명 -> 전용 이미지. 과거 배틀 기술명을 불러와도 안전하게 대체."""
    skills = [entry[2] for entry in SKILL_TREE.get(dragon_key, [])]
    i = skills.index(move) + 1 if move in skills else 1
    path = Path(__file__).resolve().parent / "assets" / "effects" / f"{dragon_key}_{i}.webp"
    return str(path) if path.is_file() else None


def monster_image(key):
    path = Path(__file__).resolve().parent / "assets" / "monsters" / f"{key}.webp"
    return str(path) if path.is_file() else None


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
            "last_correct":False, "last_skill":"", "rewarded":False,
            "enemy":monster_for_scope(scope)}


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



# ----- v1.2.3 Kid-friendly UI primitives: no selectbox, radio or checkbox -----
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



# ----- v1.2.3.8: flip cards; recall practice never changes quiz/review scores -----
FLASHCARD_SCOPES = {
    "8급 50자": GROUPS["8급"],
    "7급Ⅰ 50자": GROUPS["7급"],
    "7급Ⅱ 50자": GROUPS["7급Ⅱ"],
    "신규 7급 100자": NEW,
    "7급 전체 150자": ALL,
}


def fresh_flashcard_deck(scope, previous_round=0):
    """Shuffle all available cards once; show every character before repeating."""
    if scope not in FLASHCARD_SCOPES:
        raise ValueError("알 수 없는 카드 범위입니다.")
    pool = FLASHCARD_SCOPES[scope]
    return {"scope": scope,
            "deck": random.sample([card["char"] for card in pool], len(pool)),
            "index": 0, "revealed": False,
            "round": previous_round + 1}


def page_flashcards():
    kid_heading("🧩", "한자 카드 맞추기", "큰 한자 카드를 터치해 뜻과 음을 확인해요!")
    options = [
        ("8급 50자", "🏅 8급 · 50자"),
        ("7급Ⅰ 50자", "🌿 7급Ⅰ · 50자"),
        ("7급Ⅱ 50자", "🌱 7급Ⅱ · 50자"),
        ("신규 7급 100자", "⭐ 신규 7급 · 100자"),
        ("7급 전체 150자", "🏰 7급 전체 · 150자"),
    ]
    # 이전 버전의 선택 값이 세션에 남아도 해당 50자 학습범위로 이어집니다.
    old_scopes = {"신규 7급 50자": "7급Ⅰ 50자",
                  "신규 7급Ⅱ 50자": "7급Ⅱ 50자"}
    previous = st.session_state.get("flashcard_scope")
    if previous in old_scopes:
        st.session_state.flashcard_scope = old_scopes[previous]
    scope = tile_picker(options, "flashcard_scope", cols=2,
                        title="어떤 한자를 맞혀 볼까요?")
    game = st.session_state.get("flashcard_deck")
    if (not isinstance(game, dict) or game.get("scope") != scope or
            not game.get("deck") or game.get("index", 0) >= len(game["deck"])):
        game = fresh_flashcard_deck(scope)
        st.session_state.flashcard_deck = game

    idx = game["index"]
    total = len(game["deck"])
    card = INDEX[game["deck"][idx]]
    revealed = game["revealed"]
    st.markdown(
        f'<div class="flashcard-meter">'
        f'<strong>⭐ {idx + 1} / {total}</strong>'
        f'<span>· {escape(card["grade"])} · {game["round"]}번째 모험</span>'
        '</div>', unsafe_allow_html=True)
    st.progress(idx / total)
    st.markdown(
        '<div class="flashcard-hint">'
        + ('✨ 정답을 확인했어요! 다음 카드를 만나 보세요.' if revealed
           else '👆 아래 한자 카드를 눌러 뜻과 음을 확인해 보세요.')
        + '</div>', unsafe_allow_html=True)
    # v1.2.3.8: 위젯 자신에게 고유 key를 주어 CSS가 실제 버튼에 적용되게 합니다.
    # 이전 버전은 바깥 container key만 대상으로 지정하여 모바일에서 무시됐습니다.
    with st.container(key="flashcard_area"):
        if st.button(label(card) if revealed else card["char"],
                     key="flashcard_face_back" if revealed else "flashcard_face_front",
                     use_container_width=True,
                     help="카드를 눌러 한자와 뜻·음을 번갈아 보기"):
            game["revealed"] = not revealed
            st.rerun()
    if revealed:
        st.markdown(
            f'<div class="flashcard-reveal">'
            f'<span>{escape(card["char"])}</span>의 뜻과 음 · '
            f'<strong>{escape(label(card))}</strong>'
            '</div>', unsafe_allow_html=True)

    left, right = st.columns([1, 2], gap="small")
    with left:
        if st.button("🔀 다시 섞기", key="flashcard_restart",
                     use_container_width=True):
            st.session_state.flashcard_deck = fresh_flashcard_deck(
                scope, previous_round=game["round"])
            st.rerun()
    with right:
        is_last = idx == total - 1
        next_label = "🎉 모두 봤어요! 새 카드 섞기" if is_last else "다음 카드 ➡️"
        if st.button(next_label, key="flashcard_next", type="primary",
                     disabled=not revealed, use_container_width=True):
            if is_last:
                st.session_state.flashcard_deck = fresh_flashcard_deck(
                    scope, previous_round=game["round"])
            else:
                game["index"] += 1
                game["revealed"] = False
            st.rerun()
    st.caption("카드는 한 번씩 무작위 순서로 나옵니다. 카드 확인은 퀴즈 점수·복습 일정에 영향을 주지 않아요.")


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




@st.cache_data(show_spinner=False, max_entries=64)
def _battle_image_data(path):
    """Battle assets are local WebP files; inline URLs work in iframe/mobile browsers."""
    if not path or not Path(path).is_file():
        return ""
    return "data:image/webp;base64," + base64.b64encode(Path(path).read_bytes()).decode("ascii")


def battle_attack_html(dragon_key, dragon_stage, enemy_id, move, is_correct, hp_after):
    """Mobile-safe, self-contained battle animation with separate enemy name/HP rows."""
    dragon = DRAGONS[dragon_key]
    enemy = MONSTERS[enemy_id]
    player_src = _battle_image_data(dragon_image(dragon_key, dragon_stage))
    enemy_src = _battle_image_data(monster_image(enemy_id))
    spell_src = _battle_image_data(effect_image(dragon_key, move)) if is_correct else ""
    player_html = (f'<img src="{player_src}" alt="{escape(dragon["name"])}"/>'
                   if player_src else f'<span class="fallback">{dragon["icon"]}🐉</span>')
    enemy_html = (f'<img src="{enemy_src}" alt="{escape(enemy["name"])}"/>'
                  if enemy_src else f'<span class="fallback">{enemy["emoji"]}</span>')
    projectile_html = (f'<img class="projectile" id="projectile" src="{spell_src}" alt="{escape(move)}"/>'
                       if spell_src else '')
    before_hp = min(100, hp_after + (25 if is_correct else 0))
    summary = (f'✨ 공격 성공! {escape(enemy["name"])}에게 25 피해!'
               if is_correct else '📖 아쉬워요! 한 번 더 연습하면 더 강해져요.')
    template = r"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<style>
*{box-sizing:border-box}
html,body{padding:0;margin:0;background:transparent;overflow:hidden;
 font-family:system-ui,-apple-system,'Malgun Gothic',sans-serif}
.scene{position:relative;width:100%;height:290px;border-radius:18px;
 background:linear-gradient(180deg,#F0F9FF,#F6F3FF 65%,#E8F7E8);
 border:2px solid #E2D5F3;overflow:hidden;isolation:isolate}
.scene:before{content:"";position:absolute;left:0;right:0;bottom:36px;height:24px;
 background:linear-gradient(#C3E7B5,#D7E8AA);border-radius:50%;opacity:.72}
.banner{position:absolute;z-index:4;left:6%;right:6%;top:7px;text-align:center;
 font-size:clamp(16px,4.3vw,21px);font-weight:950;color:#593F94;
 text-shadow:0 1px #fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.actors{position:absolute;left:8px;right:8px;top:39px;bottom:57px;z-index:2;
 display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:10px}
.unit{min-width:0;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:flex-end}
.art{flex:1;min-height:0;width:100%;display:flex;align-items:flex-end;justify-content:center}
.art img{display:block;max-width:100%;max-height:100%;width:auto;height:auto;object-fit:contain;
 filter:drop-shadow(0 5px 4px rgba(77,60,95,.16))}
.fallback{font-size:clamp(45px,15vw,75px);line-height:1}
.stats{flex:0 0 52px;width:100%;display:flex;flex-direction:column;justify-content:center;
 align-items:center;gap:2px;min-height:52px;position:relative;z-index:4}
.name{display:block;max-width:100%;line-height:19px;min-height:23px;
 padding:2px 7px;font-size:clamp(11px,3.25vw,15px);font-weight:850;color:#3C376B;
 border-radius:10px;background:#ffffffea;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.hp{font-size:12px;line-height:16px;min-height:17px;white-space:nowrap;
 color:#455B72;background:#ffffffed;border-radius:8px;padding:0 7px}
.healthbar{width:80%;height:7px;flex:0 0 7px;border-radius:99px;
 background:#EEE8E9;overflow:hidden}
.healthfill{height:100%;background:#EC776B;width:__BEFORE__%;transition:width .45s ease}
.player .hp,.player .healthbar{visibility:hidden}
.projectile{position:absolute;left:0;top:0;width:clamp(62px,28vw,115px);
 max-height:120px;height:auto;object-fit:contain;z-index:8;opacity:0;
 pointer-events:none;will-change:transform,opacity;
 filter:drop-shadow(0 0 11px rgba(255,190,73,.62))}
.trail{position:absolute;left:0;top:0;width:75px;height:35px;
 border-radius:100%;background:radial-gradient(ellipse,rgba(255,255,255,.8),rgba(133,186,250,.37) 55%,transparent 75%);
 opacity:0;pointer-events:none;z-index:7;filter:blur(5px);will-change:transform,opacity}
.impact{position:absolute;width:69px;height:69px;left:0;top:0;border:5px solid #fff5a4;
 border-radius:50%;opacity:0;pointer-events:none;z-index:9;transform:translate(-50%,-50%) scale(.3)}
.impact.visible{animation:impactPulse .58s ease-out both}
.target.damaged .art img{animation:hitShake .62s ease-in-out both}
.result{position:absolute;z-index:10;bottom:7px;left:3%;right:3%;min-height:38px;
 display:flex;align-items:center;justify-content:center;text-align:center;
 border-radius:13px;background:#FFFBF1;border:1px solid #EDDAAB;padding:6px 5px;
 color:#7A4B1D;font-size:clamp(11px,3.2vw,15px);font-weight:900;
 opacity:0;transform:translateY(7px);transition:opacity .3s ease,transform .3s ease}
.result.visible{opacity:1;transform:translateY(0)}
.scene.miss .result{background:#FFF5FB;color:#7C4B76;border-color:#EDD4E9}
.replay{position:absolute;z-index:11;top:7px;right:8px;font-size:11px;
 border:1px solid #D7C8EF;border-radius:10px;background:#FFFFFFEA;
 padding:4px 7px;color:#5A458E;cursor:pointer;display:none}
.replay.visible{display:block}
@keyframes hitShake{0%,100%{transform:translateX(0);filter:none}
 27%{transform:translateX(-8px);filter:brightness(1.5)}65%{transform:translateX(8px)}}
@keyframes impactPulse{0%{opacity:0;transform:translate(-50%,-50%) scale(.25)}
 38%{opacity:1;transform:translate(-50%,-50%) scale(1.1)}
 100%{opacity:0;transform:translate(-50%,-50%) scale(1.9)}}
@media(max-width:400px){.scene{height:266px}.actors{top:37px;bottom:54px;gap:5px}
 .stats{flex-basis:52px;min-height:52px}.name{font-size:12px}
 .projectile{width:72px;max-height:82px}.result{font-size:12px}}
</style></head><body>
<div class="scene __SCENETYPE__" id="battleScene" aria-label="드래곤 전투 공격 장면">
 <div class="banner">__MOVE__!</div>
 <div class="actors">
  <div class="unit player" id="player"><div class="art" id="playerArt">__PLAYER_HTML__</div>
    <div class="stats"><div class="name">__DRAGON_NAME__</div>
    <div class="hp">　</div><div class="healthbar"></div></div></div>
  <div class="unit target" id="target"><div class="art" id="enemyArt">__ENEMY_HTML__</div>
    <div class="stats"><div class="name" id="enemyName">__ENEMY_NAME__</div>
    <div class="hp" id="enemyHp">HP __BEFORE__/100</div>
    <div class="healthbar"><div class="healthfill" id="healthfill"></div></div></div></div>
 </div>
 <div id="trail" class="trail"></div>
 __PROJECTILE_HTML__
 <div id="impact" class="impact"></div>
 <div class="result" id="result" aria-live="polite">__SUMMARY__</div>
 <button type="button" class="replay" id="replay" aria-label="공격 움직임 다시 보기">↻ 다시 보기</button>
</div>
<script>
(function(){
  'use strict';
  const scene=document.getElementById('battleScene');
  const proj=document.getElementById('projectile');
  const trail=document.getElementById('trail');
  const impact=document.getElementById('impact');
  const target=document.getElementById('target');
  const result=document.getElementById('result');
  const replay=document.getElementById('replay');
  const hp=document.getElementById('enemyHp');
  const healthfill=document.getElementById('healthfill');
  const before=Number('__BEFORE__');
  const after=Number('__AFTER__');
  let animationId=0;
  let runId=0;
  // An explicit answer-button action starts this short battle animation.
  // Mobile reduced-motion settings previously forced the projectile to the end
  // immediately; its flight is now calculated by requestAnimationFrame instead.
  const hasHit=scene.classList.contains('hit') && !!proj;
  function place(el,x,y,scale,opacity){
    if(!el)return;
    el.style.transform='translate3d('+x.toFixed(2)+'px,'+y.toFixed(2)+'px,0) translate(-50%,-50%) scale('+scale.toFixed(3)+')';
    el.style.opacity=String(opacity);
  }
  function newRun(){
    runId++;
    const token=runId;
    cancelAnimationFrame(animationId);
    result.classList.remove('visible');
    replay.classList.remove('visible');
    target.classList.remove('damaged');
    impact.classList.remove('visible');
    healthfill.style.width=before+'%';
    hp.textContent='HP '+before+'/100';
    if(proj){proj.style.opacity='0';proj.style.transform='translate3d(-999px,0,0)';}
    if(trail)trail.style.opacity='0';
    if(!hasHit){
      window.setTimeout(()=>{
        if(token!==runId)return;
        result.classList.add('visible');replay.classList.add('visible');
      },450);
      return;
    }
    // Element positions are recomputed for the actual iframe width, not hardcoded
    // percentage offsets which can place sprites outside narrow mobile scenes.
    const rScene=scene.getBoundingClientRect();
    const rPlayer=document.getElementById('playerArt').getBoundingClientRect();
    const rEnemy=document.getElementById('enemyArt').getBoundingClientRect();
    const startX=rPlayer.left-rScene.left+rPlayer.width*.73;
    const startY=rPlayer.top-rScene.top+rPlayer.height*.54;
    const endX=rEnemy.left-rScene.left+rEnemy.width*.56;
    const endY=rEnemy.top-rScene.top+rEnemy.height*.56;
    const flight=1500;
    let initial=null;
    function frame(now){
      if(token!==runId)return;
      if(initial===null)initial=now;
      const p=Math.min(1,(now-initial)/flight);
      const ease=p*p*(3-2*p);
      const x=startX+(endX-startX)*ease;
      const y=startY+(endY-startY)*ease-13*Math.sin(Math.PI*p);
      const scale=.52+(.61*p);
      const alpha=Math.min(1,p*7,(1-p)*10);
      place(proj,x,y,scale,Math.max(0,alpha));
      place(trail,x-18,y+6,.8+(.45*p),Math.min(.75,Math.max(0,alpha)*.7));
      scene.dataset.flightProgress=p.toFixed(3);
      if(p<1){animationId=requestAnimationFrame(frame);return;}
      proj.style.opacity='0';trail.style.opacity='0';
      place(impact,endX,endY,1,0);
      // Reflow lets replay restart the impact/shake animations.
      void impact.offsetWidth;
      impact.classList.add('visible');
      target.classList.add('damaged');
      hp.textContent='HP '+after+'/100';
      healthfill.style.width=after+'%';
      window.setTimeout(()=>{
        if(token!==runId)return;
        result.classList.add('visible');replay.classList.add('visible');
      },550);
    }
    animationId=requestAnimationFrame(frame);
  }
  replay.addEventListener('click',newRun);
  const sprites=Array.from(scene.querySelectorAll('img'));
  const ready=Promise.all(sprites.map(img=>{
    if(typeof img.decode==='function')return img.decode().catch(()=>{});
    if(img.complete)return Promise.resolve();
    return new Promise(resolve=>{img.addEventListener('load',resolve,{once:true});img.addEventListener('error',resolve,{once:true});});
  }));
  let launched=false;
  function start(){if(launched)return;launched=true;requestAnimationFrame(()=>requestAnimationFrame(newRun));}
  ready.then(start);
  setTimeout(start,1800); // Handles image decoding failures in mobile webviews.
})();
</script></body></html>"""
    values = {
        '__SCENETYPE__': 'hit' if is_correct else 'miss',
        '__MOVE__': escape(move),
        '__PLAYER_HTML__': player_html,
        '__ENEMY_HTML__': enemy_html,
        '__PROJECTILE_HTML__': projectile_html,
        '__DRAGON_NAME__': escape(dragon['name']),
        '__ENEMY_NAME__': escape(enemy['name']),
        '__AFTER__': str(hp_after),
        '__BEFORE__': str(before_hp),
        '__SUMMARY__': summary,
    }
    for key, value in values.items():
        template = template.replace(key, value)
    return template


@st.dialog("⚔️ 드래곤의 공격!")
def show_battle_attack_dialog():
    """Always shows the scene at the viewport center; no scrolling back to the arena."""
    battle = st.session_state.get('dragon_battle')
    if not battle or not battle.get('answered'):
        return
    progress = st.session_state.progress
    game = progress['game']
    dragon_key = game['active']
    stage = evolution_stage(completed_unit_count(progress), len(game['won_battles']))
    enemy_id = battle.get('enemy')
    if enemy_id not in MONSTERS:
        enemy_id = monster_for_scope(battle['scope'], completed_unit_count(progress))
    hit = bool(battle.get('last_correct'))
    hp_after = max(0, 100 - 25 * battle['correct'])
    scene_html = battle_attack_html(dragon_key, stage, enemy_id,
                                    battle.get('last_skill', ''), hit, hp_after)
    components.html(scene_html, height=302, scrolling=False)
    if not hit:
        q = battle['questions'][battle['index']]
        st.caption(f"이번 정답은 '{q['answer']}'이에요. 기억하고 다시 도전해요!")
    n = len(battle['questions'])
    next_label = '배틀 결과 보기' if battle['index'] + 1 >= n else '다음 문제로 가기'
    if st.button('➡️ ' + next_label, key=f"dragon_dialog_next_{battle['serial']}_{battle['index']}",
                 type='primary', use_container_width=True):
        battle['index'] += 1
        battle['selected'] = None
        battle['answered'] = False
        st.rerun()
    if st.button('배틀 종료', key=f"dragon_dialog_quit_{battle['serial']}_{battle['index']}",
                 use_container_width=True):
        st.session_state.dragon_battle = None
        st.rerun()


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

    wins = len(game["won_battles"])
    stage = evolution_stage(units, wins)
    chosen = game["active"]
    dragon = DRAGONS[chosen]
    skills = unlocked_skills(chosen, units, stage)
    # 게임 도중에는 큰 드래곤 선택/도감/통계를 숨겨
    # 스마트폰 한 화면에 상대·기술·문제·답안이 최대한 들어오게 합니다.
    if battle is None:
        # 소유 캐릭터는 카드로 전환. 전투 중에는 변경을 막아 배틀 보상/연출 상태를 보존.
        st.markdown("### 내 드래곤 선택")
        cols = st.columns(3, gap="medium")
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

        game_stats([('📚','학습 단원',f'{units}/20'),('⚡','배운 기술',f'{len(skills)}/5'),
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
            st.caption("각 기술을 배울 때마다 새로운 전용 공격 이펙트가 열립니다.")
            with st.container(key="dragon_skill_catalog"):
                for start_idx in range(0, len(SKILL_TREE[chosen]), 2):
                    cols = st.columns(2, gap="small")
                    for i, col in zip(range(start_idx, min(start_idx+2, 5)), cols):
                        requirement, min_stage, move, _ = SKILL_TREE[chosen][i]
                        available = units >= requirement and stage >= min_stage
                        with col:
                            with st.container(key=f"dragon_catalog_{chosen}_{i}"):
                                art = effect_image(chosen, move)
                                if art:
                                    st.image(art, width=120)
                                st.markdown(f"**{'✨' if available else '🔒'} {move}**")
                                if available:
                                    st.caption('습득 완료')
                                else:
                                    st.caption(f'{requirement}단원 완료 · 진화 {min_stage}단계')
            st.caption("전체 5개 · 0/5/10/15/20단원 기준으로 해금해요.")

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
            st.session_state.dragon_battle["enemy"] = monster_for_scope(scope, units)
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
    enemy_id = battle.get("enemy")
    if enemy_id not in MONSTERS:
        enemy_id = monster_for_scope(battle["scope"], units)
        battle["enemy"] = enemy_id  # v1.2.3 진행 중이던 배틀도 안전하게 이어갑니다.
    enemy = MONSTERS[enemy_id]
    st.caption(f"문제 {index+1} / {n} · 현재 정답 {battle['correct']}개 · 상대 {enemy['name']}")
    q = battle["questions"][index]
    enemy_hp = max(0, 100 - 25 * battle["correct"])
    with st.container(key="dragon_battle_arena"):
        col1, col2 = st.columns([1, 1], gap="small")
        with col1:
            with st.container(key="dragon_battle_fighter"):
                dragon_art(chosen, stage)
                st.markdown(f'<div class="dragon-art-caption">{escape(dragon["name"])} · 내 드래곤</div>',
                            unsafe_allow_html=True)
        with col2:
            with st.container(key="dragon_battle_enemy"):
                art = monster_image(enemy_id)
                if art:
                    st.image(art, width=176)
                else:
                    st.markdown(f'<div class="dragon-enemy-icon">{enemy["emoji"]}</div>',
                                unsafe_allow_html=True)
                badge = f" · {enemy['class']}" if enemy['class'] != '일반' else ''
                st.markdown(f'<div class="dragon-art-caption">{escape(enemy["name"])}{badge} · HP {enemy_hp}/100</div>',
                            unsafe_allow_html=True)
                st.progress(enemy_hp / 100)
    # 기술은 캐릭터 바로 아래에서 고릅니다. 이미지 + 한 번 탭하는 버튼만 유지.
    if not battle["answered"]:
        skill_names = [entry[2] for entry in skills]
        if battle.get("move") not in skill_names:
            battle["move"] = skill_names[-1]
        st.markdown('<div class="dragon-skill-title">⚡ 기술 고르기</div>', unsafe_allow_html=True)
        with st.container(key="dragon_skill_grid"):
            cs = st.columns(len(skill_names), gap="small")
            for move_idx, (col, name) in enumerate(zip(cs, skill_names)):
                with col:
                    with st.container(key=f"dragon_skill_card_{move_idx}"):
                        art = effect_image(chosen, name)
                        if art:
                            st.image(art, use_container_width=True)
                        else:
                            st.markdown(f'<div class="dragon-skill-fallback">{SKILL_ICONS[chosen][move_idx]}</div>',
                                        unsafe_allow_html=True)
                        selected_move = battle["move"] == name
                        if st.button(name + (" ✓" if selected_move else ""),
                                     key=f"dragon_skill_{battle['serial']}_{index}_{move_idx}",
                                     type="primary" if selected_move else "secondary",
                                     use_container_width=True):
                            battle["move"] = name
                            st.rerun()

    st.markdown(f'<div class="battle-char">{escape(q["char"])}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="battle-prompt">{escape(q["title"])}</div>', unsafe_allow_html=True)
    if not battle["answered"]:
        st.markdown("#### 정답 선택")
        with st.container(key="dragon_answers"):
            for start_idx in (0, 2):
                cols = st.columns(2, gap="small")
                for i, col in zip(range(start_idx, start_idx + 2), cols):
                    option = q["choices"][i]
                    with col:
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
            # Native modal stays centered on mobile regardless of the button's scroll position.
            # One self-contained iframe plays the full image flight instead of relying on
            # Streamlit's version-dependent markdown wrappers or :has() CSS selectors.
            show_battle_attack_dialog()
    else:
        st.markdown(f'<div class="dragon-skill-shout">{escape(dragon["name"])}의 '
                    f'{escape(battle["last_skill"])}!</div>', unsafe_allow_html=True)
        if battle["last_correct"]:
            st.markdown(f'<div class="dragon-attack-result dragon-attack-{chosen}">'
                        f'✨ 공격 성공! {escape(enemy["name"])}에게 25 피해!'
                        '</div>', unsafe_allow_html=True)
        else:
            st.warning(f"공격이 빗나갔어요! 정답은 '{q['answer']}'입니다. 다시 도전해요.")
        if st.button("▶ 공격 장면 다시 보기", key=f"dragon_replay_{battle['serial']}_{index}",
                     use_container_width=True):
            show_battle_attack_dialog()
        if st.button("다음 문제" if index+1 < n else "배틀 결과 보기",
                     type="primary", use_container_width=True):
            battle["index"] += 1
            battle["selected"] = None
            battle["answered"] = False
            st.rerun()
    if st.button("현재 배틀 종료", type="secondary"):
        st.session_state.dragon_battle = None
        st.rerun()
    st.caption("드래곤·몬스터·기술 효과는 이 게임 전용 이미지입니다. 한국식 획순 검증은 별도 진행 중입니다.")



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


# v1.2.3 playground theme. The HanziWriter iframe and grading logic are untouched.
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
/* v1.2.3.2 — 범위 선택은 다른 메뉴 버튼 글자와 어울리게 조정. */
[class*="st-key-unit_groups_"] div.stButton > button {
  min-height:52px!important;padding:6px 2px!important;
  border-radius:16px!important;font-size:17px!important;font-weight:900!important;
}
[class*="st-key-unit_groups_"] div.stButton > button [data-testid="stMarkdownContainer"],
[class*="st-key-unit_groups_"] div.stButton > button p,
[class*="st-key-unit_groups_"] div.stButton > button span {
  font-size:inherit!important;font-weight:900!important;line-height:1.2!important;
}
/* 한자 선택은 v1.2.3.1 대비 약 75%로 축소. 개별 단원 버튼은 v1.2.2 그대로. */
.st-key-stroke_unit_buttons div.stButton > button {
  min-height:90px!important;padding:9px 3px!important;
  font-size:clamp(41px,5.25vw,53px)!important;
  font-family:"Noto Serif CJK KR","Batang",serif;
}
.st-key-stroke_unit_buttons div.stButton > button [data-testid="stMarkdownContainer"],
.st-key-stroke_unit_buttons div.stButton > button p,
.st-key-stroke_unit_buttons div.stButton > button span {
  font-size:inherit!important;line-height:1.15!important;font-weight:800!important;
}
[class*="st-key-hanja_gallery_"] div.stButton > button {min-height:91px!important;}
[class*="st-key-hanja_gallery_"] div.stButton > button p {
  font-size:clamp(20px,2.85vw,27px)!important;
  font-family:"Noto Serif CJK KR","Batang",serif;
}
/* v1.2.3.2 — compact encounter and visibly slower dragon-to-monster motion. */
.st-key-dragon_battle_arena {position:relative;isolation:isolate;overflow:visible;}
.st-key-dragon_battle_fighter,.st-key-dragon_battle_enemy,.st-key-dragon_battle_enemy_hit{
  padding:7px 9px!important;min-height:0!important;border-radius:19px!important;
}
.st-key-dragon_battle_fighter img,.st-key-dragon_battle_enemy img,
.st-key-dragon_battle_enemy_hit img{max-height:165px!important;object-fit:contain;margin:auto;display:block;}
.st-key-dragon_battle_enemy_hit img{animation:monsterHitSlow .65s ease-in-out 1.82s both;}
/* Streamlit의 markdown 래퍼를 절대 위치로 바꿔 레이아웃을 밀지 않습니다. */
.st-key-dragon_battle_arena [data-testid="stElementContainer"]:has(.dragon-projectile){
  position:absolute;inset:0;z-index:10;pointer-events:none;overflow:visible;
}
.dragon-projectile{position:absolute;top:31%;left:10%;width:clamp(60px,13vw,110px);
  pointer-events:none;z-index:10;
  animation:dragonToMonster 2.7s ease-in-out both;}
.dragon-projectile img{width:100%!important;height:auto!important;max-height:110px!important;
  filter:drop-shadow(0 5px 10px rgba(86,42,127,.28));}
@keyframes dragonToMonster{
  0%{left:11%;opacity:0;transform:translate(-50%,-30%) scale(.55) rotate(-10deg);}
  12%{opacity:1;}
  55%{left:54%;opacity:1;transform:translate(-50%,-30%) scale(.85) rotate(5deg);}
  73%{left:76%;opacity:1;transform:translate(-50%,-30%) scale(1.08) rotate(0deg);}
  83%{left:77%;opacity:1;transform:translate(-50%,-30%) scale(1.15);}
  100%{left:77%;opacity:0;transform:translate(-50%,-30%) scale(1.45);}
}
@keyframes monsterHitSlow{
  0%,100%{transform:translateX(0);filter:none;}
  25%{transform:translateX(-9px);filter:brightness(1.55);}
  55%{transform:translateX(8px);filter:saturate(1.5);}
  82%{transform:translateX(-3px);}
}
.dragon-skill-title{font-size:16px;font-weight:950;color:#624AA2;margin:8px 0 5px;}
.st-key-dragon_skill_grid{margin:0 0 6px;}
.st-key-dragon_skill_grid [data-testid="stHorizontalBlock"]{
  gap:5px!important;flex-wrap:nowrap!important;align-items:stretch!important;
}
.st-key-dragon_skill_grid [data-testid="stColumn"]{
  min-width:0!important;flex:1 1 0!important;width:0!important;max-width:100px!important;
}
[class*="st-key-dragon_skill_card_"]{border:2px solid #E3D8F2;border-radius:13px;
  background:linear-gradient(#FFFFFF,#FFF9F0);padding:4px 2px;min-width:0;text-align:center;}
[class*="st-key-dragon_skill_card_"] img{width:auto!important;max-width:100%!important;
  max-height:55px!important;object-fit:contain;margin:auto;}
[class*="st-key-dragon_skill_card_"] div.stButton>button{min-height:42px!important;
  font-size:clamp(11px,1.45vw,15px)!important;line-height:1.15!important;
  padding:5px 1px!important;border-radius:10px!important;white-space:normal!important;
  word-break:keep-all!important;overflow-wrap:anywhere!important;}
[class*="st-key-dragon_skill_card_"] div.stButton>button p{font-size:inherit!important;
  font-weight:900!important;line-height:1.15!important;}
.dragon-skill-fallback{text-align:center;font-size:29px;}
.st-key-dragon_answers div.stButton>button{min-height:60px!important;
  font-size:clamp(16px,2vw,23px)!important;padding:7px 5px!important;}
.st-key-dragon_answers div.stButton>button p{font-size:inherit!important;}
.battle-char{font-size:clamp(86px,14vw,128px)!important;
  line-height:1.12!important;margin:8px 0 3px!important;padding:3px 4px!important;}
.battle-prompt{font-size:clamp(18px,2.5vw,25px)!important;margin:5px 0 8px!important;}
.dragon-skill-shout{text-align:center;font-size:clamp(18px,2.5vw,26px);font-weight:950;
 color:#79459E;background:#FFF7E5;border-radius:14px;padding:9px 12px;margin:7px 0;}
[class*="st-key-dragon_catalog_"]{border:2px solid #E9DCF4;border-radius:18px;
 background:#FFFDF9;text-align:center;padding:9px;margin-bottom:7px;}
[class*="st-key-dragon_catalog_"] img{max-height:113px;object-fit:contain;margin:auto;}
@media(max-width:700px){
 [class*="st-key-unit_groups_"] div.stButton>button{
   font-size:16px!important;min-height:53px!important;padding:6px 2px!important;
 }
 .st-key-stroke_unit_buttons div.stButton>button{
   font-size:41px!important;min-height:88px!important;
 }
 [class*="st-key-hanja_gallery_"] div.stButton>button p{font-size:20px!important;}
 .st-key-dragon_battle_fighter img,.st-key-dragon_battle_enemy img,
 .st-key-dragon_battle_enemy_hit img{max-height:115px!important;}
 .st-key-dragon_battle_fighter,.st-key-dragon_battle_enemy,.st-key-dragon_battle_enemy_hit{
   padding:4px!important;min-height:0!important;
 }
 .st-key-dragon_battle_arena .dragon-art-caption{font-size:12px!important;}
 .st-key-dragon_skill_grid [data-testid="stHorizontalBlock"]{gap:3px!important;}
 [class*="st-key-dragon_skill_card_"]{padding:3px 1px;border-radius:10px;}
 [class*="st-key-dragon_skill_card_"] img{max-height:43px!important;}
 [class*="st-key-dragon_skill_card_"] div.stButton>button{
   min-height:46px!important;font-size:11px!important;padding:4px 0!important;
 }
 .st-key-dragon_answers div.stButton>button{min-height:54px!important;font-size:17px!important;}
 .battle-char{font-size:96px!important;padding:2px!important;}
 .battle-prompt{font-size:18px!important;}
 .dragon-projectile{width:74px;top:26%;}
}
@media(prefers-reduced-motion:reduce){
 .dragon-projectile{animation:none!important;opacity:1!important;left:76%!important;
  transform:translate(-50%,-30%) scale(1)!important;}
 .st-key-dragon_battle_enemy_hit img{animation:none!important;}
}
@media (prefers-reduced-motion:reduce){div.stButton>button,.dragon-attack-result{animation:none!important;transition:none!important;}}

/* v1.2.3.8 — consistent readable mobile labels, scoped overrides only. */
@media(max-width:700px){
 .st-key-kid_top_nav div.stButton>button{font-size:13px!important;}
 .record-reading{font-size:12px!important;white-space:normal!important;
   line-height:1.3!important;overflow-wrap:anywhere;}
 [class*="st-key-dragon_skill_card_"] div.stButton>button{font-size:12px!important;}
}
/* v1.2.3.8 — 버튼 자체 key에 적용: 컨테이너 내부 구조에 의존하지 않음. */
.flashcard-meter {display:flex;align-items:center;gap:9px;flex-wrap:wrap;
  margin:18px 0 5px;color:#644A86;font-size:16px;font-weight:750;}
.flashcard-meter strong {font-size:20px;color:#503B78;}
.flashcard-meter span {color:#7B6A97;font-size:14px;}
.flashcard-hint {text-align:center;font-size:16px;font-weight:800;
  color:#6D518E;margin:13px 0 11px;}
/* st.button(key=...)의 st-key-... 클래스는 버튼을 포함하는 요소에 붙습니다. */
.st-key-flashcard_face_front button,
.st-key-flashcard_face_back button {
  display:flex!important;align-items:center!important;justify-content:center!important;
  width:100%!important;height:clamp(380px,58dvh,560px)!important;min-height:0!important;box-sizing:border-box!important;
  padding:18px 14px!important;
  border:3px solid #D8C4F1!important;border-radius:30px!important;
  background:linear-gradient(145deg,#FFFFFF,#F4EDFF)!important;
  color:#4B3777!important;text-align:center!important;
  box-shadow:0 7px 0 #E8DCF5,0 11px 18px rgba(100,74,130,.09)!important;
  white-space:normal!important;overflow:hidden!important;
  transition:transform .12s ease,box-shadow .12s ease!important;
}
.st-key-flashcard_face_front button:active,
.st-key-flashcard_face_back button:active {
  transform:translateY(3px)!important;
  box-shadow:0 4px 0 #E8DCF5!important;
}
/* 버튼 내부 텍스트가 p·span으로 렌더링되더라도 크기를 별도 보장합니다. */
.st-key-flashcard_face_front button,
.st-key-flashcard_face_front button [data-testid="stMarkdownContainer"],
.st-key-flashcard_face_front button [data-testid="stMarkdownContainer"] p,
.st-key-flashcard_face_front button p,
.st-key-flashcard_face_front button span {
  font-family:'Noto Serif CJK KR','Noto Serif KR','Batang',serif!important;
  font-size:clamp(180px,28vw,340px)!important;
  font-weight:700!important;line-height:1.17!important;
  text-align:center!important;word-break:keep-all!important;
}
.st-key-flashcard_face_back button {
  background:linear-gradient(145deg,#FFFDF1,#F1F7FF)!important;
  border-color:#E2CF9F!important;
}
.st-key-flashcard_face_back button,
.st-key-flashcard_face_back button [data-testid="stMarkdownContainer"],
.st-key-flashcard_face_back button [data-testid="stMarkdownContainer"] p,
.st-key-flashcard_face_back button p,
.st-key-flashcard_face_back button span {
  font-size:clamp(34px,4vw,60px)!important;line-height:1.35!important;
  font-weight:850!important;white-space:normal!important;
  word-break:keep-all!important;text-align:center!important;
}
.flashcard-reveal {font-size:17px;text-align:center;margin:12px 0;
  color:#625077;font-weight:700;}
.flashcard-reveal span {font-family:'Noto Serif CJK KR','Batang',serif;
  color:#71459D;font-size:25px;font-weight:900;margin-right:3px;}
.flashcard-reveal strong {color:#453A67;}
@media(max-width:700px) {
  .st-key-flashcard_face_front button,
  .st-key-flashcard_face_back button {
    height:clamp(305px,45dvh,430px)!important;
    padding:15px 8px!important;border-radius:25px!important;
  }
  .st-key-flashcard_face_front button,
  .st-key-flashcard_face_front button [data-testid="stMarkdownContainer"],
  .st-key-flashcard_face_front button [data-testid="stMarkdownContainer"] p,
  .st-key-flashcard_face_front button p,
  .st-key-flashcard_face_front button span {
    font-size:clamp(150px,44vw,224px)!important;line-height:1.12!important;
  }
  .st-key-flashcard_face_back button,
  .st-key-flashcard_face_back button [data-testid="stMarkdownContainer"],
  .st-key-flashcard_face_back button [data-testid="stMarkdownContainer"] p,
  .st-key-flashcard_face_back button p,
  .st-key-flashcard_face_back button span {
    font-size:clamp(30px,8vw,46px)!important;line-height:1.25!important;
  }
  .flashcard-hint {font-size:14px;}
}
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
           ('퀴즈','🎯 퀴즈'),('복습','🧠 복습'),('카드 맞추기','🧩 카드'),
           ('드래곤 게임','🐉 드래곤'),('학습 기록','🏆 기록')]
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
elif menu=='카드 맞추기':
    page_flashcards()
else:
    page_records()
st.divider()
st.caption('한자 탐험대 v1.2.3.8 · 개인 학습용 · 시험 공식 모의고사는 아닙니다.')
