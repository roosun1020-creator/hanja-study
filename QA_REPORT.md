# v1.2.2 검증 기록

- Python 전체 소스 AST 파싱과 `py_compile` 통과
- v1.2.1의 최상위 함수 32개 제거 없음, 새로운 UI 헬퍼 함수 6개 추가
- 수정된 최상위 함수: `page_home`, `page_learning`, `page_quiz`, `page_review`, `page_records`, `page_dragons`, `page_writing`
- 기존 핵심 함수의 AST 일치: `load_cards`, `fresh_game`, `fresh_progress`, `register_answer`, `make_question`, `start_quiz`, `quiz_panel`, `restore_progress`, 배틀 생성·보상·진화·스킬 해금 등
- 기존 획순 HTML/JS 및 획수 판정 로직 별도 미수정
- 원본 150자 데이터 유지 (8급 50 / 7급Ⅱ 50 / 7급 50)
- `st.checkbox`, `st.radio`, `st.selectbox` 호출 0개; 학부모용 파일업로드 및 검색창 등은 유지
- 불(火→炎→焱), 물(水→江→海), 숲(木→林→森) 진화 계보 확인
- 모든 속성/단원/진화 단계의 기술 해금 제약 검사: 3 × 21 × 3 = 189조합
- 배틀 문제 400회 생성, 서로 다른 5문항/4지선다/정답 포함 확인
- 배틀 보상 중복 지급 방지, 신규 한자 20단원 학습 완료 카운트, 1·2·3단계 진화 조건 점검
- 구버전 및 v1.2.x JSON 백업 정제·복원 확인
- 드래곤 WebP 이미지 9개 ZIP 존재 확인
- Playwright의 headless Chromium으로 데스크톱/모바일 **정적 HTML 시안** 이미지가 깨지지 않고 그려지는지 확인

## 미검증 항목

현재 실행 환경에서 Streamlit 패키지 다운로드에 필요한 네트워크가 차단되어 있어 **실제 Streamlit 런타임 테스트 및 Streamlit Cloud 배포·모바일 터치 검증은 미완료**입니다. 코드의 문법, 정적 검사, 일부 핵심 로직 테스트 결과와 실제 서비스 사용성 확인을 구분해야 합니다.
