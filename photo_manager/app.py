import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory

app = Flask(__name__)
app.secret_key = 'kh6686028'

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf', 'ai'}
LOGIN_PASSWORD = 'admin123'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_logged_in():
    return session.get('logged_in')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == LOGIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('密碼錯誤，請再試一次', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    if not is_logged_in():
        return redirect(url_for('login'))
    folders = []
    if os.path.exists(UPLOAD_FOLDER):
        folders = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isdir(os.path.join(UPLOAD_FOLDER, f))]
    return render_template('index.html', folders=folders)

@app.route('/create_folder', methods=['POST'])
def create_folder():
    if not is_logged_in():
        return redirect(url_for('login'))

    folder_name = request.form.get('folder_name').strip()
    folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
    if not folder_name:
        flash('資料夾名稱不可為空', 'warning')
    elif not os.path.exists(folder_path):
        os.makedirs(folder_path)
        flash(f'已建立資料夾：{folder_name}', 'success')
    else:
        flash('資料夾已存在', 'warning')
    return redirect(url_for('index'))

@app.route('/folder/<folder_name>')
def folder_view(folder_name):
    if not is_logged_in():
        return redirect(url_for('login'))
    folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
    if not os.path.exists(folder_path):
        flash('資料夾不存在', 'warning')
        return redirect(url_for('index'))
    files = os.listdir(folder_path)
    return render_template('upload.html', folder_name=folder_name, files=files)

@app.route('/upload/<folder_name>', methods=['POST'])
def upload_file(folder_name):
    if not is_logged_in():
        return redirect(url_for('login'))

    file = request.files.get('file')
    if not file or file.filename == '':
        flash('沒有選擇檔案', 'warning')
        return redirect(url_for('folder_view', folder_name=folder_name))

    if allowed_file(file.filename):
        folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
        file_path = os.path.join(folder_path, file.filename)
        file.save(file_path)
        flash(f'檔案「{file.filename}」已上傳', 'success')
    else:
        flash('不支援的檔案格式', 'danger')

    return redirect(url_for('folder_view', folder_name=folder_name))

@app.route('/delete/<folder_name>/<filename>', methods=['POST'])
def delete_file(folder_name, filename):
    if not is_logged_in():
        return redirect(url_for('login'))

    path = os.path.join(UPLOAD_FOLDER, folder_name, filename)
    if os.path.exists(path):
        os.remove(path)
        flash(f'檔案「{filename}」已刪除', 'success')
    else:
        flash('檔案不存在', 'warning')

    return redirect(url_for('folder_view', folder_name=folder_name))

@app.route('/uploads/<folder_name>/<filename>')
def uploaded_file(folder_name, filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, folder_name), filename)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True, port=5001)

