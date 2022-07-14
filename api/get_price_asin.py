from Base import *
from flask_api import FlaskAPI
from operator import itemgetter
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


app = FlaskAPI(__name__)


# def stype_link(CodeAsin, stype, price_old):
#     # tyle_link1 :
#     if stype == "gp":
#         link1 = 'https://www.amazon.com/gp/product/{}?th=1'.format(CodeAsin)
#         stype1 = "gp"
#         codeasin = CodeAsin
#         price_old = price_old
#         return getdata(link1, stype1, codeasin, price_old)
#     else:
#         # type_link2
#         if stype == "dp":
#             link2 = 'https://www.amazon.com/dp/{}?th=1&psc=1'.format(CodeAsin)
#             stype2 = "dp"
#             codeasin = CodeAsin
#             price_old = price_old
#         return getdata(link2, stype2, codeasin, price_old)


def homnay(thao):
    link = 'https://www.amazon.com/dp/{}?th=1&psc=1'.format(thao)
    codeHTML = CodeHTML(link)
    html = codeHTML.getPage()
    htmlTest = codeHTML.beautifulSoup()
    viet = ""
    type = htmlTest.find('div', class_="a-row a-spacing-micro")
    if (type):
        st = type.text.strip()
        if "Size:" in st:
            viet = "ok"
            return viet
        else:
            viet = "no"
            return viet
    return viet


def getSizes(html):
    html = html.replace(';\n', ';<--hoa-->')
    html = html.replace('; //', ';<--hoa-->')
    html = html.replace('\n', ' ')
    html = html.replace('    ', '')
    html = html.replace('  ', ' ')
    html = html.replace(' +', ' ')
    html = html.replace('var ', '\nvar ')
    html = html.replace(';<--hoa-->', ';\n')

    mask = """var dataToReturn = (.+);"""
    matchs = re.findall(mask, html, re.M)
    sizes = []
    for m in matchs:
        json_string = m.replace("\'", '"')
        json_string = json_string.replace('\t', '')
        json_string = json_string.replace(', ]', ']')
        json_string = json_string.replace(',]', ']')

        obj = json.loads(json_string)
        color_names = []
        size_names = []
        asinVariationValues = []

        if 'variationValues' in obj:
            variationValues = obj['variationValues']
            if 'color_name' in variationValues:
                a = variationValues['color_name']
            if 'size_name' in variationValues:
                size_names = variationValues['size_name']
                sizes = size_names
    return sizes


def getdata_codeasin(codeasin, price_old, dem):
    link = 'https://www.amazon.com/dp/{}?th=1&psc=1'.format(codeasin)
    codeHTML = CodeHTML(link)
    html = codeHTML.getPage()
    htmlTest = codeHTML.beautifulSoup()
    price_old = price_old
    dem = dem
    type = htmlTest.find('div', class_="a-row a-spacing-micro")
    if (type):
        st = type.text.strip()
        if "Size:" in st:
            sizes = getSizes(html)
            info_sort = []
            try:
                info = getInfos(sizes, html, codeHTML, codeasin)
                info_sort = sorted(info, key=itemgetter('indexSort'))
            except:
                info_sort = []
            data = info_sort
        else:
            data = getype(codeasin, price_old)
    else:
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


def getPrice2(codeAsin):
    link = 'https://www.amazon.com/dp/{}?th=1&psc=1'.format(codeAsin)
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
    delivery = htmlTest.find('span', id="contextualIngressPtLabel")
    if(delivery):
        print(delivery.text.strip())
    element = htmlTest.find('span', class_="a-size-medium a-color-price")
    if(element):
        print(element.text.strip())
        return element.text.strip()

    return None


def getInfosThread(codeASIN, size_name, infos, indexSort, price_old):
    isFind = False
    isSoldOut = False
    product = None
    print(f"START {codeASIN} - {size_name}")
    # products = Product.objects(amazon_codeASIN=codeASIN)
    # if products.count() > 0:
    # 	isFind = True
    # 	if products.count() > 1:
    # 		print("Loi dupliacation database: amazon_codeASIN= {}".format(codeASIN))
    # 	product = products[0]
    price = getPrice2(codeASIN)
    # print(f"END {price}")
    # if price == None:
    # 	isSoldOut = True
    # 	if isFind == True:
    # 		price = product.amazon_price
    # else:
    # 	if isFind == True:
    # 		product.amazon_price = price
    # 		product.save()
    # 	else:
    # 		product = Product(title="N/A", amazon_codeASIN=codeASIN)
    # 		product.amazon_price = price
    # 		product.save()
    info = {'codeasin': codeASIN, 'sizeName': size_name,
            'isSoldOut': isSoldOut, 'price_new': price, 'indexSort': indexSort, "price_old": price_old}
    infos.append(info)


def getInfos(sizes, html, codeHTML, productDir, price_old):
    print("START")
    executor = ThreadPoolExecutor(max_workers=30)
    futures = []
    infos = []
    price_old = price_old
    html = html.replace(';\n', ';<--hoa-->')
    html = html.replace('; //', ';<--hoa-->')
    html = html.replace('\n', ' ')
    html = html.replace('    ', '')
    html = html.replace('  ', ' ')
    html = html.replace(' +', ' ')
    html = html.replace('var ', '\nvar ')
    html = html.replace(';<--hoa-->', ';\n')

    mask = """var dataToReturn = (.+);"""
    matchs = re.findall(mask, html, re.M)

    for m in matchs:
        json_string = m.replace("\'", '"')
        json_string = json_string.replace('\t', '')
        json_string = json_string.replace(', ]', ']')
        json_string = json_string.replace(',]', ']')

        obj = json.loads(json_string)
        color_names = []
        size_names = []
        asinVariationValues = []

        if 'variationValues' in obj:
            variationValues = obj['variationValues']
            if 'color_name' in variationValues:
                a = variationValues['color_name']
            if 'size_name' in variationValues:
                size_names = variationValues['size_name']
        if 'asinVariationValues' in obj:
            asinVariationValues = obj['asinVariationValues']
        selectedColorName = 0
        if "selectedVariationValues" in obj:
            selectedVariationValues = obj['selectedVariationValues']
            if "color_name" in selectedVariationValues:
                selectedColorName = selectedVariationValues["color_name"]
        if asinVariationValues == []:
            continue
        for key, value in asinVariationValues.items():
            code_size = value['size_name']
            code_color = value['color_name']
            size_name = size_names[int(code_size)]
            if selectedColorName != int(code_color):
                continue
            if sizes != [] and size_name not in sizes:
                continue
            codeASIN = value['ASIN']
            print(sizes)
            # print("A", value['ASIN'], size_name)
            indexSort = sizes.index(size_name)
            # print("B", indexSort)
            future = executor.submit(
                getInfosThread, codeASIN, size_name, infos, indexSort, price_old)
            futures.append(future)
    wait(futures)
    if infos == []:
        priceElement = codeHTML.elementWithXpath(
            '//*[@id="priceblock_ourprice"]')
        print("priceElement = ", priceElement)
        if priceElement != None:
            price = priceElement.text.strip()
            codeASIN = productDir
            isSoldOut = True
            if price != None:
                isSoldOut = False
            info = {'codeASIN': codeASIN, 'sizeName': None, "price_old": price_old,
                    'isSoldOut': isSoldOut, 'price_new': price}
            infos.append(info)
    print("END")
    return infos
