# PaddleHub  web抠图服务
## step1. 启动flask服务
```python
python app.py
```
## step2. 启动PaddleHub 一键部署deeplabv3p_xception65_humanseg服务
```python
set CUDA_VISIBLE_DEVICES=0
hub serving start -m deeplabv3p_xception65_humanseg
hub serving start --config config.json
```
## step3. 打开浏览器体验web 抠图服务
```python
http://localhost
```

## step4. 添加证件照更换背景服务
```python
2020.5.5 20：00
http://localhost/zhegnjianzhao
添加证件照功能
```
## step5. 修复菜单自适应
```python
2020.5.5 20：00
```
## step6. 依赖
```python
1.PaddlePaddle(飞桨)
2.PaddleHub
3.Flask
```
## step7. 增加颜值计算

## step8. 增加OCR
### flask bootstrap支持
```.bash
pip install flask_bootstrap
```

### flask blueprint
```.env
pip install flask-blueprint
```

###  cpu 模式下run
```.bash
hub serving start --config cpuconfig.json &
python app.py &
```
###  gpu 模式下run
```.bash
set CUDA_VISIBLE_DEVICES=0
hub serving start --config config.json
python app.py
```

![Image text](20200508002203939.png)
![Image text](20200508002228512.png)
![Image text](20200508002325959.png)

## step 9. 增加进程监控

> https://github.com/livingbody/fangtanginuse

### ![Image text](20201217140937684.jpg)

![](20201217140937702.jpg)

