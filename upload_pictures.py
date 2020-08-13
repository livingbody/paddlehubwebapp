# coding:utf-8
# author: Livingbody
# date: 2020.05.06
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import requests
import math
import numpy as np
import ssl
import json
import base64
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode
import cv2
import time
from PIL import Image, ImageDraw, ImageFont
import numpy
from datetime import timedelta

ssl._create_default_https_context = ssl._create_unverified_context
API_KEY = 'eMgcu4RUSI4Vfo0nLR5OYaXU'
SECRET_KEY = 'kc2oB7wWKF88nNhXx4p9WRnRRzVlyYCM'
FACE_DETECT = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
"""  TOKEN start """
TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'

# 设置允许的文件格式
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'bmp', 'jpeg'])


def allowed_file(filename):
    filename = filename.lower()
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


app = Flask(__name__)
# 设置静态文件缓存过期时间
app.send_file_max_age_default = timedelta(seconds=1)
# 当前文件所在路径
basepath = os.path.dirname(__file__)


# 首页
@app.route('/', methods=['POST', 'GET'])  # 添加路由
def index():
    return render_template('upload.html')


@app.route('/error', methods=['POST', 'GET'])  # 添加路由
def error():
    return render_template('404.html')


# 颜值
@app.route('/yanzhi', methods=['POST', 'GET'])  # 添加路由
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
            print(filename)
            return render_template('yanzhi_ok.html', val1=time.time(), sourcefile=sourcefile, filename=filename)
        except:
            return render_template('404.html')
    return render_template('yanzhi.html')


# 上传并抠图
@app.route('/upload', methods=['POST', 'GET'])  # 添加路由
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
            return render_template('upload_ok.html', val1=time.time(), sourcefile=sourcefile, filename=filename)
        except Exception:
            return render_template('404.html')
    return render_template('upload.html')


# 上传更换背景色
@app.route('/zhengjianzhao', methods=['POST', 'GET'])  # 添加路由
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


# 美颜服务
@app.route('/meiyan', methods=['POST', 'GET'])  # 添加路由
def meiyan():
    if request.method == 'POST':
        try:
            f = request.files['file']
            if not (f and allowed_file(f.filename)):
                return render_template('404.html')
            t = time.time()
            dst_filename = str(t) + '.' + f.filename.split('.')[-1]
            new_img_filename = 'meiyan' + dst_filename
            sourcefile = os.path.join('static/images/source', new_img_filename)
            sourcefilepath = os.path.join('static/images/source', new_img_filename)
            sourcefilepath = os.path.join(basepath, sourcefile)
            f.save(sourcefilepath)
            selected_meiyan = request.form.get('selected_meiyan')
            meiyan_imgfile = meiyan_fun(sourcefilepath, selected_meiyan)
            filename = os.path.join('static/images/target', meiyan_imgfile)
            return render_template('meiyan_ok.html', val1=time.time(), sourcefile=sourcefile, filename=filename)
        except Exception:
            return render_template('404.html')
    return render_template('meiyan.html')


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
    targetfilename = 'yanzhi' + str(time.time()) + os.path.split(filename)[-1]
    targetfilename = os.path.join(basepath, 'static/images/target', targetfilename)
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
        cv2.imwrite(targetfilename, temp_img, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
    return targetfilename


def cv2_to_base64(image):
    data = cv2.imencode('.jpg', image)[1]
    return base64.b64encode(data.tostring()).decode('utf8')


# 美颜
def meiyan_fun(filename, selected_meiyan):
    source_img_path = filename
    t = time.time()
    dst_filename = str(t) + '.' + source_img_path.split('.')[-1]
    new_img_filename = 'meiyan' + dst_filename
    new_img_path = os.path.join(basepath, 'static/images/target', new_img_filename)
    src_img = cv2.imread(source_img_path)
    url = "http://127.0.0.1:8866/predict/face_landmark_localization"
    data = {'images': [cv2_to_base64(cv2.imread(source_img_path))]}
    headers = {"Content-type": "application/json"}
    r = requests.post(url=url, headers=headers, data=json.dumps(data))
    # 打印预测结果
    result = r.json()["results"]
    data = result[0]['data'][0]
    face_landmark = np.array(data, dtype='int')
    if isinstance(selected_meiyan, str):
        # 瘦脸
        if selected_meiyan == '4':
            src_img = thin_face(src_img, face_landmark)
            cv2.imwrite(new_img_path, src_img)
        # 美白
        elif selected_meiyan == '2':
            src_img = whitening(src_img, face_landmark)
            cv2.imwrite(new_img_path, src_img)
        # 在瘦脸的基础上，继续放大双眼
        elif selected_meiyan == '3':
            enlarge_eyes(src_img, face_landmark, radius=13, strength=13)
            cv2.imwrite(new_img_path, src_img)
        # 全套
        elif selected_meiyan == '1':
            src_img = whitening(src_img, face_landmark)
            # cv2.imwrite(new_img_path, src_img)
            enlarge_eyes(src_img, face_landmark, radius=13, strength=13)
            cv2.imwrite(new_img_path, src_img)
        else:
            raise Exception('选择设置有误')
    else:
        raise Exception('设置有误')
    print('美颜照已生成，已保存到' + new_img_path)
    return new_img_filename


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


def local_traslation_warp(image, start_point, end_point, radius):
    """
    局部平移算法
    """
    radius_square = math.pow(radius, 2)
    image_cp = image.copy()

    dist_se = math.pow(np.linalg.norm(end_point - start_point), 2)
    height, width, channel = image.shape
    for i in range(width):
        for j in range(height):
            # 计算该点是否在形变圆的范围之内
            # 优化，第一步，直接判断是会在（start_point[0], start_point[1])的矩阵框中
            if math.fabs(i - start_point[0]) > radius and math.fabs(j - start_point[1]) > radius:
                continue

            distance = (i - start_point[0]) * (i - start_point[0]) + (j - start_point[1]) * (j - start_point[1])

            if (distance < radius_square):
                # 计算出（i,j）坐标的原坐标
                # 计算公式中右边平方号里的部分
                ratio = (radius_square - distance) / (radius_square - distance + dist_se)
                ratio = ratio * ratio

                # 映射原位置
                new_x = i - ratio * (end_point[0] - start_point[0])
                new_y = j - ratio * (end_point[1] - start_point[1])

                new_x = new_x if new_x >= 0 else 0
                new_x = new_x if new_x < height - 1 else height - 2
                new_y = new_y if new_y >= 0 else 0
                new_y = new_y if new_y < width - 1 else width - 2

                # 根据双线性插值法得到new_x, new_y的值
                image_cp[j, i] = bilinear_insert(image, new_x, new_y)

    return image_cp


def thin_face(image, face_landmark):
    """
    实现自动人像瘦脸
    image： 人像图片
    face_landmark: 人脸关键点
    """
    end_point = face_landmark[30]

    # 瘦左脸，3号点到5号点的距离作为瘦脸距离
    dist_left = np.linalg.norm(face_landmark[3] - face_landmark[5])
    local_traslation_warp(image, face_landmark[3], end_point, dist_left)

    # 瘦右脸，13号点到15号点的距离作为瘦脸距离
    dist_right = np.linalg.norm(face_landmark[13] - face_landmark[15])
    image = local_traslation_warp(image, face_landmark[13], end_point, dist_right)
    return image


def enlarge_eyes(image, face_landmark, radius=15, strength=10):
    """
    放大眼睛
    image： 人像图片
    face_landmark: 人脸关键点
    radius: 眼睛放大范围半径
    strength：眼睛放大程度
    """
    # 以左眼最低点和最高点之间的中点为圆心
    left_eye_top = face_landmark[37]
    left_eye_bottom = face_landmark[41]
    left_eye_center = (left_eye_top + left_eye_bottom) / 2
    # 以右眼最低点和最高点之间的中点为圆心
    right_eye_top = face_landmark[43]
    right_eye_bottom = face_landmark[47]
    right_eye_center = (right_eye_top + right_eye_bottom) / 2

    # 放大双眼
    local_zoom_warp(image, left_eye_center, radius=radius, strength=strength)
    local_zoom_warp(image, right_eye_center, radius=radius, strength=strength)


def local_zoom_warp(image, point, radius, strength):
    """
    图像局部缩放算法
    """
    height = image.shape[0]
    width = image.shape[1]
    left = int(point[0] - radius) if point[0] - radius >= 0 else 0
    top = int(point[1] - radius) if point[1] - radius >= 0 else 0
    right = int(point[0] + radius) if point[0] + radius < width else width - 1
    bottom = int(point[1] + radius) if point[1] + radius < height else height - 1

    radius_square = math.pow(radius, 2)
    for y in range(top, bottom):
        offset_y = y - point[1]
        for x in range(left, right):
            offset_x = x - point[0]
            dist_xy = offset_x * offset_x + offset_y * offset_y

            if dist_xy <= radius_square:
                scale = 1 - dist_xy / radius_square
                scale = 1 - strength / 100 * scale
                new_x = offset_x * scale + point[0]
                new_y = offset_y * scale + point[1]
                new_x = new_x if new_x >= 0 else 0
                new_x = new_x if new_x < height - 1 else height - 2
                new_y = new_y if new_y >= 0 else 0
                new_y = new_y if new_y < width - 1 else width - 2

                image[y, x] = bilinear_insert(image, new_x, new_y)


def whitening(img, face_landmark):
    """
    美白
    """
    # 简单估计额头所在区域
    # 根据0号、16号点画出额头(以0号、16号点所在线段为直径的半圆)
    radius = (np.linalg.norm(face_landmark[0] - face_landmark[16]) / 2).astype('int32')
    center_abs = tuple(((face_landmark[0] + face_landmark[16]) / 2).astype('int32'))
    angle = np.degrees(np.arctan((lambda l: l[1] / l[0])(face_landmark[16] - face_landmark[0]))).astype('int32')
    face = np.zeros_like(img)
    cv2.ellipse(face, center_abs, (radius, radius), angle, 180, 360, (255, 255, 255), 2)

    points = face_landmark[0:17]
    hull = cv2.convexHull(points)
    cv2.polylines(face, [hull], True, (255, 255, 255), 2)

    index = face > 0
    face[index] = img[index]
    dst = np.zeros_like(face)
    # v1:磨皮程度
    v1 = 9
    # v2: 细节程度
    v2 = 2

    tmp1 = cv2.bilateralFilter(face, v1 * 5, v1 * 12.5, v1 * 12.5)
    tmp1 = cv2.subtract(tmp1, face)
    tmp1 = cv2.add(tmp1, (10, 10, 10, 128))
    tmp1 = cv2.GaussianBlur(tmp1, (2 * v2 - 1, 2 * v2 - 1), 0)
    tmp1 = cv2.add(img, tmp1)
    dst = cv2.addWeighted(img, 0.1, tmp1, 0.9, 0.0)
    dst = cv2.add(dst, (10, 10, 10, 255))

    index = dst > 0
    img[index] = dst[index]

    return img


if __name__ == '__main__':
    # app.debug = True
    app.run(host='0.0.0.0', port=8080, debug=False)
