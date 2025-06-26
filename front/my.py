import streamlit as st

def show():
    st.header("🏠 마이페이지에 오신 걸 환영합니다!")
    st.write("웹툰 속 대사를 기반으로 자연스럽게 외국어를 학습하세요.")
    #st.image("https://media.giphy.com/media/l0MYB8Ory7Hqefo9a/giphy.gif", width=400)
    st.write("내정보를 입력해주세요")
    user_input = st.text_input("📝 이름을 입력하세요:", "")
    if user_input:
        st.success(f"🎉 안녕하세요, {user_input}님!")
    st.write("마이페이지는 아직 개발 중입니다. 곧 더 많은 기능을 추가할 예정입니다.")
    st.write("추가하고 싶은 기능이 있다면 알려주세요!")
    st.write("관심목록")
    st.selectbox("관심목록", ["유미의 세포들", "김부장", "화산귀환", "스릴러"])
    st.write("최근 본 웹툰")
    st.selectbox("최근 본 웹툰", ["유미의 세포들", "김부장", "화산귀환", "스릴러"])
    st.write("나의 맞춤 정보")
    st.selectbox("나의 맞춤 정보", ["살아야 죽는 남자", "입학용병", "무협", "참교육"])