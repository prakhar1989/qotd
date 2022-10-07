from PIL import Image, ImageFont, ImageDraw 
from random import choice
from datetime import datetime
import shutil
import json
import os
import requests
import textwrap
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

image_backdrops = ['landscape', 'nature', 'stars', 'mountains']
canned_seeds = []
title_font = ImageFont.truetype('lato.ttf', 48)

cred = credentials.Certificate('serviceaccount.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': '{}.appspot.com'.format(os.environ["FIREBASE_BUCKET"])
})
bucket = storage.bucket()


# read seeds from file
with open('seeds.txt') as f:
    canned_seeds = [line.rstrip('\n') for line in f]

def download_img():
    backdrop = choice(image_backdrops)
    response = requests.get("https://source.unsplash.com/random/800×800/?"+ backdrop, stream=True)
    with open('img.png', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response


def generate_img(text):
    print("Generating image")
    img = Image.open("img.png")
    width, height = img.size
    image_editable = ImageDraw.Draw(img)
    lines = textwrap.wrap(text, width=40)
    line_count = len(lines)
    y_offset = height/2 - (line_count/2 * title_font.getbbox(lines[0])[3])
    for line in lines:
        (_, _, line_w, line_h) = title_font.getbbox(line)
        x = (width - line_w)/2
        image_editable.text((x,y_offset), line, (237, 230, 211), font=title_font)
        y_offset += line_h
    img.save("result.jpg")
    print("generated result.jpg")

def upload_img(filename):
    print("Uploading image")
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)
    blob.make_public()
    return blob.public_url

def get_quote():
    print("Generating quote")
    seed = choice(canned_seeds)
    resp = requests.post('http://127.0.0.1:8000/generate', data=json.dumps({"text": seed}))
    return resp.json()["text"]

def send_courier(image_url):
    print("Sending courier")
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(os.environ['COURIER_AUTH_TOKEN'])
    }
    message={
        "to": { "email": os.environ["COURIER_RECIPIENT"] },
        "data": {
            "date": datetime.today().strftime("%B %d, %Y"),
            "img": image_url
        },
        "routing": {
            "method": "single",
            "channels": [
                "email"
            ]
        },
        "template": os.environ["COURIER_TEMPLATE"]
    }
    resp = requests.post("https://api.courier.com/send", json={"message": message}, headers=headers)
    print(resp.json())

quote = get_quote()
download_img()
generate_img(quote)
img_url = upload_img("result.jpg")
send_courier(img_url)