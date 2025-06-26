import streamlit as st
from front import home, crawl, mu, my

# 1️⃣ 필수: 맨 위에서 page 설정
st.set_page_config(page_title="COMIC STUDY 🍀", layout="wide")


# 2️⃣ 초록 귀여운 테마 CSS
st.markdown("""
    <style>
    /* 배경색 */
    body {
        background-color: #1e1e1e;

    }

    .stApp {
        background-color: #1e1e1e;
        font-family: 'Comic Sans MS', 'Noto Sans KR', sans-serif;
        color: #2f4f4f;
        animation: fadeIn 1s ease-in;
    }

    /* 타이틀 애니메이션 */
    h1 {
        animation: bounceIn 1s ease-out;
        color: #2e8b57;
    }

    /* 버튼 꾸미기 */
    div.stButton > button {
        background: linear-gradient(45deg, #98fb98, #2e8b57);
        color: white;
        font-weight: bold;
        padding: 10px 24px;
        border: none;
        border-radius: 20px;
        box-shadow: 2px 2px 10px #90ee90;
        transition: 0.3s ease;
    }

    div.stButton > button:hover {
        background: linear-gradient(45deg, #2e8b57, #006400);
        transform: scale(1.05);
    }

    /* 애니메이션 키프레임 */
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
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
    st.image("스크린샷 2025-06-26 오전 10.24.19.png", use_column_width=True)
    col1, col2 = st.columns(2)
    with col1:
        st.button("🏠 홈", key="home_button")
        st.button("🖼️ 액션", key="crawl_button")
    with col2:
        st.button("📚 무협", key="study_button")
        st.button("🧑‍🎓 마이", key="my_button")

    st.markdown("---")
    page = st.selectbox("🌱 페이지 선택", ["홈", "크롤링", "무협", "마이페이지"])

# 5️⃣ 라우팅 처리
if page == "홈":
    home.show()
elif page == "크롤링":
    crawl.show()
elif page == "무협":
    mu.show()
elif page == "마이페이지":
    my.show()

