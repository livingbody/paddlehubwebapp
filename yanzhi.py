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

ssl._create_default_https_context = ssl._create_unverified_context
API_KEY = 'eMgcu4RUSI4Vfo0nLR5OYaXU'
SECRET_KEY = 'kc2oB7wWKF88nNhXx4p9WRnRRzVlyYCM'
FACE_DETECT = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
"""  TOKEN start """
TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import requests
import base64
import time
from flask import Blueprint, render_template

index_yanzhi = Blueprint("yanzhi", __name__)
# 设置允许的文件格式
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'bmp', 'jpeg'])
# 当前文件所在路径
basepath = os.path.dirname(__file__)


def allowed_file(filename):
    filename = filename.lower()
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# 上传并抠图
@index_yanzhi.route('/yanzhi', methods=['POST', 'GET'])  # 添加路由
def myyanzhi():
    if request.method == 'POST':
        try:
            f = request.files['file']
            if not (f and allowed_file(f.filename)):
                return render_template('404.html')
            sourcefile = os.path.join('static/images/source', secure_filename(f.filename))
            upload_path = os.path.join(basepath, sourcefile)  # 注意：没有的文件夹一定要先创建，不然会提示没有该路径
            f.save(upload_path)
            filename = yanzhi_fun(upload_path)
            filename = os.path.join('static/images/target', secure_filename(filename))
            print(filename)
            return render_template('yanzhi_ok.html', val1=time.time(), sourcefile=sourcefile, filename=filename)
        except:
            return render_template('404.html')
    return render_template('yanzhi.html')


def yanzhi_fun(filename):
    token = fetch_token()
    # concat url
    url = FACE_DETECT + "?access_token=" + token
    file_content = read_file(filename)
    response = myrequest(url, urlencode(
        {
            'image': base64.b64encode(file_content),
            'image_type': 'BASE64',
            'face_field': 'gender,age,beauty,glasses',
            'max_face_num': 10
        }))
    data = json.loads(response)
    img = cv2.imread(filename)
    temp_img = img.copy()
    result = data['result']
    face_num = result['face_num']
    targetfilename = 'yanzhi' + str(time.time()) + os.path.splitext(filename)[-1]
    real_targetfilename = os.path.join(basepath, 'static/images/target', targetfilename)
    print(targetfilename + 50 * '*')

    if face_num > 0:
        face_list = result['face_list']
        for i in range(face_num):
            temp_face = face_list[i]
            temp_face_location = temp_face['location']
            left = int(temp_face_location['left'])
            top = int(temp_face_location['top'])
            width = int(temp_face_location['width'])
            height = int(temp_face_location['height'])

            if face_list[i]["gender"]["type"] == "male":
                gender = "男"
                # female face
            if face_list[i]["gender"]["type"] == "female":
                gender = "女"
            beauty = face_list[i]["beauty"]
            simple_info = " 年龄: " + str(face_list[i]["age"]) + "   颜值：" + str(beauty)
            cv2.rectangle(temp_img, (left, top), (left + width, top + height), (0, 255, 0), 1)
            temp_img = cv2ImgAddText(temp_img, simple_info, left, top)
        cv2.imwrite(real_targetfilename, temp_img, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
    return targetfilename


def cv2_to_base64(image):
    data = cv2.imencode('.jpg', image)[1]
    return base64.b64encode(data.tostring()).decode('utf8')


def myrequest(url, data):
    req = Request(url, data.encode('utf-8'))
    has_error = False
    try:
        f = urlopen(req)
        result_str = f.read()
        result_str = result_str.decode()
        return result_str
    except URLError as err:
        print(err)


def cv2ImgAddText(img, text, left, top, textColor=(0, 255, 0), textSize=20):
    if (isinstance(img, numpy.ndarray)):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(img)
    # 字体的格式
    fontStyle = ImageFont.truetype(
        "Alibaba-PuHuiTi-Regular.ttf", textSize, encoding="utf-8")
    # 绘制文本
    draw.text((left, top), text, textColor, font=fontStyle)
    # 转换回OpenCV格式
    return cv2.cvtColor(numpy.asarray(img), cv2.COLOR_RGB2BGR)


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


def fetch_token():
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req, timeout=5)
        result_str = f.read()
    except URLError as err:
        print('url error:' + 50 * '*')
        print(err)
    result_str = result_str.decode()

    result = json.loads(result_str)

    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not 'brain_all_scope' in result['scope'].split(' '):
            print('please ensure has check the  ability')
            exit()
        return result['access_token']
    else:
        print('please overwrite the correct API_KEY and SECRET_KEY')
        exit()
