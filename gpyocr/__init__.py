"""
gpyocr - Python wrapper to Tesseract OCR and Google Vision OCR
"""


__version__ = "1.4"


from ._gpyocr import (
    SUPPORTED_FORMATS,
    get_tesseract_version,
    tesseract_ocr,
)
