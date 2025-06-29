import streamlit as st

# --- Sample Data ---
webtoon_title = "화산귀환"
episode = 3
kor_sentence = "눈에 보이는 모든 것이 붉다."
correct_eng = "Everything is red."
user_choice = "I'll leave right now."

# 유사 문장 리스트 (한/영 쌍)
similar_sentences = [
    {"kor": "하늘이 온통 붉게 물들었다.", "eng": "The sky is crimson."},
    {"kor": "모든 게 붉게 보인다.", "eng": "It all looks red."},
    {"kor": "시야가 전부 빨갛게 물들었다.", "eng": "My vision is red."},
    {"kor": "붉은 색이 세상을 뒤덮었다.", "eng": "Red covers everything."}
]

# --- UI ---
st.title("📘 마이 페이지 - 학습 기록")

st.subheader(f"🔹 웹툰: {webtoon_title} (에피소드 {episode})")
st.write("### 🗨️ 원문 (한국어)")
st.markdown(f"> **{kor_sentence}**")

st.write("### ✅ 정답 (영어 번역)")
st.markdown(f"> **{correct_eng}**")

st.write("### ❌ 당신의 선택")
st.markdown(f"👉 _{user_choice}_")

st.write("### 💡 유사 추천 문장 (한/영)")
for i, sentence in enumerate(similar_sentences, 1):
    st.markdown(f"**{i}.** {sentence['kor']}  \n&nbsp;&nbsp;&nbsp;&nbsp;→ *{sentence['eng']}*")

st.info("※ 추천 문장은 문장 임베딩 기반 시맨틱 검색으로 제공됩니다.")