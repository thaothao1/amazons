from Base import *
import re
import requests
import glob
import os
import shutil
import json
from datetime import date, datetime, timedelta
import time

from flask import request, url_for, send_file, jsonify
from flask_api import FlaskAPI, status, exceptions
from operator import itemgetter
from lxml import html

from concurrent import futures
from concurrent.futures import ThreadPoolExecutor, wait
from operator import itemgetter


link = {}
links = []


def getstype(codeasin):
    link = 'https://www.amazon.com/dp/{}?th=1&psc=1'.format(codeasin)
    codeHTML = CodeHTML(link)
    html = codeHTML.getPage()
    htmlTest = codeHTML.beautifulSoup()
    type = htmlTest.find('div', class_="a-row a-spacing-micro")
    tt = ""
    if (type):
        st = type.text.strip()
        if "Size:" in st:
            tt = "size"
            return tt
        else:
            tt = "stype"
            return tt
    return tt


def getPrice(codeAsin):
    link = link = 'https://www.amazon.com/dp/{}?th=1&psc=1'.format(codeAsin)
    codeHTML = CodeHTML(link)
    root = codeHTML.tree()
    elements = root.xpath(
        '//*/td[@class="a-span12"]/span[@id="priceblock_ourprice"]')
    if elements != None and len(elements) != 0:
        return elements[0].text.strip()
    elements = root.xpath(
        '//*/td[@class="a-span12"]/span[@id="priceblock_saleprice"]')
    if elements != None and len(elements) != 0:
        return elements[0].text.strip()

    elements = root.xpath(
        '//*/div[@class="a-section a-spacing-small a-spacing-top-small"]/div[@id="olp-upd-new"]/span/a')
    if elements != None and len(elements) != 0:
        element = elements[0]
        str = html.tostring(element, encoding='utf-8').decode("utf-8")
        mask = """(\\$[0-9\\.]+)"""
        matchs = re.findall(mask, str)

        for m in matchs:
            return m
    htmlTest = codeHTML.beautifulSoup()
    # delivery = htmlTest.find('span', id="a-offscreen")
    # if(delivery):
    #     print(delivery.text.strip())
    element = htmlTest.find('span', class_="a-offscreen")
    if(element):
        print(element.text.strip())
        return element.text.strip()
    return None


def getname(codeAsin):
    link = link = 'https://www.amazon.com/dp/{}?th=1&psc=1'.format(codeAsin)
    codeHTML = CodeHTML(link)
    htmlTest = codeHTML.beautifulSoup()
    delivery = htmlTest.find('span', id="productTitle")
    if(delivery):
        print(delivery.text.strip())
        return delivery.text.strip()
    element = htmlTest.find(
        'span', class_="a-size-large product-title-word-break")
    if(element):
        print(element.text.strip())
        return element.text.strip()
    return None


def getdata(codeAsin):
    link = link = 'https://www.amazon.com/dp/{}?th=1&psc=1'.format(codeAsin)
    codeHTML = CodeHTML(link)
    htmlTest = codeHTML.beautifulSoup()

    codeasins = htmlTest.findAll("li", class_="swatchAvailable")
    codeasin = htmlTest.findAll("li", class_="swatchSelect")

    for code in codeasin:
        link = {}
        texts_price = str(code['id']+"_price")
        st = str(code['title'])
        name_color = st[15:]
        link["codeasin"] = code['data-defaultasin']
        link["color"] = name_color
        element = htmlTest.find('span', id=texts_price)
        stt = element.text.strip()
        if "option" in stt:
            link["option"] = stt[:9]
            link["price"] = stt[14:]
        else:
            link["price"] = element.text.strip()
        links.append(link)
    for codes in codeasins:
        link = {}
        texts_price = str(codes['id']+"_price")
        st = str(codes['title'])
        name_color = st[15:]
        link["codeasin"] = codes['data-defaultasin']
        link["color"] = name_color
        element = htmlTest.find('span', id=texts_price)
        tt = element.text.strip()
        if "option" in tt:
            link["option"] = tt[:9]
            link["price"] = tt[14:]
        else:
            link["price"] = element.text.strip()
        links.append(link)
    return links
