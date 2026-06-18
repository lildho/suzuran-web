"""
utils/mailer.py
Kelas EmailSender — mengirim email ke mahasiswa via Brevo HTTP API.

Kenapa Brevo HTTP API, bukan SMTP Gmail?
  Banyak platform hosting (mis. Railway) MEMBLOKIR port SMTP (587/465), sehingga
  koneksi smtplib ke Gmail timeout. Brevo mengirim lewat HTTPS (port 443) yang
  tidak diblokir, jadi tetap jalan di hosting.

Environment variable:
  - BREVO_API_KEY     : API key Brevo. Ambil di https://app.brevo.com →
                        menu "SMTP & API" → tab "API Keys" → Generate.
  - MAIL_FROM_EMAIL   : email pengirim — HARUS sudah diverifikasi sebagai
                        "sender" di Brevo. Bila kosong, fallback ke GMAIL_USER.
  - MAIL_FROM_NAME    : nama tampilan pengirim. Bila kosong, fallback ke
                        GMAIL_SENDER_NAME.
"""

import os
import json
import urllib.request
import urllib.error


class EmailSender:
    """
    Pengelola pengiriman email melalui Brevo HTTP API.
    Single Responsibility: hanya menyusun & mengirim email.
    """

    API_URL = "https://api.brevo.com/v3/smtp/email"

    def __init__(self):
        self.api_key    = os.environ.get("BREVO_API_KEY", "").strip()
        # Pengirim: pakai MAIL_FROM_EMAIL, atau fallback ke GMAIL_USER lama.
        self.from_email = (os.environ.get("MAIL_FROM_EMAIL", "")
                           or os.environ.get("GMAIL_USER", "")).strip()
        self.from_name  = (os.environ.get("MAIL_FROM_NAME", "")
                           or os.environ.get("GMAIL_SENDER_NAME", "")
                           or "SUZURAN University").strip()

    # ── Status Konfigurasi ─────────────────────────────────────────────────────
    def is_configured(self) -> bool:
        """True jika API key dan email pengirim sudah tersedia."""
        return bool(self.api_key and self.from_email)

    # ── Kirim Email ────────────────────────────────────────────────────────────
    def send(self, to_email: str, subject: str, body: str) -> tuple[bool, str]:
        """
        Kirim satu email teks biasa via Brevo.
        Return: (sukses: bool, pesan: str)
        """
        if not self.is_configured():
            return False, ("Email belum dikonfigurasi. Set environment variable "
                           "BREVO_API_KEY dan MAIL_FROM_EMAIL (atau GMAIL_USER).")

        if not to_email:
            return False, "Alamat email tujuan kosong."

        payload = {
            "sender"     : {"name": self.from_name, "email": self.from_email},
            "to"         : [{"email": to_email}],
            "subject"    : subject,
            "textContent": body,
        }
        data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(self.API_URL, data=data, method="POST")
        req.add_header("api-key", self.api_key)
        req.add_header("Content-Type", "application/json")
        req.add_header("accept", "application/json")

        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                if 200 <= resp.status < 300:
                    return True, f"Email berhasil dikirim ke {to_email}."
                return False, f"Gagal mengirim email (HTTP {resp.status})."

        except urllib.error.HTTPError as e:
            try:
                detail = e.read().decode("utf-8")
            except Exception:
                detail = ""
            if e.code in (401, 403):
                return False, ("API key Brevo tidak valid atau email pengirim belum "
                               f"diverifikasi sebagai sender di Brevo. Detail: {detail}")
            return False, f"Gagal mengirim email (HTTP {e.code}): {detail}"
        except urllib.error.URLError as e:
            return False, f"Tidak bisa terhubung ke server email: {e.reason}"
        except Exception as e:
            return False, f"Terjadi kesalahan saat mengirim email: {str(e)}"
