from subprocess import Popen, PIPE, CalledProcessError
def check_output(commands):
    print('cmd:')
    print(commands)
    import subprocess
    with Popen(cmd, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
    	for line in p.stdout:
    		print('from me' + line)

if __name__ == '__main__':
    import subprocess
    cmd = ['./youtube-dl', 'https://www.youtube.com/watch?v=uAFdeLvT520', '--get-url']
    # subprocess.call(cmd)
    check_output(cmd)
