from flask import Flask, render_template, request, redirect, session, flash
from supabase import create_client, Client
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='templates')
app.secret_key = "your_secret_key"


SUPABASE_URL = "https://acvvhfcfzogxhfrzqsqq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFjdnZoZmNmem9neGhmcnpxc3FxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0MjM1MTcsImV4cCI6MjA2Njk5OTUxN30.zM5z6okmsKZ8dIKnVx0O7WpgN_-e_Mt0wty3CuHzKWc"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

BUCKET_NAME = "uploads"

@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')
    files = supabase.storage().from_(BUCKET_NAME).list()
    filenames = [f['name'] for f in files] if files else []
    return render_template('index.html', user=session['user'], files=filenames)

@app.route('/upload', methods=['POST'])
def upload():
    if 'user' not in session:
        return redirect('/login')
    if 'file' not in request.files:
        flash("沒有檔案")
        return redirect('/')
    file = request.files['file']
    filename = secure_filename(file.filename)
    content = file.read()
    res = supabase.storage().from_(BUCKET_NAME).upload(filename, content, {"content-type": file.content_type})
    if res.get("error"):
        flash(f"上傳失敗：{res['error']['message']}")
    else:
        flash("上傳成功")
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not email or not password:
            return "請輸入完整帳號密碼", 400
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res.get("session"):
            session['user'] = res['user']
            return redirect('/')
        else:
            flash("登入失敗")
            return redirect('/login')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)
