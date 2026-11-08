# UTS Automation Systems - Online Book Catalog Organizer

## 1. Deskripsi Project

**Online Book Catalog Organizer** merupakan aplikasi otomatisasi berbasis Python Command Line Interface (CLI) yang digunakan untuk mengambil dan mengelola data katalog buku dari website Goodreads melalui teknik *web scraping*.

Aplikasi ini menggunakan library Requests untuk mengambil halaman website dan BeautifulSoup untuk mengekstraksi informasi buku. Regular Expressions (Regex) digunakan untuk mengambil informasi rating dan tahun terbit dari data yang diperoleh.

Data buku yang berhasil dikumpulkan meliputi:
- Judul buku (*Title*)
- Nama penulis (*Author*)
- Kategori buku (*Category*)
- Rating buku (*Rating*)
- Tahun terbit (*Publication Year*)
- Tautan buku (*Book Link*)

Hasil scraping disimpan dalam format TXT dan CSV. Aplikasi juga menyediakan fitur pencarian berdasarkan data katalog yang telah disimpan serta fitur backup otomatis ke dalam format ZIP.

## 2. Anggota Kelompok

1. Gilang Prayoga - 312310232
2. Rifqi Putra Adhadi - 312310281
3. Adira Alvian Zein - 312310263
4. Wasis Wibisono - 312310661

## 3. Prasyarat Sistem

Sebelum menjalankan aplikasi, pastikan perangkat telah memenuhi persyaratan berikut:

- Python versi 3.8 atau lebih baru.
- Koneksi internet untuk mengambil data dari Goodreads.
- Terminal atau PowerShell untuk menjalankan perintah CLI.

## 4. Instalasi

### 4.1 Menyiapkan Project

Ekstrak folder project, kemudian buka terminal atau PowerShell pada direktori project.

### 4.2 Menginstal Dependencies

Jalankan perintah berikut untuk menginstal seluruh library yang dibutuhkan:

```bash
pip install -r requirements.txt
```

Dependencies yang digunakan:
- `requests` - Mengirim permintaan HTTP ke website Goodreads.
- `beautifulsoup4` - Membantu proses parsing dan ekstraksi data HTML.

## 5. Cara Menjalankan Program

Program dijalankan melalui terminal atau PowerShell menggunakan perintah Python.

### 5.1 Mengambil Data Buku

Untuk mengambil maksimal 30 data buku dengan kategori yang dipilih secara acak:

```bash
python main.py --limit 30
```

Program akan mengacak urutan kategori dari daftar keyword yang tersedia dan mengambil data sampai mencapai jumlah yang diminta.

### 5.2 Mengambil Data Berdasarkan Keyword

Untuk mengambil data berdasarkan kategori atau keyword tertentu:

```bash
python main.py --keyword fiction --limit 30
```

Pada contoh tersebut, program akan melakukan pencarian menggunakan keyword `fiction` dengan batas maksimal 30 buku.

### 5.3 Mengambil Data dan Membuat Backup

Untuk menjalankan scraping sekaligus membuat arsip backup ZIP:

```bash
python main.py --limit 30 --backup
```

Program akan mengambil data buku, menyimpan hasilnya, kemudian membuat file backup dalam folder `backup`.

### 5.4 Mencari Buku dari Katalog

Untuk mencari buku berdasarkan data CSV yang sudah tersimpan:

```bash
python main.py --search harry
```

Program akan menampilkan data buku yang sesuai dengan kata pencarian.

Pencarian juga dapat ditentukan berdasarkan kolom tertentu:

```bash
python main.py --search harry --search-field title
```

Pilihan kolom pencarian:
- `title` - Mencari berdasarkan judul buku.
- `author` - Mencari berdasarkan nama penulis.
- `category` - Mencari berdasarkan kategori buku.
- `all` - Mencari pada seluruh kolom yang didukung.

## 6. Struktur Folder Project

Berikut struktur folder yang digunakan dalam project:

```text
UTS_Project_Kelompok_01/
│
├── main.py
├── requirements.txt
├── README.md
│
├── data/
│   └── raw_data.txt
│
├── output/
│   ├── hasil_scraping.csv
│   └── laporan.txt
│
├── backup/
│   └── backup_data.zip
│
└── dokumentasi/
    └── laporan_uts.pdf
```

Keterangan:
- `main.py` - File utama yang menjalankan seluruh proses aplikasi.
- `requirements.txt` - Daftar library Python yang dibutuhkan.
- `README.md` - Dokumentasi penggunaan aplikasi.
- `data/` - Menyimpan data mentah hasil scraping.
- `output/` - Menyimpan hasil scraping dalam format CSV dan laporan TXT.
- `backup/` - Menyimpan arsip backup ZIP.
- `dokumentasi/` - Menyimpan laporan akhir project dalam format PDF.

## 7. Hasil Output Program

Aplikasi menghasilkan beberapa file sebagai berikut:

| File | Fungsi |
|---|---|
| `data/raw_data.txt` | Menyimpan data mentah hasil scraping. |
| `output/hasil_scraping.csv` | Menyimpan data buku dalam format CSV. |
| `output/laporan.txt` | Menyimpan ringkasan hasil pemrosesan data. |
| `backup/backup_data.zip` | Menyimpan arsip ZIP dari folder data dan output. |

Folder dan file output akan dibuat secara otomatis oleh program apabila belum tersedia.

## 8. Fitur Utama

Aplikasi Online Book Catalog Organizer memiliki fitur berikut:

1. **Web Scraping** - Mengambil informasi buku dari Goodreads.
2. **Random Keyword Selection** - Mengacak urutan kategori pencarian buku.
3. **Regular Expressions (Regex)** - Mengekstraksi rating dan tahun terbit buku.
4. **Data Filtering** - Menghindari data buku yang duplikat.
5. **File Handling** - Menyimpan data ke format TXT dan CSV.
6. **Catalog Search** - Mencari buku dari katalog yang telah tersimpan.
7. **Automatic Folder Management** - Membuat folder output secara otomatis menggunakan pathlib.
8. **ZIP Backup** - Mengarsipkan hasil scraping ke dalam file ZIP.
9. **Error Handling** - Menangani kesalahan koneksi, respons HTTP, dan file yang tidak ditemukan.

## 9. Catatan

- Jumlah data yang dikumpulkan ditentukan melalui parameter `--limit`.
- Kategori pencarian dipilih secara acak apabila parameter `--keyword` tidak digunakan.
- Apabila menggunakan `--keyword`, program hanya melakukan pencarian berdasarkan keyword yang ditentukan.
- Pengambilan data bergantung pada ketersediaan dan struktur halaman Goodreads serta koneksi internet.
- Program tidak menjamin jumlah data selalu terpenuhi apabila data tidak tersedia atau terjadi kendala saat proses scraping.

---

**UTS Automation Systems - Online Book Catalog Organizer**  
*Python-Based Web Scraping and Book Catalog Management*