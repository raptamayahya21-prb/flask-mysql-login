#kalau bisa difahami semua ya lek hehe
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymysql import MySQL
from werkzeug.security import check_password_hash, generate_password_hash 
import os 

app = Flask(__name__)
app.secret_key = os.urandom(24) 

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root' 
app.config['MYSQL_PASSWORD'] = 'password_mysql_anda' 
app.config['MYSQL_DB'] = 'login_db' 
mysql = MySQL(app)

@app.route('/create_admin_user')
def create_admin_user():
    hashed_password = generate_password_hash('password123') 
    username = 'admin'
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT username FROM users WHERE username = %s", [username])
        if cur.fetchone() is None:
            cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed_password))
            mysql.connection.commit()
            cur.close()
            return f'User "{username}" berhasil dibuat dengan password hash!'
        else:
            cur.close()
            return f'User "{username}" sudah ada.'
    except Exception as e:
        return f'Gagal membuat user: {str(e)}', 500

@app.route('/')
def index():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Isi nama pengguna dan kata sandi.', 'error')
            return redirect(url_for('index'))

        cur = mysql.connection.cursor()
        cur.execute("SELECT user_id, password_hash FROM users WHERE username = %s", [username])
        user = cur.fetchone()
        cur.close()

        if user:
            if check_password_hash(user[1], password): 
                session['loggedin'] = True
                session['id'] = user[0]
                session['username'] = username
                flash(f'Selamat datang kembali, {username}!', 'success')
                return redirect(url_for('dashboard')) 
            else:
                flash('Nama pengguna atau kata sandi salah.', 'error')
                return redirect(url_for('index'))
        else:
            flash('Nama pengguna atau kata sandi salah.', 'error')
            return redirect(url_for('index'))

    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        return render_template('dashboard.html', username=session['username'])
    
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    flash('Anda telah berhasil keluar (logout).', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':

    app.run(debug=True)
