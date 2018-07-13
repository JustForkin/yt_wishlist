from __future__ import unicode_literals
import youtube_dl

def my_hook(d):
    print(d)
    if d['status'] == 'downloading':
        print('Downloading: ' + d['_percent_str'])
    elif d['status'] == 'finished':
        print('Done downloading, now converting ...')


ydl_opts = {
    'outtmpl': '1' + '.%(ext)s',
    'progress_hooks': [my_hook],
}
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download(['https://www.youtube.com/watch?v=BaW_jenozKc'])
    print('good to go')