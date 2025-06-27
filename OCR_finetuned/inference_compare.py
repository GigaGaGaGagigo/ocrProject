# inference_compare.py

import torch
from torchvision import transforms
from PIL import Image
import yaml
import easyocr
import importlib.util
import sys
import os

"""
fine-tuned 된 easyocr 모델을 불러와 인식하고 
기본 easyocr 모델 성능 결과와 비교하는 코드입니다. 
"""

# 1. 사용자 정의 모델 불러오기
spec = importlib.util.spec_from_file_location("finetuned", "./finetuned.py")
finetuned_module = importlib.util.module_from_spec(spec)
sys.modules["finetuned"] = finetuned_module
spec.loader.exec_module(finetuned_module)

# 2. config.yaml 로딩 및 문자셋 추출
with open("finetuned.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)

if "character" in config:
    character = config["character"]
elif "character_list" in config:
    character = config["character_list"]
else:
    raise ValueError("❌ config 파일에 'character' 또는 'character_list'가 없습니다.")

num_class = len(character) + 1  # CTC blank
img_height = config.get("imgH", 64)
img_width = config.get("imgW", 600)  # 없을 경우 600

input_channel = config.get("network_params", {}).get("input_channel", 1)
output_channel = config.get("network_params", {}).get("output_channel", 256)
hidden_size = config.get("network_params", {}).get("hidden_size", 256)

# 3. 모델 초기화 및 가중치 로딩
Model = finetuned_module.Model
model = Model(
    input_channel=input_channel,
    output_channel=output_channel,
    hidden_size=hidden_size,
    num_class=num_class
)
model.eval()

# 멀티 GPU 가중치 대응: "module." prefix 제거
state_dict = torch.load("finetuned.pth", map_location="cpu")
if any(k.startswith("module.") for k in state_dict.keys()):
    from collections import OrderedDict
    state_dict = OrderedDict((k.replace("module.", ""), v) for k, v in state_dict.items())
model.load_state_dict(state_dict)

# 4. 이미지 전처리
image_path = "1.jpeg"
image = Image.open(image_path).convert("RGB")
transform = transforms.Compose([
    transforms.Grayscale(1),
    transforms.Resize((img_height, img_width)),
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])
input_tensor = transform(image).unsqueeze(0)  # shape: [1, 1, H, W]

# 5. 사용자 모델로 추론
with torch.no_grad():
    output = model(input_tensor, text=None)
    probs = output.softmax(2)
    _, preds = probs.max(2)
    preds = preds.squeeze(0).tolist()

def decode_ctc(preds, charset):
    result = ''
    prev = -1
    for p in preds:
        if p != prev and p != len(charset):  # skip blank
            result += charset[p]
        prev = p
    return result

finetuned_text = decode_ctc(preds, character)

# 6. EasyOCR 기본 모델 추론
reader = easyocr.Reader(['ko', 'en'], gpu=False)
easyocr_result = reader.readtext(image_path, detail=0)

# 7. 결과 비교 출력
print("\n📌 [Fine-tuned Model 결과]")
print(finetuned_text)

print("\n📌 [EasyOCR 기본 모델 결과]")
for line in easyocr_result:
    print(line)