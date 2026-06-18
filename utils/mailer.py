"""
utils/mailer.py
Kelas EmailSender — mengirim email ke mahasiswa via Gmail SMTP.
Menggunakan OOP (Object-Oriented Programming) dengan encapsulation.

Konfigurasi diambil dari environment variable:
  - GMAIL_USER          : alamat Gmail pengirim (contoh: namaanda@gmail.com)
  - GMAIL_APP_PASSWORD  : App Password 16 digit dari Google
                          (BUKAN password akun biasa — buat di
                           https://myaccount.google.com/apppasswords)
  - GMAIL_SENDER_NAME   : nama tampilan pengirim (opsional)
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr


class EmailSender:
    """
    Pengelola pengiriman email melalui server SMTP Gmail.
    Single Responsibility: hanya bertugas menyusun & mengirim email.
    """

    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 587

    def __init__(self):
        self.user        = os.environ.get("GMAIL_USER", "").strip()
        self.password    = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
        self.sender_name = os.environ.get("GMAIL_SENDER_NAME", "SUZURAN University").strip()

    # ── Status Konfigurasi ─────────────────────────────────────────────────────
    def is_configured(self) -> bool:
        """True jika kredensial Gmail sudah tersedia di environment."""
        return bool(self.user and self.password)

    # ── Kirim Email ────────────────────────────────────────────────────────────
    def send(self, to_email: str, subject: str, body: str) -> tuple[bool, str]:
        """
        Kirim satu email teks biasa.
        Return: (sukses: bool, pesan: str)
        """
        if not self.is_configured():
            return False, ("Gmail belum dikonfigurasi. Set environment variable "
                           "GMAIL_USER dan GMAIL_APP_PASSWORD terlebih dahulu.")

        if not to_email:
            return False, "Alamat email tujuan kosong."

        try:
            msg = MIMEMultipart()
            msg["From"]    = formataddr((self.sender_name, self.user))
            msg["To"]      = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain", "utf-8"))

            with smtplib.SMTP(self.SMTP_HOST, self.SMTP_PORT, timeout=20) as server:
                server.ehlo()
                server.starttls()
                server.login(self.user, self.password)
                server.sendmail(self.user, [to_email], msg.as_string())

            return True, f"Email berhasil dikirim ke {to_email}."

        except smtplib.SMTPAuthenticationError:
            return False, ("Login Gmail gagal. Pastikan GMAIL_USER benar dan "
                           "GMAIL_APP_PASSWORD adalah App Password (bukan password biasa).")
        except smtplib.SMTPException as e:
            return False, f"Gagal mengirim email (SMTP): {str(e)}"
        except Exception as e:
            return False, f"Terjadi kesalahan saat mengirim email: {str(e)}"
