import requests
from bs4 import BeautifulSoup

# URL yang menggunakan PHP dan menampilkan data dalam HTML
url = "https://rankcrack.com/data-hongkong.php"

# Mengirim permintaan HTTP ke URL
response = requests.get(url)

# Memastikan permintaan berhasil
if response.status_code == 200:
    # Mengurai konten HTML dengan BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Mencari elemen yang berisi nomor (misalnya di dalam tabel atau div tertentu)
    # Contoh: Jika datanya ada di dalam tabel dengan kelas 'data-table'
    # Sesuaikan selector sesuai dengan struktur HTML sebenarnya dari halaman tersebut
    data_numbers = []
    for row in soup.select('#myTable tr'):
        columns = row.find_all('td')
        if columns:
            # Ambil teks dari kolom tertentu
            nomor = columns[0].get_text(strip=True)
            data_numbers.append(nomor)
    
    # Tampilkan data yang diambil
    print("Data Nomor yang Ditemukan:")
    for nomor in data_numbers:
        print(nomor)
else:
    print("Gagal mengakses URL")
    