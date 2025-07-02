import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from db.database import SessionLocal
from db.crawl_sql import Webtoon, CutImage, Episode, Dialogue
from function.ocr_easy import analyze_image , analyze_image_from_url
from function.code_label import GENRE_MAP, GENRE_LABEL_TO_CODE
from function.quiz_utils import quiz_page  # 퀴즈 함수 불러오기
import time
import io
import os

# st.set_page_config(page_title="웹툰 비교 뷰어", layout="wide")
# st.title("📖 한영 웹툰 컷 비교 뷰어")

# 🧩 한글 URL에서 컷 번호 조합
def jpg_url_update(url: str, num: int) -> str:
    url = url[:-5]
    while url and url[-1] != '_':
        url = url[:-1]
    if url.endswith('_'):
        return f"{url}{num}.jpg"
    else:
        raise ValueError("유효한 base URL 형식이 아닙니다.")

# 🧩 영어 웹툰 캡처 함수 (시작 y에서 50px 아래서 자르기)
def capture_webtoon_crop(url, y_start, y_end, cute_size: int, target_height=None):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1600,6000')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(0.5)

    driver.execute_script(f"window.scrollTo(0, {y_start})")
    time.sleep(0.5)
    png = driver.get_screenshot_as_png()
    driver.quit()

    image = Image.open(io.BytesIO(png))

    adjusted_start = cute_size  # 상단 50px 잘라냄
    adjusted_end = adjusted_start + (y_end - y_start)
    cropped = image.crop((440, adjusted_start, 1600 - 470, adjusted_end))  # 좌우 잘라냄

    # 📏 높이 맞추기 (한글 컷과 동일하게)
    if target_height:
        aspect_ratio = cropped.width / cropped.height
        target_width = int(aspect_ratio * target_height)
        cropped = cropped.resize((target_width, target_height), Image.BILINEAR)

    return cropped

def select_webtoon():
    session = SessionLocal()

    # 세션 상태 기본값 설정
    if "search_keyword" not in st.session_state:
        st.session_state.search_keyword = ""
    if "selected_genre" not in st.session_state:
        st.session_state.selected_genre = "전체"
    if "selected_webtoon_id" not in st.session_state:
        st.session_state.selected_webtoon_id = None

    # ✅ 리더 모드 진입 시
    if st.session_state.get("view_mode") == "reader":
        selected_ep_kr = st.session_state["selected_ep_kr"]
        selected_ep_en = st.session_state.get("selected_ep_en")
        webtoon_read(selected_ep_kr, selected_ep_en)
        return

    # 본문 영역 상단에 검색 필터 표시
    st.subheader("🔍 웹툰 검색")
    col1, col2 = st.columns([1, 5])

    with col1:
        st.session_state.selected_genre = st.selectbox(
            "장르 선택",
            ["전체"] + list(GENRE_MAP.values()),
            index=(["전체"] + list(GENRE_MAP.values())).index(st.session_state.selected_genre)
        )

    with col2:
        st.session_state.search_keyword = st.text_input(
            "웹툰 제목 검색",
            value=st.session_state.search_keyword
        )

    # # --- 웹툰 필터링 --- (초기 버전)
    # query = session.query(Webtoon).filter(Webtoon.language == 'kr')
    # if selected_genre != "전체":
    #     genre_code = list(GENRE_MAP.keys())[list(GENRE_MAP.values()).index(selected_genre)]
    #     query = query.filter(Webtoon.genre == genre_code)
    # if search_keyword:
    #     query = query.filter(Webtoon.title.contains(search_keyword))

    # webtoon_list = query.order_by(Webtoon.title).all()

    # if search_keyword and webtoon_list:
    #     st.subheader("🇰🇷 웹툰 목록")
    #     selected_webtoon = st.selectbox("웹툰 선택", webtoon_list, format_func=lambda w: w.title)

    #     if selected_webtoon:
    #         st.markdown(f"### ✏️ 선택한 웹툰: {selected_webtoon.title}")
            
    #         ep_kr = session.query(Episode).filter_by(webtoon_id=selected_webtoon.id, lang="kr").order_by(Episode.episode_number).all()
    #         ep_en = session.query(Episode).filter_by(webtoon_id=selected_webtoon.id, lang="en").order_by(Episode.episode_number).all()

    #         kr_eps = [f"{ep.episode_number}화" for ep in ep_kr]
    #         selected_idx = st.selectbox("🇰🇷 에피소드 선택", list(range(1, len(kr_eps)+1)), format_func=lambda i: kr_eps[i-1])

    #         if selected_idx:
    #             selected_ep_kr = ep_kr[selected_idx - 1]
    #             selected_ep_en = ep_en[selected_idx - 1] if len(ep_en) >= selected_idx else None

    #             # --- 에피소드 정보는 주석 처리 ---
    #             # st.markdown("---")
    #             # st.markdown(f"### 🇰🇷 한글 에피소드 정보")
    #             # st.write(f"- 에피소드 번호: {selected_ep_kr.episode_number}")
    #             # st.write(f"- URL: {selected_ep_kr.url}")
    #             # st.write(f"- 이미지 경로: {selected_ep_kr.jpg_url}")
    #             # st.write(f"- 컷 수: {selected_ep_kr.cut_size}")

    #             # if selected_ep_en:
    #             #     st.markdown(f"### 🇺🇸 영어 에피소드 정보")
    #             #     st.write(f"- 에피소드 번호: {selected_ep_en.episode_number}")
    #             #     st.write(f"- URL: {selected_ep_en.url}")
    #             # else:
    #             #     st.warning("❌ 해당 회차의 영어 버전이 존재하지 않습니다.")

    #             # 🎯 퀴즈 expander 추가
    #             if selected_ep_en:
    #                 with st.expander("🎯 퀴즈 풀기", expanded=False):
    #                     quiz_page(selected_ep_kr, selected_ep_en)

    #                 # ▶️ 리더 모드 진입 버튼 - 퀴즈 아래에 따로 오른쪽 정렬
    #                 _, col_btn = st.columns([6, 1])
    #                 with col_btn:
    #                     if st.button("📖 이 회차 보기", key="btn_reader"):
    #                         st.session_state["view_mode"] = "reader"
    #                         st.session_state["selected_ep_kr"] = selected_ep_kr
    #                         st.session_state["selected_ep_en"] = selected_ep_en
    #                         st.rerun()
    #             else:
    #                 st.info("❌ 영어 에피소드가 없어 퀴즈를 만들 수 없습니다.")
    # elif search_keyword:
    #     st.warning("❌ 해당 검색어에 맞는 웹툰이 없습니다.")

    # 🔍 웹툰 필터링 (개선)
    query = session.query(Webtoon).filter(Webtoon.language == 'kr') 
    if st.session_state.selected_genre != "전체":
        genre_code = list(GENRE_MAP.keys())[list(GENRE_MAP.values()).index(st.session_state.selected_genre)]
        query = query.filter(Webtoon.genre == genre_code)
    if st.session_state.search_keyword:
        query = query.filter(Webtoon.title.contains(st.session_state.search_keyword))

    webtoon_list = query.order_by(Webtoon.title).all()

    if st.session_state.search_keyword and webtoon_list:
        st.subheader("🇰🇷 웹툰 목록")

        # ✅ 자동 선택을 위한 인덱스 계산
        selected_index = 0
        if st.session_state.selected_webtoon_id:
            for i, w in enumerate(webtoon_list):
                if w.id == st.session_state.selected_webtoon_id:
                    selected_index = i
                    break

        # ✅ 웹툰 선택 with 자동 선택 기능
        selected_webtoon = st.selectbox(
            "웹툰 선택",
            webtoon_list,
            index=selected_index,
            format_func=lambda w: w.title
        )

        # ✅ 선택한 웹툰 ID 기억
        st.session_state.selected_webtoon_id = selected_webtoon.id

        if selected_webtoon:
            st.markdown(f"### ✏️ 선택한 웹툰: {selected_webtoon.title}")

            # ✅ 해당 웹툰의 에피소드들 가져오기
            ep_kr = session.query(Episode).filter_by(webtoon_id=selected_webtoon.id, lang="kr").order_by(Episode.episode_number).all()
            ep_en = session.query(Episode).filter_by(webtoon_id=selected_webtoon.id, lang="en").order_by(Episode.episode_number).all()

            # ✅ 한글 에피소드 번호 리스트
            kr_eps = [f"{ep.episode_number}화" for ep in ep_kr]
            selected_idx = st.selectbox("🇰🇷 에피소드 선택", list(range(1, len(kr_eps)+1)), format_func=lambda i: kr_eps[i-1])

            if selected_idx:
                selected_ep_kr = ep_kr[selected_idx - 1]
                selected_ep_en = ep_en[selected_idx - 1] if len(ep_en) >= selected_idx else None

                # 🎯 퀴즈 보기
                if selected_ep_en:
                    with st.expander("🎯 퀴즈 풀기", expanded=False):
                        quiz_page(selected_ep_kr, selected_ep_en)

                    # ▶️ 회차 보기 버튼 (오른쪽 정렬)
                    _, col_btn = st.columns([5.7, 1.3])
                    with col_btn:
                        if st.button("📖 이 회차 보기", key="btn_reader"):
                            st.session_state["view_mode"] = "reader"
                            st.session_state["selected_ep_kr"] = selected_ep_kr
                            st.session_state["selected_ep_en"] = selected_ep_en
                            st.rerun()
                else:
                    st.info("❌ 영어 에피소드가 없어 퀴즈를 만들 수 없습니다.")

    elif st.session_state.search_keyword:
        st.warning("❌ 해당 검색어에 맞는 웹툰이 없습니다.")

    session.close()


def webtoon_read(ep_kr: Episode, ep_en: Episode):

    session = SessionLocal()

    ocr_check = 0

    # 🧩 세션 상태 초기화
    for key, default in {
        "kr_url": "",
        "en_url": "",
        "cut_index": 1,
        "kor_heights": []
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    # 웹툰 이름 및 에피소드 정보 추가 
    webtoon_title = session.query(Webtoon).get(ep_kr.webtoon_id).title
    episode_number = ep_kr.episode_number

    # 🧭 상단 바: 뒤로가기 + 제목 표시
    col_title, col_back = st.columns([6, 1])

    with col_title:
        st.subheader(f"📚 {webtoon_title} - {episode_number}화")

    with col_back:
        if st.button("🔎 웹툰검색", key="back_btn"):
            st.session_state.view_mode = None
            st.rerun()

    # ◀️ 이전 / 다음 ▶️ 버튼
    left, center, right = st.columns([1, 6, 1])

    # 🔗 URL 입력
    with center:
        if not ep_kr.jpg_url or not ep_en.url:
            st.warning("한글/영어 URL이 모두 필요합니다.")
            st.stop()

        st.session_state.kr_url = ep_kr.jpg_url
        st.session_state.en_url = ep_en.url

        idx = st.session_state.cut_index
        headers = {"User-Agent": "Mozilla/5.0"}
        st.markdown(f"### 🎬 컷 번호: {idx}")

        # 여기 코드 추가
        # 🔍 CutImage 검색 및 렌더링
        kr_cut = session.query(CutImage).filter_by(
            episode_id=ep_kr.id,
            cut_number=idx
        ).first()

        en_cut = session.query(CutImage).filter_by(
            episode_id=ep_en.id,
            cut_number=idx
        ).first()

        col_kr, col_en = st.columns(2)

        if(kr_cut and en_cut):
            with col_kr:
                try:
                    response = requests.get(kr_cut.image_path, headers=headers)
                    if response.status_code == 200:
                        kr_img = Image.open(BytesIO(response.content))
                        st.image(kr_img, use_container_width=True)

                    else:
                        st.warning("❌ 한글 컷을 불러올 수 없습니다.")
                except Exception as e:
                    st.error(f"한글 URL 오류: {e}")

            # 🇺🇸 영어 컷 (같은 높이 만큼만 잘라서 표시)
            with col_en:    
                try:

                    filename = "image/" + en_cut.image_path
                    st.image(filename)
                    
                except Exception as e:
                    st.warning(f"영어 웹툰 불러오기 실패: {e}")
                    st.rerun
        else:
            # 🇰🇷 한글 컷
            kr_img_height = None

            with col_kr:
                try:
                    kr_full_url = jpg_url_update(st.session_state.kr_url, idx)
                    response = requests.get(kr_full_url, headers=headers)
                    if response.status_code == 200:
                        kr_img = Image.open(BytesIO(response.content))
                        kr_img_height = kr_img.height
                        st.image(kr_img, use_container_width=True)

                        # 컷별 높이 기록
                        if len(st.session_state.kor_heights) < idx:
                            accumulated = sum(h[1] - h[0] for h in st.session_state.kor_heights)
                            st.session_state.kor_heights.append((accumulated, accumulated + kr_img_height))
                        
                        if(kr_cut is None):
                            # db에 저장
                            new_kr_cut = CutImage(
                                episode_id=ep_kr.id,
                                cut_number=idx,
                                image_path=kr_full_url,
                                height_px=kr_img_height
                            )
                            session.add(new_kr_cut)
                            session.commit()
                    else:
                        st.warning("❌ 한글 컷을 불러올 수 없습니다.")
                except Exception as e:
                    st.error(f"한글 URL 오류: {e}")
                    st.rerun

            # 🇺🇸 영어 컷 (같은 높이 만큼만 잘라서 표시)
            new_en_cut = None

            with col_en:
                try:
                    # 한글 이미지 높이 기록이 누락되어 있으면 계산 후 추가
                    if len(st.session_state.kor_heights) < idx:
                        accumulated = sum(h[1] - h[0] for h in st.session_state.kor_heights)
                        st.session_state.kor_heights.append((accumulated, accumulated + kr_img_height))

                    # ✅ 리스트 길이 확인 후 안전하게 접근
                    if len(st.session_state.kor_heights) >= idx:
                        y_start, y_end = st.session_state.kor_heights[idx - 1]
                        eng_crop = capture_webtoon_crop(
                            st.session_state.en_url,
                            y_start,
                            y_end,
                            ep_en.cut_size,
                            target_height=kr_img_height if kr_img_height else None
                        )

                        st.image(eng_crop, use_container_width=True)

                    # ocr실행할지 체크
                    ocr_check = 1

                    # --- 이미지 저장 ---
                    save_dir = "image"
                    os.makedirs(save_dir, exist_ok=True)
                    filename = f"{ep_en.webtoon_id}_{ep_en.episode_number}_{idx}.jpg"
                    save_path = os.path.join(save_dir, filename)

                    # 저장
                    eng_crop.save(save_path, format="JPEG", quality=90)

                    # db에 저장
                    new_en_cut = CutImage(
                        episode_id=ep_en.id,
                        cut_number=idx,
                        image_path=filename,
                        height_px=kr_img_height
                    )
                    session.add(new_en_cut)
                    session.commit()
                    
                except Exception as e:
                    st.warning(f"❌ 영어 웹툰 캡처 실패: {e} - 다시 시도 중...")
                    st.rerun()  # ✅ 함수로 호출해야 정상 동작

    ci_kr = kr_cut if kr_cut else new_kr_cut
    ci_en = en_cut if en_cut else new_en_cut

    half_height = ci_kr.height_px - 1000
    half_height = int(half_height / 2)

    with left:
        st.markdown(f"<div style='height:{half_height}px'></div>", unsafe_allow_html=True)
        if st.button("이전 컷 ◀️", use_container_width=True):
            if st.session_state.cut_index > 1:
                st.session_state.cut_index -= 1
                st.rerun()
    with right:
        st.markdown(f"<div style='height:{half_height}px'></div>", unsafe_allow_html=True)
        if st.button("다음 컷 ▶️", use_container_width=True):
            st.session_state.cut_index += 1
            st.rerun()

    if ci_kr and ci_en:
        webtoon_dialogue(ci_kr, ci_en, ocr_check)
    else:
        st.warning("❗컷 이미지 정보를 찾을 수 없어 대사 분석을 생략합니다.")
    session.close()
    

def webtoon_dialogue(ci_kr: CutImage, ci_en: CutImage, ocr_check):
    session = SessionLocal()
    st.header("💬 웹툰 대사 매칭 및 편집")

    # 기존 대사 불러오기
    kr_dialogues = session.query(Dialogue).filter_by(cut_image_id=ci_kr.id).order_by(Dialogue.sequence).all()
    en_dialogues = session.query(Dialogue).filter_by(cut_image_id=ci_en.id).order_by(Dialogue.sequence).all()
    max_len = max(len(kr_dialogues), len(en_dialogues))

    # ocr 실행
    if(len(kr_dialogues) == 0 and len(en_dialogues) == 0 and ocr_check == 1):

        try:
            #  # EasyOCR 분석 실행
            kr_easy_raw, kr_easy_merged = analyze_image_from_url(ci_kr.image_path)

            kr_dialogue_objs = []  # 이 리스트에 DB에 넣은 한국어 Dialogue 객체들을 저장할 거예요

            for i, (x, y, w, h, text, conf) in enumerate(kr_easy_merged):
                if(conf > 0.4):
                    ocr_kr_d = Dialogue(
                        cut_image_id=ci_kr.id,
                        sequence=i + 1,
                        content=text,
                        dialogue_type="대사"
                    )
                    session.add(ocr_kr_d)
                    kr_dialogue_objs.append(ocr_kr_d)

            session.flush()  # DB에 ID 자동 할당되게 하고 계속 사용 가능하게 함 (commit 전에 id 사용 가능)




            eg_img_path = "image/" + ci_en.image_path
            
            easy_raw, easy_merged  = analyze_image(eg_img_path)

            for i, (x, y, w, h, text, conf) in enumerate(easy_merged):
                if(conf > 0.6):
                    matched_kr_d = kr_dialogue_objs[i] if i < len(kr_dialogue_objs) else None

                    ocr_eg_d = Dialogue(
                        cut_image_id=ci_en.id,
                        sequence=i + 1,
                        content=text,
                        matched_dialogue_id=matched_kr_d.id if matched_kr_d else None
                    )
                    session.add(ocr_eg_d)

            session.commit()
        except Exception as e:
            print("검색된 글이 없는 경우", e)
        st.rerun()

        

    # ✅ 대사 목록 표시 (개별 삭제 및 수정 가능)
    for i in range(max_len):
        col_type, col1, col2, col3 = st.columns([1.2, 4, 4, 0.2])
        with col_type:
            current_type = kr_dialogues[i].dialogue_type if i < len(kr_dialogues) and kr_dialogues[i].dialogue_type else "대사"
            new_type = st.selectbox("", ["대사", "효과음", "배경 글씨"], index=["대사", "효과음", "배경 글씨"].index(current_type), key=f"type_{i}", label_visibility="collapsed")
            if i < len(kr_dialogues):
                kr_dialogues[i].dialogue_type = new_type

        with col1:
            if i < len(kr_dialogues):
                kr_d = kr_dialogues[i]
                kr_d.content = st.text_input(label="", value=kr_d.content, key=f"kr_{i}", label_visibility="collapsed")
            else:
                st.text_input(label="", value="대사 없음", key=f"kr_empty_{i}", disabled=True, label_visibility="collapsed")

        with col2:
            if i < len(en_dialogues):
                en_d = en_dialogues[i]
                en_d.content = st.text_input(label="", value=en_d.content, key=f"en_{i}", label_visibility="collapsed")
            else:
                st.text_input(label="", value="No dialogue", key=f"en_empty_{i}", disabled=True, label_visibility="collapsed")

        with col3:
            if st.button("🗑️", key=f"delete_{i}"):
                if i < len(kr_dialogues):
                    session.delete(kr_dialogues[i])
                if i < len(en_dialogues):
                    session.delete(en_dialogues[i])
                session.commit()
                st.rerun()

    # ✅ 대사 추가 영역 (언제든 추가 가능)
    with st.expander("### ➕ 새로운 대사 추가", expanded=False):
        col_type, col1, col2 = st.columns([1, 3, 3])
        with col_type:
            new_type = st.selectbox("글 종류", ["대사", "효과음", "배경 글씨"], key="new_type_input")
        with col1:
            new_kr = st.text_input("한국어 대사", key="new_kr_input")
        with col2:
            new_en = st.text_input("영어 대사", key="new_en_input")

        sequence = max_len + 1

        __, add_btn_col = st.columns([6, 1])
        with add_btn_col:
            if st.button(label="➕ 추가"):
                if new_kr.strip():
                    new_kr_d = Dialogue(
                        cut_image_id=ci_kr.id,
                        sequence=sequence,
                        content=new_kr.strip(),
                        dialogue_type=new_type  # 선택한 타입 저장
                    )
                    session.add(new_kr_d)
                if new_en.strip():
                    new_en_d = Dialogue(
                        cut_image_id=ci_en.id,
                        sequence=sequence,
                        content=new_en.strip(),
                        matched_dialogue_id = new_kr_d.id
                    )
                    session.add(new_en_d)

                session.commit()
                st.success("✅ 대사 추가 완료")
                st.rerun()

    __, save_btn_col = st.columns([6, 1])

    # ✅ 저장 버튼
    with save_btn_col:
        if max_len > 0 and st.button("💾 전체 저장"):
            for d in kr_dialogues + en_dialogues:
                session.add(d)
            session.commit()
            st.success("✅ 전체 저장 완료")

    session.close()