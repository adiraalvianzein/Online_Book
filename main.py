
import re
import csv
import zipfile
import argparse
import random
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote_plus
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


# ==========================================
# KONFIGURASI
# ==========================================

OUTPUT_DIR = "output"
RAW_DIR = "data"
BACKUP_DIR = "backup"

CSV_FILE = "hasil_scraping.csv"
RAW_FILE = "raw_data.txt"
REPORT_FILE = "laporan.txt"

FIELDNAMES = [
    "title",
    "author",
    "category",
    "rating_str",
    "rating_num",
    "year_str",
    "year_published",
    "link"
]

DEFAULT_URL = "https://www.goodreads.com/search?q=books"

DEFAULT_KEYWORDS = [
    "fiction", "business", "history", "science",
    "novel", "fantasy", "psychology", "technology",
    "philosophy", "biography", "art", "thriller"
]


# ==========================================
# 1. MEMBUAT URL PENCARIAN
# ==========================================

def build_search_url(base_url, keyword):
    """
    Membuat URL pencarian berdasarkan keyword.
    Mendukung URL dengan parameter q atau template {keyword}.
    """

    if "{keyword}" in base_url:
        return base_url.replace("{keyword}", quote_plus(keyword))

    parsed = urlparse(base_url)
    params = parse_qs(parsed.query)

    if "q" in params or "search" in parsed.path.lower():
        params["q"] = [keyword]

        new_query = urlencode(params, doseq=True)

        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))

    return base_url


# ==========================================
# 2. WEB SCRAPING
# ==========================================

def fetch_books(base_url, keyword, limit):
    """
    Mengambil data buku dari Goodreads menggunakan
    Requests dan BeautifulSoup.
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9"
    }

    # Menentukan keyword pencarian
    if keyword:
        search_keywords = [keyword]
    else:
        search_keywords = DEFAULT_KEYWORDS.copy()
        random.shuffle(search_keywords)

    books = []
    seen_titles = set()

    print("\n[+] Memulai web scraping katalog buku Goodreads...")

    with requests.Session() as session:

        session.headers.update(headers)

        for kw in search_keywords:

            if len(books) >= limit:
                break

            url = build_search_url(base_url, kw)

            print(f"\n[+] Mencari kategori: {kw}")

            try:
                response = session.get(url, timeout=15)
                response.raise_for_status()

            except requests.exceptions.Timeout:
                print("[!] Koneksi timeout. Melanjutkan pencarian berikutnya.")
                continue

            except requests.exceptions.HTTPError as e:
                print(f"[!] HTTP Error: {e}")
                continue

            except requests.exceptions.ConnectionError as e:
                print(f"[!] Gagal terhubung ke website: {e}")
                continue

            except requests.exceptions.RequestException as e:
                print(f"[!] Network Error: {e}")
                continue

            # Parsing HTML
            soup = BeautifulSoup(response.text, "html.parser")

            items = soup.select(
                "tr[itemtype='http://schema.org/Book']"
            )

            if not items:
                items = soup.select("tr[itemtype*='Book']")

            if not items:
                print("[!] Data buku tidak ditemukan pada halaman ini.")
                continue

            print(f"[+] Ditemukan {len(items)} elemen buku.")

            for item in items:

                if len(books) >= limit:
                    break

                # ----------------------------------
                # Judul Buku
                # ----------------------------------

                title_tag = item.select_one(
                    "a.bookTitle"
                )

                if not title_tag:
                    continue

                title = title_tag.get_text(strip=True)

                if not title:
                    continue

                # Menghindari data duplikat

                author_tag = item.select_one("a.authorName")

                author = (
                    author_tag.get_text(strip=True)
                    if author_tag
                    else "Anonim"
                )

                title_key = (title.casefold(), author.casefold())

                if title_key in seen_titles:
                    continue

                # ----------------------------------
                # Penulis Buku
                # ----------------------------------

                author_tag = item.select_one(
                    "a.authorName"
                )

                author = (
                    author_tag.get_text(strip=True)
                    if author_tag
                    else "Anonim"
                )

                # ----------------------------------
                # Informasi Gabungan
                # ----------------------------------

                info_text = item.get_text(" ", strip=True)

                # REGEX 1: Ekstraksi rating
                rating_match = re.search(
                    r"(\d+(?:\.\d+)?)\s+avg rating",
                    info_text,
                    re.IGNORECASE
                )

                rating_num = (
                    float(rating_match.group(1))
                    if rating_match
                    else 0.0
                )

                rating_str = (
                    f"{rating_num:.2f}"
                    if rating_num > 0
                    else "N/A"
                )

                # REGEX 2: Ekstraksi tahun terbit
                year_match = re.search(
                    r"published\s+(19\d\d|20\d\d)",
                    info_text,
                    re.IGNORECASE
                )

                year_published = (
                    int(year_match.group(1))
                    if year_match
                    else 0
                )

                year_str = (
                    str(year_published)
                    if year_published > 0
                    else "N/A"
                )

                # ----------------------------------
                # Kategori
                # ----------------------------------

                category = kw.capitalize()

                # ----------------------------------
                # Link Buku
                # ----------------------------------

                link_suffix = title_tag.get("href", "")

                link = (
                    urljoin(response.url, link_suffix)
                    if link_suffix
                    else response.url
                )

                # Menyimpan data buku
                book = {
                    "title": title,
                    "author": author,
                    "category": category,
                    "rating_str": rating_str,
                    "rating_num": rating_num,
                    "year_str": year_str,
                    "year_published": year_published,
                    "link": link
                }

                books.append(book)
                seen_titles.add(title_key)

    print(
        f"\n[+] Total data buku berhasil dikumpulkan: "
        f"{len(books)}"
    )

    return books


# ==========================================
# 3. MENYIMPAN DATA
# ==========================================

def filter_and_save(books, output_dir, raw_dir):
    """
    Menyimpan data mentah TXT, hasil scraping CSV,
    dan laporan ringkasan TXT.
    """

    output_path = Path(output_dir)
    raw_path = Path(raw_dir)

    try:

        # Membuat folder otomatis
        output_path.mkdir(parents=True, exist_ok=True)
        raw_path.mkdir(parents=True, exist_ok=True)

        # ----------------------------------
        # Menyimpan RAW DATA
        # ----------------------------------

        raw_file = raw_path / RAW_FILE

        with raw_file.open("w", encoding="utf-8") as f:

            for book in books:
                f.write(f"{book}\n")

        # ----------------------------------
        # Menyimpan CSV
        # ----------------------------------

        csv_file = output_path / CSV_FILE

        with csv_file.open(
            "w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.DictWriter(
                f,
                fieldnames=FIELDNAMES
            )

            writer.writeheader()
            writer.writerows(books)

        # ----------------------------------
        # Membuat Laporan
        # ----------------------------------

        report_file = output_path / REPORT_FILE

        ratings = [
            book["rating_num"]
            for book in books
            if book["rating_num"] > 0
        ]

        avg_rating = (
            sum(ratings) / len(ratings)
            if ratings
            else 0
        )

        categories = {}

        for book in books:

            category = book["category"]

            categories[category] = (
                categories.get(category, 0) + 1
            )

        with report_file.open("w", encoding="utf-8") as f:

            f.write(
                "=== LAPORAN RINGKASAN AUTOMATION SYSTEMS ===\n"
            )

            f.write("Sumber Data : Goodreads\n")
            f.write(f"Total Data Buku : {len(books)}\n")
            f.write(f"Data Rating Valid : {len(ratings)}\n")

            f.write(
                f"Rata-rata Rating : {avg_rating:.2f} / 5.00\n"
            )

            f.write("\n=== JUMLAH BUKU PER KATEGORI ===\n")

            for category, total in categories.items():

                f.write(f"{category} : {total}\n")

        print("\n[+] Penyimpanan data berhasil.")
        print(f"[+] RAW DATA : {raw_file}")
        print(f"[+] CSV      : {csv_file}")
        print(f"[+] LAPORAN  : {report_file}")

        return True

    except FileNotFoundError as e:

        print(f"[!] File tidak ditemukan: {e}")
        return False

    except PermissionError as e:

        print(f"[!] Tidak memiliki izin mengakses file: {e}")
        return False

    except OSError as e:

        print(f"[!] Kesalahan penyimpanan file: {e}")
        return False


# ==========================================
# 4. PENCARIAN KATALOG LOKAL
# ==========================================

def search_catalog(keyword, search_field, output_dir):
    """
    Mencari buku dari katalog CSV yang sudah tersimpan.
    Pencarian berdasarkan judul, penulis, kategori, atau semua.
    """

    csv_file = Path(output_dir) / CSV_FILE

    print("\n=== PENCARIAN KATALOG BUKU ===")
    print(f"Kata kunci: {keyword}")
    print(f"Kolom pencarian: {search_field}")

    try:

        with csv_file.open(
            "r",
            newline="",
            encoding="utf-8"
        ) as f:

            reader = csv.DictReader(f)

            if not reader.fieldnames:
                print("[!] File CSV kosong atau tidak memiliki header.")
                return

            results = []

            for book in reader:

                if search_field == "all":

                    searchable_text = " ".join([
                        book.get("title", ""),
                        book.get("author", ""),
                        book.get("category", "")
                    ])

                else:

                    searchable_text = book.get(
                        search_field,
                        ""
                    )

                if keyword.casefold() in searchable_text.casefold():

                    results.append(book)

            # Menampilkan hasil pencarian
            if not results:

                print("\n[!] Buku tidak ditemukan.")
                return

            print(f"\n[+] Ditemukan {len(results)} buku.\n")

            for index, book in enumerate(results, start=1):

                print(f"--- Buku {index} ---")
                print(f"Judul    : {book.get('title', 'N/A')}")
                print(f"Penulis  : {book.get('author', 'N/A')}")
                print(f"Kategori : {book.get('category', 'N/A')}")
                print(f"Rating   : {book.get('rating_str', 'N/A')}")
                print(f"Tahun    : {book.get('year_str', 'N/A')}")
                print(f"Link     : {book.get('link', 'N/A')}")
                print()

    except FileNotFoundError:

        print(
            "\n[!] File katalog belum ditemukan."
        )

        print(
            "[!] Jalankan scraping terlebih dahulu "
            "untuk membuat hasil_scraping.csv."
        )

    except PermissionError:

        print("[!] Tidak memiliki izin membaca file katalog.")

    except csv.Error as e:

        print(f"[!] Kesalahan format CSV: {e}")

    except UnicodeDecodeError:

        print("[!] File CSV memiliki format encoding yang tidak sesuai.")

    except OSError as e:

        print(f"[!] Kesalahan membaca file: {e}")


# ==========================================
# 5. BACKUP ZIP
# ==========================================


def create_backup(source_dirs, backup_dir):
    """
    Membuat backup ZIP dari folder data dan output.
    """

    backup_path = Path(backup_dir)
    zip_file = backup_path / "backup_data.zip"

    try:
        backup_path.mkdir(
            parents=True,
            exist_ok=True
        )

        print("\n[+] Memulai proses backup ZIP...")

        files_found = []

        for folder in source_dirs:

            path = Path(folder)

            if not path.exists():
                print(f"[!] Folder tidak ditemukan: {path}")
                continue

            for file in path.rglob("*"):

                if file.is_file():
                    files_found.append(file)

        if not files_found:
            print("[!] Tidak ada file yang dapat di-backup.")
            return False

        with zipfile.ZipFile(
            zip_file,
            "w",
            zipfile.ZIP_DEFLATED
        ) as zipf:

            for file in files_found:

                # Menggunakan path relatif secara konsisten
                zipf.write(file, file.as_posix())

        print("[+] Backup ZIP berhasil dibuat.")
        print(f"[+] Lokasi: {zip_file}")

        return True

    except FileNotFoundError as e:
        print(f"[!] File tidak ditemukan: {e}")
        return False

    except PermissionError as e:
        print(f"[!] Izin akses ditolak: {e}")
        return False

    except (OSError, zipfile.BadZipFile) as e:
        print(f"[!] Gagal membuat backup: {e}")
        return False

# ==========================================
# 6. VALIDASI ARGUMEN CLI
# ==========================================

def positive_integer(value):
    """
    Memastikan nilai limit merupakan bilangan positif.
    """

    number = int(value)

    if number <= 0:
        raise argparse.ArgumentTypeError(
            "Limit harus lebih besar dari 0."
        )

    return number


# ==========================================
# 7. PROGRAM UTAMA
# ==========================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Goodreads Book Catalog Scraper "
            "& Organizer"
        )
    )

    parser.add_argument(
        "--url",
        type=str,
        default=DEFAULT_URL,
        help="URL pencarian Goodreads"
    )

    mode = parser.add_mutually_exclusive_group()

    mode.add_argument(
        "--keyword",
        type=str,
        default="",
        help="Keyword untuk mencari buku di Goodreads"
    )

    mode.add_argument(
        "--search",
        type=str,
        help="Mencari buku dari katalog CSV lokal"
    )

    parser.add_argument(
        "--search-field",
        type=str,
        choices=["title", "author", "category", "all"],
        default="all",
        help="Kolom katalog yang ingin dicari"
    )

    parser.add_argument(
        "--limit",
        type=positive_integer,
        default=30,
        help="Jumlah maksimal data buku yang diambil"
    )

    parser.add_argument(
        "--backup",
        action="store_true",
        help="Membuat backup ZIP"
    )

    args = parser.parse_args()

    print("=" * 50)
    print("   GOODREADS BOOK CATALOG ORGANIZER")
    print("       AUTOMATION SYSTEMS UTS")
    print("=" * 50)

    # MODE 1: PENCARIAN KATALOG LOKAL

    if args.search is not None:

        search_catalog(
            args.search,
            args.search_field,
            OUTPUT_DIR
        )

        return

    # MODE 2: WEB SCRAPING

    data_books = fetch_books(
        args.url,
        args.keyword,
        args.limit
    )

    # Memeriksa data kosong

    if not data_books:

        print("\n[!] Tidak ada data yang berhasil diambil.")
        print("[!] Proses dihentikan.")

        return

    # Menyimpan data

    save_success = filter_and_save(
        data_books,
        OUTPUT_DIR,
        RAW_DIR
    )

    if not save_success:

        print("[!] Penyimpanan gagal. Proses dihentikan.")
        return

    # Membuat backup jika diminta

    if args.backup:
        backup_success = create_backup(
            [OUTPUT_DIR, RAW_DIR],
            BACKUP_DIR
        )

        if not backup_success:
            print("[!] Proses scraping berhasil, tetapi backup gagal.")
            return

    # Ringkasan terminal

    print("\n" + "=" * 50)
    print("       PEMROSESAN BERHASIL")
    print("=" * 50)

    print(f"Total buku       : {len(data_books)}")
    print(f"Folder data      : {RAW_DIR}")
    print(f"Folder output    : {OUTPUT_DIR}")

    if args.backup:
        print(f"Folder backup    : {BACKUP_DIR}")

    print("=" * 50)


# ==========================================
# 8. EKSEKUSI PROGRAM
# ==========================================

if __name__ == "__main__":

    main()
