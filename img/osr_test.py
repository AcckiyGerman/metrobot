#! python
from PIL import Image
import pytesseract

img = Image.open('repeat.png')
print( pytesseract.image_to_string(img) )