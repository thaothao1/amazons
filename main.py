from itertools import product
from unittest import result
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
from api.get_api_size import getAsin, getHTML, getInfos, getInfosThread, getPrice2, getSizes, loadImages, getlink
from api.get_api_stype import getname, getPrice, getstype,  getdata
from api.get_zip_code import zip_code
from api.get_price_asin import getdata_codeasin, homnay


app = FlaskAPI(__name__)
FORDER_IMAGE = os.path.join('tmp', '')
# FORDER_IMAGE_UPLOAD = os.path.join('uploads', '')
urlEntry = None
spEntry = None
nColor = 0
imageFolder = "./tmp"
executor = ThreadPoolExecutor(max_workers=10)
futures = []
data = {}
entryUrls = []
test = []
db = {}


def main():
    app = FlaskAPI(__name__)

    app.config["FORDER_IMAGE"] = FORDER_IMAGE

    @app.after_request
    def after_request(response):
        ContentSecurityPolicy = ''
        ContentSecurityPolicy += "default-src 'self'; "
        ContentSecurityPolicy += "script-src 'self' 'unsafe-inline'; "
        ContentSecurityPolicy += "style-src 'self' 'unsafe-inline'; "
        ContentSecurityPolicy += "img-src 'self' data:; "
        ContentSecurityPolicy += "connect-src 'self';"
        response.headers.add('Content-Security-Policy',  ContentSecurityPolicy)
        response.headers.add('X-Content-Type-Options', 'nosniff')
        response.headers.add('Strict-Transport-Security',
                             'max-age=86400; includeSubDomains')
        response.headers.add('X-Frame-Options', 'deny')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        response.headers.add('X-XSS-Protection', '1; mode=block')
        response.headers.set('Server', '')

        # This is neccessary for a project partner
        response.headers.add('Access-Control-Allow-Origin', '*')
        # header = response.headers
        # header['Access-Control-Allow-Origin'] = '*'
        # header['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        # header['Access-Control-Allow-Methods'] = 'OPTIONS, HEAD, GET, POST, DELETE, PUT'
        return response

    @app.route("/amazon/api/getImage", methods=['POST'])
    def getAllImage():
        global data
        data = {}
        url = str(request.data.get('link_ref', ''))
        link = zip_code(url)
        productDir = getAsin(link)
        codeHTML = CodeHTML(link)
        html = codeHTML.getPage()
        stype = getstype(productDir)
        if stype == "size":
            sizes = getSizes(html)
            data["asinCode"] = productDir
            data["linkRoot"] = link
            price = getPrice2(productDir)
            info_sort = []
            try:
                info = getInfos(sizes, html, codeHTML, productDir)
                info_sort = sorted(info, key=itemgetter('indexSort'))
            except:
                info_sort = []
            data["price"] = price
            data["info"] = info_sort
            response = jsonify({"data": data})
            # response = jsonify({"data": data})
            # Enable Access-Control-Allow-Origin
            return response
        else:
            stype = getdata(productDir)
            name = getname(productDir)
            db["asinCode"] = productDir
            db["linkRoot"] = link
            db["name"] = name
            db["stype"] = stype
            # response = jsonify({"data" : data})
            return {"response": db}

    @app.route("/get_price_codeasin", methods=['POST'])
    def get_price_codeasin():
        response = []
        dem = 0
        vit = ""
        url = request.data.get('data', '')
        for i in url:
            codeasin = i["codeasin"]
            price_old = i["price"]
            vit = homnay(codeasin)
            if vit == "ok":
                data1 = getdata_codeasin(codeasin, price_old, dem)
                response.append(data1)
                return {"data": response}
            else:
                data1 = getdata_codeasin(codeasin, price_old, dem)
                response.append(data1)
            dem = dem + 1
        return {"data": response}

    @app.route("/stype", methods=['POST'])
    def getstpe():
        global data
        data = {}
        url = str(request.data.get('link_ref', ''))
        # link = zip_code(url)
        productDir = getAsin(url)
        codeHTML = CodeHTML(url)
        html = codeHTML.getPage()
        stype = getstype(productDir)
        return stype
    if __name__ == '__main__':
        app.run(debug=True, host="0.0.0.0", port="5000")


main()
