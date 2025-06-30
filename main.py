import streamlit as st
from front import url_insert, mu, my, use_home

# 페이지 설정
st.set_page_config(page_title="Comic Study", layout="wide")

# ✅ 1. 테마 및 폰트 크기 선택 UI (사이드바)
with st.sidebar:
    st.image("images/loge.png", width=90, use_container_width=True)

    st.markdown('<div class="sidebar-title">🌟 사용자 메뉴</div>', unsafe_allow_html=True)
    page = st.selectbox("📖 페이지 이동", ["홈", "마이페이지"])

    st.markdown("---")
    st.markdown('<div class="sidebar-title">🎨 사용자 설정</div>', unsafe_allow_html=True)
    theme = st.selectbox("🌈 테마 선택", ["연초록", "라벤더", "핑크", "다크"])
    font_size = st.radio("🔠 폰트 크기", ["작게", "보통", "크게"], index=1)

    st.markdown("---")
    st.markdown('<div class="sidebar-title">🔐 관리자 메뉴</div>', unsafe_allow_html=True)
    admin_mode = st.checkbox("관리자 모드")
    if admin_mode:
        page1 = st.selectbox("🛠️ 관리자 기능", ["URL 입력"])
    else:
        page1 = None

# ✅ 2. 테마 정의
font_size_css = {
    "작게": "14px",
    "보통": "16px",
    "크게": "20px"
}[font_size]

themes = {
    "연초록": {"bg": "#e9fbe5", "sidebar": "#c6f6c4", "title": "#2e8b57", "font": "#2f4f4f"},
    "라벤더": {"bg": "#f3e5f5", "sidebar": "#e1bee7", "title": "#7b1fa2", "font": "#4a148c"},
    "핑크": {"bg": "#ffe4e1", "sidebar": "#ffc1cc", "title": "#ff69b4", "font": "#c2185b"},
    "다크": {"bg": "#1e1e1e", "sidebar": "#2e2e2e", "title": "#90ee90", "font": "#eeeeee"}
}
selected_theme = themes[theme]

# ✅ 3. CSS 테마 적용
st.markdown(f"""
    <style>
    img {{
        pointer-events: none;
    }}
    body {{
        background-color: {selected_theme["bg"]};
    }}
    .stApp {{
        background-color: {selected_theme["bg"]};
        font-family: 'Comic Sans MS', 'Noto Sans KR', sans-serif;
        color: {selected_theme["font"]};
        font-size: {font_size_css};
        animation: fadeIn 1s ease-in;
    }}
    section[data-testid="stSidebar"] {{
        background-color: {selected_theme["sidebar"]};
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 2px 2px 10px #aaa;
        color: {selected_theme["font"]};
    }}
    h1, h2, h3 {{
        color: {selected_theme["title"]};
        animation: bounceIn 1s ease-out;
    }}
    div.stButton > button {{
        background: linear-gradient(45deg, #98fb98, {selected_theme["title"]});
        color: white;
        font-weight: bold;
        padding: 10px 24px;
        border: none;
        border-radius: 20px;
        box-shadow: 2px 2px 10px #90ee90;
        transition: 0.3s ease;
    }}
    div.stButton > button:hover {{
        background: linear-gradient(45deg, {selected_theme["title"]}, #006400);
        transform: scale(1.05);
    }}
    label, .stSelectbox > div {{
        color: {selected_theme["font"]} !important;
    }}
    @keyframes fadeIn {{
        0% {{ opacity: 0; transform: translateY(20px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes bounceIn {{
        0%, 20%, 40%, 60%, 80%, 100% {{
            transition-timing-function: cubic-bezier(0.215, 0.610, 0.355, 1.000);
        }}
        0% {{ transform: scale(0.3); opacity: 0; }}
        20% {{ transform: scale(1.1); }}
        40% {{ transform: scale(0.9); }}
        60% {{ transform: scale(1.03); opacity: 1; }}
        80% {{ transform: scale(0.97); }}
        100% {{ transform: scale(1); }}
    }}
    </style>
""", unsafe_allow_html=True)

# ✅ 4. 상단 타이틀
st.title(f"🌿 Comic Study - {theme} 에디션")

# ✅ 5. 페이지 라우팅 처리
if admin_mode and page1 == "URL 입력":
    url_insert.show()
else:
    if page == "홈":
        use_home.select_webtoon()
    elif page == "마이페이지":
        my.show()