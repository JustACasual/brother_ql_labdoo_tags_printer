import json
import logging
import subprocess
import os

import urllib.request
from urllib.request import urlopen
from bs4 import BeautifulSoup

from PIL import Image, ImageDraw, ImageFont


def read_battery_capacity(tag):
    try:
        url = 'https://www.labdoo.org/content/tag-one-dooject?id=0000' + tag
        html = urlopen(url)
        html_soup = BeautifulSoup(html, 'html.parser')

        bat_cap = str(html_soup)[str(html_soup).find(
            'watt-hours:') + 16:str(html_soup).find("watt-hours:") + 20]

        if bat_cap == "Not ":
            bat_cap = "Not Available"
        else:
            bat_cap = bat_cap + " Wh"

        return bat_cap
    except Exception as e:
        logging.error("Error Reading Battery Capacity")
        logging.error(e)
        return ""


def read_save_qr_code(tag):
    try:
        qr_add = "https://api.qrserver.com/v1/create-qr-code/?"
        qr_add = qr_add + "size=180x180&data=http%3A%2F%2Fplatform.labdoo.org%2Fcontent%2F"
        urllib.request.urlretrieve(
            qr_add + tag, "img/qr.png")
    except Exception as e:
        logging.error("Error Reading QR Code")
        logging.error(e)


def create_device_label(tag):
    try:
        filename = "img/device_tag.png"

        img = Image.new('RGB', (554, 200), color=(255, 255, 255))

        if os.name == "nt":  # get windows font
            big_fnt = ImageFont.truetype('arial.ttf', 30)
            small_fnt = ImageFont.truetype('arial.ttf', 14)
        else:  # get linux font (likely ubuntu here, may not work for other OS)
            big_fnt = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 30)
            small_fnt = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 14)

        d = ImageDraw.Draw(img)
        d.text((10, 70), "Device Tag ID:", font=big_fnt, fill=(0, 0, 0))
        d.text((10, 105), "000" + tag, font=big_fnt, fill=(0, 0, 0))


        im_qr = Image.open('img/qr.png')
        im_logo = Image.open('logo.png')
        img.paste(im_qr, (360, 10))
        img.paste(im_logo.resize((210, 55)), (5, 5))
        img.save(filename)

        return filename
    except Exception as e:
        logging.error("Error Creating Label")
        logging.error(e)
        return ""

def create_power_adapter_label(tag):
    try:
        filename = "img/power_tag.png"
        img = Image.new('RGB', (554, 200), color=(255, 255, 255))

        if os.name == "nt":  # get windows font
            big_fnt = ImageFont.truetype('arial.ttf', 30)
        else:  # get linux font (likely ubuntu here, may not work for other OS)
            big_fnt = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 30)

        d = ImageDraw.Draw(img)
        d.text((10, 70), "Power Adap.Tag ID:", font=big_fnt, fill=(0, 0, 0))
        d.text((10, 105), "000" + tag, font=big_fnt, fill=(0, 0, 0))

        im_qr = Image.open('img/qr.png')
        im_logo = Image.open('logo.png')
        img.paste(im_qr, (360, 10))
        img.paste(im_logo.resize((210, 55)), (5, 5))
        img.save(filename)

        return filename
    except Exception as e:
        logging.error("Error Creating Label")
        logging.error(e)
        return ""


def create_battery_label(tag, bat_cap):
    try:
        filename = "img/battery_tag.png"
        img = Image.new('RGB', (554, 200), color=(255, 255, 255))

        if os.name == "nt":  # get windows font
            big_fnt = ImageFont.truetype('arial.ttf', 30)
            small_fnt = ImageFont.truetype('arial.ttf', 20)
        else:  # get linux font (likely ubuntu here, may not work for other OS)
            big_fnt = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 30)
            small_fnt = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 20)

        d = ImageDraw.Draw(img)
        d.text((10, 70), "Battery Comp. ID:", font=big_fnt, fill=(0, 0, 0))
        d.text((10, 105), "000" + tag, font=big_fnt, fill=(0, 0, 0))

        d.text((10, 140), "Battery Watt-Hours", font=small_fnt, fill=(0, 0, 0))
        d.text((10, 165), bat_cap, font=small_fnt, fill=(0, 0, 0))

        im_qr = Image.open('img/qr.png')
        im_logo = Image.open('logo.png')
        img.paste(im_qr, (360, 10))
        img.paste(im_logo.resize((210, 55)), (5, 5))
        img.save(filename)

        return filename
    except Exception as e:
        logging.error("Error Creating Label")
        logging.error(e)
        return ""


def create_images(tag: str, conf: dict):
    """
    Function to look in labdoo.org for a tag and
    create the images of the labels
    """
    read_save_qr_code(tag)

    img_files = []
    if conf['print_device_tag']:
        device_img = create_device_label(tag)
        img_files.append(device_img)

    if conf['print_power_adapter']:
        power_adapter_img = create_power_adapter_label(tag)
        img_files.append(power_adapter_img)

    if conf['print_battery_comp']:
        bat_cap = read_battery_capacity(tag)
        battery_img = create_battery_label(tag, bat_cap)
        img_files.append(battery_img)

    return img_files


def print_label(img_file, conf: dict):
    """Given a image file print the label"""

    model = conf['model']
    printer = conf['printer']
    brother_ql_cmd= conf['brother_ql_cmd']
    abs_img_path = os.path.abspath(img_file)
    # working command:
    # brother_ql -m QL-500 -p usb://0x04f9:0x2015 print -l 29 C:\Users\the_b\labdoo_print\brother_ql_labdoo_tags_printer\img\device_tag.png -r 90

    bash_command = brother_ql_cmd + " -m " + model + " -p " + printer + " print -l 29 " + abs_img_path + " -r 90"
    logging.info(bash_command)

    subprocess.run(bash_command,  shell=True)

    print("")
    input("Press Enter key to continue next image")


if __name__ == '__main__':
    logging.basicConfig(
        format="%(asctime)s: %(message)s",
        # filemode='a',
        # filename='HA-Watch.log',
        level=logging.INFO,
        datefmt="%H:%M:%S")

    # Read Printer Configuration File
    with open('config.json', 'r') as f:
        conf = json.load(f)
    for conf_elem in conf:
        logging.info(str(conf_elem) + ": " + str(conf[conf_elem]))
    logging.info("current OS: " + os.name)
    # Read Tags
    with open('tags.txt', 'r') as f:
        labdoo_tags = f.readlines()

    for curr_tag in labdoo_tags:
        try:

            # Read the website tag and create images
            img_files = create_images(curr_tag, conf)

            if not img_files:
                continue

            # Print the Labels
            for img in img_files:
                print_label(img, conf)
        except Exception as exc:
            logging.error("tag " + curr_tag + " could not be printed:")
            logging.error(exc)
    logging.info("print job finished")
