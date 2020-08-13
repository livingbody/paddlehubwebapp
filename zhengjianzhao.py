# coding:utf-8
# author: Livingbody
# date: 2020.05.06

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import requests
import base64
import time
from flask import Blueprint, render_template
import numpy as np
import cv2
import json
from PIL import Image, ImageDraw, ImageFont
import math

index_zhengjianzhao = Blueprint("zhengjianzhao", __name__)
# 设置允许的文件格式
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'bmp', 'jpeg'])
# 当前文件所在路径
basepath = os.path.dirname(__file__)


def allowed_file(filename):
    filename = filename.lower()
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# 上传并抠图
@index_zhengjianzhao.route('/zhengjianzhao', methods=['POST', 'GET'])  # 添加路由
def zhengjianzhao():
    if request.method == 'POST':
        try:
            f = request.files['file']
            if not (f and allowed_file(f.filename)):
                # return jsonify({"error": 1001, "msg": "请检查上传的图片类型，仅限于png、PNG、jpg、JPG、bmp"})
                return render_template('404.html')
            sourcefile = os.path.join('static/images/source', secure_filename(f.filename))
            upload_path = os.path.join(basepath, sourcefile)  # 注意：没有的文件夹一定要先创建，不然会提示没有该路径
            f.save(upload_path)

            selected_color = request.form.get('selected_color')
            print(selected_color)
            filename = convert(upload_path)
            change_color_imgfile = change_back_groundcolor(filename, selected_color)
            filename = os.path.join('static/images/target', change_color_imgfile)

            print(filename)
            return render_template('zhengjianzhao_ok.html', val1=time.time(), sourcefile=sourcefile, filename=filename)
        except Exception:
            return render_template('404.html')
    return render_template('zhengjianzhao.html')


# 去除背景色
def convert(upload_path):
    file_list = [upload_path]
    files = [("image", (open(item, "rb"))) for item in file_list]
    # 指定图片分割方法为deeplabv3p_xception65_humanseg并发送post请求
    url = "http://127.0.0.1:8866/predict/image/deeplabv3p_xception65_humanseg"
    r = requests.post(url=url, files=files)
    t = time.time()
    filename = str(t) + '.jpg'
    results = eval(r.json()["results"])
    for item in results:
        mypath = os.path.join(basepath, 'static/images/target', filename)
        with open(mypath, "wb") as fp:
            fp.write(base64.b64decode(item["base64"].split(',')[-1]))
            item.pop("base64")
    return filename


# 更换背景
def change_back_groundcolor(filename, background_color):
    if isinstance(background_color, str):
        if background_color == '1':
            color = [255, 0, 0, 1]
        elif background_color == '2':
            color = [67, 142, 219, 1]
        elif background_color == '3':
            color = [255, 255, 255, 1]
        else:
            raise Exception('背景色设置有误')
    elif isinstance(background_color, list) or isinstance(background_color, tuple):
        color = [background_color[0], background_color[1], background_color[2], 1]
    else:
        raise Exception('背景色设置有误')
    base_img_filename = os.path.join(basepath, 'static/images/target', filename)
    new_img_filename = 'color' + filename
    new_img_path = os.path.join(basepath, 'static/images/target', new_img_filename)
    print(new_img_filename)
    base_img = Image.open(base_img_filename)
    img = np.array(base_img)
    for i in range(0, img.shape[0]):
        for j in range(0, img.shape[1]):
            if img[i][j][3] < 1:
                img[i][j] = color

    im = Image.fromarray(img)
    im = im.convert('RGB')
    im.save(new_img_path)

    print('证件照已生成，已保存到' + new_img_path)
    return new_img_filename


def bilinear_insert(image, new_x, new_y):
    """
    双线性插值法
    """
    w, h, c = image.shape
    if c == 3:
        x1 = int(new_x)
        x2 = x1 + 1
        y1 = int(new_y)
        y2 = y1 + 1
        part1 = image[y1, x1].astype(np.float) * (float(x2) - new_x) * (float(y2) - new_y)
        part2 = image[y1, x2].astype(np.float) * (new_x - float(x1)) * (float(y2) - new_y)
        part3 = image[y2, x1].astype(np.float) * (float(x2) - new_x) * (new_y - float(y1))
        part4 = image[y2, x2].astype(np.float) * (new_x - float(x1)) * (new_y - float(y1))

        insertValue = part1 + part2 + part3 + part4
        return insertValue.astype(np.int8)
