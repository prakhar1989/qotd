import re
from PIL import Image, ImageFont, ImageDraw 
from random import choice
import shutil
import json
import requests
import textwrap

image_backdrops = ['landscape', 'nature', 'stars', 'mountains']
canned_seeds = []
title_font = ImageFont.truetype('lato.ttf', 48)

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


def get_quote():
    seed = choice(canned_seeds)
    resp = requests.post('http://127.0.0.1:8000/generate', data=json.dumps({"text": seed}))
    return resp.json()["text"]

quote = get_quote()
download_img()
generate_img(quote)
