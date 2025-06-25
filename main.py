import streamlit as st
from front import home, crawl, mu

st.set_page_config(page_title="웹툰 OCR 학습기", layout="centered")

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
    
    page = st.selectbox("📌 페이지 선택", ["크롤링", "홈", "무협"])


if page == "크롤링":
    crawl.show()
elif page == "홈":
    home.show()
elif page == "무협":
    mu.show()