# -*- coding: utf-8 -*-
import os
import sys
import re
from flask import Flask, render_template, send_from_directory, flash, request, redirect, session, abort
from shutil import rmtree, copyfile, copytree
from unicodedata import normalize


# 复制 werkzeug.utils import secure_filename
# 支持中文
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
    fileList = []
    dirList = []
    for x in os.listdir(path):
        if os.path.isfile(os.path.join(path, x)):
            fileList.append(x)
        else:
            dirList.append(x)

    return fileList, dirList


def history(currentPath):
    isPre = session.get('isPre', False)
    isNext = session.get('isNext', False)

    if not session.get('pathHistory', False):
        session['pathHistory'] = []
        session['pathHistory'].append(currentPath)
        session['p'] = len(session['pathHistory']) - 1
    elif currentPath != session['pathHistory'][-1] and not isPre and not isNext:
        if len(session['pathHistory']) - 1 != session['p']:
            for key in session['pathHistory'][session['p'] + 1:]:
                session['pathHistory'].remove(key)
        session['pathHistory'].append(currentPath)
        session['p'] = len(session['pathHistory']) - 1

    session.pop('isPre', False)
    session.pop('isNext', False)


SECRET_KEY = 'SECRET_KEY'
CURRENT_DIR = os.getcwd()

app = Flask(__name__)

app.config.from_object(__name__)


# 懒得弄logo, 直接返回404
@app.route('/favicon.ico', methods=['GET'])
def favicon_ico():
    abort(404)


# 跳转到/ftp
@app.route('/', methods=['GET'])
def home_of_no_variable_get():
    return redirect('/ftp')


@app.route('/ftp/', methods=['GET'])
@app.route('/ftp/<path:path>', methods=['GET'])
def ftp_get(path = ''):
    currentPath = path
    path = os.path.join(CURRENT_DIR, currentPath)

    isUpload = session.get('isUpload', False)
    session.pop('isUpload', False)

    isSearchFile = session.get('isSearchFile', False)
    session.pop('isSearchFile', False)

    isSearchText = session.get('isSearchText', False)
    session.pop('isSearchText', False)

    isCreateDir = session.get('isCreateDir', False)
    session.pop('isCreateDir', False)

    isCreateFile = session.get('isCreateFile', False)
    session.pop('isCreateFile', False)

    isCopy = session.get('isCopy', False)

    isMov = session.get('isMov', False)

    searchFileRes = session.get('searchFileRes', False)
    session.pop('searchFileRes', False)

    searchTextRes = session.get('searchTextRes', False)
    session.pop('searchTextRes', False)

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

    fileList, dirList = dir_list(path)

    history(currentPath)

    session['currentPath'] = currentPath

    if currentPath:
        path = currentPath + '/'
    else:
        path = currentPath

    return render_template('base.html',
                           title=currentPath,
                           flashPath=currentPath,
                           isUpload=isUpload,
                           isSearchFile=isSearchFile,
                           isSearchText=isSearchText,
                           isCreateDir=isCreateDir,
                           isCreateFile=isCreateFile,
                           searchFileRes=searchFileRes,
                           searchTextRes=searchTextRes,
                           path=path,
                           fileList=fileList,
                           dirList=dirList,
                           isCopy=isCopy,
                           isMov=isMov)


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


@app.route('/upPath', methods=['GET'])
def upPath_get():
    currentPath = session['currentPath']

    upPath = currentPath.split('/')
    upPath.pop(-1)
    upPath = '/'.join(upPath)

    return redirect('/ftp/%s' % upPath)


@app.route('/prePath', methods=['GET'])
def prePath_get():
    if session['p'] > 0:
        session['p'] -= 1

    prePath = session['pathHistory'][session['p']]

    session['isPre'] = True

    return redirect('/ftp/%s' % prePath)


@app.route('/nextPath', methods=['GET'])
def nextPath_get():
    if session['p'] < len(session['pathHistory']) - 1:
        session['p'] += 1

    nextPath = session['pathHistory'][session['p']]

    session['isNext'] = True

    return redirect('/ftp/%s' % nextPath)


@app.route('/searchFile', methods=['GET'])
def search_file_get():
    currentPath = session['currentPath']
    session['isSearchFile'] = True
    return redirect('/ftp/%s' % currentPath)


@app.route('/searchFile', methods=['POST'])
def search_file_post():
    currentPath = session['currentPath']
    session.pop('isSearchFile', False)

    if not currentPath:
        walkPath = '.'
    else:
        walkPath = currentPath

    session['searchFileRes'] = []
    searchText = request.form['search_text']
    for dirpath, dirnames, filenames in os.walk(walkPath):
        if searchText in dirpath:
            session['searchFileRes'].append(dirpath)
        for filename in filenames:
            if searchText in filename:
                filepath = os.path.join(dirpath, filename)
                session['searchFileRes'].append(filepath)

    return redirect('/ftp/%s' % currentPath)


@app.route('/searchText', methods=['GET'])
def search_text_get():
    currentPath = session['currentPath']
    session['isSearchText'] = True
    return redirect('/ftp/%s' % currentPath)


@app.route('/searchText', methods=['POST'])
def search_test_post():
    currentPath = session['currentPath']
    session.pop('isSearchText', False)

    if not currentPath:
        walkPath = '.'
    else:
        walkPath = currentPath

    session['searchTextRes'] = []
    searchText = request.form['search_text']
    for dirpath, dirnames, filenames in os.walk(walkPath):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                with open(filepath, 'r') as f:
                    if searchText in f.read():
                        session['searchTextRes'].append(filepath)
            except:
                pass

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

    dirname = my_secure_filename(request.form['dirname'])
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
    filename = my_secure_filename(request.form['filename'])
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


# 取消
@app.route('/cancel', methods=['POST'])
def cancel_post():
    currentPath = session['currentPath']

    session.pop('isUpload', False)
    session.pop('isSearchFile', False)
    session.pop('searchFileRes', False)
    session.pop('isSearchText', False)
    session.pop('searchTextRes', False)
    session.pop('isCreateDir', False)
    session.pop('isCreateFile', False)
    session.pop('filePrePath', False)
    session.pop('fileList', False)
    session.pop('isCopy', False)
    session.pop('isMov', False)

    return redirect('/ftp/%s' % currentPath)


# 清除session
@app.route('/clear', methods=['GET'])
def clear_get():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
