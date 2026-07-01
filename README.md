# Web Portofolio dengan Integrasi API (Flask, TiDB, Cloudinary, & Resend)

Aplikasi web portofolio interaktif yang dibangun menggunakan **Python & Flask** di backend dan **HTML, CSS, & JavaScript** di frontend. Aplikasi ini memiliki halaman utama (Portofolio) dinamis serta halaman Admin yang mendukung operasi CRUD (Create, Read, Update, Delete) lengkap dengan integrasi API pihak ketiga.

## Fitur Utama

1. **Website Portofolio Dinamis**: Menampilkan data Profil, Skill, Pengalaman Kerja, dan Proyek langsung dari database.
2. **Halaman Admin & CRUD**: Panel admin interaktif untuk mengelola seluruh data aplikasi.
3. **Upload Gambar Cloudinary**: Integrasi dengan Cloudinary API untuk mengunggah gambar profil dan proyek secara langsung ke cloud.
4. **Pengiriman Email Resend**: Kontak form di halaman utama terintegrasi dengan Resend API untuk mengirim pemberitahuan email ke admin ketika ada pesan baru masuk.
5. **Dukungan TiDB Cloud & SQLite**: Konfigurasi database online TiDB dengan SSL (Ca.pem) atau database lokal SQLite secara fallback.

## Struktur Direktori

```text
Backend/
  admin/
    dashboard.py
    experience.py
    login.py
    profiles.py
    projects.py
    skills.py
    upload.py
  utama/
    utama.py
Frontend/
  admin/
    css/ (base.css, dashboard.css, experience.css, login.css, profiles.css, projects.css, skills.css)
    js/ (api.js, base.js, dashboard.js, experience.js, login.js, profiles.js, projects.js, skills.js)
    base.html
    dashboard.html
    experience.html
    login.html
    profiles.html
    projects.html
    skills.html
  utama/
    css/ (style.css)
    js/ (script.js)
.env
.gitignore
app.py
config.py
database.sql
DB_NIM_NAMA.sql
favicon.ico
index.html
model.py
README.md
requirements.txt
struktur_folder.txt
```

## Persyaratan (Requirements)
Aplikasi membutuhkan Python 3.8+ dan pustaka berikut yang tertera di `requirements.txt`:
- Flask
- Flask-SQLAlchemy
- PyMySQL
- python-dotenv
- cloudinary
- resend
- Flask-WTF
- Werkzeug

## Cara Menjalankan Aplikasi

1. **Instalasi Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Konfigurasi Environment**:
   Salin file `.env.example` menjadi `.env` dan isi kunci API serta kredensial database Anda:
   ```bash
   cp .env.example .env
   ```
   *Jika `USE_TIDB=false`, aplikasi akan otomatis menggunakan SQLite lokal (`instance/portfolio.db`).*

3. **Jalankan Aplikasi**:
   ```bash
   python app.py
   ```
   Buka `http://localhost:5000` di web browser Anda.

4. **Akses Halaman Admin**:
   - URL: `http://localhost:5000/admin/login`
   - **Username**: `admin`
   - **Password**: `admin123`
