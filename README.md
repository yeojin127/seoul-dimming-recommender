# SW-경진대회 | 서울특별시 디밍 운영 제안 시스템

## 팀 정보

- 팀명: **NewLight**
- 팀원: **장여진(팀장), 박서현, 이준희, 임유진**

### 역할 분담

| 이름 | 역할 | 
|---|---|
| 장여진 | 프로젝트 아키텍처 설계, 데이터 수집, 룰 생성, 더미데이터 생성, 모델 학습 및 성능평가, 보고서 작성 |
| 박서현 | 프론트엔드 개발(지도 기반 UI 구현), 화면 구성·사용자 흐름 설계, 시연 영상 제작, 보고서 작성 |
| 이준희 | 데이터 수집, 데이터 전처리, AI 모델 시연 및 결과 평가, 보고서작성 |
| 임유진 | 아이디어 기획, 데이터 수집, 더미데이터 설계·생성, 시연 영상 제작, 보고서 작성 |


---

## 프로젝트 설명

본 프로젝트는 서울특별시를 250m 격자 단위로 분할하고, 성수동(파일럿)을 대상으로 교통량·CCTV·공원·상권/주거 밀집도 등 공공데이터 기반 도시환경 지표를 결합하여
각 격자별로 심야 시간대(01:00~04:00, 3시간 고정) 에 가로등 밝기를 얼마나 줄일지(디밍 수준) 를 추천하는 의사결정 지원 시스템입니다.

### 핵심 아이디어
- 본 시스템은 “조도를 무조건 낮추는” 방식이 아니라, 밝기를 낮춰도 되는 요인(DIM) 과 밝기를 크게 낮추면 안 되는 요인(SHIELD) 을 함께 반영합니다.
- 모든 추천 결과는 기존 조도(existing_lx) 대비 추천 조도(recommended_lx), 변화율(delta_percent) 과 함께, 추천 근거 Top3(reasons) 를 같이 제공하여 “왜 그렇게 추천했는지”를 설명 가능하게 설계했습니다.
  
### 웹 흐름
1. 사용자가 지도에서 격자(또는 구/동 범위)를 선택
2. 시스템이 해당 격자의 입력 변수(정규화 지표)를 기반으로 추천 조도를 산출
3. 지도에서 격자 색으로 감광 정도(기존 대비 변화율)를 시각화
4. 격자 클릭 시 기존 조도 / 추천 조도 / 변화율 / 유지시간(3h)/ 추천 근거 Top3(요인·방향·문장)을 카드 형태로 확인

---

## 레포 파일 구조 (Monorepo)

```text
seoul-dimming-recommender/
├─ .gitignore
├─ README.md
├─ backend/
│  ├─ app/
│  │  ├─ api.py                                 # FastAPI 서버 / 예측·추천 API 엔드포인트 / 모델 로드 & 추론 / JSON 응답
│  │  ├─ main.py                                # FastAPI 애플리케이션 진입점
│  │  ├─ requirements.txt
│  │  ├─ api/
│  │  │  ├─ routes.py
│  │  │  └─ __init__.py
│  │  ├─ core/
│  │  │  ├─ config.py
│  │  │  ├─ model_loader.py
│  │  │  ├─ predictor.py
│  │  │  └─ __init__.py
│  │  └─ data/
│  │     ├─ grid_loader.py
│  │     └─ __init__.py
│  ├─ models/
│  │  ├─ .gitkeep
│  │  ├─ elastic_reco.pkl                       # ElasticNet 기반 추천(회귀) 모델 파일
│  │  ├─ lgbm_reco.pkl                          # LightGBM 기반 추천 모델 파일
│  │  ├─ mlp_reco.pkl                           # MLP(신경망) 기반 추천 모델 파일
│  │  └─ recommend_model/
│  │     ├─ predict.py
│  │     └─ recommend_output.csv	              # 추천조도 결과
│  │
│  └─ pipeline/
│     ├─ get_seoul_brtitle_info.py              # 건축물대장(표제부) API 수집
│     ├─ get_seoul_ntl.py                       # 서울 격자 포인트별 VIIRS 야간조도(NTL)
│     ├─ make_dummy_features.py                 # 더미데이터 생성
│     ├─ make_seoul_eupmyeondong.py             # 서울 법정동(읍면동) 코드 테이블 생성/정리
│     ├─ report_savings.py                      # 디밍 적용 시 절감량 리포트 계산
│     ├─ train_models.py                        # 더미/전처리 데이터로 모델 학습
│     └─ notebooks/
│        ├─ building_seoungsu.ipynb             # 주거 건물, 상업 건물 밀집도 칼럼 구하기
│        ├─ final_data_seongsu.ipynb            # 전처리 데이터 머지 및 빠진 연산 수행
│        ├─ seongsu_preprocess.ipynb            # csv데이터(cctv, 공원, 가로등) 전처리
│        └─ traffic_seongsu.ipynb               # 최종 성수 데이터
├─ data/
│  └─ processed/
│     ├─ data_seoungsu.csv                      
│     ├─ dummy_features_9cols.csv   
│     ├─ dummy_train_ready.csv                  # 학습용 최종 전처리 더미데이터(피처·라벨 정리 완료)
│     ├─ grid_features_final_seoungsu.csv       
│     ├─ seoul_eupmyeondong_codes.csv           # 서울 읍면동(법정동) 코드 매핑 테이블
│     └─ seoul_ntl_2025_grid_points_250m.csv    # 250m 격자 포인트별 2025년 NTL(야간조도) 결과 CSV
├─ docs/
│  ├─ data_sources.txt
│  ├─ 룰 설정 정리.txt
│  └─ 멘토링보고서_NewLight.hwp
└─ frontend/
   ├─ .gitignore
   ├─ eslint.config.js
   ├─ index.html                                # SPA 진입 HTML
   ├─ package-lock.json
   ├─ package.json                              # 의존성/스크립트
   ├─ README.md
   ├─ tsconfig.app.json
   ├─ tsconfig.json
   ├─ tsconfig.node.json
   ├─ vite.config.ts                            # Vite 설정
   │
   ├─ public/
   │  ├─ logo.svg
   │  └─ reco.csv
   │
   ├─ scripts/
   │  └─ sync_reco_csv.mjs
   │
   └─ src/
      ├─ App.css                                # 전역/레이아웃 스타일
      ├─ App.tsx                                # 라우팅/인증 분기(보호 라우트)
      ├─ index.css                              # 전역/레이아웃 스타일
      ├─ main.tsx                               # React 엔트리    
      │
      ├─ assets/
      │  └─ react.svg
      │
      ├─ components/
      │  ├─ Auth/
      │  │  └─ ProtectedRoute.tsx               # 로그인 여부 체크/리다이렉트
      │  ├─ Filters/
      │  │  └─ FiltersBar.tsx
      │  ├─ Header/
      │  │  └─ LogoutButton.tsx
      │  ├─ Map/
      │  │  └─ MapView.tsx                      # Leaflet 지도 + 250m 격자 폴리곤 렌더링/클릭 처리
      │  └─ Panel/
      │     └─ GridDetailPanel.tsx              # 선택 격자 추천 결과/근거 표시
      │
      ├─ data/
      │  └─ mock/
      │     ├─ areas.mock.json                  # areas 데이터
      │     ├─ grids.mock.json                  # grids 데이터
      │     └─ reco.mock.json                   # reco 데이터
      │
      ├─ pages/
      │  ├─ LoginPage/
      │  │  ├─ LoginPage.css
      │  │  └─ LoginPage.tsx                    # 로그인 화면(Mock 인증)
      │  └─ MapPage/
      │     └─ MapPage.tsx                      # 메인 지도 페이지(상태/선택 관리)
      │
      ├─ services/
      │  └─ recoService.ts                      # 추천 데이터 조회(현재는 mock 기반)
      │
      ├─ types/
      │  └─ domain.ts                           # Area/GridCell/Recommendation 타입
      │
      └─ utils/
         ├─ auth.ts                             # localStorage 기반 mock 인증
         └─ geoUtils.ts                         # centroid→250m 폴리곤 생성, 좌표 변환, 색상 매핑
```


---

## 브랜치 전략

- `main` : 배포/최종 통합 브랜치

### 개인 작업 브랜치
- `front` : 프론트엔드
- `feat/api` : 추천 API / 프론트 응답 포맷 변환 (Backend)
- `feat/pipeline` : 데이터 수집 / 전처리 / 격자화 (Backend)
- `feat/api-reco` : 디밍 룰 설정 / 추천 로직 / AI 학습·성능평가 / API (Backend)
- `feat/dummy-data` : 더미데이터 제작 (Backend)
- `feat/ui` : UI/UX 설계 / 화면 구성 / 지도 시각화 / API 연동 (Frontend)
