import streamlit as st
from front import home, crawl, mu
# 스트림릿 페이지 설정
st.set_page_config(
    initial_sidebar_state="collapsed",
    page_icon="📘",
    page_title="웹툰 OCR 학습기기",
    layout="centered")#wide, centered, narrow


#with st.sidebar:
#    st.markdown("<div style='text-align: center;'><a href='https://www.naver.com' target='_blank'>버튼</a></div>", unsafe_allow_html=True)
#    st.markdown("<div style='text-align: center;'><a href='http://localhost:8501/' target='_blank'>홈</a></div>", unsafe_allow_html=True)
#    st.markdown("<div style='text-align: center;'><a href='http://localhost:8501/' target='_blank'>크롤링</a></div>", unsafe_allow_html=True)



# 페이지 레이아웃 설정=
#st.set_page_config(layout="wide")

# 상단 버튼 (뒤로가기, 의견추가)
col1, col2, col3 = st.columns([1, 8, 1])

with col1:
    if st.button("← 뒤로가기"):
        st.write("뒤로가기 실행")

with col3:
    if st.button("의견추가"):
        st.write("의견 추가하기")

# 이미지 영역
undo_col1, img_col1, img_col2, next_col1 = st.columns(4)
with undo_col1:
    st.button("↩️ 되돌리기")
    st.markdown("""
    <style>
    .custom-button {
        background-color: #4CAF50;
        color: white;
        padding: 20px 40px;
        font-size: 20px;
        border: none;
        border-radius: 10px;
    }
    </style>

    <button class="custom-button">🔙</button>
    """, unsafe_allow_html=True)
   
st.page_link("main2.py", label="➡ 다음 페이지", icon="➡")

# 이미지 1과 이미지 2를 나란히 배치
with img_col1:
    st.image("20250519192639_3b58aab64215b9c094c0e205a404a6a7_IMAG01_2.jpg", caption="이미지1", use_column_width=True)

with img_col2:
    st.image("image/image.png", caption="이미지2", use_column_width=True)
with next_col1:
    st.button("➡️ 다음")
    st.markdown("""
    <style>
    .custom-button {
        background-color: #4CAF50;
        color: white;
        padding: 20px 40px;
        font-size: 20px;
        border: none;
        border-radius: 10px;
    }
    </style>

    <button class="custom-button">🔜</button>
    """, unsafe_allow_html=True)

# 오른쪽 다음 버튼
#right_col1, right_col2 = st.columns([10, 1])
#with right_col2:
#    if st.button("다음"):
#        st.write("다음 버튼 클릭")

# 하단 선택 영역
st.markdown("---")
st.subheader("틀린그림찾기:")
selected = st.radio("정답을 선택하세요:", ["다른게 있다", "다른게 없다", "모르겠다"])
st.write(f"선택된 옵션: {selected}")



st.title("📘 웹툰 기반 AI 언어 학습")
with st.sidebar:
    # 사이드바 헤더 이미지 추가
    st.image("image/image.png", use_column_width=True)
    #st.image("https://cdn.pixabay.com/photo/2024/02/17/15/59/plum-blossoms-8579641_1280.jpg", use_column_width=True)

    
    col1, col2 = st.columns(2) 
    with col1:
        st.button("홈", key="home_button")
        st.button("크롤링", key="crawl_button")
    with col2:
        st.button("공부", key="study_button")
        st.button("마이", key="my_button")
        
    # 메뉴 선택 버튼
    st.markdown("<h3 style='text-align: center;'>메뉴 선택</h3>", unsafe_allow_html=True)
    st.write("홈 페이지로 이동합니다.")
    #st.button("🏠 홈", key="home_button")

    st.write("크롤링 페이지로 이동합니다.")
    #st.button("\n📄 크롤링", key="crawl_button")

    st.write("공부 페이지로 이동합니다.")
    #st.button("📄 공부", key="study_button")

    st.write("마이 페이지로 이동합니다.")
   # st.button("📄 마이", key="my_button")

   
    
    # 구분선 추가
    st.markdown("---")
    
    # 도움말 섹션
    st.markdown("<h3 style='text-align: center;'>도움말</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>이 앱은 웹툰 기반 AI 언어 학습을 위한 앱입니다.</p>", unsafe_allow_html=True)
    
    # 개발자 정보
    st.markdown("<h3 style='text-align: center;'>개발자</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>개발자: 홍길동</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>이 앱은 Streamlit을 사용하여 개발되었습니다.</p>", unsafe_allow_html=True)
    
    # GitHub 링크
    st.markdown("<h3 style='text-align: center;'>GitHub</h3>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'><a href='https://www.naver.com' target='_blank'>네이버로 이동</a></div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'><a href='http://localhost:8501/' target='_blank'>홈</a></div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'><a href='http://localhost:8501/' target='_blank'>크롤링</a></div>", unsafe_allow_html=True)
    
    # 사용자 입력 추가
    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>사용자 입력</h3>", unsafe_allow_html=True)
    user_input = st.text_input("이름을 입력하세요:", "")
    if user_input:
        st.write(f"안녕하세요, {user_input}님!")

# 페이지 선택
page = st.sidebar.selectbox("📌 페이지 선택", ["홈", "크롤링", "무협"])

if page == "홈":
    home.show()
elif page == "크롤링":
    crawl.show()
elif page == "무협":
    mu.show()
st.button("홈페이지")
st.button("크롤링 페이지")
st.button("무협 페이지")

st.title("📘 웹툰 기반 AI 언어 학습")
with st.sidebar:
    
    
    st.markdown("# 📋메뉴")
    st.markdown("웹툰 기반 AI 언어 학습을 위한 앱입니다.")
    st.markdown("### 메뉴 선택")
    st.button("- 홈")
    st.button("- 크롤링")
    st.markdown("---")
    st.markdown("### 도움말")
    st.markdown("이 앱은 웹툰 기반 AI 언어 학습을 위한 앱입니다.")
    st.markdown("### 개발자")
    st.markdown("개발자: 홍길동")
    st.markdown("이 앱은 Streamlit을 사용하여 개발되었습니다.")
    st.markdown("### GitHub")
    st.link_button("버튼", "https://www.naver.com")  # 버튼을 클릭하면 네이버로 이동합니다
    st.link_button("홈", " http://localhost:8501/")
    st.link_button("크롤링", "http://localhost:8501/")





#mu사이트랑 크롤링이랑 왜 같이 나오는지? 틀잡았는데 저거 위치 조정이 안된다는점, 페이지 불러오기,