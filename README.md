# 한자 탐험대 v1.2.3 — 드래곤 가디언즈 전투 효과 및 글자 확대

## 구성
- `streamlit_app.py` — 기존 기능을 포함하는 **전체 프로그램**
- `requirements.txt` — 기존과 동일 (`streamlit>=1.40,<2`)
- `assets/dragons/*.webp` — 기존 드래곤 9개 이미지 유지
- `assets/effects/*.webp` — 불/물/숲 전용 기술 이미지 15개 신규
- `assets/monsters/*.webp` — 일반 6, 중간 보스 2, 최종 보스 1 (총 9개) 신규
- `QA_REPORT.md` — 검사 범위 및 한계

## 드래곤 기술 개편
총 **5개 기술/드래곤**. 해금 완료 단원 수는 `0/5/10/15/20`이고, 진화 단계는 `1/2/2/3/3` 이상이어야 합니다.

| 완료 단원 | 화루 | 수루 | 그루 |
|---|---|---|---|
| 시작 | 불꽃탄 | 물방울탄 | 새싹탄 |
| 5 | 화염꼬리 | 물대포 | 덩굴채찍 |
| 10 | 불꽃회오리 | 물의파동 | 잎날베기 |
| 15 | 화염방사 | 강물베기 | 숲의뿌리 |
| 20 | 대화염 | 대해의파도 | 고대숲의힘 |

**진화 조건은 v1.2.2와 동일**: 5단원+서로 다른 배틀 승리 1개 → 2단계, 15단원+서로 다른 배틀 승리 3개 → 3단계. 학습한 단원 수와 진화 단계를 동시에 만족해야 새 기술을 사용할 수 있습니다.

## 몬스터
- 1~3단원: 보라 말랑이
- 4~6단원: 새싹 도깨비
- 7~9단원: 버섯 요정
- 10단원: 바위 골렘 **중간 보스**
- 11~12단원: 수정 박쥐
- 13~14단원: 번개 여우
- 15단원: 고대 나무 정령 **중간 보스**
- 16~17단원: 불꽃 도깨비
- 18단원: 번개 여우, 19단원: 불꽃 도깨비
- 20단원: 그림자 용왕 **최종 보스**

기본 8급 복습은 보라 말랑이, 배운 한자 복합 전투는 완료 단원 수에 따른 몬스터가 나옵니다. 현재 버전에서 보스는 **외형·이름·등장 위치를 다르게 하는 보스**이며, 문제 개수·정답 점수·HP를 더 어렵게 변경하지 않았습니다. 어린이의 학습 난이도 급상승을 막기 위해서입니다.

## 화면 크기 변경
- 배우기·쓰기에서 공유하는 `1~5`, `6~10` 범위 버튼 글자를 키움
- 개별 단원 버튼 글자 확대
- 쓰기 `한자를 하나 골라 보세요`의 5개 글자 타일/전체 한자 도감의 한자 버튼 확대
- PC·모바일 크기를 별도 설정, 작은 화면 줄바꿈에 대응

## GitHub Codespaces 설치 (기존 v1.2.2에서 업그레이드)
1. `hanja-study-v1.2.3.zip`을 Codespaces 탐색기로 업로드하세요. 이전처럼 `.devcontainer` 폴더에 들어가도 괜찮습니다.
2. **앱 실행 중인 터미널을 건드리지 말고**, 별도 새 터미널을 엽니다.
3. 현재 파일을 먼저 백업합니다.

```bash
cd /workspaces/hanja-study
cp streamlit_app.py /tmp/hanja_v1.2.2_backup.py
find /workspaces/hanja-study -name 'hanja-study-v1.2.3.zip'
```

4. 찾은 경로에 맞게 아래 둘 중 하나를 실행합니다.

```bash
# ZIP이 .devcontainer 폴더에 있을 때
unzip -o .devcontainer/hanja-study-v1.2.3.zip -d /workspaces/hanja-study

# ZIP이 hanja-study 최상위 폴더에 있을 때
unzip -o hanja-study-v1.2.3.zip -d /workspaces/hanja-study
```

5. 압축 해제 이후 확인합니다.

```bash
python -m py_compile streamlit_app.py
ls assets/effects/ | wc -l      # 15
ls assets/monsters/ | wc -l     # 9
ls assets/dragons/ | wc -l      # 9
```

6. Source Control에서 **코드와 이미지 자산만** 커밋하세요. `.zip`과 백업파일은 스테이징하지 않습니다.

```bash
git add streamlit_app.py assets/dragons assets/effects assets/monsters
git status -sb
git commit -m 'Hanja Study v1.2.3'
git push origin main
```

**이미 과거 ZIP/백업 파일이 스테이징돼 있다면 `git status`에서 확인하고 커밋하기 전에 제외해야 합니다.** 기존 학습기록을 지우거나 초기화하지 마세요. 웹앱 서버 내 세션 유지 방식은 기존과 같으므로, 기록 보존이 중요하다면 학부모 메뉴에서 JSON 파일을 내보내 두는 것이 안전합니다.
