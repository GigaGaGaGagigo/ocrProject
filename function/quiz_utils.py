import random
import streamlit as st
from db.database import SessionLocal
from db.crawl_sql import Dialogue, Episode, CutImage

def quiz_page(ep_kr: Episode, ep_en: Episode):
    st.header("🔠 영어 대사 퀴즈")
    session = SessionLocal()

     # 1. 영어 컷 이미지 ID 조회
    en_cuts = session.query(CutImage.id).filter_by(episode_id=ep_en.id).all()
    en_cut_ids = [cut_id for (cut_id,) in en_cuts]

    # 2. 영어 대사 조회 (sequence 정렬)
    en_dialogues = session.query(Dialogue).filter(Dialogue.cut_image_id.in_(en_cut_ids)).order_by(Dialogue.sequence).all()

    # 3. matched_dialogue_id를 통해 한국어 대사 매핑
    quiz_pairs = []
    for en_d in en_dialogues:
        if en_d.matched_dialogue_id:
            kr_d = session.query(Dialogue).filter_by(id=en_d.matched_dialogue_id).first()
            if kr_d:
                quiz_pairs.append((kr_d.content.strip(), en_d.content.strip()))

    # 최소 문제 수 확인
    if len(quiz_pairs) < 4:
        st.warning("❌ 퀴즈 생성을 위한 대사 쌍이 부족합니다.")
        session.close()
        return

    # 4. 퀴즈 문제 4~5개 랜덤 선정
    questions = random.sample(quiz_pairs, min(5, len(quiz_pairs)))

    for i, (kr_text, en_text) in enumerate(questions, start=1):
        st.markdown(f"#### 𝗤 문제 {i}")
        st.markdown(f"**한글 대사:** {kr_text}")

        # 오답 보기 3개 (정답 제외)
        other_choices = [e for (_, e) in quiz_pairs if e != en_text]
        wrong_choices = random.sample(other_choices, min(3, len(other_choices)))

        # 보기 섞기
        options = wrong_choices + [en_text]
        random.shuffle(options)

        user_answer = st.radio(
            f"영어 번역을 고르세요:",
            options,
            key=f"q_{i}"
        )

        if st.button(f"✅ 정답 확인 {i}", key=f"check_{i}"):
            if user_answer == en_text:
                st.success("🎉 정답입니다!")
            else:
                st.error(f"❌ 틀렸습니다. 정답은: {en_text}")

        st.markdown("---")

    session.close()