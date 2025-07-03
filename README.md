# Deepdive AI OCR Project

## Comicstudy 

웹툰 이미지를 기반으로 말풍선 텍스트를 인식하고, 한/영 텍스트 비교 및 퀴즈 학습 기능을 제공하는 Easyocr, Streamlit 기반 언어 학습 웹 서비스 입니다.


## 1. 주요 기능

- 웹툰 이미지에 있는 텍스트(말풍선 등) 인식 
- EasyOCR 기반 말풍선 텍스트 추출
- 한글/영어 컷 이미지 + 대사 비교 뷰어 제공
- 대사 편집 및 저장 기능
- 영어 대사 기반 자동 퀴즈 생성
- 관리자 모드로 웹툰 등록 등 진행 


## 2. 기술 스택

| 분야 | 기술 |
|------|------|
| 언어 | Python |
| UI | Streamlit |
| OCR | EasyOCR (Fine-tuned) |
| 데이터베이스 | MySQL (SQLAlchemy ORM 사용) |
| 기타 | Selenium, OpenCV, DBSCAN 등 |



## 3. 프로젝트 폴더 구조

<details>
<summary> 📦 폴더 구조 상세 </summary>

```
ocrProject/
├── db/                            # DB 설계 관련
│   ├── crawl_spl.py
│   └── database.py
│
├── front/                         # Streamlit 프론트엔드 관련 코드
│   ├── home.py
│   ├── my.py
│   ├── url_insert.py
│   └── use_home.py
│
├── function/                      # 핵심 기능 모듈 (OCR, 퀴즈 등)
│   ├── crawler.py
│   ├── cut_insert.py
│   ├── ocr_easy.py
│   ├── process_images_sb.py
│   ├── quiz_utils.py
│   ├── save_cut_images_from_episode.py
│   ├── webtoon_capture.py
│   ├── .EasyOCR/
│   └── finetuned/
│
├── images/                         # 예제 이미지, 로고
├── install_checker/                # OCR 설치 확인 유틸리티
├── OCR_Custom/                     # OCR 파인튜닝 관련 디렉토리
├── OCR_dev/                        # OCR 기능 개발 디렉토리
├── ProjectProposal/                # 프로젝트 기획 문서
├── sql/                            # DB 스키마, 쿼리 등
├── test/                           # 테스트 코드 디렉토리
├── main.py                         # Streamlit 메인 실행 파일
├── README.md
└── setting.txt
```
</details>


## 4. 주요 모듈 설명

| 경로 | 설명 |
|------|------|
| `main.py` | Streamlit 앱 실행 메인 |
| `front/use_home.py` | 사용자 홈 뷰어 페이지 |
| `function/ocr_easy.py` | EasyOCR 분석 및 병합 기능 |
| `function/process_images_sb.py` | 말풍선 단위 클러스터링 |
| `function/quiz_utils.py` | 퀴즈 문제 생성 |


