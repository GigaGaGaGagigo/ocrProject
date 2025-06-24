from PIL import Image
import pytesseract
import gradio as gr

def extract_text_from_webtoon(image):
    # 한글 + 영어 인식
    result = pytesseract.image_to_string(image, lang='kor+eng')
    return result

demo = gr.Interface(
    fn=extract_text_from_webtoon,
    inputs=gr.Image(type="pil", label="웹툰 이미지 업로드"),
    outputs=gr.Textbox(label="인식된 대사 / 텍스트"),
    title="웹툰 글자 인식 학습기",
    description=(
        "웹툰 이미지에서 말풍선 속 글자나 자막을 추출하는 도구입니다.\n"
        "OCR 결과는 교육용이나 제작 보조 용도로 활용할 수 있습니다."
    ),
    allow_flagging="never"
)

if __name__ == "__main__":
    demo.launch()
