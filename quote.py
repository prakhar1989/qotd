import re
from PIL import Image, ImageFont, ImageDraw 
from random import choice
import shutil
import json
import requests
import textwrap

canned_seeds = ["Opportunities", "When in doubt",
        "Always remember", "Today is", "Never forget", "It is okay to"]

title_font = ImageFont.truetype('lato.ttf', 48)

def download_img():
    response = requests.get("https://source.unsplash.com/random/800×800/?landscape", stream=True)
    with open('img.png', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response


def generate_img(text):
    img = Image.open("img.png")
    w, h = img.size
    image_editable = ImageDraw.Draw(img)
    y_offset = h/2
    for line in textwrap.wrap(text, width=40):
        length = title_font.getbbox(line)[2]
        x = (w - length)/2
        image_editable.text((x,y_offset), line, (237, 230, 211), font=title_font)
        y_offset += title_font.getbbox(line)[3]
    img.save("result.jpg")


def get_quote():
    seed = choice(canned_seeds)
    resp = requests.post('http://127.0.0.1:8000/generate', data=json.dumps({"text": seed}))
    return resp.json()["text"]

quote = get_quote()
download_img()
generate_img(quote)
