"""
utils/mahasiswa.py
Kelas Mahasiswa — representasi entitas data mahasiswa (Model / OOP).
Menggunakan __slots__ untuk efisiensi memori dan property untuk enkapsulasi.
"""


class Mahasiswa:
    """
    Model data mahasiswa.
    Atribut divalidasi saat assignment menggunakan property.
    """

    __slots__ = ("_nim", "_nama", "_email", "_prodi",
                 "_angkatan", "_ipk", "_no_telp", "_alamat")

    def __init__(self, nim: str, nama: str, email: str, prodi: str,
                 angkatan: str, ipk, no_telp: str, alamat: str):
        self._nim      = nim.strip().upper()
        self._nama     = nama.strip().title()
        self._email    = email.strip().lower()
        self._prodi    = prodi.strip()
        self._angkatan = str(angkatan).strip()
        self._ipk      = float(ipk)
        self._no_telp  = no_telp.strip()
        self._alamat   = alamat.strip()

    # ── Properties ─────────────────────────────────────────────────────────────
    @property
    def nim(self):      return self._nim
    @property
    def nama(self):     return self._nama
    @property
    def email(self):    return self._email
    @property
    def prodi(self):    return self._prodi
    @property
    def angkatan(self): return self._angkatan
    @property
    def ipk(self):      return self._ipk
    @property
    def no_telp(self):  return self._no_telp
    @property
    def alamat(self):   return self._alamat

    # ── Representasi ───────────────────────────────────────────────────────────
    def __repr__(self):
        return f"<Mahasiswa nim={self._nim} nama={self._nama}>"

    def to_dict(self) -> dict:
        return {
            "nim"     : self._nim,
            "nama"    : self._nama,
            "email"   : self._email,
            "prodi"   : self._prodi,
            "angkatan": self._angkatan,
            "ipk"     : self._ipk,
            "no_telp" : self._no_telp,
            "alamat"  : self._alamat,
        }
