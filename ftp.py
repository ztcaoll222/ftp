import os
from flask import Flask, render_template, send_from_directory, flash

SECRET_KEY = 'g6a1g91g91SASDd1f+a1f1'
CURRENT_DIR = os.getcwd()

app = Flask(__name__)

app.config.from_object(__name__)

def dir_list(path):
    return [x for x in os.listdir(path)]

@app.route('/', methods=['GET'])
@app.route('/<path:Path>', methods=['GET'])
def ftp_get(Path = ''):
    path = os.path.join(CURRENT_DIR, Path)

    if os.path.isfile(path):
        format = os.path.splitext(path)[1]

        if format in ['.png', '.jpg', '.jpeg', '.gif']:
            with open(path, 'rb') as f:
                res = app.make_response(f.read())
            res.headers['Content-Type'] = 'image'
            return res

        if format in ['.mp4']:
            with open(path, 'rb') as f:
                res = app.make_response(f.read())
            res.headers['Content-Type'] = 'video'
            return res

        if format in ['.mp3']:
            with open(path, 'rb') as f:
                res = app.make_response(f.read())
            res.headers['Content-Type'] = 'audio'
            return res

        if format in ['.txt', '.xml', '.py', '.html']:
            with open(path, 'rb') as f:
                res = app.make_response(f.read())
            res.headers['Content-Type'] = 'text/plain'
            return res

        return send_from_directory(os.path.split(path)[0],
                                   os.path.split(path)[1],
                                   as_attachment=True)

    temp = '/'
    if Path == '':
        temp = ''
    Path = temp + Path + '/'

    try:
        up = Path.split('/')
        up.pop(-1)
        up.pop(-1)
        up = '/'.join(up)
    except:
        up = ''

    return render_template('base.html',
                           title = Path,
                           up = up,
                           dirList = dir_list(path),
                           Path = Path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
