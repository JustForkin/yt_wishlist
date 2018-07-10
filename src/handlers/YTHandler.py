import json
import utils
import traceback

from datetime import datetime
from flask import abort
from handlers import get_request_json_args
from models.DLItem import DLItem
from sqlalchemy import exc

class YTHandler(object):
    @staticmethod
    def parse_args(request, app, db, logWorker):
        req = _Request()

        if request.method == 'POST':
            args = get_request_json_args(request)
        else:
            args = request.args

        req.app = app
        req.db = db
        req.logWorker = logWorker
        req.url = args.get('url')
        return req

    @staticmethod
    def download(req):
        # check if url is valid
        # check if duplicated, if true, start again or return cached one?

        # create ticket
        title, thumbUrl, duration = YTHandler._get_meta_data(req)
        reqId = YTHandler._add_dl_item(req)
        if reqId is None:
            abort(500)

        # add to queue
        req.ticketId = reqId
        req.logWorker.addTask(YTHandler._download_ytdl_p, (req,), None)

        result = {'reqId': reqId,
                  'url': req.url,
                  'title': title,
                  'thumbnail_url': thumbUrl,
                  'duration': duration}

        return json.dumps(result)

    @staticmethod
    def list_downloads(req, reqId=None):
        items = YTHandler._list_dl_items(req, reqId)
        return json.dumps([item.to_dict() for item in items])

    @staticmethod
    def _download_impl(req):
        # run in another process and report progress
        progress = 0
        for _i in range(10):
            import time
            time.sleep(0.5)
            progress += 10

            YTHandler._on_progress(req, progress)
        YTHandler._on_finished(req, 'path_is_here')

    @staticmethod
    def _get_meta_data(req):
        cmd = ['./youtube-dl', req.url, '--get-title', '--get-thumbnail', '--get-duration']
        results = utils.check_output(cmd)
        if len(results) != 3:
            print('fail to get meta data: ' + str(results))

        title, thumbUrl, duration = results
        return title, thumbUrl, duration

    @staticmethod
    def _download_ytdl(url):
        import subprocess
        print("Starting download of " + url)
        subprocess.run(["youtube-dl", "-o", "./youtube-dl/.incomplete/%(title)s.%(ext)s", "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]", "--exec", "touch {} && mv {} ./youtube-dl/", "--merge-output-format", "mp4", url])
        print("Finished downloading " + url)

    @staticmethod
    def _download_ytdl_p(req):
        from subprocess import Popen, PIPE, CalledProcessError

        f_name = '{0}.mp4'.format(req.ticketId)
        cmd = ["./youtube-dl", "-o", ".incomplete/%(title)s.%(ext)s",
                "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
                "--exec", "touch {} && mv {} .complete/" + f_name, "--merge-output-format", "mp4",
                req.url, '--newline']

        with Popen(cmd, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
            for line in p.stdout:
                # print(line, end='') # process line here
                if '[download]' not in line or 'ETA' not in line:
                    continue

                try:
                    l = line.strip('[download]')
                    progress, r = l.split('of')
                    total_size, r = r.split('at')
                    speed, eta = r.split('ETA')

                    print('Get progress {0} for size {1} at {2} with ETA {3}'.format(progress, total_size, speed, eta))
                    YTHandler._on_progress(req, YTHandler._convert_progress_text(progress))
                except:
                    pass

            YTHandler._on_finished(req, f_name)

        if p.returncode != 0:
            raise CalledProcessError(p.returncode, p.args)

    @staticmethod
    def _convert_progress_text(t):
        return float(t.strip().strip('%'))

    @staticmethod
    def _on_progress(req, progress):
        newDLItem = DLItem(progress=progress).to_dict()
        print('progress: {0}'.format(progress))
        return YTHandler._update_dl_item(req, newDLItem)

    @staticmethod
    def _on_finished(req, path):
        newDLItem = DLItem(progress=100,
                           path=path).to_dict()
        print('finished, saved in {0}'.format(path))
        return YTHandler._update_dl_item(req, newDLItem)

    @staticmethod
    def _add_dl_item(req):
        '''
            add a DLItem in database and return its id (primary key)
        '''
        entry = DLItem(utc_time=datetime.utcnow(),
                    url=req.url,
                    status='started',
                    progress=0)
        saved = utils.write_to_db(req.app, req.db, [entry])
        if saved is None or len(saved) == 0:
            return
        return saved[0]['id']

    @staticmethod
    def _update_dl_item(req, newDLItem):
        ''' update a existing user in the database '''
        status = newDLItem.get('status')
        progress = newDLItem.get('progress')
        path = newDLItem.get('path')
        try:
            query = req.db.session.query(DLItem).filter_by(id=req.ticketId)

            # query and commit
            item = query.first()
            if item is None:
                return

            if status is not None:
                item.status = status
            if progress is not None:
                item.progress = progress
            if path is not None:
                item.path = path

            updateResult = item.to_dict()
            req.db.session.commit()
            return updateResult

        except exc.SQLAlchemyError:
            traceback.print_exc()

    @staticmethod
    def _list_dl_items(req, reqId=None):
        '''
        list all DLItems in database
        '''
        try:
            query = None
            if reqId:
                query = (req.db.session.query(DLItem)
                         .filter_by(id=reqId)
                         )
            else:
                query = req.db.session.query(DLItem)

            return query.order_by(DLItem.utc_time.desc()).limit(20).all()

        except exc.SQLAlchemyError:
            traceback.print_exc()
            abort(500)

class _Request(object):
    pass

if __name__ == '__main__':
    import os
    os.chdir('..')
    print(os.getcwd())
    url = 'https://www.youtube.com/watch?v=7CVtTOpgSyY'
    YTHandler._download_ytdl(url)
