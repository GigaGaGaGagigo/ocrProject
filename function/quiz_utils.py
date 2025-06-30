import random
import streamlit as st
from db.database import SessionLocal
from db.crawl_sql import Dialogue, Episode

def quiz_page(ep_kr: Episode, ep_en: Episode):
    st.header("🔠 영어 대사 퀴즈")
    session = SessionLocal()

    # 1. 대사 쌍 수집 (양쪽 다 존재하는 대사만)
    kr_dialogues = session.query(Dialogue).filter_by(cut_image_id=ep_kr.id).order_by(Dialogue.sequence).all()
    en_dialogues = session.query(Dialogue).filter_by(cut_image_id=ep_en.id).order_by(Dialogue.sequence).all()

    pairs = [(kr.content.strip(), en.content.strip()) for kr, en in zip(kr_dialogues, en_dialogues)
             if kr.content and en.content]

    if len(pairs) < 5:
        st.warning("❌ 퀴즈 생성을 위한 대사 쌍이 부족합니다.")
        return

    # 2. 퀴즈 문제 5개 랜덤 선정
    questions = random.sample(pairs, min(5, len(pairs)))

    for i, (kr_text, en_text) in enumerate(questions, start=1):
        st.markdown(f"#### 𝗤 문제 {i}")
        st.markdown(f"**한글 대사:** {kr_text}")

        # 오답 보기 3개 (정답 제외한 영어 대사 중에서 선택)
        other_choices = list(set([e for _, e in pairs if e != en_text]))
        wrong_choices = random.sample(other_choices, min(3, len(other_choices)))

        # 정답 포함 보기 섞기
        options = wrong_choices + [en_text]
        random.shuffle(options)

        # 선택지 표시
        user_answer = st.radio(
            f"영어 번역을 고르세요:",
            options,
            key=f"q_{i}"
        )

        # 정답 확인 버튼
        if st.button(f"✅ 정답 확인 {i}", key=f"check_{i}"):
            if user_answer == en_text:
                st.success("🎉 정답입니다!")
            else:
                st.error(f"❌ 틀렸습니다. 정답은: {en_text}")

        st.markdown("---")

    session.close()