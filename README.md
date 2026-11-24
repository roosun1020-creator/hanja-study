# 한자 탐험대 v1.2.2 — 어린이용 판타지 UI 전면 개편

## 변경 기준

정상 동작하던 v1.2.1 코드를 **기준선으로 유지**했습니다. `load_cards`, `register_answer`, `make_question`, `start_quiz`, `quiz_panel`, `restore_progress`, 배틀 문제 생성, 경험치 중복 방지, 진화, 스킬 해금 로직은 변경하지 않았습니다. 획순 애니메이션·자동 판정 관련 HTML/JavaScript도 변경하지 않았습니다.

### 화면별 변경점

- **전체 메뉴**: 7개 상단 라디오 메뉴 → 4+3 배열의 큰 모험 버튼 (현재 페이지 표시)
- **홈**: Streamlit 업무형 metric → 별·메달·연속 공부 카드, 추천 단원 직접 이동
- **한자 학습**: 라디오·드롭다운 → 급수 선택 카드, 5개 단원씩 표시하는 큰 타일
- **한자 퀴즈**: 출제범위 드롭다운 → 6개 모험 카드; 기존 큰 정답 버튼 유지
- **복습**: 복습 개수·해당 한자를 카드와 큰 액션 버튼으로 표시
- **획순 쓰기**: 방식/급수/단원 드롭다운 제거, 5개 단원 페이지·큰 한자 타일, 전체 한자와 배운 한자는 검색 + 12개씩 페이지로 선택
- **드래곤**: 기존 이미지 9개, 기술 버튼, 문제 풀이·진화 유지, 전체 파스텔 판타지 카드 스킨 통합; 배틀 범위도 카드/단원 타일로 전환
- **학습기록**: 어린이 화면은 한자 도감(50자/급수)으로 표시, 상세 데이터 표·JSON 백업 및 복원은 학부모 메뉴 안으로 이동
- **기록 초기화**: 체크박스 제거. ‘초기화 메뉴 열기’ → 별도의 ‘정말 모두 삭제’로 2단계 확인

## 버전 유지 / 주의

- 총 한자 150자 (8급 50, 7급Ⅱ 50, 7급 50) 유지
- 드래곤 진화: 화루 火→炎→焱, 수루 水→江→海, 그루 木→林→森
- 기술은 각 드래곤 8개, 단원/진화 기준 그대로
- **학습 기록은 브라우저 세션에 보관**됩니다. 앱 새로고침·재배포·서버 재시작 시 데이터가 사라질 수 있으므로 **학습기록 → 학부모용 상세기록·백업 → JSON 다운로드**를 먼저 진행하세요.
- 기존 JSON 백업은 `restore_progress` 변경 없이 복원 지원합니다.
- 획순 쓰기는 HanziWriter 중국식 획순 데이터 기반이며 한국식 획순 검증이 완료된 것은 아닙니다.
- 무료 Streamlit Cloud 실제 모바일 렌더링/터치 테스트는 아직 진행하지 않았습니다. 디자인 미리보기 PNG는 **임의의 예시 진도 수치로 그린 정적 시안**입니다.

## Codespaces 업그레이드 (추천)

현재 저장소 최상위 `/workspaces/hanja-study`에 새 ZIP을 끌어 업로드한 뒤:

```bash
pwd
# /workspaces/hanja-study 인지 확인
cp streamlit_app.py /tmp/streamlit_app_before_v1.2.2.py
unzip -o hanja-study-v1.2.2.zip
python -m py_compile streamlit_app.py
ls assets/dragons/*.webp
```

모든 이미지가 보이는지 확인하세요. 다음으로 Git의 상태를 확인합니다.

```bash
git status -sb
```

**중요:** 이전에 업로드한 `hanja-study-v1.2.1.zip`과 `streamlit_app_backup_v1.2.0.py`가 초록색 `A`로 **스테이징되어 있었을 수 있습니다.** 이 파일은 배포에 필요하지 않습니다. 스테이징되어 있다면:

```bash
git restore --staged hanja-study-v1.2.1.zip streamlit_app_backup_v1.2.0.py
```

새 ZIP과 임시 백업도 GitHub에 올릴 필요가 없습니다. 변경된 코드와 이미지만 커밋:

```bash
git add streamlit_app.py assets/dragons/
git diff --cached --name-only
# 출력에 streamlit_app.py와 assets/dragons/...만 포함됐는지 확인
git commit -m "Hanja Study v1.2.2 kids UI"
git push origin main
```

동기화 후 Streamlit Cloud 웹앱의 **홈 / 배우기 / 퀴즈 / 복습 / 쓰기 / 드래곤 / 기록** 각 화면을 확인하세요.

**이미 운영 중인 코드를 Codespaces에서 별도로 수정했다면**, 이 ZIP을 바로 덮어쓰기 전에 원본과 비교해 병합하세요.

## 포함 파일

- `streamlit_app.py`: 전체 Python 앱 코드
- `requirements.txt`: Streamlit 버전 범위 (v1.2.1과 동일)
- `assets/dragons/*.webp`: 드래곤 3종 × 진화 3단계, 총 9개
- `design-preview.html`: 실제 Streamlit과 별개인 정적 UI 시안
- `design-desktop.png`, `design-mobile.png`: 예시 데이터를 이용한 디자인 확인용 이미지
- `QA_REPORT.md`: 정적/로직 테스트 및 실행 환경 한계
