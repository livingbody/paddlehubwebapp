# coding:utf-8
# author: Livingbody
# date: 2020.05.06
import ssl
import json
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode
import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy

import sys
import base64

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import requests
import base64
import time
from flask import Blueprint, render_template

index_ocr = Blueprint("ocr", __name__)
# 设置允许的文件格式
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'bmp', 'jpeg'])
# 当前文件所在路径
basepath = os.path.dirname(__file__)


def read_file(image_path):
    f = None
    try:
        f = open(image_path, 'rb')
        return f.read()
    except:
        print('read image file fail')
        return None
    finally:
        if f:
            f.close()


def allowed_file(filename):
    filename = filename.lower()
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# 上传并抠图
@index_ocr.route('/ocr', methods=['POST', 'GET'])  # 添加路由
def myocr():
    if request.method == 'POST':
        try:
            f = request.files['file']
            if not (f and allowed_file(f.filename)):
                return render_template('404.html')
            sourcefile = os.path.join('static/images/source', secure_filename(f.filename))
            upload_path = os.path.join(basepath, sourcefile)  # 注意：没有的文件夹一定要先创建，不然会提示没有该路径
            f.save(upload_path)
            ocr_content = ocr_fun(upload_path)
            print("sourcefile: " + sourcefile)
            for item in ocr_content:
                print(item)
            return render_template('ocr_ok.html', sourcefile=sourcefile, ocr_content=ocr_content)
        except Exception as e:
            print(e)
            return render_template('404.html')
    return render_template('ocr.html')


def ocr_fun(filename):
    # get access
    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=idGjUibmqyqzVGcWF4bhlHLA&client_secret=GiKSXEmTw2DFp0ZiFsmuSYPxwCctiBmg'
    response = requests.get(host)
    token = response.json()['access_token']
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
    # 二进制方式打开图片文件
    f = open(filename, 'rb')
    img = base64.b64encode(f.read())

    params = {"image": img,
              "language_type": 'CHN_ENG',
              "detect_direction": "true",
              "paragraph": "true"}
    access_token = token
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    words_result = response.json()['words_result']
    orc_content = []
    for words in words_result:
        orc_content.append(words['words'])
    return orc_content
