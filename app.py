###
# MADE BY MARVIS, thank you!
###

from PIL import Image
from pathlib import Path
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import pytesseract
import uvicorn
import string
import random


pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe" # Comment this out if you are on Linux

blacklisted_words = [
    "fallout", "detected", "fallout", "player options", "self options", "weapon options", "world options", "teleport options", "lua options", "online players", "execute", "screenshot-basic",
    "aimbot", "resource", "invicible", "injected", "modifiers", "god mode", "infinite stamina", "refill health in cover", "no ragdoll", "antistun", "infinite combat roll",
    "invisibility", "noclip", "executor", "load .lua", "sugarMenu", "eulen", "wallhack", "not-safe", "esp active", "show npc", "disable while in game menu", 
    "enemy_visible", "lock at one target", "view aim point", "visibility check", "nearest bone aiming", "Nearest max dist", "Prediction", "Self-Healing", "infinite ammo", "norecoil", "no collision", 
    "save/load settings"
]

app = FastAPI()


def get_data(image):
    return pytesseract.image_to_string(image, output_type=pytesseract.Output.DICT)


def generate_random_name():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + ".jpg"


def check_data(data):
    data = data["text"].lower().strip()
    for word in blacklisted_words:
        if word in data:
            return word

@app.post("/uploadImage")
async def upload_image(file: UploadFile = File(...)):
    if file.content_type == "image/jpeg":
        random_name = generate_random_name()
        image = Image.open(file.file)
        image.save(f"images/{random_name}")
        return random_name
    else:
        return {"error": "only .jpg files, please"}

@app.post('/processImage')
async def process_image(file: UploadFile = File(...)):
    if file.content_type == "image/jpeg":
        image = Image.open(file.file)
        ocrText = get_data(image)
        result = check_data(ocrText)
        if result:
            random_name = generate_random_name()
            folder = Path("images")
            if not folder.is_dir():
                Path.mkdir(folder)
            image.save(f"images/{random_name}")
            return {"blacklisted_word": result, "image_name": random_name}
        else:
            return False
    else:
        return {"error": "only .jpg files, please"}


@app.get("/images/{file_name}")
async def get_image(file_name: str):
    image = Path(f"images/{file_name}")
    if image.is_file():
        return FileResponse(str(image))

if __name__ == '__main__':
    uvicorn.run("app:app", port=5000, host='0.0.0.0')
