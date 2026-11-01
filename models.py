from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Tabel Pengguna / Petugas SAMSAT"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    nama_lengkap = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='Petugas', nullable=False)  # 'Admin' / 'Petugas'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relasi dengan penentuan foreign_keys yang eksplisit
    verifikasi_dokumen = db.relationship(
        'FiskalDocument',
        foreign_keys='FiskalDocument.verified_by',
        backref='verifier',
        lazy=True
    )
    hapus_dokumen = db.relationship(
        'FiskalDocument',
        foreign_keys='FiskalDocument.deleted_by',
        backref='deleter',
        lazy=True
    )
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username} - {self.role}>"


class FiskalDocument(db.Model):
    """
    Tabel Data Fiskal Mutasi Kendaraan (Satu kesatuan data fiskal lengkap)
    Menampung seluruh 16 field resmi dokumen fiskal + metadata sistem untuk file & status.
    """
    __tablename__ = 'fiskal_documents'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # ================= 16 FIELD DATA FISKAL RESMI =================
    # 1. Nomor Surat
    nomor_surat = db.Column(db.String(100), unique=True, nullable=False, index=True)

    # 2. Nomor Polisi
    nomor_polisi = db.Column(db.String(20), nullable=False, index=True)

    # 3. Nama Pemilik
    nama_pemilik = db.Column(db.String(150), nullable=False)

    # 4. Alamat
    alamat = db.Column(db.Text, nullable=False)

    # 5. Merk/Type Kendaraan
    merk_type = db.Column(db.String(100), nullable=False)

    # 6. Tahun Kendaraan
    tahun_kendaraan = db.Column(db.String(10), nullable=False)

    # 7. CC Kendaraan
    cc_kendaraan = db.Column(db.String(20), nullable=False)

    # 8. Warna
    warna = db.Column(db.String(50), nullable=False)

    # 9. Nomor Rangka
    nomor_rangka = db.Column(db.String(100), nullable=False, index=True)

    # 10. Nomor Mesin
    nomor_mesin = db.Column(db.String(100), nullable=False, index=True)

    # 11. Nomor STNK
    nomor_stnk = db.Column(db.String(100), nullable=False)

    # 12. Nomor Kohir (jika ada / nullable)
    nomor_kohir = db.Column(db.String(100), nullable=True)

    # 13. Nama Pemohon/Perwakilan (istilah sementara)
    nama_pemohon = db.Column(db.String(150), nullable=False)

    # 14. Daerah Mutasi
    daerah_mutasi = db.Column(db.String(100), nullable=False)

    # 15. Tanggal Fiskal
    tanggal_fiskal = db.Column(db.Date, nullable=False)

    # 16. Kategori Fiskal ('Fiskal Sumatera Utara' atau 'Fiskal Provinsi')
    kategori_fiskal = db.Column(db.String(50), nullable=False)

    # ================= METADATA SISTEM & BERKAS ASLI =================
    file_path = db.Column(db.String(255), nullable=False)  # Lokasi file fisik relatif di uploads
    file_name = db.Column(db.String(255), nullable=False)  # Nama file asli yang diunggah
    file_type = db.Column(db.String(20), nullable=False)   # 'jpg', 'jpeg', 'png', 'pdf'
    
    # Status Verifikasi: 'Belum Terverifikasi' (default) atau 'Terverifikasi'
    status_verifikasi = db.Column(db.String(50), default='Belum Terverifikasi', nullable=False)
    
    # Data Petugas yang Memverifikasi
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)

    # Soft Delete / Pengarsipan Dokumen
    is_deleted = db.Column(db.Boolean, default=False, nullable=False, index=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # Waktu Pencatatan Sistem
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relasi
    audit_logs = db.relationship('AuditLog', backref='document', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FiskalDocument {self.nomor_surat} - {self.nomor_polisi}>"


class AuditLog(db.Model):
    """Tabel Log Aktivitas Audit Perubahan & Verifikasi Data Fiskal"""
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    document_id = db.Column(db.Integer, db.ForeignKey('fiskal_documents.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(50), nullable=False)  # 'UPLOAD', 'VERIFIKASI', 'EDIT', 'HAPUS'
    catatan = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog {self.action} by User {self.user_id}>"
