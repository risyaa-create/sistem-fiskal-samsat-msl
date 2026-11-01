import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "db_fiskal_samsat")

def migrate():
    print("[*] Memeriksa struktur tabel fiskal_documents untuk kolom soft delete...")
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4"
    )
    cursor = conn.cursor()

    cursor.execute("SHOW COLUMNS FROM fiskal_documents LIKE 'is_deleted';")
    if not cursor.fetchone():
        print("[*] Menambahkan kolom is_deleted, deleted_at, dan deleted_by...")
        cursor.execute("ALTER TABLE fiskal_documents ADD COLUMN is_deleted TINYINT(1) NOT NULL DEFAULT 0;")
        cursor.execute("ALTER TABLE fiskal_documents ADD COLUMN deleted_at DATETIME NULL;")
        cursor.execute("ALTER TABLE fiskal_documents ADD COLUMN deleted_by INT NULL;")
        try:
            cursor.execute("ALTER TABLE fiskal_documents ADD CONSTRAINT fk_fiskal_deleted_by FOREIGN KEY (deleted_by) REFERENCES users(id) ON DELETE SET NULL;")
        except Exception as e:
            print(f"[!] Info FK: {e}")
        conn.commit()
        print("[+] Migrasi database berhasil: Kolom soft delete ditambahkan!")
    else:
        print("[+] Kolom soft delete sudah ada di database.")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    migrate()
