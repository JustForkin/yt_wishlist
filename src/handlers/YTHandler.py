import json

from handlers import get_request_json_args

class YTHandler(object):
    @staticmethod
    def parse_args(request, app, db, logWorker):
        req = Request()

        if request.method == 'POST':
            args = get_request_json_args(request)
        else:
            args = request.args

        req.app = app
        req.db = db
        req.logWorker = logWorker
        return req

    @staticmethod
    def start_download(req):
        return json.dumps({})

class Request(object):
    pass
