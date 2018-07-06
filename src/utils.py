import codecs
import json
import requests
import traceback

from os import getenv
from os.path import dirname, realpath, join
from queue import Queue
from sqlalchemy import exc
from subprocess import Popen, PIPE, CalledProcessError
from threading import Thread

# connection & read timeout
# see: https://stackoverflow.com/questions/21965484/timeout-for-python-requests-get-entire-response
TIMEOUT = 10

def check_output(cmd):
    with Popen(cmd, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
        results = [line for line in p.stdout]
        return results

def send_request(url, method='POST', headers=None, jsonData=None, rawData=None, is_pretty_print=False):
    request = requests.Request(method, url, headers=headers, data=rawData, json=jsonData)
    prepared = request.prepare()
    if is_pretty_print:
        prettyPrintPost(prepared)

    s = requests.Session()
    r = s.send(prepared, timeout=TIMEOUT)
    return r

def prettyPrintPost(req):
    print ('{}\n{}\n{}\n\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))

def get_test_sentences(filename):
    ''' get test sentences in unicode '''
    with codecs.open(filename, 'r', encoding='utf-8') as f:
        return [sentence.strip() for sentence in f.readlines()]

def get_absolute_path(module_name, relative_path):
    return join(dirname(realpath(module_name)), relative_path)

def parse_json_str_safely(jsonStr, fallback=None):
    retVal = fallback
    try:
        retVal = json.loads(jsonStr)
    except:
        pass
    return retVal

def write_to_db(app, db, entries):
    with app.app_context():
        try:
            for entry in entries:
                print(entry)
                db.session.add(entry)
            db.session.flush()
            savedEntries = [entry.to_dict() for entry in entries]
            db.session.commit()
            return savedEntries
        except exc.SQLAlchemyError:
            traceback.print_exc()

class _Task(object):
    ''' Executor task '''

    def __init__(self, func, args, argd=None):
        self._func = func
        self._args = args
        self._argd = {} if argd is None else argd
        self._ret = None

    def execute(self):
        self._ret = self._func(*self._args, **self._argd)
        return self._ret

class TaskExecutor(object):
    ''' Executor which runs tasks w/ many threads '''

    def __init__(self, threadCount=1):
        self.threadCount = threadCount
        self.threads = []
        self.taskQueue = Queue()
        self.resultQueue = Queue()

        self.start()

    def start(self):
        for i in range(self.threadCount):
            t = Thread(target=self._consumeTask, args=(i,))
            t.setName('TaskExecutor worker %d' % (i,))
            t.setDaemon(True)  # finishes when non-daemon threads terminate
            t.start()
            self.threads.append(t)

    def addTask(self, func, args, argd):
        ''' Add task to queue '''
        task = _Task(func, args, argd)
        self.taskQueue.put(item=task)

    def _consumeTask(self, threadID):
        while 1:
            task = self.taskQueue.get()
            try:
                task.execute()
                self.resultQueue.put(task)
            except:
                traceback.print_exc()

if __name__ == '__main__':
    cmd = ['./youtube-dl', 'https://www.youtube.com/watch?v=uAFdeLvT520', '--get-thumbnail']
    check_output(cmd)