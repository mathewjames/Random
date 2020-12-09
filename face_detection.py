import zipfile, io

from PIL import Image, ImageDraw
import pytesseract
import cv2 as cv
import numpy as np

# loading the face detection classifier
face_cascade = cv.CascadeClassifier('readonly/haarcascade_frontalface_default.xml')

# the rest is up to you!
def face_crop(img_data, faces):
    pil_img = Image.open(io.BytesIO(img_data))
    # Set our drawing context
    #drawing=ImageDraw.Draw(pil_img)
    # Surround it with a white box
    images = []
    for x,y,w,h in faces:
        face = pil_img.crop((x,y,x+w,y+h))
        if face.height > 100:
            face = face.resize((100,100))
        images.append(face)
    return images
def contact_sheet(images):
    img_num = len(images)
    if img_num % 5 == 0:
        height = int(img_num / 5)
    else:
        height = int(img_num / 5) + 1
    contact_sheet = Image.new('RGB', (500,100 * height))
    x=0
    y=0
    for img in images:
    # Paste the current image into the contact sheet
        contact_sheet.paste(img, (x, y) )
        # Update our X position. If it is going to be the width of the image, then we set it to 0
        # and update Y as well to point to the next "line" of the contact sheet.
        if x+img.width == contact_sheet.width:
            x=0
            y=y+img.height
        else:
            x=x+img.width
    display(contact_sheet)
def search(name, zip_file):
    with zipfile.ZipFile(zip_file, 'r') as myzip:
        for img in myzip.namelist():
            img_data = myzip.read(img)
            cv_img = cv.imdecode(np.frombuffer(img_data, np.uint8), 1)
            gray = cv.cvtColor(cv_img, cv.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(gray)
            if name in text:
                print(f'Results found in file {img}')
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                # 'faces' is a list of rectangles in the format of (x,y,w,h) where x and y denote the upper
                # left hand point for the image and the width and height represent the bounding box.
                length = len(faces)
                if length < 1:
                    print('But there were no faces in that file!')
                else:
                    images = face_crop(img_data, faces)
                    contact_sheet(images)
print("For Chris\n")
search('Chris', 'readonly/small_img.zip')
print("For Mark\n")
search('Mark', 'readonly/images.zip')
