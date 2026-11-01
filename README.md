# Sistem Informasi Digitalisasi Data Fiskal Mutasi Kendaraan
**SAMSAT Medan Selatan**

Sistem berbasis web untuk mendigitalkan, mengelola, mencari, dan mengarsipkan berkas data fiskal mutasi kendaraan bermotor pada SAMSAT Medan Selatan.

---

## 🚀 Cara Menjalankan Sistem (1-Klik Praktis)

Anda **tidak perlu membuka XAMPP Control Panel atau mengetik perintah di Command Prompt terlebih dahulu**. Cukup gunakan file yang sudah disediakan:

1. **Jalankan Aplikasi:**
   - Cukup klik ganda (double-click) file **`JALANKAN_SISTEM.bat`** (atau **`JALANKAN_SISTEM_BACKGROUND.vbs`**).
   - Skrip akan secara otomatis:
     - Memeriksa dan mengaktifkan database MySQL XAMPP di latar belakang jika belum berjalan.
     - Mengaktifkan server web Flask.
     - Membuka halaman web secara otomatis di browser Anda.

2. **Akses dari Laptop Lain (Jaringan Wi-Fi yang Sama):**
   - Di laptop utama: `http://localhost:5000`
   - Dari laptop lain / HP / tablet: **`http://192.168.179.143:5000`**
   - *(Jika laptop lain belum bisa terhubung, klik kanan file `BUKA_AKSES_LAPTOP_LAIN.bat` lalu pilih **Run as administrator** untuk membuka port 5000 di firewall Windows)*.

3. **Menghentikan Aplikasi:**
   - Klik ganda file **`HENTIKAN_SISTEM.bat`** jika sudah selesai menggunakan aplikasi.

---

## 📌 Fitur Utama Sistem

1. **Autentikasi & Registrasi Akun Mandiri:**
   - Siapa saja staf/pegawai tata usaha yang belum memiliki akun dapat langsung mendaftar melalui menu **Daftar Akun Baru** pada halaman login.
2. **Satu Dokumen Fiskal = Satu Kesatuan Data Utuh:** Seluruh 16 field resmi dokumen fiskal disimpan dalam satu kesatuan data.
3. **Unggah Dokumen Fisik Asli:** Menyimpan berkas foto/scan fisik asli (JPG, PNG, PDF) dan menautkannya langsung ke data fiskal.
4. **Status Verifikasi:** Dokumen baru yang diunggah secara otomatis berstatus **"Belum Terverifikasi"** sampai petugas berwenang mencocokkan fisik dan melakukan verifikasi.
5. **Fitur Edit Data Fiskal:** Mengubah data pada 16 field atau mengganti berkas asli dengan riwayat perubahan otomatis tercatat di audit log.
6. **Fitur Hapus Data Fiskal:** Menghapus data langsung dari tabel daftar arsip atau halaman detail (menggunakan mekanisme *Soft Delete* agar arsip tetap aman dan terlacak).
7. **Pratinjau Berdampingan (Split-View):** Menampilkan berkas fisik asli di samping 16 field data.
8. **Pencarian Multi-Kriteria:** Pencarian cepat berdasarkan Nomor Polisi, Nomor Rangka, Nomor Mesin, Nomor Surat, atau Nama Pemilik.
9. **Log Audit Lengkap:** Pencatatan riwayat setiap aksi tambah, edit, hapus, dan verifikasi dokumen.

---

## 🗂️ 16 Field Resmi Dokumen Fiskal

1. **Nomor Surat**
2. **Nomor Polisi**
3. **Nama Pemilik**
4. **Alamat**
5. **Merk / Type Kendaraan**
6. **Tahun Kendaraan**
7. **CC Kendaraan**
8. **Warna**
9. **Nomor Rangka**
10. **Nomor Mesin**
11. **Nomor STNK**
12. **Nomor Kohir**
13. **Nama Pemohon/Perwakilan**
14. **Daerah Mutasi**
15. **Tanggal Fiskal**
16. **Kategori Fiskal:**
    - `Fiskal Sumatera Utara`
    - `Fiskal Provinsi`
