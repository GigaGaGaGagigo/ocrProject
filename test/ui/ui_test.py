import streamlit as st
import random

st.title("📝 웹툰 4지선다 영어 퀴즈")
st.write("한글과 영어 대사 파일을 업로드하면 자동으로 퀴즈를 생성합니다.")


st.text_input('한글 url을 입력하세요', placeholder ='https://comic.naver.com/webtoon/..')
st.text_input('영어 url을 입력하세요', placeholder ='https://www.webtoons.com/en/action/..')

if st.button("실행"):
    # 버튼이 클릭되었을 때 실행될 코드
    if text_input:
        st.write(f"입력된 텍스트: {text_input}")
    else:
        st.write("텍스트를 입력해주세요.")

# 여백
st.write(" ")
st.write(" ")
st.write(" ")

# 파일 업로드
kor_file = st.file_uploader("📂 한글 대사 파일 업로드", type=["txt"])
eng_file = st.file_uploader("📂 영어 대사 파일 업로드", type=["txt"])

if kor_file and eng_file:
    kor_lines = kor_file.read().decode("utf-8").splitlines()
    eng_lines = eng_file.read().decode("utf-8").splitlines()
    
    if len(kor_lines) != len(eng_lines):
        st.error("❌ 한글과 영어 대사의 줄 수가 다릅니다.")
    else:
        # 퀴즈 생성
        idx = random.randint(0, len(kor_lines) - 1)
        question = kor_lines[idx]
        correct_answer = eng_lines[idx]
        
        # 오답 추출
        wrong_answers = random.sample(
            [eng for i, eng in enumerate(eng_lines) if i != idx],
            k=3
        )

        options = wrong_answers + [correct_answer]
        random.shuffle(options)

        st.markdown(f"### ❓ Q. 다음 문장의 영어 번역은 무엇일까요?")
        st.markdown(f"**👉 \"{question}\"**")

        selected = st.radio("정답을 선택하세요:", options)

        if selected:
            if selected == correct_answer:
                st.success("🎉 정답입니다!")
            else:
                st.error(f"❌ 오답입니다. 정답은: `{correct_answer}`")

        st.markdown("---")
        if st.button("🔄 새 문제 만들기"):
            st.experimental_rerun()
