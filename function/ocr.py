import easyocr

reader = easyocr.Reader(['ko', 'en'])

def extract_text_from_image(image_path):
    result = reader.readtext(image_path, detail=0)
    return "\n".join(result)