# SUZURAN — Suzuran University Student Data System

> Tugas Akhir — Manajemen Data Mahasiswa berbasis Web
> Framework: **Flask (Python)** · Database: **SQLite** · Hosting: **Railway**

---

## Fitur

| Fitur | Keterangan |
|-------|-----------|
| **CRUD** | Create, Read, Update, Delete data mahasiswa |
| **Import / Export** | CSV dan JSON |
| **Pencarian** | Linear Search O(n), Binary Search O(log n) |
| **Sorting** | Bubble Sort O(n²), Selection Sort O(n²) |
| **Kirim Email** | Kirim email ke mahasiswa via Brevo HTTP API |
| **OOP & Class** | `Mahasiswa`, `Database`, `SearchEngine`, `SortEngine`, `Validator`, `EmailSender` |
| **Validasi Regex** | NIM, Email, No. Telp, IPK, Angkatan |
| **Estimasi Complexity** | Waktu teoritis per operasi |
| **Build Log** | Riwayat pencarian + komentar |
| **Login System** | Autentikasi session dengan password hash (SHA-256) |
| **UI** | Tema clean & minimalist (putih–kuning), responsif |

---

## Menjalankan di Komputer Lokal (dari awal)

### 1. Prasyarat
- **Python 3.11+** — cek: `python --version`
- **Git** — cek: `git --version`

### 2. Ambil kode
```bash
git clone https://github.com/lildho/suzuran-web.git
cd suzuran-web
```

### 3. (Opsional) Virtual environment
```bash
python -m venv venv
venv\Scripts\Activate.ps1      # Windows PowerShell
# source venv/bin/activate     # macOS / Linux
```

### 4. Install dependency
```bash
pip install -r requirements.txt
```

### 5. (Opsional) Konfigurasi email
Hanya jika ingin memakai fitur **Kirim Email**. Buat file `.env` di root project:
```
GMAIL_USER=emailpengirim@gmail.com
GMAIL_SENDER_NAME=Nama Pengirim
BREVO_API_KEY=xkeysib-xxxxxxxx...
```
> `.env` otomatis terbaca (sudah masuk `.gitignore`, tidak ikut ke GitHub).
> Tanpa konfigurasi ini app tetap jalan — hanya tombol Kirim Email yang nonaktif.

### 6. Jalankan
```bash
python app.py
```
Buka browser ke **http://localhost:5000**

**Login default:** `admin` / `admin123`

> Database `suzuran.db` dibuat otomatis saat pertama dijalankan (termasuk akun admin).
> Untuk reset data, hapus file `suzuran.db` lalu jalankan lagi.

---

## Environment Variables

| Variable | Wajib? | Keterangan |
|----------|--------|-----------|
| `SECRET_KEY` | disarankan | Kunci rahasia session Flask |
| `PORT` | otomatis | Disediakan platform hosting (default 5000) |
| `DB_PATH` | opsional | Lokasi file SQLite (mis. `/data/suzuran.db` untuk volume) |
| `BREVO_API_KEY` | untuk email | API key dari dashboard Brevo |
| `GMAIL_USER` | untuk email | Email pengirim (harus diverifikasi sebagai sender di Brevo) |
| `GMAIL_SENDER_NAME` | opsional | Nama tampilan pengirim |

---

## Deploy ke Railway

1. Push project ke GitHub.
2. Buka [railway.app](https://railway.app) → **Login with GitHub**.
3. **New Project** → **Deploy from GitHub repo** → pilih repo ini.
4. Railway otomatis membaca `requirements.txt` dan `Procfile`
   (`gunicorn app:app --bind 0.0.0.0:$PORT ...`), lalu deploy.
5. **Settings → Networking → Generate Domain** untuk mendapatkan URL publik.
6. **Variables** → set `SECRET_KEY`, `BREVO_API_KEY`, `GMAIL_USER`, `GMAIL_SENDER_NAME`.

### Data permanen (opsional)
Filesystem Railway bersifat *ephemeral* (data reset tiap redeploy). Agar permanen:
1. Tambah **Volume** dengan mount path `/data`.
2. Set variable `DB_PATH=/data/suzuran.db`.

### Catatan email
Railway memblokir port SMTP (587/465), sehingga pengiriman lewat SMTP Gmail gagal.
Aplikasi ini memakai **Brevo HTTP API** (HTTPS port 443) agar email tetap terkirim
dari hosting. Pengirim (`GMAIL_USER`) harus diverifikasi sebagai *sender* di Brevo.

### Alur update
```bash
git add -A
git commit -m "deskripsi perubahan"
git push
```
Railway otomatis men-deploy versi terbaru setiap kali ada push.

---

## Struktur Project

```
suzuran-web/
├── app.py                  ← Routing utama Flask
├── requirements.txt
├── Procfile                ← Start command (gunicorn) untuk hosting
├── .python-version
├── render.yaml             ← Konfigurasi alternatif (Render.com)
├── utils/
│   ├── database.py         ← Kelas Database (SQLite, OOP)
│   ├── mahasiswa.py        ← Model Mahasiswa
│   ├── algoritma.py        ← SearchEngine & SortEngine
│   ├── validator.py        ← Validasi Regex
│   └── mailer.py           ← EmailSender (Brevo HTTP API)
└── templates/
    ├── base.html           ← Layout + design system (tema putih–kuning)
    ├── login.html
    ├── dashboard.html
    ├── pencarian.html
    ├── sorting.html
    ├── import_export.html
    ├── log.html
    └── mahasiswa/
        ├── list.html
        ├── form.html
        ├── detail.html
        └── email.html      ← Halaman kirim email
```

---

## Detail Algoritma

### Pencarian
| Algoritma | Kompleksitas | Cara Kerja |
|-----------|-------------|-----------|
| **Linear Search** | O(n) | Iterasi satu per satu dari awal hingga akhir |
| **Binary Search** | O(log n) | Data diurutkan dulu, lalu dicari dengan teknik bagi dua |

### Pengurutan
| Algoritma | Kompleksitas | Cara Kerja |
|-----------|-------------|-----------|
| **Bubble Sort** | O(n²) | Bandingkan elemen berdekatan, tukar jika tidak urut |
| **Selection Sort** | O(n²) | Temukan min/max, letakkan di posisi yang benar |

### Validasi Regex
| Field | Pola |
|-------|------|
| NIM | `^\d{8,12}$` |
| Nama | `^[A-Za-z\s'.,-]{2,100}$` |
| Email | `^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$` |
| No. Telp | `^(\+62\|62\|0)[0-9]{8,13}$` |
| Angkatan | `^(20[0-9]{2})$` |
| IPK | `^[0-3](\.\d{1,2})?$\|^4(\.00?)?$` |

---

*Dibuat dengan Flask + SQLite*
