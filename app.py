from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from datetime import timedelta

app = Flask(__name__)
from koutu import *

app.register_blueprint(index_koutu)

from yanzhi import *

app.register_blueprint(index_yanzhi)

from meiyan import *

app.register_blueprint(index_meiyan)

from zhengjianzhao import *

app.register_blueprint(index_zhengjianzhao)
from ocr import *

app.register_blueprint(index_ocr)

from poetry import *

app.register_blueprint(index_poetry)



Bootstrap(app)

app.send_file_max_age_default = timedelta(seconds=1)


@app.route('/', methods=['POST', 'GET'])  
def index():
    return render_template('koutu.html')


@app.route('/error', methods=['POST', 'GET'])  
def error():
    return render_template('404.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
