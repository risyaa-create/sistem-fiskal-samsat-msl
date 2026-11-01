import os
import uuid
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect, url_for, flash, send_from_directory, abort
)
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)
from werkzeug.utils import secure_filename

from config import Config
from models import db, User, FiskalDocument, AuditLog

app = Flask(__name__)
app.config.from_object(Config)

# Inisialisasi Database & Login Manager
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Silakan login terlebih dahulu untuk mengakses sistem."
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

import socket

def allowed_file(filename):
    """Cek apakah ekstensi file diizinkan"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@app.context_processor
def inject_network_ip():
    """Menyediakan IP lokal aktif untuk ditampilkan di template web"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception:
        ip = "127.0.0.1"
    return dict(network_ip=ip)


# ==========================================
# ROUTE AUTENTIKASI (LOGIN, REGISTER, LOGOUT)
# ==========================================

@app.route("/register", methods=["GET", "POST"])
def register():
    """Pendaftaran Akun Baru Petugas Tata Usaha"""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        nama_lengkap = request.form.get("nama_lengkap", "").strip()
        password = request.form.get("password", "")
        konfirmasi_password = request.form.get("konfirmasi_password", "")

        if not (username and nama_lengkap and password and konfirmasi_password):
            flash("Semua field wajib diisi.", "danger")
            return render_template("auth/register.html")

        if len(password) < 6:
            flash("Password minimal harus 6 karakter.", "danger")
            return render_template("auth/register.html")

        if password != konfirmasi_password:
            flash("Konfirmasi password tidak cocok dengan password yang dimasukkan.", "danger")
            return render_template("auth/register.html")

        # Cek apakah username sudah dipakai
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash(f"Username '{username}' sudah terdaftar. Silakan pilih username lain atau login.", "danger")
            return render_template("auth/register.html")

        # Buat akun petugas baru
        new_user = User(
            username=username,
            nama_lengkap=nama_lengkap,
            role="Petugas"
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Pendaftaran akun berhasil! Silakan masuk menggunakan username dan password Anda.", "success")
        return redirect(url_for("login"))

    return render_template("auth/register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f"Selamat datang, {user.nama_lengkap} ({user.role})!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))
        else:
            flash("Username atau password salah. Silakan coba lagi.", "danger")

    return render_template("auth/login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Anda telah berhasil logout.", "info")
    return redirect(url_for("login"))


# ==========================================
# ROUTE DASHBOARD
# ==========================================

@app.route("/")
@login_required
def dashboard():
    # Hitung statistik dokumen aktif (hanya yang belum di-soft delete)
    total_dokumen = FiskalDocument.query.filter_by(is_deleted=False).count()
    belum_verifikasi = FiskalDocument.query.filter_by(is_deleted=False, status_verifikasi="Belum Terverifikasi").count()
    terverifikasi = FiskalDocument.query.filter_by(is_deleted=False, status_verifikasi="Terverifikasi").count()
    fiskal_sumut = FiskalDocument.query.filter_by(is_deleted=False, kategori_fiskal="Fiskal Sumatera Utara").count()
    fiskal_provinsi = FiskalDocument.query.filter_by(is_deleted=False, kategori_fiskal="Fiskal Provinsi").count()

    # Ambil 5 dokumen aktif terbaru
    dokumen_terbaru = (
        FiskalDocument.query.filter_by(is_deleted=False)
        .order_by(FiskalDocument.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard.html",
        total_dokumen=total_dokumen,
        belum_verifikasi=belum_verifikasi,
        terverifikasi=terverifikasi,
        fiskal_sumut=fiskal_sumut,
        fiskal_provinsi=fiskal_provinsi,
        dokumen_terbaru=dokumen_terbaru
    )


# ==========================================
# ROUTE DAFTAR & PENCARIAN DATA FISKAL
# ==========================================

@app.route("/fiskal")
@login_required
def fiskal_index():
    query = request.args.get("q", "").strip()
    kategori = request.args.get("kategori", "").strip()
    status = request.args.get("status", "").strip()

    # Hanya tampilkan dokumen aktif (bukan soft deleted)
    fiskal_query = FiskalDocument.query.filter_by(is_deleted=False)

    # Filter Kategori Fiskal
    if kategori:
        fiskal_query = fiskal_query.filter(FiskalDocument.kategori_fiskal == kategori)

    # Filter Status Verifikasi
    if status:
        fiskal_query = fiskal_query.filter(FiskalDocument.status_verifikasi == status)

    # Pencarian Kata Kunci Multi-Kriteria
    if query:
        search_pattern = f"%{query}%"
        fiskal_query = fiskal_query.filter(
            db.or_(
                FiskalDocument.nomor_polisi.ilike(search_pattern),
                FiskalDocument.nomor_surat.ilike(search_pattern),
                FiskalDocument.nomor_rangka.ilike(search_pattern),
                FiskalDocument.nomor_mesin.ilike(search_pattern),
                FiskalDocument.nama_pemilik.ilike(search_pattern),
                FiskalDocument.daerah_mutasi.ilike(search_pattern),
            )
        )

    # Urutkan berdasarkan yang paling baru dibuat
    dokumen_list = fiskal_query.order_by(FiskalDocument.created_at.desc()).all()

    return render_template(
        "fiskal/index.html",
        dokumen_list=dokumen_list,
        query=query,
        kategori=kategori,
        status=status,
        total_hasil=len(dokumen_list)
    )


# ==========================================
# ROUTE TAMBAH / UPLOAD DATA FISKAL
# ==========================================

@app.route("/fiskal/create", methods=["GET", "POST"])
@login_required
def fiskal_create():
    if request.method == "POST":
        # 1. Validasi Berkas Dokumen Fisik
        if "dokumen_file" not in request.files:
            flash("Silakan pilih file dokumen fisik untuk diunggah.", "danger")
            return redirect(request.url)

        file = request.files["dokumen_file"]
        if file.filename == "":
            flash("File dokumen fisik belum dipilih.", "danger")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("Format file tidak didukung. Harap unggah format JPG, JPEG, PNG, atau PDF.", "danger")
            return redirect(request.url)

        # 2. Ambil 16 Field Data Fiskal dari Form
        nomor_surat = request.form.get("nomor_surat", "").strip()
        nomor_polisi = request.form.get("nomor_polisi", "").strip().upper()
        nama_pemilik = request.form.get("nama_pemilik", "").strip()
        alamat = request.form.get("alamat", "").strip()
        merk_type = request.form.get("merk_type", "").strip()
        tahun_kendaraan = request.form.get("tahun_kendaraan", "").strip()
        cc_kendaraan = request.form.get("cc_kendaraan", "").strip()
        warna = request.form.get("warna", "").strip()
        nomor_rangka = request.form.get("nomor_rangka", "").strip().upper()
        nomor_mesin = request.form.get("nomor_mesin", "").strip().upper()
        nomor_stnk = request.form.get("nomor_stnk", "").strip()
        nomor_kohir = request.form.get("nomor_kohir", "").strip() or None
        nama_pemohon = request.form.get("nama_pemohon", "").strip()
        daerah_mutasi = request.form.get("daerah_mutasi", "").strip()
        tanggal_fiskal_raw = request.form.get("tanggal_fiskal", "").strip()
        kategori_fiskal = request.form.get("kategori_fiskal", "").strip()

        # Validasi field wajib
        if not (nomor_surat and nomor_polisi and nama_pemilik and alamat and
                merk_type and tahun_kendaraan and cc_kendaraan and warna and
                nomor_rangka and nomor_mesin and nomor_stnk and nama_pemohon and
                daerah_mutasi and tanggal_fiskal_raw and kategori_fiskal):
            flash("Semua field wajib diisi kecuali Nomor Kohir jika tidak ada.", "danger")
            return render_template("fiskal/create.html", form_data=request.form)

        # Cek duplikasi Nomor Surat (hanya periksa data yang aktif/belum dihapus)
        if FiskalDocument.query.filter_by(nomor_surat=nomor_surat, is_deleted=False).first():
            flash(f"Nomor Surat '{nomor_surat}' sudah terdaftar dalam sistem.", "danger")
            return render_template("fiskal/create.html", form_data=request.form)

        # Parsing tanggal
        try:
            tanggal_fiskal = datetime.strptime(tanggal_fiskal_raw, "%Y-%m-%d").date()
        except ValueError:
            flash("Format tanggal fiskal tidak valid.", "danger")
            return render_template("fiskal/create.html", form_data=request.form)

        # 3. Simpan File Asli ke Direktori Uploads
        orig_filename = secure_filename(file.filename)
        file_ext = orig_filename.rsplit(".", 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}_{orig_filename}"
        file_save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        file.save(file_save_path)

        # 4. Simpan ke Database dengan Status Awal 'Belum Terverifikasi'
        fiskal_doc = FiskalDocument(
            nomor_surat=nomor_surat,
            nomor_polisi=nomor_polisi,
            nama_pemilik=nama_pemilik,
            alamat=alamat,
            merk_type=merk_type,
            tahun_kendaraan=tahun_kendaraan,
            cc_kendaraan=cc_kendaraan,
            warna=warna,
            nomor_rangka=nomor_rangka,
            nomor_mesin=nomor_mesin,
            nomor_stnk=nomor_stnk,
            nomor_kohir=nomor_kohir,
            nama_pemohon=nama_pemohon,
            daerah_mutasi=daerah_mutasi,
            tanggal_fiskal=tanggal_fiskal,
            kategori_fiskal=kategori_fiskal,
            file_path=unique_filename,
            file_name=orig_filename,
            file_type=file_ext,
            status_verifikasi="Belum Terverifikasi",
            is_deleted=False
        )

        db.session.add(fiskal_doc)
        db.session.commit()

        # 5. Catat Log Audit
        log = AuditLog(
            document_id=fiskal_doc.id,
            user_id=current_user.id,
            action="UPLOAD",
            catatan=f"Dokumen fiskal nomor {nomor_surat} ({nomor_polisi}) diunggah oleh {current_user.nama_lengkap} dan disimpan sebagai Belum Terverifikasi."
        )
        db.session.add(log)
        db.session.commit()

        flash(
            f"Dokumen fiskal untuk kendaraan {nomor_polisi} berhasil disimpan! Status: Belum Terverifikasi.",
            "success"
        )
        return redirect(url_for("fiskal_detail", id=fiskal_doc.id))

    return render_template("fiskal/create.html", form_data={})


# ==========================================
# ROUTE DETAIL & PRATINJAU DOKUMEN FISKAL
# ==========================================

@app.route("/fiskal/<int:id>")
@login_required
def fiskal_detail(id):
    dokumen = FiskalDocument.query.get_or_404(id)
    logs = AuditLog.query.filter_by(document_id=dokumen.id).order_by(AuditLog.created_at.desc()).all()
    return render_template("fiskal/detail.html", dokumen=dokumen, logs=logs)


# ==========================================
# ROUTE EDIT DATA FISKAL
# ==========================================

@app.route("/fiskal/<int:id>/edit", methods=["GET", "POST"])
@login_required
def fiskal_edit(id):
    dokumen = FiskalDocument.query.get_or_404(id)

    if dokumen.is_deleted:
        flash("Dokumen fiskal ini telah diarsipkan/dihapus sehingga tidak dapat diubah.", "warning")
        return redirect(url_for("fiskal_detail", id=dokumen.id))

    if request.method == "POST":
        # 1. Ambil input 16 field dari form
        new_nomor_surat = request.form.get("nomor_surat", "").strip()
        new_nomor_polisi = request.form.get("nomor_polisi", "").strip().upper()
        new_nama_pemilik = request.form.get("nama_pemilik", "").strip()
        new_alamat = request.form.get("alamat", "").strip()
        new_merk_type = request.form.get("merk_type", "").strip()
        new_tahun_kendaraan = request.form.get("tahun_kendaraan", "").strip()
        new_cc_kendaraan = request.form.get("cc_kendaraan", "").strip()
        new_warna = request.form.get("warna", "").strip()
        new_nomor_rangka = request.form.get("nomor_rangka", "").strip().upper()
        new_nomor_mesin = request.form.get("nomor_mesin", "").strip().upper()
        new_nomor_stnk = request.form.get("nomor_stnk", "").strip()
        new_nomor_kohir = request.form.get("nomor_kohir", "").strip() or None
        new_nama_pemohon = request.form.get("nama_pemohon", "").strip()
        new_daerah_mutasi = request.form.get("daerah_mutasi", "").strip()
        new_tanggal_raw = request.form.get("tanggal_fiskal", "").strip()
        new_kategori_fiskal = request.form.get("kategori_fiskal", "").strip()

        # Validasi wajib isi
        if not (new_nomor_surat and new_nomor_polisi and new_nama_pemilik and new_alamat and
                new_merk_type and new_tahun_kendaraan and new_cc_kendaraan and new_warna and
                new_nomor_rangka and new_nomor_mesin and new_nomor_stnk and new_nama_pemohon and
                new_daerah_mutasi and new_tanggal_raw and new_kategori_fiskal):
            flash("Seluruh 16 field wajib diisi kecuali Nomor Kohir jika tidak ada.", "danger")
            return render_template("fiskal/edit.html", dokumen=dokumen)

        # Cek duplikasi Nomor Surat dengan dokumen lain
        duplikat = FiskalDocument.query.filter(
            FiskalDocument.nomor_surat == new_nomor_surat,
            FiskalDocument.id != dokumen.id,
            FiskalDocument.is_deleted == False
        ).first()
        if duplikat:
            flash(f"Nomor Surat '{new_nomor_surat}' sudah digunakan oleh dokumen lain ({duplikat.nomor_polisi}).", "danger")
            return render_template("fiskal/edit.html", dokumen=dokumen)

        # Parsing tanggal
        try:
            new_tanggal_fiskal = datetime.strptime(new_tanggal_raw, "%Y-%m-%d").date()
        except ValueError:
            flash("Format tanggal fiskal tidak valid.", "danger")
            return render_template("fiskal/edit.html", dokumen=dokumen)

        # 2. Deteksi Perubahan Data untuk Dicatat di Audit Log
        perubahan = []
        field_map = [
            ("Nomor Surat", dokumen.nomor_surat, new_nomor_surat),
            ("Nomor Polisi", dokumen.nomor_polisi, new_nomor_polisi),
            ("Nama Pemilik", dokumen.nama_pemilik, new_nama_pemilik),
            ("Alamat", dokumen.alamat, new_alamat),
            ("Merk/Type", dokumen.merk_type, new_merk_type),
            ("Tahun Kendaraan", dokumen.tahun_kendaraan, new_tahun_kendaraan),
            ("CC Kendaraan", dokumen.cc_kendaraan, new_cc_kendaraan),
            ("Warna", dokumen.warna, new_warna),
            ("Nomor Rangka", dokumen.nomor_rangka, new_nomor_rangka),
            ("Nomor Mesin", dokumen.nomor_mesin, new_nomor_mesin),
            ("Nomor STNK", dokumen.nomor_stnk, new_nomor_stnk),
            ("Nomor Kohir", dokumen.nomor_kohir or "(Kosong)", new_nomor_kohir or "(Kosong)"),
            ("Nama Pemohon/Perwakilan", dokumen.nama_pemohon, new_nama_pemohon),
            ("Daerah Mutasi", dokumen.daerah_mutasi, new_daerah_mutasi),
            ("Tanggal Fiskal", dokumen.tanggal_fiskal.strftime('%Y-%m-%d'), new_tanggal_raw),
            ("Kategori Fiskal", dokumen.kategori_fiskal, new_kategori_fiskal),
        ]

        for label, lama, baru in field_map:
            if str(lama).strip() != str(baru).strip():
                perubahan.append(f"{label}: '{lama}' → '{baru}'")

        # 3. Cek jika ada pergantian berkas dokumen asli (opsional)
        file = request.files.get("dokumen_file")
        if file and file.filename != "":
            if not allowed_file(file.filename):
                flash("Format file baru tidak didukung. Harap unggah format JPG, JPEG, PNG, atau PDF.", "danger")
                return render_template("fiskal/edit.html", dokumen=dokumen)
            
            orig_filename = secure_filename(file.filename)
            file_ext = orig_filename.rsplit(".", 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}_{orig_filename}"
            file_save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
            file.save(file_save_path)

            perubahan.append(f"Berkas Dokumen: '{dokumen.file_name}' diganti dengan '{orig_filename}'")
            dokumen.file_path = unique_filename
            dokumen.file_name = orig_filename
            dokumen.file_type = file_ext

        # 4. Simpan Perubahan ke Database
        dokumen.nomor_surat = new_nomor_surat
        dokumen.nomor_polisi = new_nomor_polisi
        dokumen.nama_pemilik = new_nama_pemilik
        dokumen.alamat = new_alamat
        dokumen.merk_type = new_merk_type
        dokumen.tahun_kendaraan = new_tahun_kendaraan
        dokumen.cc_kendaraan = new_cc_kendaraan
        dokumen.warna = new_warna
        dokumen.nomor_rangka = new_nomor_rangka
        dokumen.nomor_mesin = new_nomor_mesin
        dokumen.nomor_stnk = new_nomor_stnk
        dokumen.nomor_kohir = new_nomor_kohir
        dokumen.nama_pemohon = new_nama_pemohon
        dokumen.daerah_mutasi = new_daerah_mutasi
        dokumen.tanggal_fiskal = new_tanggal_fiskal
        dokumen.kategori_fiskal = new_kategori_fiskal
        dokumen.updated_at = datetime.utcnow()

        # 5. Catat Log Audit jika ada perubahan
        if perubahan:
            catatan_log = f"Perubahan oleh {current_user.nama_lengkap} ({current_user.role}): " + "; ".join(perubahan)
            log = AuditLog(
                document_id=dokumen.id,
                user_id=current_user.id,
                action="EDIT",
                catatan=catatan_log
            )
            db.session.add(log)
            db.session.commit()
            flash(f"Data fiskal kendaraan {dokumen.nomor_polisi} berhasil diperbarui!", "success")
        else:
            flash("Tidak ada perubahan data yang dilakukan.", "info")

        return redirect(url_for("fiskal_detail", id=dokumen.id))

    return render_template("fiskal/edit.html", dokumen=dokumen)


# ==========================================
# ROUTE HAPUS DATA FISKAL (SOFT DELETE)
# ==========================================

@app.route("/fiskal/<int:id>/delete", methods=["POST"])
@app.route("/fiskal/<int:id>/hapus", methods=["POST"])
@login_required
def fiskal_delete(id):
    """
    Menghapus data fiskal menggunakan mekanisme Soft Delete (Pengarsipan).
    Dapat diakses oleh seluruh petugas tata usaha yang berwenang.
    """
    dokumen = FiskalDocument.query.get_or_404(id)

    if dokumen.is_deleted:
        flash("Dokumen fiskal ini sudah diarsipkan/dihapus sebelumnya.", "info")
        return redirect(url_for("fiskal_index"))

    # Lakukan mekanisme Soft Delete
    dokumen.is_deleted = True
    dokumen.deleted_at = datetime.utcnow()
    dokumen.deleted_by = current_user.id

    # Catat aksi penghapusan ke audit log
    log = AuditLog(
        document_id=dokumen.id,
        user_id=current_user.id,
        action="HAPUS",
        catatan=f"Dokumen fiskal No. Surat {dokumen.nomor_surat} (Plat {dokumen.nomor_polisi}) diarsipkan/dihapus oleh {current_user.nama_lengkap} ({current_user.role})."
    )
    db.session.add(log)
    db.session.commit()

    flash(
        f"Dokumen fiskal kendaraan {dokumen.nomor_polisi} berhasil dihapus/diarsipkan dari daftar aktif.",
        "success"
    )
    return redirect(url_for("fiskal_index"))


# ==========================================
# ROUTE VERIFIKASI DOKUMEN
# ==========================================

@app.route("/fiskal/<int:id>/verifikasi", methods=["POST"])
@login_required
def fiskal_verifikasi(id):
    dokumen = FiskalDocument.query.get_or_404(id)

    if dokumen.is_deleted:
        flash("Dokumen fiskal yang telah diarsipkan/dihapus tidak dapat diverifikasi.", "warning")
        return redirect(url_for("fiskal_detail", id=dokumen.id))

    if dokumen.status_verifikasi == "Terverifikasi":
        flash("Dokumen fiskal ini sudah terverifikasi sebelumnya.", "info")
        return redirect(url_for("fiskal_detail", id=dokumen.id))

    # Ubah status menjadi terverifikasi
    dokumen.status_verifikasi = "Terverifikasi"
    dokumen.verified_by = current_user.id
    dokumen.verified_at = datetime.utcnow()

    # Catat ke audit log
    log = AuditLog(
        document_id=dokumen.id,
        user_id=current_user.id,
        action="VERIFIKASI",
        catatan=f"Data fisik dan data sistem telah dicocokkan dan diverifikasi resmi oleh {current_user.nama_lengkap} ({current_user.role})."
    )
    db.session.add(log)
    db.session.commit()

    flash(f"Dokumen fiskal {dokumen.nomor_polisi} berhasil diverifikasi menjadi data resmi!", "success")
    return redirect(url_for("fiskal_detail", id=dokumen.id))


# ==========================================
# ROUTE AKSES / DOWNLOAD BERKAS DOKUMEN ASLI
# ==========================================

@app.route("/documents/<path:filename>")
@login_required
def serve_document(filename):
    """Menampilkan atau mengunduh file asli dokumen fiskal"""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":
    # Host 0.0.0.0 agar aplikasi dapat diakses dari laptop/perangkat lain dalam satu jaringan WiFi/LAN
    app.run(host="0.0.0.0", port=5000, debug=True)
