import os
import pymysql
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "db_fiskal_samsat")

def create_database():
    """Membuat database MySQL db_fiskal_samsat jika belum ada"""
    print(f"[*] Menghubungkan ke MySQL Server ({DB_HOST}:{DB_PORT})...")
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        charset="utf8mb4"
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    print(f"[+] Database `{DB_NAME}` berhasil diperiksa/dibuat.")
    cursor.close()
    conn.close()

def seed_data():
    """Membuat tabel dan mengisi data awal (dummy users & dummy fiskal)"""
    from flask import Flask
    from config import Config
    from models import db, User, FiskalDocument, AuditLog

    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # Pastikan folder upload dokumen tersedia
    upload_dir = Config.UPLOAD_FOLDER
    os.makedirs(upload_dir, exist_ok=True)

    # Buat file gambar contoh dummy dokumen fiskal jika belum ada
    sample_doc_1 = os.path.join(upload_dir, "sample_fiskal_bk1234aa.txt")
    sample_doc_2 = os.path.join(upload_dir, "sample_fiskal_bk5678bb.txt")
    sample_doc_3 = os.path.join(upload_dir, "sample_fiskal_bk9999zz.txt")

    for path, content in [
        (sample_doc_1, "DOKUMEN FISKAL RESMI SAMSAT MEDAN SELATAN\nNo Surat: 001/FSK/MSL/2026\nNo Polisi: BK 1234 AA\nNama: Budi Santoso\nStatus: Terverifikasi"),
        (sample_doc_2, "DOKUMEN FISKAL RESMI SAMSAT MEDAN SELATAN\nNo Surat: 002/FSK/MSL/2026\nNo Polisi: BK 5678 BB\nNama: Siti Rahmawati\nStatus: Belum Terverifikasi"),
        (sample_doc_3, "DOKUMEN FISKAL RESMI SAMSAT MEDAN SELATAN\nNo Surat: 003/FSK/MSL/2026\nNo Polisi: BK 9999 ZZ\nNama: Hendra Wijaya\nStatus: Belum Terverifikasi"),
    ]:
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

    with app.app_context():
        print("[*] Membuat tabel-tabel di database MySQL...")
        db.create_all()
        print("[+] Seluruh tabel berhasil dibuat!")

        # 1. Buat Pengguna Dummy jika belum ada
        admin_user = User.query.filter_by(username="admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                nama_lengkap="Administrator Tata Usaha",
                role="Admin"
            )
            admin_user.set_password("admin123")
            db.session.add(admin_user)
            print("[+] Akun dummy dibuat: username=admin, password=admin123 (Role: Admin)")

        petugas_user = User.query.filter_by(username="petugas").first()
        if not petugas_user:
            petugas_user = User(
                username="petugas",
                nama_lengkap="Petugas Arsip Fiskal",
                role="Petugas"
            )
            petugas_user.set_password("petugas123")
            db.session.add(petugas_user)
            print("[+] Akun dummy dibuat: username=petugas, password=petugas123 (Role: Petugas)")

        db.session.commit()

        # 2. Buat Dokumen Fiskal Dummy jika tabel masih kosong
        if FiskalDocument.query.count() == 0:
            doc1 = FiskalDocument(
                nomor_surat="001/FSK/MSL/2026",
                nomor_polisi="BK 1234 AA",
                nama_pemilik="Budi Santoso",
                alamat="Jl. Sisingamangaraja No. 45, Medan",
                merk_type="Toyota Avanza 1.3 G",
                tahun_kendaraan="2020",
                cc_kendaraan="1300",
                warna="Hitam Metalik",
                nomor_rangka="MHFM1BA3JK1234567",
                nomor_mesin="1NR-FE-9876543",
                nomor_stnk="08765432",
                nomor_kohir="K-2026-0045",
                nama_pemohon="Budi Santoso",
                daerah_mutasi="Deli Serdang",
                tanggal_fiskal=date(2026, 1, 15),
                kategori_fiskal="Fiskal Sumatera Utara",
                file_path="sample_fiskal_bk1234aa.txt",
                file_name="arsip_fiskal_bk1234aa.txt",
                file_type="txt",
                status_verifikasi="Terverifikasi",
                verified_by=admin_user.id,
                verified_at=datetime(2026, 1, 16, 10, 30, 0)
            )

            doc2 = FiskalDocument(
                nomor_surat="002/FSK/MSL/2026",
                nomor_polisi="BK 5678 BB",
                nama_pemilik="Siti Rahmawati",
                alamat="Jl. Brigjend Katamso No. 88, Medan",
                merk_type="Honda Vario 160",
                tahun_kendaraan="2022",
                cc_kendaraan="160",
                warna="Merah Doff",
                nomor_rangka="MH1KF1111NK234567",
                nomor_mesin="KF11E-1234567",
                nomor_stnk="09871234",
                nomor_kohir=None,  # Nomor kohir kosong / tidak ada
                nama_pemohon="Ahmad Fauzi (Kuasa)",
                daerah_mutasi="Pekanbaru, Riau",
                tanggal_fiskal=date(2026, 2, 10),
                kategori_fiskal="Fiskal Provinsi",
                file_path="sample_fiskal_bk5678bb.txt",
                file_name="scan_fiskal_bk5678bb.txt",
                file_type="txt",
                status_verifikasi="Belum Terverifikasi"
            )

            doc3 = FiskalDocument(
                nomor_surat="003/FSK/MSL/2026",
                nomor_polisi="BK 9999 ZZ",
                nama_pemilik="Hendra Wijaya",
                alamat="Jl. Juanda No. 12, Medan",
                merk_type="Mitsubishi Pajero Sport Dakar",
                tahun_kendaraan="2023",
                cc_kendaraan="2400",
                warna="Putih Mutiara",
                nomor_rangka="MMBJRKL88PH999999",
                nomor_mesin="4N15-U765432",
                nomor_stnk="11223344",
                nomor_kohir="K-2026-0089",
                nama_pemohon="Hendra Wijaya",
                daerah_mutasi="Binjai",
                tanggal_fiskal=date(2026, 3, 5),
                kategori_fiskal="Fiskal Sumatera Utara",
                file_path="sample_fiskal_bk9999zz.txt",
                file_name="dokumen_fiskal_bk9999zz.txt",
                file_type="txt",
                status_verifikasi="Belum Terverifikasi"
            )

            db.session.add_all([doc1, doc2, doc3])
            db.session.commit()

            # Tambah Audit Log Awal
            log1 = AuditLog(
                document_id=doc1.id,
                user_id=admin_user.id,
                action="VERIFIKASI",
                catatan="Data diverifikasi sesuai dokumen fisik asli."
            )
            log2 = AuditLog(
                document_id=doc2.id,
                user_id=petugas_user.id,
                action="UPLOAD",
                catatan="Dokumen diunggah oleh petugas, menunggu pemeriksaan admin."
            )
            log3 = AuditLog(
                document_id=doc3.id,
                user_id=petugas_user.id,
                action="UPLOAD",
                catatan="Dokumen diunggah oleh petugas, menunggu pemeriksaan admin."
            )
            db.session.add_all([log1, log2, log3])
            db.session.commit()
            print("[+] 3 Dokumen fiskal simulasi dan log audit berhasil ditambahkan!")

    print("[SUCCESS] Inisialisasi Database Selesai!")

if __name__ == "__main__":
    create_database()
    seed_data()
