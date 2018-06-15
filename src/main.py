import sys
sys.path.append('src')

import i18n
import utils

# i18n.setup_get_text(utils.get_absolute_path(__file__, 'src'),
#                     utils.get_absolute_path(__file__, 'res/lang'),
#                     'bot',
#                     'zh_TW')

from flask import Flask, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from handlers.YTHandler import YTHandler
from jinja2 import FileSystemLoader

DIRECTORY_WEBSITE_ALIS = 'alis-website'

app = Flask(__name__)
db = None
logWorker = None

@app.before_first_request
def setup():
    init_database(app)

    global logWorker
    logWorker = utils.TaskExecutor()

    init_jinja()

def init_database(app):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     app.config['SQLALCHEMY_DATABASE_URI'] = rc.get_sqlalchemy_database_uri('config/db.ini', server)
    global db
    db = SQLAlchemy(app)

    # create all tables if not exist
    # classes must be included and declared before create_all()
    from models.Base import Base
    Base.metadata.create_all(bind=db.engine)

def init_jinja():
    app.jinja_loader = FileSystemLoader([DIRECTORY_WEBSITE_ALIS])
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

@app.route('/')
def index():
    return send_from_directory(DIRECTORY_WEBSITE_ALIS, 'index.html')

@app.route('/<path:path>')
def send_main(path):
    return send_from_directory(DIRECTORY_WEBSITE_ALIS, path)

@app.route('/download', methods=['GET', 'POST'])
def start_download():
    req = YTHandler.parse_args(request, app, db, logWorker)
    return YTHandler.start_download(req)

@app.after_request
def add_header(r):
    r.headers['Access-Control-Allow-Origin'] = '*'
    r.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS, PUT, DELETE'
    r.headers['Access-Control-Allow-Headers'] = ','.join(['Content-Type'])
    # set no cache policy for confidential data
    r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    r.headers['Pragma'] = 'no-cache'
    return r

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True, port=5002)
