// ========================================================
// SISTEM INFORMASI DIGITALISASI DATA FISKAL MUTASI KENDARAAN
// SAMSAT MEDAN SELATAN - JAVASCRIPT DASAR
// ========================================================

document.addEventListener("DOMContentLoaded", function () {
    // 1. Auto dismiss alert messages after 5 seconds
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = "opacity 0.5s ease";
            alert.style.opacity = "0";
            setTimeout(function () {
                alert.remove();
            }, 500);
        }, 5000);
    });

    // 2. Pratinjau File yang Dipilih pada Form Upload
    const fileInput = document.getElementById("dokumen_file");
    const previewContainer = document.getElementById("file-preview-container");
    const previewText = document.getElementById("file-preview-text");
    const previewImage = document.getElementById("file-preview-image");

    if (fileInput && previewContainer) {
        fileInput.addEventListener("change", function (event) {
            const file = event.target.files[0];
            if (file) {
                previewContainer.style.display = "block";
                const fileSizeKB = (file.size / 1024).toFixed(1);
                previewText.innerHTML = `<strong>File Terpilih:</strong> ${file.name} (${fileSizeKB} KB) - Tipe: ${file.type || 'Dokumen'}`;

                // Jika file berupa gambar, tampilkan pratinjau thumbnail
                if (file.type.startsWith("image/") && previewImage) {
                    const reader = new FileReader();
                    reader.onload = function (e) {
                        previewImage.src = e.target.result;
                        previewImage.style.display = "block";
                    };
                    reader.readAsDataURL(file);
                } else if (previewImage) {
                    previewImage.style.display = "none";
                }
            } else {
                previewContainer.style.display = "none";
            }
        });
    }

    // 3. Konfirmasi sebelum tombol verifikasi diklik
    const formVerifikasi = document.getElementById("form-verifikasi");
    if (formVerifikasi) {
        formVerifikasi.addEventListener("submit", function (e) {
            const confirmed = confirm(
                "Apakah Anda yakin data fisik dan data sistem sudah sesuai dan ingin memverifikasi dokumen fiskal ini?"
            );
            if (!confirmed) {
                e.preventDefault();
            }
        });
    }

    // 3b. Konfirmasi sebelum tombol hapus (soft delete) diklik
    const formHapus = document.getElementById("form-hapus");
    if (formHapus) {
        formHapus.addEventListener("submit", function (e) {
            const confirmed = confirm(
                "PERINGATAN: Apakah Anda yakin ingin menghapus data dokumen fiskal ini?\nData akan diarsipkan (soft delete) dan tidak akan tampil lagi pada daftar arsip aktif."
            );
            if (!confirmed) {
                e.preventDefault();
            }
        });
    }

    // 4. Transform huruf besar otomatis (Uppercase) untuk No Polisi, Rangka, Mesin
    const uppercaseInputs = document.querySelectorAll(".uppercase-input");
    uppercaseInputs.forEach(function (input) {
        input.addEventListener("input", function () {
            this.value = this.value.toUpperCase();
        });
    });
});
