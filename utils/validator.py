"""
utils/validator.py
Kelas Validator — validasi input menggunakan Regular Expression (Regex).
Setiap field memiliki aturan validasi yang ketat untuk mencegah data kotor.
"""

import re
from datetime import datetime


class Validator:
    """
    Validator berbasis Regex untuk data mahasiswa.
    Pola regex dikompilasi sekali (compile) untuk efisiensi.
    """

    # ── Pola Regex (dikompilasi saat class di-load) ────────────────────────────
    POLA = {
        # NIM: 8–12 digit angka (bisa tambah huruf sesuai kampus)
        "nim"     : re.compile(r"^\d{8,12}$"),

        # Nama: huruf (termasuk spasi, titik, tanda petik, strip) 2–100 karakter
        "nama"    : re.compile(r"^[A-Za-z\s'.,-]{2,100}$"),

        # Email: format standar RFC5322 sederhana
        "email"   : re.compile(r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$"),

        # No Telpon: 08xxxxxxx atau +628xxxxxxx, panjang 10–15 digit
        "no_telp" : re.compile(r"^(\+62|62|0)[0-9]{8,13}$"),

        # Angkatan: 4 digit tahun, misal 2020 – 2030
        "angkatan": re.compile(r"^(20[0-9]{2})$"),

        # IPK: 0.00 – 4.00
        "ipk"     : re.compile(r"^[0-3](\.\d{1,2})?$|^4(\.00?)?$"),
    }

    def __init__(self, data: dict):
        self.data = data

    def validate_mahasiswa(self) -> dict:
        """
        Validasi lengkap field mahasiswa.
        Return: dict error {field: pesan_error}, kosong jika valid.
        """
        errors = {}

        try:
            # ── NIM ────────────────────────────────────────────────────────────
            nim = self.data.get("nim", "")
            if not nim:
                errors["nim"] = "NIM wajib diisi."
            elif not self.POLA["nim"].match(nim):
                errors["nim"] = "NIM harus berupa 8–12 digit angka."

            # ── Nama ───────────────────────────────────────────────────────────
            nama = self.data.get("nama", "")
            if not nama:
                errors["nama"] = "Nama wajib diisi."
            elif not self.POLA["nama"].match(nama):
                errors["nama"] = "Nama hanya boleh mengandung huruf dan spasi (2–100 karakter)."

            # ── Email ──────────────────────────────────────────────────────────
            email = self.data.get("email", "")
            if not email:
                errors["email"] = "Email wajib diisi."
            elif not self.POLA["email"].match(email):
                errors["email"] = "Format email tidak valid (contoh: nama@domain.com)."

            # ── Program Studi ──────────────────────────────────────────────────
            prodi = self.data.get("prodi", "")
            if not prodi or len(prodi.strip()) < 2:
                errors["prodi"] = "Program studi wajib diisi (minimal 2 karakter)."

            # ── Angkatan ───────────────────────────────────────────────────────
            angkatan = self.data.get("angkatan", "")
            if not angkatan:
                errors["angkatan"] = "Angkatan wajib diisi."
            elif not self.POLA["angkatan"].match(angkatan):
                errors["angkatan"] = "Angkatan harus berupa tahun 4 digit (misal: 2022)."
            else:
                tahun_sekarang = datetime.now().year
                tahun = int(angkatan)
                if tahun < 2000 or tahun > tahun_sekarang:
                    errors["angkatan"] = f"Angkatan harus antara 2000 – {tahun_sekarang}."

            # ── IPK ────────────────────────────────────────────────────────────
            ipk_str = self.data.get("ipk", "")
            if not ipk_str:
                errors["ipk"] = "IPK wajib diisi."
            elif not self.POLA["ipk"].match(str(ipk_str)):
                errors["ipk"] = "IPK harus berupa angka desimal 0.00 – 4.00."
            else:
                try:
                    ipk_val = float(ipk_str)
                    if not (0.0 <= ipk_val <= 4.0):
                        errors["ipk"] = "IPK harus antara 0.00 dan 4.00."
                except ValueError:
                    errors["ipk"] = "IPK harus berupa angka."

            # ── No Telpon ──────────────────────────────────────────────────────
            no_telp = self.data.get("no_telp", "")
            if not no_telp:
                errors["no_telp"] = "Nomor telepon wajib diisi."
            elif not self.POLA["no_telp"].match(no_telp):
                errors["no_telp"] = "Format nomor telepon tidak valid (contoh: 081234567890)."

            # ── Alamat ─────────────────────────────────────────────────────────
            alamat = self.data.get("alamat", "")
            if not alamat or len(alamat.strip()) < 5:
                errors["alamat"] = "Alamat wajib diisi (minimal 5 karakter)."
            elif len(alamat) > 300:
                errors["alamat"] = "Alamat terlalu panjang (maksimal 300 karakter)."

        except Exception as e:
            errors["_system"] = f"Kesalahan sistem validasi: {str(e)}"

        return errors
