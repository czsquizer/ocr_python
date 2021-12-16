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

#pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe" # Uncomment this if you are using Windows

blacklisted_words = [
    "fallout", "undetected", "fallout", "player options", "self options", "weapon options", "world options", "teleport options", "lua options", "online players", "execute", "screenshot-basic",
    "aimbot", "resource:", "invicible", "injected"
]
app = FastAPI()
queue = queue.Queue()


def store_in_queue(f):
    def wrapper(*args):
        queue.put(f(*args))
    return wrapper


@store_in_queue
def get_data(image):
    return pytesseract.image_to_string(image, output_type=pytesseract.Output.DICT)


def generate_random_name():
    return "".join(random.choices(string.ascii_letters + string.digits, k=30)) + ".jpg"


def check_data(data):
    data = data["text"].lower().strip()
    for word in blacklisted_words:
        if word in data:
            return word

@app.post("/uploadImage")
async def upload_image(file: UploadFile = File(...)):
    if file.content_type == "image/jpeg":
        image = Image.open(file.file)
        random_name = generate_random_name()
        image.save(f"images/{random_name}")
        return random_name
    else:
        return {"error": "only .jpg files, please"}

@app.post("/processImage")
async def process_image(file: UploadFile = File(...)):
    if file.content_type == "image/jpeg":
        image = Image.open(file.file)
        t = threading.Thread(target=get_data, args=(image,))
        t.start()
        ocrText = queue.get()
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


@app.get("/images/{file_name}")
async def get_image(file_name: str):
    image = Path(f"images/{file_name}")
    if image.is_file():
        return FileResponse(str(image))

if __name__ == "__main__":
    uvicorn.run("app:app", port=5000, host="0.0.0.0")
