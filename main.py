import streamlit as st
from front import home, mu, my, use_home, url_insert

# 1️⃣ 필수: 맨 위에서 page 설정
st.set_page_config(page_title="COMIC STUDY 🍀", layout="wide")


# 2️⃣ 초록 귀여운 테마 CSS
st.markdown("""
    <style>
    /* 앱 전체 배경과 글꼴 */
    .stApp {
        background-color: #f0fff0;  /* 밝은 민트 배경 */
        font-family: 'Noto Sans KR', 'Comic Sans MS', sans-serif;
        color: #2f4f4f;
        animation: fadeIn 0.6s ease-in;
    }

    /* 타이틀 텍스트 */
    h1 {
        color: #228B22;  /* 진한 초록 */
        animation: bounceIn 0.6s ease-out;
        text-shadow: 1px 1px 2px #ccc;
    }

    /* 일반 텍스트 */
    .stMarkdown, .stText, .stSelectbox, .stTextInput, .stNumberInput label {
        color: #2f4f4f !important;
        font-size: 16px;
    }

    /* 버튼 스타일 */
    div.stButton > button {
        background: linear-gradient(45deg, #90ee90, #2e8b57);
        color: white;
        font-weight: bold;
        padding: 10px 20px;
        border: none;
        border-radius: 15px;
        box-shadow: 1px 2px 6px #a9a9a9;
        transition: 0.3s ease-in-out;
    }

    div.stButton > button:hover {
        background: linear-gradient(45deg, #2e8b57, #006400);
        transform: scale(1.04);
    }

    /* 선택 박스 텍스트 컬러 고정 */
    .stSelectbox > div {
        color: #2f4f4f !important;
    }

    /* 사이드바 배경과 구분선 */
    .css-1d391kg {
        background-color: #e6ffe6;
    }
    .stSidebar {
        background-color: #e6ffe6;
    }

    /* 구분선 스타일 */
    hr {
        border-top: 1px solid #b0c4b1;
    }

    /* 애니메이션 */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes bounceIn {
        0%, 20%, 40%, 60%, 80%, 100% {
            transition-timing-function: cubic-bezier(0.215, 0.610, 0.355, 1.000);
        }
        0% { transform: scale(0.3); opacity: 0; }
        20% { transform: scale(1.1); }
        40% { transform: scale(0.9); }
        60% { transform: scale(1.03); opacity: 1; }
        80% { transform: scale(0.97); }
        100% { transform: scale(1); }
    }
    </style>
""", unsafe_allow_html=True)

# 3️⃣ 상단 타이틀
st.title("🌿 Comic Study💚")

# 4️⃣ 사이드바 메뉴
with st.sidebar:
    # st.image("스크린샷 2025-06-26 오전 10.24.19.png", use_column_width=True)
    col1, col2 = st.columns(2)
    with col1:
        st.button("🏠 홈", key="home_button")
        st.button("🖼️ 액션", key="crawl_button")
    with col2:
        st.button("📚 무협", key="study_button")
        st.button("🧑‍🎓 마이", key="my_button")

    st.markdown("---")
    page = st.selectbox("🌱 페이지 선택", ["홈", "URL 입력", "무협", "마이페이지"])

# 5️⃣ 라우팅 처리
if page == "홈":
    # use_home.show("https://image-comic.pstatic.net/webtoon/769209/1/20220712144919_d6b1ac55df98a2583c89c89188cb7612_IMAG01_1.jpg", "https://www.webtoons.com/en/action/return-of-the-blossoming-blade/episode-1/viewer?title_no=2849&episode_no=1")
    use_home.select_webtoon()
elif page == "URL 입력":
    url_insert.show()
elif page == "무협":
    mu.show()
elif page == "마이페이지":
    my.show()