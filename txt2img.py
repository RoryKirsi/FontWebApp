from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from os import listdir
from os.path import isfile, join
from selenium import webdriver
import base64
import os
import uuid
import functions

def make_test_img(text, align, spacing, font_path, font_name, font_format, color):
    file_path = 'html_temp'
    functions.dir_create(file_path)
    text = text.replace('\n', '<br>')
    text = text.replace('%S2F', '/')
    print(repr(text))
    #driver = webdriver.Chrome('Drivers/chromedriver')
    #driver = webdriver.Remote("http://127.0.0.1:4444/wd/hub", DesiredCapabilities.CHROME)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1420,1080')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    file_name = create_file(text, align, spacing, file_path, font_path, font_name, font_format, color)
    file_relative = "/"+file_path+"/"+file_name
    file_abstr = os.path.abspath(file_relative)
    print('getting sc from '+file_abstr, flush=True)
    driver.get('file://'+file_abstr)
    #driver.get("http://host.docker.internal:5000/sample/"+file_name)
    image_base64 = driver.find_element_by_id('page').screenshot_as_base64
    driver.quit()
    if os.path.exists(file_relative):
        os.remove(file_relative)
    else:
        print("Temp HTML not existed.")
    img = Image.open(BytesIO(base64.b64decode(image_base64)))
    width, height = img.size
    return image_base64, (width, height)

def make_test_img_2(format, text, selected_font, alignment, color):
    #preset properties
    font_size = 60
    preset_size = font_size

    #scratch image
    font = ImageFont.truetype("Fonts/"+selected_font, font_size)
    img = Image.new('RGBA', (1,1))
    draw = ImageDraw.Draw(img)
    width, height = draw.textsize(text, font)

    #adjust width and heigh, cannot handle all font height, only spacing to fit all font. Bug Note: https://stackoverflow.com/questions/43060479/how-to-get-the-font-pixel-height-using-pils-imagefont-class
    ascent, descent = font.getmetrics()
    height += descent

    #draw final image
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("Fonts/"+selected_font, preset_size)
    draw.text((0,0), text, fill=color, font=font, align=alignment)
    img_str = img_to_base64(format, img)
    return img_str, (width, height)

def make_test_img_3(format, text, selected_font, alignment):
    #preset properties
    font_size = 60
    preset_size = font_size

    #scratch image
    font = ImageFont.truetype("Fonts/"+selected_font, font_size)
    img = Image.new('RGBA', (1,1))
    draw = ImageDraw.Draw(img)
    width, height = draw.textsize(text, font)

    #draw final image
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("Fonts/"+selected_font, preset_size)

    text = process_text(text)

    gap_width = 0
    xpos = 0
    for line in text:
        for letter in line:
            width_offset, height_offset = font.getoffset(letter)
            draw.text((xpos, 0), letter, fill=(0,0,0), font=font)
            letter_width, letter_height = draw.textsize(letter, font=font)
            xpos += letter_width + gap_width

    img_str = img_to_base64(format, img)
    return img_str, (width, height)

def make_img(filename, format, text, width_size, height_size, align, spacing, font, color):
    out = Image.new("RGB", (width_size, height_size), (255, 255, 255))

    fnt = ImageFont.truetype("Fonts/Vudotronic.otf", 40)

    d = ImageDraw.Draw(out)

    d.multiline_text((10, 10), text,  font=fnt, fill=(0, 0, 0))

    out.save("Temp_Imgs/"+filename+format)

def img_to_base64(format, img):
    output_buffer = BytesIO()
    img.save(output_buffer, format=format)
    byte_data = output_buffer.getvalue()
    base64_bytes = base64.b64encode(byte_data)
    output_buffer.close()
    return base64_to_string(base64_bytes)

def base64_to_string(bytes_data):
    return bytes_data.decode('utf-8')

def read_dic(path):
    return ([f for f in listdir(path) if isfile(join(path, f))])

def adjust_new_width_size(old_width, old_height, height):
    return int(round((float(old_width)/float(old_height))*float(height)))

def adjust_new_height_size(old_width, old_height, width):
    return int(round((float(old_height)/float(old_width))*float(width)))

def adjust_font_size(size_change_code, given_width, given_height, old_width, old_height):
    if size_change_code == '100':
        return (given_width, adjust_new_height_size(old_width, old_height, given_width))
    elif size_change_code == '000':
        return (old_width, old_height)
    else:
        return (adjust_new_width_size(old_width, old_height, given_height), given_height)

def process_text(text):
    print(text)
    text = text.replace('%20', ' ')
    return text.split('%0A')

def img_char_test(text, selected_font, font_size):
    font = ImageFont.truetype("Fonts/"+selected_font, font_size)
    img = Image.new('RGBA', (1,1))
    draw = ImageDraw.Draw(img)
    width, height = draw.textsize(text, font)
    w_offset, h_offset = font.getoffset(text)
    ascent, descent = font.getmetrics()
    height += descent
    print(width,height)
    print(w_offset, h_offset)
    img = Image.new('RGBA', (width+1, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("Fonts/"+selected_font, font_size)
    draw.text((-w_offset,-h_offset), text, fill=(0,0,0), font=font)
    (x0,y0,x1,y1) = font.getmask(text).getbbox()
    img2 = Image.new('RGBA', (x1, y1), (255, 255, 255, 0))
    print(x0,y0,x1,y1)
    draw.rectangle((x0,y0,x1,y1), outline='red')
    img.show()

def make_font_html():
    pass

def create_file(text, align, spacing, file_path, font_path, font_name, font_format, color):
    state=os.path.exists(file_path)
    if not state:
        os.mkdir(file_path)

    fileUUID = uuid.uuid1()
    fileName = str(fileUUID)+'.html'

    html_content = ('<!DOCTYPE html>\n<html lang="en">\n\n<style>\n@font-face {\nfont-family: %s;\nsrc: url("%s");\nfont-weight: normal;\nfont-style: normal;\n}\n#page\n{\nfont-family: %s;\nfont-size: 60px;\nletter-spacing: %spx;\nwidth: 100%%;\npadding-right: 0.1em;\ntext-align: %s;\ncolor: %s;\n}\n#page_container{\ndisplay: inline-block;\nwidth: auto;\nheight: auto;\n}\n</style>\n\n<head>\n<meta charset="UTF-8">\n</head>\n<body>\n<div id="page_container">\n<p id="page">%s</p>\n</div>\n</body>\n</html>') % (font_name, font_path+font_name+font_format, font_name, spacing, align, color, text)

    with open(file_path+"/"+fileName, 'a') as f:
        f.writelines(html_content)
        f.close()

    return fileName

