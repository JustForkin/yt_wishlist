import json
import utils
import traceback
import youtube_dl

from datetime import datetime
from flask import abort
from handlers import get_request_json_args
from models.DLItem import DLItem
from os.path import splitext
from sqlalchemy import exc

class YTHandler(object):
    @staticmethod
    def parse_args(request, app, db, logWorker, ydl):
        req = _Request()

        if request.method == 'POST':
            args = get_request_json_args(request)
        else:
            args = request.args

        req.app = app
        req.db = db
        req.logWorker = logWorker
        req.url = args.get('url')
        req.ydl = None
        req.video_ext = ''
        return req

    @staticmethod
    def download(req):
        # TODO: use get_meta API to check if url is valid

        # check if there is already a result
        dlItem = YTHandler._list_dl_item(req, req.url)
        if dlItem is not None:
            return json.dumps([dlItem.to_dict()])

        # create ticket
        title, thumbUrl, duration = YTHandler._download_meta_impl_ydl(req)
        dlItemDict = YTHandler._add_dl_item(req, title, thumbUrl, duration)
        if dlItemDict is None:
            abort(500)

        # add to queue
        req.ticketId = dlItemDict['id']
        req.logWorker.addTask(YTHandler._download_file_impl_ydl, (req,), None)

        return json.dumps([dlItemDict])

    @staticmethod
    def list_downloads(req, reqId=None):
        items = YTHandler._list_dl_items(req, reqId)
        return json.dumps([item.to_dict() for item in items])

    @staticmethod
    def _download_meta_impl_ydl(req):
        ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})

        with ydl:
            result = ydl.extract_info(
                req.url,
                download=False # We just want to extract the info
            )

        if 'entries' in result:
            # Can be a playlist or a list of videos
            video = result['entries'][0]
        else:
            # Just a video
            video = result

        return video.get('title', ''), video.get('thumbnail', ''), video.get('duration', '')

    @staticmethod
    def _download_file_impl_ydl(req):
        # WORKAROUND: I guess the video output extension
        # is the same as the converted file
        def my_hook(d):
            print(d)
            if d['status'] == 'downloading':
                if req.video_ext == '':
                    req.video_ext = splitext(d['filename'])[1]
                print('Downloading: ' + d['_percent_str'])
                YTHandler._on_progress(req, YTHandler._convert_progress_text(d['_percent_str']))
            elif d['status'] == 'finished':
                print('Done downloading, now converting ...')

        ydl_opts = {
            'outtmpl': '.complete/' + str(req.ticketId) + '.%(ext)s',
            'progress_hooks': [my_hook],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([req.url])

        f_name = '{0}{1}'.format(req.ticketId, req.video_ext)
        YTHandler._on_finished(req, f_name)

    @staticmethod
    def _convert_progress_text(t):
        return float(t.strip().strip('%'))

    @staticmethod
    def _on_progress(req, progress):
        newDLItem = DLItem(status=Status.DOWNLOADING, progress=progress).to_dict()
        print('progress: {0}'.format(progress))
        return YTHandler._update_dl_item(req, newDLItem)

    @staticmethod
    def _on_finished(req, path):
        newDLItem = DLItem(status=Status.FINISHED,
                           progress=100,
                           path=path).to_dict()
        print('finished, saved in {0}'.format(path))
        return YTHandler._update_dl_item(req, newDLItem)

    @staticmethod
    def _add_dl_item(req, title, thumbUrl, duration):
        '''
            add a DLItem in database and return its id (primary key)
        '''
        entry = DLItem(utc_time=datetime.utcnow(),
                    url=req.url,
                    title=title,
                    thumb_url=thumbUrl,
                    duration=duration,
                    status=Status.PENDING,
                    progress=0)
        saved = utils.write_to_db(req.app, req.db, [entry])
        if saved is None or len(saved) == 0:
            return
        return saved[0]

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

    @staticmethod
    def _list_dl_item(req, url):
        try:
            return req.db.session.query(DLItem).filter_by(url=url).first()
        except exc.SQLAlchemyError:
            traceback.print_exc()
            abort(500)

class _Request(object):
    pass

class Status(object):
    PENDING = 'pending'
    DOWNLOADING = 'downloading'
    FINISHED = 'finished'
    FAILED = 'failed'
