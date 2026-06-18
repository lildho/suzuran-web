"""
SUZURAN University — Student Data Management System
Tugas Akhir - Manajemen Data Mahasiswa
Framework : Flask (Python)
Database  : SQLite
Author    : (Nama Anda)
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from functools import wraps
import os, time, json, csv, io, re
from datetime import datetime

# Import modul internal (OOP Classes)
from utils.database  import Database
from utils.mahasiswa import Mahasiswa
from utils.algoritma import SearchEngine, SortEngine
from utils.validator  import Validator
from utils.mailer     import EmailSender

# ─── App Config ───────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "suzuran-secret-2025")

db  = Database(os.environ.get("DB_PATH", "suzuran.db"))
db.init_tables()
db.seed_admin()          # Buat akun admin default jika belum ada


# ─── Auth Decorator ───────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ═══════════════════════════════════════════════════════════════════════════════
#  AUTH ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # Validasi input kosong
        if not username or not password:
            error = "Username dan password wajib diisi."
        else:
            try:
                user = db.get_user(username, password)
                if user:
                    session["user_id"]  = user["id"]
                    session["username"] = user["username"]
                    flash(f"Selamat datang, {user['username']}! 👋", "success")
                    return redirect(url_for("dashboard"))
                else:
                    error = "Username atau password salah."
            except Exception as e:
                error = f"Terjadi kesalahan sistem: {str(e)}"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    flash("Anda telah logout.", "info")
    return redirect(url_for("login"))


# ═══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/dashboard")
@login_required
def dashboard():
    stats = db.get_stats()
    return render_template("dashboard.html", stats=stats)


# ═══════════════════════════════════════════════════════════════════════════════
#  CRUD MAHASISWA
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/mahasiswa")
@login_required
def mahasiswa_list():
    page     = request.args.get("page", 1, type=int)
    per_page = 10
    data, total = db.get_mahasiswa_paginated(page, per_page)
    return render_template(
        "mahasiswa/list.html",
        mahasiswa=data,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=(total + per_page - 1) // per_page
    )


@app.route("/mahasiswa/tambah", methods=["GET", "POST"])
@login_required
def mahasiswa_tambah():
    errors = {}
    form_data = {}

    if request.method == "POST":
        form_data = {
            "nim"        : request.form.get("nim", "").strip(),
            "nama"       : request.form.get("nama", "").strip(),
            "email"      : request.form.get("email", "").strip(),
            "prodi"      : request.form.get("prodi", "").strip(),
            "angkatan"   : request.form.get("angkatan", "").strip(),
            "ipk"        : request.form.get("ipk", "").strip(),
            "no_telp"    : request.form.get("no_telp", "").strip(),
            "alamat"     : request.form.get("alamat", "").strip(),
        }

        try:
            # Validasi dengan Regex (OOP Validator)
            v = Validator(form_data)
            errors = v.validate_mahasiswa()

            if not errors:
                # Cek duplikat NIM
                if db.nim_exists(form_data["nim"]):
                    errors["nim"] = "NIM sudah terdaftar."
                else:
                    mhs = Mahasiswa(**form_data)
                    db.insert_mahasiswa(mhs)
                    flash(f"✅ Mahasiswa {mhs.nama} berhasil ditambahkan!", "success")
                    return redirect(url_for("mahasiswa_list"))
        except Exception as e:
            flash(f"❌ Terjadi kesalahan: {str(e)}", "danger")

    return render_template("mahasiswa/form.html", errors=errors, form_data=form_data, mode="tambah")


@app.route("/mahasiswa/edit/<int:id>", methods=["GET", "POST"])
@login_required
def mahasiswa_edit(id):
    mhs_row = db.get_mahasiswa_by_id(id)
    if not mhs_row:
        flash("❌ Data mahasiswa tidak ditemukan.", "danger")
        return redirect(url_for("mahasiswa_list"))

    errors   = {}
    form_data = dict(mhs_row)

    if request.method == "POST":
        form_data = {
            "nim"      : request.form.get("nim", "").strip(),
            "nama"     : request.form.get("nama", "").strip(),
            "email"    : request.form.get("email", "").strip(),
            "prodi"    : request.form.get("prodi", "").strip(),
            "angkatan" : request.form.get("angkatan", "").strip(),
            "ipk"      : request.form.get("ipk", "").strip(),
            "no_telp"  : request.form.get("no_telp", "").strip(),
            "alamat"   : request.form.get("alamat", "").strip(),
        }

        try:
            v = Validator(form_data)
            errors = v.validate_mahasiswa()

            if not errors:
                # Cek duplikat NIM (kecuali milik diri sendiri)
                existing = db.nim_exists(form_data["nim"], exclude_id=id)
                if existing:
                    errors["nim"] = "NIM sudah digunakan mahasiswa lain."
                else:
                    mhs = Mahasiswa(**form_data)
                    db.update_mahasiswa(id, mhs)
                    flash(f"✅ Data {mhs.nama} berhasil diperbarui!", "success")
                    return redirect(url_for("mahasiswa_list"))
        except Exception as e:
            flash(f"❌ Terjadi kesalahan: {str(e)}", "danger")

    return render_template("mahasiswa/form.html", errors=errors, form_data=form_data, mode="edit", id=id)


@app.route("/mahasiswa/hapus/<int:id>", methods=["POST"])
@login_required
def mahasiswa_hapus(id):
    try:
        mhs = db.get_mahasiswa_by_id(id)
        if mhs:
            db.delete_mahasiswa(id)
            flash(f"🗑️ Data {mhs['nama']} berhasil dihapus.", "success")
        else:
            flash("❌ Data tidak ditemukan.", "danger")
    except Exception as e:
        flash(f"❌ Gagal menghapus: {str(e)}", "danger")
    return redirect(url_for("mahasiswa_list"))


@app.route("/mahasiswa/detail/<int:id>")
@login_required
def mahasiswa_detail(id):
    mhs = db.get_mahasiswa_by_id(id)
    if not mhs:
        flash("❌ Data tidak ditemukan.", "danger")
        return redirect(url_for("mahasiswa_list"))
    return render_template("mahasiswa/detail.html", mhs=mhs)


# ═══════════════════════════════════════════════════════════════════════════════
#  KIRIM EMAIL (Gmail SMTP)
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/mahasiswa/email/<int:id>", methods=["GET", "POST"])
@login_required
def mahasiswa_email(id):
    """Halaman kirim email ke satu mahasiswa berdasarkan email yang tercatat."""
    mhs = db.get_mahasiswa_by_id(id)
    if not mhs:
        flash("❌ Data mahasiswa tidak ditemukan.", "danger")
        return redirect(url_for("mahasiswa_list"))

    mailer    = EmailSender()
    form_data = {
        "subject": request.form.get("subject", "").strip(),
        "body"   : request.form.get("body", "").strip(),
    }

    if request.method == "POST":
        if not mailer.is_configured():
            flash("❌ Gmail belum dikonfigurasi (set GMAIL_USER & GMAIL_APP_PASSWORD).", "danger")
        elif not form_data["subject"]:
            flash("❌ Subjek email wajib diisi.", "danger")
        elif not form_data["body"]:
            flash("❌ Isi pesan email wajib diisi.", "danger")
        else:
            sukses, pesan = mailer.send(mhs["email"], form_data["subject"], form_data["body"])
            if sukses:
                flash(f"✅ {pesan}", "success")
                return redirect(url_for("mahasiswa_detail", id=id))
            else:
                flash(f"❌ {pesan}", "danger")

    return render_template(
        "mahasiswa/email.html",
        mhs=mhs,
        form_data=form_data,
        configured=mailer.is_configured(),
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  PENCARIAN (SEARCH ENGINE)
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/pencarian")
@login_required
def pencarian():
    return render_template("pencarian.html")


@app.route("/api/cari", methods=["POST"])
@login_required
def api_cari():
    """
    Endpoint pencarian dengan pilihan algoritma:
    - linear   : Linear / Sequential Search  → O(n)
    - binary   : Binary Search (by NIM)      → O(log n)
    """
    try:
        payload    = request.get_json()
        keyword    = payload.get("keyword", "").strip()
        algoritma  = payload.get("algoritma", "linear")
        field      = payload.get("field", "nama")

        if not keyword:
            return jsonify({"error": "Keyword tidak boleh kosong."}), 400

        semua_data = db.get_all_mahasiswa()
        engine     = SearchEngine(semua_data)

        start_time = time.perf_counter()

        if algoritma == "binary":
            # Binary Search — data harus terurut by NIM
            hasil, langkah = engine.binary_search(keyword)
        else:
            # Linear / Sequential Search
            hasil, langkah = engine.linear_search(keyword, field)

        elapsed = time.perf_counter() - start_time
        n       = len(semua_data)
        complexity = "O(log n)" if algoritma == "binary" else "O(n)"

        # Simpan ke build log
        log_entry = {
            "waktu"      : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "keyword"    : keyword,
            "algoritma"  : algoritma.upper(),
            "field"      : field,
            "jumlah_data": n,
            "hasil"      : len(hasil),
            "durasi_ms"  : round(elapsed * 1000, 4),
            "complexity" : complexity,
            "langkah"    : langkah,
        }
        db.insert_search_log(log_entry)

        return jsonify({
            "hasil"      : hasil,
            "durasi_ms"  : round(elapsed * 1000, 4),
            "durasi_s"   : round(elapsed, 6),
            "jumlah_data": n,
            "langkah"    : langkah,
            "complexity" : complexity,
            "algoritma"  : algoritma,
            "estimasi"   : engine.estimasi_complexity(n, algoritma),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
#  SORTING
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/sorting")
@login_required
def sorting():
    return render_template("sorting.html")


@app.route("/api/sort", methods=["POST"])
@login_required
def api_sort():
    """
    Sorting algoritma:
    - bubble    : Bubble Sort    → O(n²)
    - selection : Selection Sort → O(n²)
    """
    try:
        payload   = request.get_json()
        algoritma = payload.get("algoritma", "bubble")
        field     = payload.get("field", "nama")
        order     = payload.get("order", "asc")

        semua_data = db.get_all_mahasiswa()
        engine     = SortEngine(semua_data)

        start_time = time.perf_counter()

        if algoritma == "selection":
            hasil, steps = engine.selection_sort(field, order)
        else:
            hasil, steps = engine.bubble_sort(field, order)

        elapsed = time.perf_counter() - start_time
        n       = len(semua_data)

        return jsonify({
            "hasil"     : hasil,
            "durasi_ms" : round(elapsed * 1000, 4),
            "durasi_s"  : round(elapsed, 6),
            "langkah"   : steps,
            "complexity": "O(n²)",
            "n"         : n,
            "estimasi"  : engine.estimasi(n),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
#  IMPORT / EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/import-export")
@login_required
def import_export():
    return render_template("import_export.html")


@app.route("/export/csv")
@login_required
def export_csv():
    try:
        data = db.get_all_mahasiswa()
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["nim","nama","email","prodi","angkatan","ipk","no_telp","alamat"])
        writer.writeheader()
        for row in data:
            writer.writerow({k: row[k] for k in ["nim","nama","email","prodi","angkatan","ipk","no_telp","alamat"]})
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode("utf-8")),
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"mahasiswa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
    except Exception as e:
        flash(f"❌ Gagal export CSV: {str(e)}", "danger")
        return redirect(url_for("import_export"))


@app.route("/export/json")
@login_required
def export_json():
    try:
        data = db.get_all_mahasiswa()
        result = [dict(row) for row in data]
        output = json.dumps(result, indent=2, ensure_ascii=False)
        return send_file(
            io.BytesIO(output.encode("utf-8")),
            mimetype="application/json",
            as_attachment=True,
            download_name=f"mahasiswa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
    except Exception as e:
        flash(f"❌ Gagal export JSON: {str(e)}", "danger")
        return redirect(url_for("import_export"))


@app.route("/import/csv", methods=["POST"])
@login_required
def import_csv():
    try:
        file = request.files.get("file")
        if not file or not file.filename.endswith(".csv"):
            flash("❌ Format file harus .csv", "danger")
            return redirect(url_for("import_export"))

        stream  = io.StringIO(file.stream.read().decode("utf-8"))
        reader  = csv.DictReader(stream)
        required_cols = {"nim","nama","email","prodi","angkatan","ipk","no_telp","alamat"}

        if not required_cols.issubset(set(reader.fieldnames or [])):
            flash(f"❌ Kolom CSV tidak lengkap. Harus ada: {', '.join(required_cols)}", "danger")
            return redirect(url_for("import_export"))

        sukses = 0
        gagal  = 0
        errors_list = []

        for i, row in enumerate(reader, start=2):
            try:
                form_data = {k: str(row.get(k,"")).strip() for k in required_cols}
                v = Validator(form_data)
                errs = v.validate_mahasiswa()
                if errs:
                    gagal += 1
                    errors_list.append(f"Baris {i} ({row.get('nim','')}): {'; '.join(errs.values())}")
                    continue
                if db.nim_exists(form_data["nim"]):
                    gagal += 1
                    errors_list.append(f"Baris {i}: NIM {form_data['nim']} sudah ada.")
                    continue
                mhs = Mahasiswa(**form_data)
                db.insert_mahasiswa(mhs)
                sukses += 1
            except Exception as ex:
                gagal += 1
                errors_list.append(f"Baris {i}: {str(ex)}")

        msg = f"✅ Import selesai: {sukses} berhasil, {gagal} gagal."
        if errors_list:
            msg += " Error: " + " | ".join(errors_list[:5])
        flash(msg, "success" if sukses > 0 else "danger")

    except Exception as e:
        flash(f"❌ Gagal membaca file: {str(e)}", "danger")

    return redirect(url_for("import_export"))


@app.route("/import/json", methods=["POST"])
@login_required
def import_json():
    try:
        file = request.files.get("file")
        if not file or not file.filename.endswith(".json"):
            flash("❌ Format file harus .json", "danger")
            return redirect(url_for("import_export"))

        try:
            data = json.load(file.stream)
        except json.JSONDecodeError as je:
            flash(f"❌ File JSON tidak valid: {str(je)}", "danger")
            return redirect(url_for("import_export"))

        if not isinstance(data, list):
            flash("❌ JSON harus berupa array/list objek mahasiswa.", "danger")
            return redirect(url_for("import_export"))

        sukses = 0
        gagal  = 0
        errors_list = []
        required_cols = {"nim","nama","email","prodi","angkatan","ipk","no_telp","alamat"}

        for i, item in enumerate(data, start=1):
            try:
                if not required_cols.issubset(set(item.keys())):
                    gagal += 1
                    errors_list.append(f"Item {i}: Field tidak lengkap.")
                    continue
                form_data = {k: str(item.get(k,"")).strip() for k in required_cols}
                v = Validator(form_data)
                errs = v.validate_mahasiswa()
                if errs:
                    gagal += 1
                    errors_list.append(f"Item {i} ({item.get('nim','')}): {'; '.join(errs.values())}")
                    continue
                if db.nim_exists(form_data["nim"]):
                    gagal += 1
                    errors_list.append(f"Item {i}: NIM {form_data['nim']} sudah ada.")
                    continue
                mhs = Mahasiswa(**form_data)
                db.insert_mahasiswa(mhs)
                sukses += 1
            except Exception as ex:
                gagal += 1
                errors_list.append(f"Item {i}: {str(ex)}")

        msg = f"✅ Import JSON selesai: {sukses} berhasil, {gagal} gagal."
        if errors_list:
            msg += " Error: " + " | ".join(errors_list[:5])
        flash(msg, "success" if sukses > 0 else "danger")

    except Exception as e:
        flash(f"❌ Gagal memproses JSON: {str(e)}", "danger")

    return redirect(url_for("import_export"))


# ═══════════════════════════════════════════════════════════════════════════════
#  BUILD LOG / KOMENTAR
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/log")
@login_required
def search_log():
    logs = db.get_search_logs()
    return render_template("log.html", logs=logs)


@app.route("/api/log/komentar", methods=["POST"])
@login_required
def tambah_komentar():
    try:
        payload  = request.get_json()
        log_id   = payload.get("log_id")
        komentar = payload.get("komentar", "").strip()
        if not komentar:
            return jsonify({"error": "Komentar tidak boleh kosong."}), 400
        db.update_komentar(log_id, komentar)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/log/hapus/<int:log_id>", methods=["DELETE"])
@login_required
def hapus_log(log_id):
    try:
        db.delete_log(log_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
