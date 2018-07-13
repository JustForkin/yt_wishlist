import youtube_dl

def my_hook(d):
    print(d)
    if d['status'] == 'downloading':
        print('Downloading: ' + d['_percent_str'])
    elif d['status'] == 'finished':
        print('Done downloading, now converting ...')

ydl_opts = {
    'outtmpl': '123.%(ext)s',
    'progress_hooks': [my_hook],
}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    result = ydl.extract_info(
        'https://www.youtube.com/watch?v=TMIrg8E-2Uo&list=PLA43284C6F79AD20C',
        download=False # We just want to extract the info
    )

if 'entries' in result:
    # Can be a playlist or a list of videos
    video = result['entries'][0]
else:
    # Just a video
    video = result

print(result)
