import random
import streamlit as st
from db.database import SessionLocal
from db.crawl_sql import Dialogue, Episode, CutImage, WrongNote
from sqlalchemy import and_, func

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
            if kr_d and kr_d.dialogue_type == "대사":
                quiz_pairs.append((
                    kr_d.content.strip(),
                    en_d.content.strip(),
                    kr_d.id,
                    en_d.id
                ))

    # 최소 문제 수 확인
    if len(quiz_pairs) < 4:
        st.warning("❌ 퀴즈 생성을 위한 대사 쌍이 부족합니다.")
        session.close()
        return

    # 4. 퀴즈 문제와 보기 고정
    if "quiz_questions" not in st.session_state:
        st.session_state.quiz_questions = random.sample(quiz_pairs, min(5, len(quiz_pairs)))
        st.session_state.quiz_options = {}

        for i, (_, en_text, _, _) in enumerate(st.session_state.quiz_questions):
            other_choices = [e for (_, e, _, _) in quiz_pairs if e != en_text]
            wrong_choices = random.sample(other_choices, min(3, len(other_choices)))
            options = wrong_choices + [en_text]
            random.shuffle(options)
            st.session_state.quiz_options[i] = options

    questions = st.session_state.quiz_questions
    options_dict = st.session_state.quiz_options

    # 5. 퀴즈 출력
    for i, (kr_text, en_text, kr_id, en_id) in enumerate(questions, start=1):
        st.markdown(f"#### 𝗤 문제 {i}")
        st.markdown(f"**한글 대사:** {kr_text}")

        options = options_dict[i - 1]

        user_answer = st.radio(
            "영어 번역을 고르세요:",
            options,
            key=f"q_{i}"
        )

        if st.button(f"✅ 정답 확인 {i}", key=f"check_{i}"):
            st.session_state[f"checked_{i}"] = True
            st.session_state[f"user_answer_{i}"] = user_answer

        # 정답 결과 표시
        if st.session_state.get(f"checked_{i}"):
            answer = st.session_state.get(f"user_answer_{i}")
            if answer == en_text:
                st.success("🎉 정답입니다!")
            else:
                st.error(f"❌ 틀렸습니다. 정답은: {en_text}")

                # ⛳ WrongNote에 저장 또는 시간만 업데이트
                existing_note = session.query(WrongNote).filter(
                    and_(
                        WrongNote.kr_dialogue_id == kr_id,
                        WrongNote.en_dialogue_id == en_id
                    )
                ).first()

                if existing_note:
                    existing_note.wrong_at = func.now()
                else:
                    new_note = WrongNote(
                        kr_dialogue_id=kr_id,
                        en_dialogue_id=en_id
                    )
                    session.add(new_note)

                session.commit()

        st.markdown("---")

    if st.button("🔄 문제 변경"):
        for key in list(st.session_state.keys()):
            if key.startswith("q_") or key.startswith("check_") or key.startswith("quiz_") or key.startswith("user_answer_") or key.startswith("checked_"):
                del st.session_state[key]
        st.rerun()
    session.close()
