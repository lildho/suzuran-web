"""
utils/database.py
Kelas Database — mengelola koneksi SQLite dan semua operasi CRUD.
Menggunakan OOP (Object-Oriented Programming) dengan encapsulation.
"""

import sqlite3
import hashlib
from contextlib import contextmanager


class Database:
    """
    Kelas utama pengelola database SQLite.
    Setiap method bertanggung jawab atas satu operasi (Single Responsibility).
    """

    def __init__(self, db_path: str):
        self.db_path = db_path

    # ── Context Manager ────────────────────────────────────────────────────────
    @contextmanager
    def _connect(self):
        """Membuka koneksi SQLite, auto-commit & close."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row          # Akses kolom by name
        conn.execute("PRAGMA journal_mode=WAL") # Performa lebih baik
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ── Init Tables ────────────────────────────────────────────────────────────
    def init_tables(self):
        """Membuat semua tabel jika belum ada."""
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role     TEXT DEFAULT 'admin'
                );

                CREATE TABLE IF NOT EXISTS mahasiswa (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    nim       TEXT UNIQUE NOT NULL,
                    nama      TEXT NOT NULL,
                    email     TEXT NOT NULL,
                    prodi     TEXT NOT NULL,
                    angkatan  TEXT NOT NULL,
                    ipk       REAL NOT NULL,
                    no_telp   TEXT NOT NULL,
                    alamat    TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now','localtime')),
                    updated_at TEXT DEFAULT (datetime('now','localtime'))
                );

                CREATE TABLE IF NOT EXISTS search_log (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    waktu       TEXT NOT NULL,
                    keyword     TEXT NOT NULL,
                    algoritma   TEXT NOT NULL,
                    field       TEXT NOT NULL,
                    jumlah_data INTEGER NOT NULL,
                    hasil       INTEGER NOT NULL,
                    durasi_ms   REAL NOT NULL,
                    complexity  TEXT NOT NULL,
                    langkah     INTEGER NOT NULL,
                    komentar    TEXT DEFAULT ''
                );
            """)

    # ── Admin Seeder ───────────────────────────────────────────────────────────
    def seed_admin(self):
        """Buat akun admin default jika tabel users masih kosong."""
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()
            if row["c"] == 0:
                pw_hash = self._hash(("admin123"))
                conn.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    ("admin", pw_hash)
                )

    def _hash(self, plain: str) -> str:
        return hashlib.sha256(plain.encode()).hexdigest()

    # ── Auth ───────────────────────────────────────────────────────────────────
    def get_user(self, username: str, password: str):
        pw_hash = self._hash(password)
        with self._connect() as conn:
            return conn.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, pw_hash)
            ).fetchone()

    # ── Stats ──────────────────────────────────────────────────────────────────
    def get_stats(self) -> dict:
        with self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) as c FROM mahasiswa").fetchone()["c"]
            prodi = conn.execute(
                "SELECT prodi, COUNT(*) as c FROM mahasiswa GROUP BY prodi ORDER BY c DESC LIMIT 5"
            ).fetchall()
            ipk_avg = conn.execute("SELECT AVG(ipk) as avg FROM mahasiswa").fetchone()["avg"]
            logs = conn.execute("SELECT COUNT(*) as c FROM search_log").fetchone()["c"]
            return {
                "total"   : total,
                "prodi"   : [dict(r) for r in prodi],
                "ipk_avg" : round(ipk_avg, 2) if ipk_avg else 0,
                "total_log": logs,
            }

    # ── CRUD Mahasiswa ─────────────────────────────────────────────────────────
    def get_mahasiswa_paginated(self, page: int, per_page: int):
        offset = (page - 1) * per_page
        with self._connect() as conn:
            data  = conn.execute(
                "SELECT * FROM mahasiswa ORDER BY id DESC LIMIT ? OFFSET ?",
                (per_page, offset)
            ).fetchall()
            total = conn.execute("SELECT COUNT(*) as c FROM mahasiswa").fetchone()["c"]
        return data, total

    def get_all_mahasiswa(self):
        with self._connect() as conn:
            return conn.execute("SELECT * FROM mahasiswa ORDER BY nim").fetchall()

    def get_mahasiswa_by_id(self, id: int):
        with self._connect() as conn:
            return conn.execute("SELECT * FROM mahasiswa WHERE id=?", (id,)).fetchone()

    def nim_exists(self, nim: str, exclude_id: int = None) -> bool:
        with self._connect() as conn:
            if exclude_id:
                row = conn.execute(
                    "SELECT id FROM mahasiswa WHERE nim=? AND id!=?", (nim, exclude_id)
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT id FROM mahasiswa WHERE nim=?", (nim,)
                ).fetchone()
        return row is not None

    def insert_mahasiswa(self, mhs) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """INSERT INTO mahasiswa (nim,nama,email,prodi,angkatan,ipk,no_telp,alamat)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (mhs.nim, mhs.nama, mhs.email, mhs.prodi,
                 mhs.angkatan, mhs.ipk, mhs.no_telp, mhs.alamat)
            )
        return cur.lastrowid

    def update_mahasiswa(self, id: int, mhs):
        with self._connect() as conn:
            conn.execute(
                """UPDATE mahasiswa
                   SET nim=?, nama=?, email=?, prodi=?, angkatan=?,
                       ipk=?, no_telp=?, alamat=?,
                       updated_at=datetime('now','localtime')
                   WHERE id=?""",
                (mhs.nim, mhs.nama, mhs.email, mhs.prodi,
                 mhs.angkatan, mhs.ipk, mhs.no_telp, mhs.alamat, id)
            )

    def delete_mahasiswa(self, id: int):
        with self._connect() as conn:
            conn.execute("DELETE FROM mahasiswa WHERE id=?", (id,))

    # ── Search Log ─────────────────────────────────────────────────────────────
    def insert_search_log(self, log: dict):
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO search_log
                   (waktu,keyword,algoritma,field,jumlah_data,hasil,durasi_ms,complexity,langkah)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (log["waktu"], log["keyword"], log["algoritma"], log["field"],
                 log["jumlah_data"], log["hasil"], log["durasi_ms"],
                 log["complexity"], log["langkah"])
            )

    def get_search_logs(self):
        with self._connect() as conn:
            return conn.execute(
                "SELECT * FROM search_log ORDER BY id DESC LIMIT 200"
            ).fetchall()

    def update_komentar(self, log_id: int, komentar: str):
        with self._connect() as conn:
            conn.execute(
                "UPDATE search_log SET komentar=? WHERE id=?",
                (komentar, log_id)
            )

    def delete_log(self, log_id: int):
        with self._connect() as conn:
            conn.execute("DELETE FROM search_log WHERE id=?", (log_id,))
