import streamlit as st
from front import url_insert, mu, my, use_home

def render_sidebar():
    st.image("images/loge2.png", width=120, use_container_width=True)

    st.markdown('<div class="sidebar-title"> 사용자 메뉴</div>', unsafe_allow_html=True)
    page = st.selectbox("📖 페이지 이동", ["홈", "마이페이지"])

    st.markdown("---")
    st.markdown('<div class="sidebar-title"> 사용자 설정</div>', unsafe_allow_html=True)
    theme = st.selectbox("🌈 테마 선택", ["에어블루", "애플민트", "말랑복숭아", "미스트블루", "모노샌드"])
    font_size = st.radio("🔠 폰트 크기", ["작게", "보통", "크게"], index=1)

    st.markdown("---")
    st.markdown('<div class="sidebar-title">🔐 관리자 메뉴</div>', unsafe_allow_html=True)
    admin_mode = st.checkbox("관리자 모드")
    page1 = st.selectbox("🛠️ 관리자 기능", ["URL 입력", "OCR 분석"]) if admin_mode else None

    return page, page1, theme, font_size, admin_mode

def css(page, page1, theme, font_size, admin_mode):

    # ✅ 2. 테마 정의
    font_size_css = {
        "작게": "12px",
        "보통": "16px",
        "크게": "24px"
    }[font_size]

    # 참고 샘플
    # themes = {
    #     "연초록": {"bg": "#e9fbe5", "sidebar": "#c6f6c4", "title": "#2e8b57", "font": "#2f4f4f"},
    #     "라벤더": {"bg": "#f3e5f5", "sidebar": "#e1bee7", "title": "#7b1fa2", "font": "#4a148c"},
    #     "핑크": {"bg": "#ffe4e1", "sidebar": "#ffc1cc", "title": "#ff69b4", "font": "#c2185b"},
    #     "다크": {"bg": "#1e1e1e", "sidebar": "#2e2e2e", "title": "#90ee90", "font": "#eeeeee"}
    # }

    themes = {
        "에어블루": {
            "bg": "#f2f9ff",
            "sidebar": "#d2e9f7",
            "title": "#3d8ec9",
            "font": "#2a3d4f"
        },
        "애플민트":  {
            "bg": "#f4fffa",          # 아주 연한 민트화이트
            "sidebar": "#d9f3eb",     # 은은한 세이지 민트
            "title": "#3b8f85",       # 톤다운된 청록 (채도 안정)
            "font": "#2f4e48"         # 차분한 딥세이지
        },
        "말랑복숭아": {
            "bg": "#fff7f9",         
            "sidebar": "#ffeef2",    
            "title": "#e5738a",   
            "font": "#5e4b4b"       
        },
        "미스트블루": {
            "bg": "#f6f8fa",         # 블루그레이 화이트
            "sidebar": "#dde3e9",    # 안개 낀 파란 하늘
            "title": "#6d7c8a",      # 딥 블루그레이
            "font": "#2f3a40"        # 진한 쿨그레이
        },
        "모노샌드": {
            "bg": "#fdfcf9",         # 샌드 화이트
            "sidebar": "#eae5dd",    # 뉴트럴 베이지
            "title": "#968c7f",      # 애쉬 브라운
            "font": "#403c38"        # 다크 브라운 그레이
        }
    }
    selected_theme = themes[theme] 

    # ✅ 3. CSS 테마 적용
    st.markdown(f"""
    <style>
    /* 이미지 클릭 방지 */
    img {{
        pointer-events: none;
    }}

    /* 전체 배경 */
    body {{
        background-color: {selected_theme["bg"]};
    }}

    /* 앱 전체 스타일 */
    .stApp {{
        background-color: {selected_theme["bg"]};
        font-family: 'Comic Sans MS', 'Noto Sans KR', sans-serif;
        color: {selected_theme["font"]};
        font-size: {font_size_css};
        animation: fadeIn 0.8s ease-in;
    }}

    /* 사이드바 스타일 */
    section[data-testid="stSidebar"] {{
        background-color: {selected_theme["sidebar"]};
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 2px 2px 10px #ccc;
        color: {selected_theme["font"]};
    }}

    /* 사이드바 타이틀 (사용자 메뉴, 설정 등) */
    .sidebar-title {{
        font-size: 1.1rem;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        color: {selected_theme["title"]};
    }}

    /* 제목 스타일 (크기 고정 + 자연스러운 등장) */
    h1, h2, h3 {{
        color: {selected_theme["title"]};
        animation: fadeSlideUp 0.6s ease-out;
    }}

    /* 버튼 스타일 */
    div.stButton > button {{
        background-color: {selected_theme["title"]};
        color: white !important;
        font-weight: 600;
        padding: 10px 20px;
        border: none;
        border-radius: 12px;
        cursor: pointer;
        transition: background-color 0.3s ease, color 0.3s ease;
    }}

    div.stButton > button:hover {{
        background-color: {selected_theme["title"]}CC;  /* hover 시 약간 어둡게 */
        color: white !important;
    }}

    div.stButton > button:active {{
        background-color: {selected_theme["title"]}AA;  /* active 시 더 어둡게 */
        color: white !important;
    }}

    /* 포커스 및 hover 시 붉은색 제거 + 테마색 유지 */
    button:focus, button:active, 
    input:focus, input:active, 
    textarea:focus, textarea:active, 
    select:focus, select:active {{
        outline: none !important;
        box-shadow: none !important;
        border: 1px solid {selected_theme["title"]} !important;
        background-color: inherit;
        color: inherit;
    }}

    button:hover, input:hover, select:hover, textarea:hover {{
        border: 1px solid {selected_theme["title"]} !important;
        box-shadow: none !important;
    }}

    /* 체크박스 및 라디오 버튼 포커스 효과 */
    input[type="checkbox"]:focus, input[type="radio"]:focus {{
        outline: none !important;
        box-shadow: 0 0 0 2px {selected_theme["title"]}40 !important;
        border-color: {selected_theme["title"]} !important;
    }}

    /* 셀렉트박스 및 라벨 컬러 */
    label, .stSelectbox > div {{
        color: {selected_theme["font"]} !important;
    }}

    /* 일반 텍스트 (본문 출력용) */
    .stMarkdown p, .stTextBlock, .stText, .stCaption {{
        font-size: {font_size_css} !important;
        line-height: 1.6;
    }}

    /* 입력창, 셀렉트박스 내부 텍스트 */
    input, textarea, select {{
        font-size: {font_size_css} !important;
    }}

    /* 사이드바 내부 설정 텍스트 */
    section[data-testid="stSidebar"] .stSelectbox,
    section[data-testid="stSidebar"] .stRadio,
    section[data-testid="stSidebar"] .stCheckbox,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label {{
        font-size: {font_size_css} !important;
    }}

    /* 마이페이지 라벨/입력/슬라이더/확장 등 */
    label, .css-1cpxqw2, .css-qrbaxs, .stSlider, .stSelectbox, .stTextInput, .stTextArea {{
        font-size: {font_size_css} !important;
    }}

    .css-1y4p8pa {{  /* 슬라이더 현재 값 */
        font-size: {font_size_css} !important;
    }}

    details summary {{  /* expander 제목 */
        font-size: {font_size_css} !important;
    }}

    /* 페이드인 애니메이션 */
    @keyframes fadeIn {{
        0% {{ opacity: 0; transform: translateY(20px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
    }}

    /* 자연스럽게 위에서 등장하는 효과 */
    @keyframes fadeSlideUp {{
        0% {{ opacity: 0; transform: translateY(20px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
    }}
    </style>
    """, unsafe_allow_html=True)

    # ✅ 4. 상단 타이틀
    st.title(f" Comic Study 🗯️ ")

    # ✅ 5. 페이지 라우팅 처리
    if admin_mode and page1 == "URL 입력":
        url_insert.show()
    elif admin_mode and page1 == "OCR 분석":
        from front import ocr_admin_eval
        ocr_admin_eval.show()
    else:
        if page == "홈":
            # 👉 슬로건 + 설명글 먼저 출력
            if "selected_ep_kr" not in st.session_state:
                st.markdown(f"""
                    <div class="home-header">
                        <div class="home-slogan"> 웹툰으로 배우는 스마트한 언어 학습 </div>
                        <div class="home-description">
                            AI를 활용해 자동으로 웹툰 말풍선을 인식한 뒤 자연스럽게 언어를 학습해보세요. <br>
                            지금 바로 검색창에 웹툰을 입력해보세요!
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # 👉 스타일 정의
                st.markdown(f"""
                <style>
                .home-header {{
                    text-align: left;
                    margin-top: 30px;
                    margin-bottom: 40px;
                }}
                .home-slogan {{
                    font-size: 36px;
                    font-weight: 700;
                    color: {selected_theme["title"]};
                    margin-bottom: 20px;
                }}
                .home-description {{
                    font-size: 18px;
                    color: {selected_theme["font"]};
                    line-height: 1.7;
                }}
                </style>
                """, unsafe_allow_html=True)

            # 👉 웹툰 검색 기능 실행
            use_home.select_webtoon()

        elif page == "마이페이지":
            my.show()