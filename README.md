# 한자 탐험대 v1.2.1 — 드래곤 디자인 및 버튼 UI

기준: `hanja-study` / Streamlit Community Cloud / 정상 작동 중이던 v1.2.0.

## 변경
- 드래곤 선택: 셀렉트박스에서 3종 이미지 카드 + 선택 버튼으로 변경
- 드래곤 진화: 불(火→炎→焱), 물(水→江→海), 숲(木→林→森)별 3단계 이미지 연결
- 배틀 기술: 셀렉트박스에서 2열 큰 버튼(기술별 아이콘·선택 표시)으로 변경
- 기존 문제/정답/경험치/복습·획순/성장 조건은 유지
- 배틀 정답 시 속성별 CSS 효과 텍스트 제공. 실제 캐릭터 공격 모션은 추후 개발 대상
- 상대 몬스터는 현재 임시 아이콘(👾), 추후 오리지널 이미지로 교체 가능

## 필수 파일 구조

```
hanja-study/
  streamlit_app.py
  requirements.txt
  assets/
    dragons/
      fire_1.webp
      fire_2.webp
      fire_3.webp
      water_1.webp
      water_2.webp
      water_3.webp
      forest_1.webp
      forest_2.webp
      forest_3.webp
```

**중요:** Python 파일만 교체하면 이미지가 나타나지 않습니다. `assets/dragons` 폴더도 GitHub 저장소에 올려야 합니다. 이미지 파일이 누락되면 드래곤은 이모지로 표시됩니다.

## Codespaces 적용

1. `hanja-study` 저장소에서 현재 `streamlit_app.py`를 먼저 백업합니다.
2. ZIP을 다운로드한 후 Codespaces 파일 탐색기에 드래그해 업로드합니다.
3. Codespaces 터미널에서 저장소 루트에서 `unzip -o hanja-study-v1.2.1.zip` 명령을 실행하면 Python 파일과 이미지 폴더가 생성/교체됩니다. GitHub 웹 UI에서 ZIP을 단순 업로드하는 것만으로는 압축이 풀리지 않습니다.
4. `Ctrl+S`로 저장하고 Source Control에서 변경된 파일을 스테이징 후 `Hanja Study v1.2.1 UI`로 커밋합니다.
5. `Sync Changes`를 눌러 원격 GitHub에 반영하고 Streamlit Cloud가 업데이트되는지 확인합니다.

대체로, ZIP을 PC에서 풀어 `streamlit_app.py`와 `assets/dragons/`의 9개 WebP 파일을 직접 Codespaces 탐색기에 업로드해도 됩니다.

`requirements.txt`는 기존 `streamlit>=1.40,<2`를 유지합니다.

## 동작 주의사항

- 이미 스타터 드래곤을 선택한 학습기록은 유지되며, 선택 화면이 다시 초기화되지 않습니다.
- 배틀 진행 중에는 보유 드래곤을 전환할 수 없습니다.
- 이미지 9개의 압축 용량은 합계 약 0.64MB입니다.
- 이미지 파일은 독창적으로 제작했습니다. 외부 캐릭터 IP를 포함하지 않습니다.
- 배포 앱에서 직접 터치 사용성 테스트는 별도로 진행해야 합니다.
- 원본 v1.2.0 이후 GitHub에 직접 수정한 부분이 있다면 전체 파일 교체 전 병합하세요.
