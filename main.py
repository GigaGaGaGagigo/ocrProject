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
    theme = st.selectbox("🌈 테마 선택", ["에어블루", "애플민트", "말랑복숭아", "밀크베이지"])
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
    "작게": "10px",
    "보통": "16px",
    "크게": "40px"
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
    "애플민트": {
        "bg": "#f0fff9",
        "sidebar": "#c6f5e6",
        "title": "#26a69a",
        "font": "#2e4e40"
    },
    "말랑복숭아": {
        "bg": "#fff7f9",         
        "sidebar": "#ffeef2",    
        "title": "#f6a5b5",      
        "font": "#5e4b4b"       
    },
    "밀크베이지": {
        "bg": "#fffaf2",
        "sidebar": "#f5e6d3",
        "title": "#a67c52",
        "font": "#3e2f20"
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

/* 제목 스타일 + 자연스러운 등장 */
h1, h2, h3 {{
    color: {selected_theme["title"]};
    animation: fadeSlideUp 0.6s ease-out;
}}

/* 버튼 스타일 (단색, hover 효과 없음) */
div.stButton > button {{
    background-color: {selected_theme["title"]};
    color: white;
    font-weight: 600;
    padding: 10px 20px;
    border: none;
    border-radius: 12px;
    cursor: pointer;
}}

/* 포커스 및 hover 시 붉은색 제거 + 테마색 적용 */
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

input[type="checkbox"]:focus, input[type="radio"]:focus {{
    outline: none !important;
    box-shadow: 0 0 0 2px {selected_theme["title"]}40 !important;
    border-color: {selected_theme["title"]} !important;
}}

/* 셀렉트박스 및 라벨 컬러 */
label, .stSelectbox > div {{
    color: {selected_theme["font"]} !important;
}}

/* 전체 페이드인 애니메이션 */
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
else:
    if page == "홈":
        use_home.select_webtoon()
    elif page == "마이페이지":
        my.show()