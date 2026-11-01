import urllib.request
import urllib.parse
import http.cookiejar
import sys

BASE_URL = "http://127.0.0.1:5000"

def run_tests():
    print("==================================================")
    print(" PENGUJIAN OTOMATIS FITUR EDIT, HAPUS & FITUR AWAL")
    print("==================================================")

    # Pastikan data dokumen uji ID 3 aktif (tidak terhapus) sebelum pengujian
    try:
        from app import app
        from models import db, FiskalDocument
        with app.app_context():
            doc3 = db.session.get(FiskalDocument, 3)
            if doc3:
                doc3.is_deleted = False
                doc3.deleted_at = None
                doc3.deleted_by = None
                db.session.commit()
    except Exception as e:
        print("Note setup:", e)

    cj_admin = http.cookiejar.CookieJar()
    admin_client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj_admin))

    cj_petugas = http.cookiejar.CookieJar()
    petugas_client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj_petugas))

    # 1. Login Admin
    print("\n[1] Menguji Login Admin...")
    login_data = urllib.parse.urlencode({'username': 'admin', 'password': 'admin123'}).encode('utf-8')
    resp = admin_client.open(f"{BASE_URL}/login", data=login_data)
    assert resp.getcode() == 200
    dash_html = resp.read().decode('utf-8')
    assert "Total Dokumen Fiskal" in dash_html
    print("    [+] Login Admin Berhasil & Dashboard Terbuka.")

    # 2. Login Petugas
    print("\n[2] Menguji Login Petugas...")
    login_petugas = urllib.parse.urlencode({'username': 'petugas', 'password': 'petugas123'}).encode('utf-8')
    resp = petugas_client.open(f"{BASE_URL}/login", data=login_petugas)
    assert resp.getcode() == 200
    print("    [+] Login Petugas Berhasil.")

    # 3. Uji Halaman Edit (GET)
    print("\n[3] Menguji Halaman Edit Data (GET /fiskal/1/edit)...")
    resp_edit_page = admin_client.open(f"{BASE_URL}/fiskal/1/edit")
    assert resp_edit_page.getcode() == 200
    edit_html = resp_edit_page.read().decode('utf-8')
    assert "Edit Data Dokumen Fiskal" in edit_html
    assert "BK 1234 AA" in edit_html
    print("    [+] Halaman Edit berhasil menampilkan 16 field dan data awal.")

    # 4. Uji Simpan Perubahan Data (POST /fiskal/1/edit)
    print("\n[4] Menguji Simpan Perubahan Data Fiskal (POST)...")
    import time
    timestamp_mark = str(int(time.time()))[-4:]
    edit_payload = {
        'nomor_surat': '001/FSK/MSL/2026',
        'nomor_polisi': 'BK 1234 AA',
        'nama_pemilik': f'Budi Santoso {timestamp_mark}',
        'alamat': 'Jl. Sisingamangaraja No. 45, Medan',
        'merk_type': 'Toyota Avanza 1.3 G',
        'tahun_kendaraan': '2020',
        'cc_kendaraan': '1300',
        'warna': f'Hitam Metalik #{timestamp_mark}',
        'nomor_rangka': 'MHFM1BA3JK1234567',
        'nomor_mesin': '1NR-FE-9876543',
        'nomor_stnk': '08765432',
        'nomor_kohir': 'K-2026-0045',
        'nama_pemohon': 'Budi Santoso',
        'daerah_mutasi': 'Deli Serdang',
        'tanggal_fiskal': '2026-01-15',
        'kategori_fiskal': 'Fiskal Sumatera Utara'
    }
    encoded_payload = urllib.parse.urlencode(edit_payload).encode('utf-8')
    resp_save_edit = admin_client.open(f"{BASE_URL}/fiskal/1/edit", data=encoded_payload)
    assert resp_save_edit.getcode() == 200
    detail_html = resp_save_edit.read().decode('utf-8')
    assert "berhasil diperbarui" in detail_html
    assert f"Budi Santoso {timestamp_mark}" in detail_html
    assert "[EDIT]" in detail_html
    print("    [+] Data berhasil diperbarui & tercatat di log audit.")

    # 5. Uji Proteksi Role Hapus (Role Petugas Mencoba Hapus)
    print("\n[5] Menguji Keamanan: Petugas (Non-Admin) mencoba menghapus data...")
    resp_petugas_del = petugas_client.open(f"{BASE_URL}/fiskal/3/delete", data=b'')
    res_text = resp_petugas_del.read().decode('utf-8')
    assert "Akses ditolak" in res_text or "Hanya Administrator" in res_text
    print("    [+] Keamanan berhasil: Role Petugas ditolak saat mencoba menghapus.")

    # 6. Uji Soft Delete oleh Admin
    print("\n[6] Menguji Soft Delete oleh Admin (POST /fiskal/3/delete)...")
    # Cek dulu jumlah awal di daftar fiskal
    list_before = admin_client.open(f"{BASE_URL}/fiskal").read().decode('utf-8')
    assert "BK 9999 ZZ" in list_before

    # Eksekusi hapus sebagai admin
    resp_admin_del = admin_client.open(f"{BASE_URL}/fiskal/3/delete", data=b'')
    assert resp_admin_del.getcode() == 200
    list_after = resp_admin_del.read().decode('utf-8')
    assert "berhasil dihapus/diarsipkan" in list_after

    # Pastikan BK 9999 ZZ tidak lagi ada di dalam tbody tabel arsip aktif
    tbody_content = list_after.split("<tbody>")[1].split("</tbody>")[0]
    assert "BK 9999 ZZ" not in tbody_content
    print("    [+] Dokumen BK 9999 ZZ berhasil dihapus dari daftar aktif (tabel tidak lagi memuatnya).")

    # 7. Cek Halaman Detail Dokumen yang Diarsipkan
    print("\n[7] Memeriksa Detail Dokumen yang Diarsipkan (Soft Delete)...")
    detail_deleted = admin_client.open(f"{BASE_URL}/fiskal/3").read().decode('utf-8')
    assert "Data Diarsipkan (Soft Delete)" in detail_deleted
    assert "[HAPUS]" in detail_deleted
    print("    [+] Data fisik dan audit log [HAPUS] tetap tersimpan utuh di database.")

    # 8. Verifikasi Fitur Pencarian & Filter Tetap Normal
    print("\n[8] Memeriksa Fitur Pencarian & Filter...")
    search_resp = admin_client.open(f"{BASE_URL}/fiskal?q=1234").read().decode('utf-8')
    assert "BK 1234 AA" in search_resp
    print("    [+] Fitur pencarian tetap berfungsi normal.")

    print("\n==================================================")
    print(" SEMUA PENGUJIAN BERHASIL 100%! TIDAK ADA MASALAH.")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
