import os
from flask import Flask, render_template, send_from_directory, flash, request, redirect, url_for, session

SECRET_KEY = 'g6a1g91g91SASDd1f+a1f1'
CURRENT_DIR = os.getcwd()

app = Flask(__name__)

app.config.from_object(__name__)

def dir_list(path):
    return [x for x in os.listdir(path)]

# copy from werkzeug.utils import secure_filename
# to support the chinese
def my_secure_filename(filename):
    import sys
    import re

    text_type = str
    PY2 = sys.version_info[0] == 2
    _filename_ascii_strip_re = re.compile(r'[^A-Za-z0-9\u4e00-\u9fa5_.-]')
    _windows_device_files = ('CON', 'AUX', 'COM1', 'COM2', 'COM3', 'COM4', 'LPT1',
                             'LPT2', 'LPT3', 'PRN', 'NUL')

    if isinstance(filename, text_type):
        from unicodedata import normalize
        filename = normalize('NFKD', filename).encode('utf-8', 'ignore')
        if not PY2:
            filename = filename.decode('utf-8')
    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, ' ')
    filename = str(_filename_ascii_strip_re.sub('', '_'.join(
                   filename.split()))).strip('._')

    if os.name == 'nt' and filename and \
       filename.split('.')[0].upper() in _windows_device_files:
        filename = '_' + filename

    return filename

@app.route('/')
@app.route('/<path:Path>', methods=['GET'])
def ftp(Path = ''):
    if session.get('Path'):
        session.pop('Path')
        session.pop('path')

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

    session['Path'] = Path
    session['path'] = path

    return render_template('base.html',
                           title=Path,
                           upload=False,
                           up=up,
                           Path=Path,
                           dirList=dir_list(path))

@app.route('/upload', methods=['GET'])
def upload_get():
    Path = session['Path']
    path = session['path']

    Path = Path + '/'

    try:
        up = Path.split('/')
        up.pop(-1)
        up.pop(-1)
        up = '/'.join(up)
    except:
        up = ''

    return render_template('base.html',
                           title=Path,
                           upload=True,
                           up=up,
                           Path=Path,
                           dirList=dir_list(path))

@app.route('/upload', methods=['POST'])
def upload_post():
    path = session['path']

    file = request.files['file']
    if file:
        filename = my_secure_filename(file.filename)
        file.save(os.path.join(path, filename))
        return redirect(url_for('upload_get',
                                filename=filename))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
