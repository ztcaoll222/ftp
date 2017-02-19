# -*- coding: utf-8 -*-
import os
import sys
import re
from flask import Flask, render_template, send_from_directory, flash, request, redirect, session, abort
from shutil import rmtree, copyfile, copytree
from unicodedata import normalize


# copy from werkzeug.utils import secure_filename
# to support the chinese
def my_secure_filename(filename):
    text_type = str
    PY2 = sys.version_info[0] == 2
    _filename_ascii_strip_re = re.compile(r'[^A-Za-z0-9\u4e00-\u9fa5_.-]')
    _windows_device_files = ('CON', 'AUX', 'COM1', 'COM2', 'COM3', 'COM4', 'LPT1',
                             'LPT2', 'LPT3', 'PRN', 'NUL')

    if isinstance(filename, text_type):
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


def dir_list(path):
    return [x for x in os.listdir(path)]


SECRET_KEY = 'SECRET_KEY'
CURRENT_DIR = os.getcwd()

app = Flask(__name__)

app.config.from_object(__name__)


@app.route('/favicon.ico', methods=['GET'])
def favicon_ico():
    abort(404)


@app.route('/', methods=['GET'])
def home_of_no_variable_get():
    return redirect('/ftp')


@app.route('/ftp/', methods=['GET'])
def ftp_of_no_variable_get():
    currentPath = ''
    session['currentPath'] = currentPath
    path = os.path.join(CURRENT_DIR, currentPath)

    fileList = dir_list(path)

    isUpload = session.get('isUpload', False)
    session.pop('isUpload', False)

    isCreateDir = session.get('isCreateDir', False)
    session.pop('isCreateDir', False)

    isCreateFile = session.get('isCreateFile', False)
    session.pop('isCreateFile', False)

    isCopy = session.get('isCopy', False)

    isMov = session.get('isMov', False)


    return render_template('base.html',
                           title = currentPath,
                           flashPath=currentPath,
                           upload = isUpload,
                           isCreateDir = isCreateDir,
                           isCreateFile=isCreateFile,
                           path = currentPath,
                           fileList = fileList,
                           isCopy = isCopy,
                           isMov = isMov)


@app.route('/ftp/<path:path>', methods=['GET'])
def ftp_of_variable_get(path):
    currentPath = path
    session['currentPath'] = currentPath
    path = os.path.join(CURRENT_DIR, currentPath)

    isUpload = session.get('isUpload', False)
    session.pop('isUpload', False)

    isCreateDir = session.get('isCreateDir', False)
    session.pop('isCreateDir', False)

    isCreateFile = session.get('isCreateFile', False)
    session.pop('isCreateFile', False)

    isCopy = session.get('isCopy', False)

    isMov = session.get('isMov', False)

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

        if format in ['.pdf']:
            with open(path, 'rb') as f:
                res = app.make_response(f.read())
            res.headers['Content-Type'] = 'application/pdf'
            return res

        return send_from_directory(os.path.split(path)[0],
                                   os.path.split(path)[1],
                                   as_attachment=True)

    fileList = dir_list(path)

    up = currentPath.split('/')
    up.pop(-1)
    up = '/'.join(up)

    return render_template('base.html',
                           title=currentPath,
                           up = up,
                           flashPath = currentPath,
                           upload=isUpload,
                           isCreateDir = isCreateDir,
                           isCreateFile = isCreateFile,
                           path = currentPath + '/',
                           fileList = fileList,
                           isCopy = isCopy,
                           isMov = isMov)


@app.route('/upload', methods=['GET'])
def upload_get():
    currentPath = session['currentPath']
    session['isUpload'] = True
    return redirect('/ftp/%s' % currentPath)


@app.route('/upload', methods=['POST'])
def upload_post():
    currentPath = session['currentPath']
    session.pop('isUpload', False)

    file = request.files['file']
    filename = file.filename
    if file:
        filename = my_secure_filename(filename)
        file.save(os.path.join(currentPath, filename))
        flash('%s 上传成功!' % filename)
    else:
        flash('%s 上传失败!' % filename)

    return redirect('/ftp/%s' % currentPath)


@app.route('/del', methods=['POST'])
def del_post():
    currentPath = session['currentPath']

    choice = dict(request.form)
    choice.pop('del')
    choice = list(choice)

    for filename in choice:
        path = os.path.join(currentPath, filename)
        try:
            if os.path.isfile(path):
                os.remove(path)
            else:
                rmtree(path)
            flash("删除%s成功" % path)
        except:
            flash("删除%s失败，权限不足或者此文件不存在" % path)

    flash('删除完成!' % choice)
    return redirect('/ftp/%s' % currentPath)


@app.route('/copy', methods=['POST'])
def copy_post():
    currentPath = session['currentPath']

    choice = dict(request.form)
    choice.pop('copy')
    choice = list(choice)

    session['filePrePath'] = session['currentPath']
    session['fileList'] = choice
    session['isCopy'] = True

    session.pop('isMov', False)

    return redirect('/ftp/%s' % currentPath)


@app.route('/mov', methods=['POST'])
def mov_post():
    currentPath = session['currentPath']

    choice = dict(request.form)
    choice.pop('mov')
    choice = list(choice)

    session['filePrePath'] = session['currentPath']
    session['fileList'] = choice
    session['isMov'] = True

    session.pop('isCopy', False)

    return redirect('/ftp/%s' % currentPath)


@app.route('/paste', methods=['POST'])
def paste_post():
    currentPath = session['currentPath']

    fileList = session['fileList']
    for filename in fileList:
        src = os.path.join(session['filePrePath'], filename)
        dst = os.path.join(currentPath, filename)
        if os.path.isfile(src):
            copyfile(src, dst)
        else:
            copytree(src, dst)

    if dict(request.form).get('mov'):
        for filename in fileList:
            src = os.path.join(session['filePrePath'], filename)
            if os.path.isfile(src):
                os.remove(src)
            else:
                rmtree(src)

    session.pop('isCopy', False)
    session.pop('isMov', False)

    flash("%s 成功!" % fileList)

    return redirect('/ftp/%s' % currentPath)


@app.route('/createDir', methods=['GET'])
def create_dir_get():
    currentPath = session['currentPath']
    session['isCreateDir'] = True
    return redirect('/ftp/%s' % currentPath)


@app.route('/createDir', methods=['POST'])
def create_dir_post():
    currentPath = session['currentPath']
    session.pop('isCreateDir', False)

    dirname = request.form['dirname']
    dirname = my_secure_filename(dirname)
    path = os.path.join(currentPath, dirname)

    try:
        os.mkdir(path)
    except:
        flash("文件夹已存在或权限不足")

    return redirect('/ftp/%s' % currentPath)


@app.route('/createFile', methods=['Get'])
def create_file_get():
    currentPath = session['currentPath']
    session['isCreateFile'] = True
    return redirect('/ftp/%s' % currentPath)


@app.route('/createFile', methods=['POST'])
def create_file_post():
    currentPath = session['currentPath']
    session.pop('isCreateFile', False)

    filetext = request.form['filetext']
    filename = request.form['filename']
    if filename:
        path = os.path.join(currentPath, filename)
        if not os.path.exists(path):
            with open(path, 'w') as f:
                f.write(filetext)
        else:
            flash("文件%s已存在" % path)
    else:
        flash('请输入文件名!')

    return redirect('/ftp/%s' % currentPath)


@app.route('/cancel', methods=['POST'])
def cancel_post():
    currentPath = session['currentPath']

    session.pop('filePrePath', False)
    session.pop('fileList', False)
    session.pop('isCopy', False)
    session.pop('isMov', False)

    return redirect('/ftp/%s' % currentPath)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
