###
# MADE BY MARVIS, thank you!
###

from PIL import Image
from pathlib import Path
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import pytesseract
import uvicorn
import threading
import queue
import string
import random

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe" # Comment this out if you are on Linux

blacklisted_words = [
    "fallout", "undetected", "fallout", "player options", "self options", "weapon options", "world options", "teleport options", "lua options", "online players", "execute", "screenshot-basic",
    "aimbot", "resource:", "invicible", "injected"
]
app = FastAPI()
queueText = queue.Queue()
queueImage = queue.Queue()
queueUpload = queue.Queue()

def store_in_queueText(f):
    def wrapper(*args):
        queueText.put(f(*args))
    return wrapper

def store_in_queueImage(f):
    def wrapper(*args):
        queueImage.put(f(*args))
    return wrapper

def store_in_queueUpload(f):
    def wrapper(*args):
        queueUpload.put(f(*args))
    return wrapper

@store_in_queueText
def get_data(image):
    return pytesseract.image_to_string(image, output_type=pytesseract.Output.DICT)


def generate_random_name():
    return "".join(random.choices(string.ascii_letters + string.digits, k=30)) + ".jpg"


def check_data(data):
    data = data["text"].lower().strip()
    for word in blacklisted_words:
        if word in data:
            return word

def upload_image_as(file, name):
        image = Image.open(file)
        image.save(f"images/{name}")

@app.post("/uploadImage")
async def upload_image(file: UploadFile = File(...)):
    if file.content_type == "image/jpeg":
        random_name = generate_random_name()
        t = threading.Thread(target=upload_image_as, args=(file.file, random_name,))
        t.start()
        t.join()
        return random_name
    else:
        return {"error": "only .jpg files, please"}

@app.post("/processImage")
async def process_image(file: UploadFile = File(...)):
    if file.content_type == "image/jpeg":
        image = Image.open(file.file)
        t = threading.Thread(target=get_data, args=(image,))
        t.start()
        ocrText = queueText.get()
        t.join()
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


@store_in_queueImage
def get_image_a(name):
    image = Path(f"images/{name}")
    if image.is_file():
        return FileResponse(str(image))

@app.get("/images/{file_name}")
async def get_image(file_name: str):
    t = threading.Thread(target=get_image_a, args=(file_name,))
    t.start()
    image = queueImage.get()
    t.join()
    return image

if __name__ == "__main__":
    uvicorn.run("app:app", port=5000, host="0.0.0.0")
