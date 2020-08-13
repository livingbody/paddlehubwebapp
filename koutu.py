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

index_koutu = Blueprint("koutu", __name__)
# 设置允许的文件格式
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'bmp', 'jpeg'])
# 当前文件所在路径
basepath = os.path.dirname(__file__)


def allowed_file(filename):
    filename = filename.lower()
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# 上传并抠图
@index_koutu.route('/koutu', methods=['POST', 'GET'])  # 添加路由
def upload():
    if request.method == 'POST':
        try:
            f = request.files['file']
            if not (f and allowed_file(f.filename)):
                # return jsonify({"error": 1001, "msg": "请检查上传的图片类型，仅限于png、PNG、jpg、JPG、bmp"})
                return render_template('404.html')
            sourcefile = os.path.join('static/images/source', secure_filename(f.filename))
            upload_path = os.path.join(basepath, sourcefile)  # 注意：没有的文件夹一定要先创建，不然会提示没有该路径
            f.save(upload_path)
            filename = convert(upload_path)
            filename = os.path.join('static/images/target', filename)
            print(filename)
            return render_template('koutu_ok.html', val1=time.time(), sourcefile=sourcefile, filename=filename)
        except Exception:
            return render_template('404.html')
    return render_template('koutu.html')


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
