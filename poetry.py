# coding:utf-8
# author: Livingbody
# date: 2020.05.06
import ssl
import json
from urllib.request import urlopen
from urllib.request import Request

# from flask import Flask, render_template, request, jsonify
from flask import Flask, render_template, request, jsonify
import requests
from flask import Blueprint, render_template

index_poetry = Blueprint("poetry", __name__)


# 上传并抠图
@index_poetry.route('/poetry', methods=['POST', 'GET'])  # 添加路由
def mypoetry():
    print(50 * '*')
    if request.method == 'POST':
        print('post')
        try:
            print('sentence')
            sentence = request.form.get('poetry')
            print(sentence)
            print('sentence')
            print(50 * '*')
            results = poetry_fun(sentence=sentence)
            return render_template('poetry_ok.html', results=results)
        except Exception as e:
            print(e)
            return render_template('404.html')
    return render_template('poetry.html')


def poetry_fun(sentence):
    data = {'texts': [sentence],
            'use_gpu': False, 'beam_width': 20}
    headers = {"Content-type": "application/json"}
    url = "http://127.0.0.1:8866/predict/ernie_gen_couplet"

    requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
    s = requests.session()
    s.keep_alive = False
    results = requests.post(url=url, headers=headers, data=json.dumps(data))

    # 保存结果
    results = results.json()["results"]
    print(results)
    for result in results:
        print(result)
    return results[0]
