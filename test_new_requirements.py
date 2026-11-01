import urllib.request
import urllib.parse
import http.cookiejar
import socket

def test_all():
    print("==================================================")
    print(" PENGUJIAN PERMINTAAN TERBARU SISTEM FISKAL SAMSAT")
    print("==================================================")

    base_url = "http://127.0.0.1:5000"
    
    # 1. Uji Halaman Login (Pastikan tulisan Akun Dummy sudah hilang)
    print("\n[1] Memeriksa Halaman Login (/login)...")
    req = urllib.request.urlopen(f"{base_url}/login")
    assert req.getcode() == 200
    login_html = req.read().decode('utf-8')
    assert "Akun Dummy untuk Pengujian" not in login_html, "Gagal: Teks akun dummy masih muncul!"
    assert "Daftar di sini" in login_html, "Gagal: Tautan pendaftaran akun tidak ditemukan!"
    print("    [+] Sukses: Tulisan akun dummy sudah dihapus dan tautan pendaftaran tersedia.")

    # 2. Uji Halaman Pendaftaran Akun (/register)
    print("\n[2] Memeriksa Halaman Registrasi Petugas (/register)...")
    req_reg = urllib.request.urlopen(f"{base_url}/register")
    assert req_reg.getcode() == 200
    reg_html = req_reg.read().decode('utf-8')
    assert "Pendaftaran Petugas Baru" in reg_html
    print("    [+] Sukses: Halaman pendaftaran akun baru dapat diakses.")

    # 3. Uji Proses Pendaftaran Akun Baru Petugas
    print("\n[3] Mendaftarkan Akun Petugas Baru secara Mandiri...")
    import time
    uname = f"petugas_{int(time.time())}"[-12:]
    reg_payload = urllib.parse.urlencode({
        'username': uname,
        'nama_lengkap': 'Staf Tata Usaha Baru',
        'password': 'password123',
        'konfirmasi_password': 'password123'
    }).encode('utf-8')
    
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    resp_reg = opener.open(f"{base_url}/register", data=reg_payload)
    reg_result_html = resp_reg.read().decode('utf-8')
    assert "Pendaftaran akun berhasil" in reg_result_html or "Masuk ke Sistem" in reg_result_html
    print(f"    [+] Sukses: Akun baru '{uname}' berhasil didaftarkan!")

    # 4. Uji Login Menggunakan Akun Baru
    print(f"\n[4] Menguji Login dengan Akun Baru '{uname}'...")
    login_payload = urllib.parse.urlencode({
        'username': uname,
        'password': 'password123'
    }).encode('utf-8')
    resp_login = opener.open(f"{base_url}/login", data=login_payload)
    dash_html = resp_login.read().decode('utf-8')
    assert "Staf Tata Usaha Baru" in dash_html
    assert "Dashboard Arsip Fiskal" in dash_html
    print("    [+] Sukses: Akun baru berhasil login dan masuk ke Dashboard!")

    # 5. Uji Tombol Hapus pada Daftar Arsip (/fiskal)
    print("\n[5] Memeriksa Tombol Hapus di Tabel Arsip Fiskal (/fiskal)...")
    resp_list = opener.open(f"{base_url}/fiskal")
    list_html = resp_list.read().decode('utf-8')
    assert "🗑️ Hapus" in list_html, "Gagal: Tombol Hapus tidak ditemukan di tabel!"
    print("    [+] Sukses: Tombol Hapus tersedia langsung di tabel daftar arsip.")

    # 6. Uji Penghapusan Data oleh Akun Petugas Baru
    print("\n[6] Menguji Penghapusan Data Fiskal oleh Petugas Baru...")
    # Cari ID salah satu dokumen untuk dihapus
    from app import app
    from models import db, FiskalDocument
    with app.app_context():
        # Buat dokumen tes khusus untuk uji hapus
        test_doc = FiskalDocument.query.filter_by(nomor_surat="TEST-HAPUS-001").first()
        if not test_doc:
            test_doc = FiskalDocument(
                nomor_surat="TEST-HAPUS-001",
                nomor_polisi="BK 7777 XX",
                nama_pemilik="Tes Hapus Pemilik",
                alamat="Medan",
                merk_type="Honda Beat",
                tahun_kendaraan="2021",
                cc_kendaraan="110",
                warna="Biru",
                nomor_rangka="MH1TEST7777777777",
                nomor_mesin="JM1TEST7777777",
                nomor_stnk="77778888",
                nama_pemohon="Tes Hapus",
                daerah_mutasi="Binjai",
                tanggal_fiskal="2026-03-01",
                kategori_fiskal="Fiskal Sumatera Utara",
                file_path="sample_fiskal_bk1234aa.txt",
                file_name="sample.txt",
                file_type="txt",
                status_verifikasi="Belum Terverifikasi",
                is_deleted=False
            )
            db.session.add(test_doc)
            db.session.commit()
        test_id = test_doc.id

    resp_del = opener.open(f"{base_url}/fiskal/{test_id}/delete", data=b'')
    assert resp_del.getcode() == 200
    after_del_html = resp_del.read().decode('utf-8')
    assert "berhasil dihapus/diarsipkan" in after_del_html
    print(f"    [+] Sukses: Petugas baru berhasil menghapus data fiskal (ID {test_id})!")

    # 7. Uji Akses via Local Network IP (Wi-Fi)
    print("\n[7] Menguji Binding Akses Jaringan Lokal (0.0.0.0 / IP Wi-Fi)...")
    # Cek IP lokal aktif
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"
    finally:
        s.close()
    
    print(f"    [*] IP Lokal Wi-Fi Komputer: {local_ip}")
    req_net = urllib.request.urlopen(f"http://{local_ip}:5000/login")
    assert req_net.getcode() == 200
    print(f"    [+] Sukses: Server dapat diakses dari IP jaringan: http://{local_ip}:5000")

    print("\n==================================================")
    print(" SEMUA PENGUJIAN 100% SUKSES TANPA ADA MASALAH!")
    print("==================================================")

if __name__ == "__main__":
    test_all()
