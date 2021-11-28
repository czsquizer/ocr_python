import os
import io
import logging
import gpyocr
import time
#import cv2
#import shutil

from logging import Formatter, FileHandler
from flask import Flask, request, jsonify, abort

#shutil.rmtree('uploads')
#os.mkdir('uploads')

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'

def genFilename(s):
    arr_s = s.split('.')
    t = time.strftime("%d-%m-%Yh%Hm%Ms%S", time.localtime())
    return arr_s[0] + t + '.' + arr_s[1]

@app.route('/processImage', methods=["POST"])
def ocr():
    try:
        url = request.args.get('file')
        if 'jpg' in url:
            output = gpyocr.tesseract_ocr('/home/ocr/server/uploads/'+url)
            os.remove('uploads/'+url)
            return output
        else:
            return jsonify({"error": "only .jpg files, please"})
    except:
        return jsonify(
            {"error": "Did you mean to send: {'image_url': 'some_jpeg_url'}"}
        )

@app.route("/uploadImage", methods=['POST'])
def uploadImg():
    file = request.files['file']
    file.filename = genFilename(file.filename)
    if file:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return file.filename

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: \
            %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)