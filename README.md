# SUZURAN — Suzuran University Student Data System

> Tugas Akhir — Manajemen Data Mahasiswa berbasis Web  
> Framework: **Flask (Python)** | Database: **SQLite** | Hosting: **Render.com**

---

## Fitur Lengkap

| Fitur | Keterangan |
|-------|-----------|
| **CRUD** | Create, Read, Update, Delete data mahasiswa |
| **Import/Export** | CSV dan JSON |
| **Pencarian** | Linear Search O(n), Binary Search O(log n) |
| **Sorting** | Bubble Sort O(n²), Selection Sort O(n²) |
| **OOP & Class** | `Mahasiswa`, `Database`, `SearchEngine`, `SortEngine`, `Validator` |
| **Validasi Regex** | NIM, Email, No. Telp, IPK, Angkatan |
| **Error Handling** | Try/Except + notifikasi toast alert |
| **Estimasi Complexity** | Waktu teoritis per operasi |
| **Build Log** | Riwayat pencarian + komentar |
| **Login System** | Autentikasi session dengan password hash (SHA-256) |

---

## Struktur Project

```
suzuran/
├── app.py                  ← Routing utama Flask
├── requirements.txt
├── render.yaml             ← Konfigurasi hosting Render.com
├── utils/
│   ├── database.py         ← Kelas Database (OOP)
│   ├── mahasiswa.py        ← Kelas Mahasiswa (Model / OOP)
│   ├── algoritma.py        ← SearchEngine & SortEngine (OOP)
│   └── validator.py        ← Kelas Validator dengan Regex
└── templates/
    ├── base.html
    ├── login.html
    ├── dashboard.html
    ├── pencarian.html
    ├── sorting.html
    ├── import_export.html
    ├── log.html
    └── mahasiswa/
        ├── list.html
        ├── form.html
        └── detail.html
```

---

## Cara Menjalankan Lokal

```bash
# 1. Clone / ekstrak project
cd suzuran

# 2. Install dependencies
pip install -r requirements.txt

# 3. Jalankan aplikasi
python app.py

# 4. Buka browser
# http://localhost:5000

# Default login:
# Username: admin
# Password: admin123
```

---

## Cara Deploy ke Render.com (GRATIS)

1. Push project ke GitHub
2. Buka [render.com](https://render.com) → Login
3. Klik **New → Web Service**
4. Connect repository GitHub
5. Render otomatis baca `render.yaml` → Deploy!
6. Dapatkan URL gratis: `https://suzuran-mahasiswa.onrender.com`

> ⚠️ Catatan: Render.com free tier = spin down setelah 15 menit idle. SQLite data akan reset tiap deploy. Untuk data permanen, upgrade ke paid plan atau gunakan PostgreSQL.

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

### Estimasi Waktu
- Asumsi: 1.000.000 operasi/detik
- **Linear O(n)**: `waktu = n / 1_000_000` detik
- **Binary O(log n)**: `waktu = log₂(n) / 1_000_000` detik
- **Sorting O(n²)**: `waktu = n² / 1_000_000` detik

### Validasi Regex

| Field | Pola |
|-------|------|
| NIM | `^\d{8,12}$` |
| Nama | `^[A-Za-z\s'.,-]{2,100}$` |
| Email | `^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$` |
| No. Telp | `^(\+62|62|0)[0-9]{8,13}$` |
| Angkatan | `^(20[0-9]{2})$` |
| IPK | `^[0-3](\.\d{1,2})?$|^4(\.00?)?$` |

---

## OOP Classes

```python
# Mahasiswa — Model data
mhs = Mahasiswa(nim="12345678", nama="Budi", ...)

# Database — Pengelola SQLite
db = Database("suzuran.db")
db.insert_mahasiswa(mhs)

# SearchEngine — Algoritma pencarian
engine = SearchEngine(data)
hasil, langkah = engine.linear_search("budi", "nama")
hasil, langkah = engine.binary_search("12345678")

# SortEngine — Algoritma pengurutan
sorter = SortEngine(data)
hasil, steps = sorter.bubble_sort("nama", "asc")
hasil, steps = sorter.selection_sort("ipk", "desc")

# Validator — Validasi Regex
v = Validator(form_data)
errors = v.validate_mahasiswa()
```

---

*Dibuat dengan Flask + SQLite | © 2025*
