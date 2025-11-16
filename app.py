from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymysql import MySQL
from werkzeug.security import check_password_hash, generate_password_hash # Menambahkan generate_password_hash untuk contoh
import os # Import os untuk membuat kunci rahasia yang lebih aman

app = Flask(__name__)
# Perbaikan: Menggunakan os.urandom untuk kunci yang sangat kuat (HARUS DIGANTI)
# NOTE: Ganti ini dengan string acak yang Anda simpan di tempat aman!
app.secret_key = os.urandom(24) 

# --- Konfigurasi MySQL ---
# PENTING: Ganti nilai 'password_mysql_anda' dengan password MySQL Anda
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root' 
app.config['MYSQL_PASSWORD'] = 'password_mysql_anda' 
app.config['MYSQL_DB'] = 'login_db' 
mysql = MySQL(app)
# --- Akhir Konfigurasi MySQL ---

# Catatan: Fungsi ini hanya untuk demonstrasi membuat user awal di database
# Anda bisa menghapus fungsi ini setelah database terisi.
@app.route('/create_admin_user')
def create_admin_user():
    # PENTING: GANTI 'password123' dengan password kuat
    hashed_password = generate_password_hash('password123') 
    username = 'admin'
    
    try:
        cur = mysql.connection.cursor()
        # Cek apakah user sudah ada
        cur.execute("SELECT username FROM users WHERE username = %s", [username])
        if cur.fetchone() is None:
            # Masukkan user baru
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
    # Jika sudah login, langsung arahkan ke dashboard
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    
    # Render halaman login
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Guard clause: jika username atau password kosong
        if not username or not password:
            flash('Isi nama pengguna dan kata sandi.', 'error')
            return redirect(url_for('index'))

        # 1. Koneksi ke Database
        cur = mysql.connection.cursor()
        cur.execute("SELECT user_id, password_hash FROM users WHERE username = %s", [username])
        user = cur.fetchone()
        cur.close()

        # 2. Validasi
        if user:
            # user[1] adalah password_hash dari database
            if check_password_hash(user[1], password): 
                # Login sukses
                session['loggedin'] = True
                session['id'] = user[0]
                session['username'] = username
                flash(f'Selamat datang kembali, {username}!', 'success')
                return redirect(url_for('dashboard')) 
            else:
                # Password salah
                flash('Nama pengguna atau kata sandi salah.', 'error')
                return redirect(url_for('index'))
        else:
            # Username tidak ditemukan (Pesan disamarkan untuk keamanan)
            flash('Nama pengguna atau kata sandi salah.', 'error')
            return redirect(url_for('index'))

    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    # Halaman yang hanya bisa diakses setelah login
    if 'loggedin' in session:
        # PENTING: Anda harus membuat file dashboard.html
        return render_template('dashboard.html', username=session['username'])
    
    # Jika belum login, arahkan ke halaman login
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    # Hapus data sesi
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    flash('Anda telah berhasil keluar (logout).', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Saat deploy sungguhan, ubah debug=False
    app.run(debug=True)