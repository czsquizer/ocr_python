###
# MADE BY MARVIS, thank you!
###

from PIL import Image
from pathlib import Path
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from sys import platform
import pytesseract
import uvicorn
import string
import random

token = 'NOTOKEN' # Change to token to match the token in the anticheat. It is not necessary, but HIGHLY recommended

if platform == "win32":
    pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

blacklisted_words = [
    "fallout", "detected", "fallout", "player options", "self options", "weapon options", "world options", "teleport options", "lua options", "online players", "execute", "screenshot-basic",
    "aimbot", "resource", "invicible", "injected", "modifiers", "god mode", "infinite stamina", "refill health in cover", "no ragdoll", "antistun", "infinite combat roll",
    "invisibility", "executor", "load .lua", "wallhack", "not-safe", "esp active", "show npc", "disable while in game menu", 
    "enemy_visible", "lock at one target", "view aim point", "visibility check", "nearest bone aiming", "nearest max dist", "prediction", "self-healing", "infinite ammo", "norecoil", "no collision", 
    "save/load settings"
]

app = FastAPI(docs_url=None, redoc_url=None)


def get_data(image):
    return pytesseract.image_to_string(image, output_type=pytesseract.Output.DICT)


def generate_random_name():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + ".jpg"


def check_data(data):
    data = data["text"].lower().strip()
    for word in blacklisted_words:
        if word in data:
            return word

@app.post('/'+token + "/uploadImage")
async def upload_image(file: UploadFile = File(...)):
    if file.content_type == "image/jpeg":
        random_name = generate_random_name()
        image = Image.open(file.file)
        image.save(f"images/{random_name}")
        return random_name
    else:
        return {"error": "only .jpg files, please"}

@app.post('/'+token + '/processImage')
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
