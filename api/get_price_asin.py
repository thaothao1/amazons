from flask import Flask, render_template
from flask_mysqldb import MySQL
from Base import *
from flask_api import FlaskAPI
from api.get_api_size import getAsin, getHTML, getInfos, getInfosThread, getlink, getPrice2, getSizes, loadImages

from operator import itemgetter

app = FlaskAPI(__name__)


def getdata_codeasin(codeasin, price_old, dem):
    link = 'https://www.amazon.com/dp/{}?th=1&psc=1'.format(codeasin)
    codeHTML = CodeHTML(link)
    html = codeHTML.getPage()
    htmlTest = codeHTML.beautifulSoup()
    price_old = price_old
    sizes = getSizes(html)
    info_sort = []
    try:
        info = getInfos(sizes, html, codeHTML, codeasin)
        info_sort = sorted(info, key=itemgetter('indexSort'))
    except:
        info_sort = []
        data = info_sort

    return data


def getdata_codeasin(codeasin, price_old, dem):
    link = 'https://www.amazon.com/dp/{}?th=1&psc=1'.format(codeasin)
    codeHTML = CodeHTML(link)
    html = codeHTML.getPage()
    htmlTest = codeHTML.beautifulSoup()
    price_old = price_old
    sizes = getSizes(html)
    info_sort = []
    data = []
    try:
        info = getInfos(sizes, html, codeHTML, codeasin)
        info_sort = sorted(info, key=itemgetter('indexSort'))
    except:
        info_sort = []
        data.append(info_sort)
    return data


def getdata_asin(codeasin, price_old, dem):
    link = 'https://www.amazon.com/dp/{}?th=1&psc=1'.format(codeasin)
    codeHTML = CodeHTML(link)
    html = codeHTML.getPage()
    htmlTest = codeHTML.beautifulSoup()
    price_old = price_old
    data = getype(codeasin, price_old, dem)
    return data


def getype(codeasin, price_old, dem):
    link = 'https://www.amazon.com/dp/{}?th=1&psc=1'.format(codeasin)
    codeHTML = CodeHTML(link)
    htmlTest = codeHTML.beautifulSoup()
    links = {}
    links['codeasin'] = codeasin
    color = htmlTest.find('span', class_='selection')
    links['color'] = color.text.strip()
    size = htmlTest.find('span', class_='a-dropdown-prompt')
    links['size'] = size.text.strip()
    links["price_old"] = price_old
    vv = str(dem)
    tv = "color_name_{}_price".format(vv)
    element = htmlTest.find('span', id=tv)
    if(element):
        tt = element.text.strip()
        links["price_new"] = tt[14:]
    return links

# kiem tra xem kieu quan ao hay la do dung neu co size la loai quan ao


def get(codeAsin):
    link = link = 'https://www.amazon.com/dp/{}?th=1&psc=1'.format(codeAsin)
    codeHTML = CodeHTML(link)
    htmlTest = codeHTML.beautifulSoup()
    element = htmlTest.find('span', class_="a-size-small")
    if(element):
        mm = element.text.strip()
        if mm == "Size Chart":
            return "ok"
        else:
            return "no"
    return None
