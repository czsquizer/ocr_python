###
# MADE BY MARVIS, thank you!
###

import pytesseract
from PIL import Image
from fastapi import FastAPI, File, UploadFile
import uvicorn
import threading
import queue
import time

app = FastAPI()
queue = queue.Queue()


def store_in_queue(f):
    def wrapper(*args):
        queue.put(f(*args))
    return wrapper


@store_in_queue
def get_name(file):
    image = Image.open(file)
    return pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)


@app.post('/processImage')
async def process_image(file: UploadFile = File(...)):
    start = time.perf_counter()
    if file.content_type == "image/jpeg":
        t = threading.Thread(target=get_name, args=(file.file,))
        t.start()
        ocrText = queue.get()
        t.join()
        end = time.perf_counter()
        print(end - start)
        return ocrText
    else:
        return {"error": "only .jpg files, please"}

if __name__ == '__main__':
    uvicorn.run("app:app", port=5000, host='0.0.0.0')
