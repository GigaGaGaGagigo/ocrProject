import streamlit as st
from front import url_insert, mu, my, use_home, sidebar

# 페이지 설정
st.set_page_config(page_title="Comic Study", layout="wide")

# ✅ 1. 테마 및 폰트 크기 선택 UI (사이드바)
with st.sidebar:
    page, page1, theme, font_size, admin_mode = sidebar.render_sidebar()

sidebar.css(page, page1, theme, font_size, admin_mode)

if "reader" in st.session_state and st.session_state["view_mode"] == "reader":
     if not st.session_state.get("reader_rendered"):
        use_home.webtoon_read(
            st.session_state.get("selected_ep_kr"),
            st.session_state.get("selected_ep_en")
        )
        st.session_state["reader_rendered"] = True
        st.stop()