import random
import streamlit as st
from db.database import SessionLocal
from db.crawl_sql import Dialogue, Episode, CutImage, WrongNote
from sqlalchemy import and_, func
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv(dotenv_path="db_password.env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)  # 본인 Gemini API 키

def extract_text_from_image_with_gemini(img_path):
    try:
        with open(img_path, "rb") as f:
            img_bytes = f.read()
        prompt = "이 만화/웹툰 컷의 말풍선 대사만 가능한 한 정확하게 추출해서 보여줘. 효과음, 배경글자는 제외."
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": img_bytes}
        ])
        return response.text.strip()
    except Exception as e:
        return ""

def correct_ocr_with_gemini(gemini_text, ocr_text, lang="en"):
    if not ocr_text.strip() or not gemini_text.strip():
        return gemini_text.strip() or ocr_text.strip()
    if ocr_text.strip() == gemini_text.strip():
        return gemini_text.strip()
    prompt = f"""
    아래는 만화/웹툰 이미지에서 추출한 실제 대사(정답)와 OCR로 뽑은 결과입니다.
    OCR 결과가 오타, 빠진 글자, 잘못 인식된 부분이 있을 수 있습니다.
    정답을 기준으로 OCR 결과를 올바른 {('영어' if lang == 'en' else '한글')} 문장으로 교정해 주세요.
    최종적으로 교정된 {('영어' if lang == 'en' else '한글')} 문장만 출력하세요.

    정답(이미지 인식): {gemini_text}
    OCR 결과: {ocr_text}
    교정된 결과:
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        return response.text.strip().split('\n')[0].strip()
    except Exception:
        return gemini_text.strip()

def make_gemini_choices(kr_text, en_text):
    prompt = f"""
[중요] 아래 조건을 반드시 지켜서 4지선다형 보기를 만들어줘:

- 보기 4개는 모두 실제로 쓸 수 있는 자연스러운 영어 문장이어야 함
- 반드시 정답 1개와 '정답과 단어·순서 하나만 다르거나 단어만 살짝 바꾼' 헷갈리는 오답 3개를 만들어
- 오답 3개는 절대 DB에 저장된 대사, 예전에 본 문장, '정답과 완전히 똑같은 문장'을 포함하면 안 됨
- 단, 정답과 한 단어, 한 표현, 순서, 시제, 어투, 인칭 등만 아주 미묘하게 다르게 바꿔
- 뜻이 완전히 달라지거나, 엉뚱하거나, 어색한 영어는 만들지마
- 아래처럼 예시 포맷만 지켜
1. I will go home now.
2. I will go home later.
3. I will come home now.
4. I will go back now.
정답번호: 1

---
한글 대사: "{kr_text}"
정답 영어 대사: "{en_text}"

1.
"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        out = response.text

        lines = [l.strip() for l in out.split('\n') if l.strip()]
        options = []
        for l in lines:
            if l[:2] in ["1.", "2.", "3.", "4."]:
                opt = l[2:].strip()
                options.append(opt)
        ans_line = [l for l in lines if '정답번호' in l]
        answer_idx = 1
        if ans_line:
            answer_idx = int(''.join(filter(str.isdigit, ans_line[0])))
        return options, answer_idx-1, out
    except Exception:
        return None, None, ""

def shuffle_options(options, answer_idx):
    """
    보기를 항상 무작위로 섞고, 섞인 뒤의 정답 인덱스를 반환
    """
    zipped = list(zip(options, range(4)))
    random.shuffle(zipped)
    shuffled_options, orig_indices = zip(*zipped)
    new_answer_idx = orig_indices.index(answer_idx)
    return list(shuffled_options), new_answer_idx

def quiz_page(ep_kr: Episode, ep_en: Episode, max_questions=5):
    st.header("🔠 영어 대사 퀴즈 (AI 오답 자동 생성)")

    session = SessionLocal()

    en_cuts = session.query(CutImage.id).filter_by(episode_id=ep_en.id).all()
    en_cut_ids = [cut_id for (cut_id,) in en_cuts]
    en_dialogues = session.query(Dialogue).filter(Dialogue.cut_image_id.in_(en_cut_ids)).order_by(Dialogue.sequence).all()

    quiz_pairs = []
    for en_d in en_dialogues:
        if en_d.matched_dialogue_id:
            kr_d = session.query(Dialogue).filter_by(id=en_d.matched_dialogue_id).first()
            if kr_d and kr_d.dialogue_type == "대사":
                cut_img = session.query(CutImage).filter_by(id=en_d.cut_image_id).first()
                if not cut_img:
                    continue
                img_path = cut_img.image_path

                gemini_text = extract_text_from_image_with_gemini(img_path)
                ocr_text = en_d.content.strip()
                corrected_en = correct_ocr_with_gemini(gemini_text, ocr_text, lang="en")
                kr_text = kr_d.content.strip()
                if kr_text and corrected_en:
                    quiz_pairs.append((kr_text, corrected_en, kr_d.id, en_d.id))

    n_quiz = min(max_questions, len(quiz_pairs))
    if n_quiz < 1:
        st.warning("❌ 퀴즈 생성을 위한 대사 쌍이 부족합니다.")
        session.close()
        return

    need_reset = (
        "quiz_indices" not in st.session_state or
        "quiz_options" not in st.session_state or
        "quiz_answer_indices" not in st.session_state or
        "quiz_raws" not in st.session_state or
        st.button("🔄 문제 새로 뽑기 (새로운 랜덤 퀴즈 세트)", key="reset_quiz") or
        len(st.session_state.get("quiz_indices", [])) != n_quiz
    )

    if need_reset:
        st.session_state["quiz_indices"] = sorted(random.sample(range(len(quiz_pairs)), n_quiz))
        st.session_state["quiz_options"] = []
        st.session_state["quiz_answer_indices"] = []
        st.session_state["quiz_raws"] = []
        for idx in st.session_state["quiz_indices"]:
            kr_text, en_text, kr_id, en_id = quiz_pairs[idx]
            options, answer_idx, gemini_raw = make_gemini_choices(kr_text, en_text)
            # fallback 처리
            if not options or len(options) != 4 or answer_idx not in range(4):
                other_choices = [e for (_, e, _, _) in quiz_pairs if e != en_text]
                wrong_choices = random.sample(other_choices, min(3, len(other_choices)))
                options = wrong_choices + [en_text]
                answer_idx = len(options) - 1  # en_text가 정답(맨 마지막)
            # ★ 반드시 보기와 정답 인덱스 섞기!
            options, answer_idx = shuffle_options(options, answer_idx)
            st.session_state["quiz_options"].append(options)
            st.session_state["quiz_answer_indices"].append(answer_idx)
            st.session_state["quiz_raws"].append(gemini_raw)
        # 정답 체크/입력 초기화
        for i in range(1, n_quiz + 1):
            st.session_state.pop(f"checked_{i}", None)
            st.session_state.pop(f"user_answer_{i}", None)

    indices = st.session_state["quiz_indices"]
    gemini_raw_list = []
    for i, idx in enumerate(indices, start=1):
        kr_text, en_text, kr_id, en_id = quiz_pairs[idx]
        options = st.session_state["quiz_options"][i-1]
        answer_idx = st.session_state["quiz_answer_indices"][i-1]
        gemini_raw = st.session_state["quiz_raws"][i-1]
        gemini_raw_list.append(f"문제 {i}:\n{gemini_raw}")

        st.markdown(f"#### 𝗤 문제 {i}")
        st.markdown(f"**한글 대사:** {kr_text}")

        user_answer = st.radio(
            "영어 번역을 고르세요:",
            options,
            key=f"q_{i}_{idx}"
        )

        if st.button(f"✅ 정답 확인 {i}", key=f"check_{i}_{idx}"):
            st.session_state[f"checked_{i}"] = True
            st.session_state[f"user_answer_{i}"] = user_answer

        if st.session_state.get(f"checked_{i}"):
            answer = st.session_state.get(f"user_answer_{i}")
            if options[answer_idx] == answer:
                st.success("🎉 정답입니다!")
            else:
                st.error(f"❌ 틀렸습니다. 정답은: {options[answer_idx]}")
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

    # Gemini 응답 전체 코드블록 출력 (expander X, 튜닝 참고)
    if len(gemini_raw_list) > 0:
        st.markdown("#### Gemini 원본 응답 (튜닝 참고)")
        st.code('\n\n'.join(gemini_raw_list), language='text')

    session.close()