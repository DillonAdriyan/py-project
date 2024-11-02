import requests
import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from tqdm import tqdm
import time
from bs4 import BeautifulSoup
from itertools import permutations  # Untuk menghasilkan kombinasi yang dibolak-balik
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
# URL yang menggunakan PHP dan menampilkan data dalam HTML
url = "https://rankcrack.com/data-hongkong.php"

# Mengirim permintaan HTTP ke URL
response = requests.get(url)

# Memastikan permintaan berhasil
if response.status_code == 200:
    # Mengurai konten HTML dengan BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Mencari elemen yang berisi nomor dalam semua kolom di dalam baris tabel
    data_numbers = []
    for row in soup.select('#myTable tr'):
        columns = row.find_all('td')
        if columns:
            for col in columns:
                nomor_text = col.get_text(strip=True)
                if nomor_text.isdigit():  # Cek apakah nomor hanya berisi angka
                    nomor = int(nomor_text)
                    data_numbers.append(nomor)
    
    # Konversi ke DataFrame
    df = pd.DataFrame(data_numbers, columns=['angka'])
    print("Data berhasil diambil:")
    print(df)
else:
    print("Gagal mengakses URL")
    df = None

# Lanjutkan ke langkah berikutnya jika data berhasil diambil
if df is not None and not df.empty:
    # Step 2: Pra-pemrosesan data
    print("Memproses data...")
    angka_series = df['angka'].values.reshape(-1, 1)

    # Skala data agar sesuai dengan range [0,1] untuk LSTM
    scaler = MinMaxScaler(feature_range=(0, 1))
    angka_scaled = scaler.fit_transform(angka_series)
    print("Data telah diskalakan.")

    # Membuat dataset urutan (sliding window) untuk LSTM
    def create_sequences(data, seq_length):
        X, y = [], []
        for i in range(len(data) - seq_length):
            X.append(data[i:i+seq_length])
            y.append(data[i+seq_length])
        return np.array(X), np.array(y)

    seq_length = 5
    X, y = create_sequences(angka_scaled, seq_length)
    print(f"Data telah diubah menjadi urutan dengan panjang {seq_length}.")

    # Step 3: Membuat model LSTM
    print("Membangun model LSTM...")
    model = Sequential()
    model.add(LSTM(50, activation='relu', input_shape=(seq_length, 1)))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    print("Model LSTM siap untuk dilatih.")

    # Step 4: Melatih model dengan progress bar
    epochs = 200
    batch_size = 32
    print("Memulai proses pelatihan model...")
    for epoch in tqdm(range(epochs), desc="Epochs"):
        model.fit(X, y, epochs=1, batch_size=batch_size, verbose=0)
        time.sleep(0.1)  # Menambahkan jeda untuk tampilan yang lebih jelas di tqdm
    print("Proses pelatihan selesai.")

    # Step 5: Prediksi
    print("\nMemprediksi nomor berikutnya...")
    last_sequence = angka_scaled[-seq_length:]
    last_sequence = last_sequence.reshape((1, seq_length, 1))
    prediksi_scaled = model.predict(last_sequence)
    prediksi = scaler.inverse_transform(prediksi_scaled)

    # Menampilkan hasil pencocokan dan prediksi
    print("\nHasil Pencocokan dan Prediksi:")
    print(f"Data terakhir: {angka_series[-seq_length:].flatten()}")
    print(f"Prediksi nomor berikutnya: {prediksi[0][0]:.2f}")

    # Angka prediksi yang telah dihasilkan dari model
    prediksi_angka = str(int(prediksi[0][0]))  # Konversi prediksi ke string

    # Fungsi untuk membuat kombinasi angka termasuk urutan bolak-balik
    def generate_permutations(prediction, length):
        unique_permutations = set([''.join(p) for p in permutations(prediction, length)])
        return list(unique_permutations)

    # Membuat kombinasi 2 digit, 3 digit, dan 4 digit dari angka prediksi
    print("\nVariasi kombinasi angka dari prediksi dengan urutan bolak-balik:")
    for length in range(2, min(5, len(prediksi_angka) + 1)):
        combinations_result = generate_permutations(prediksi_angka, length)
        print(f"{length} digit kombinasi: {sorted(combinations_result)}")


# Fungsi untuk menyimpan prediksi dan kombinasi ke dalam PDF
def save_to_pdf(prediksi, kombinasi):
    # Membuat nama file PDF baru berdasarkan waktu saat ini
    pdf_filename = f'Prediksi_dan_Kombinasi_{int(time.time())}.pdf'
    
    # Mengatur canvas untuk PDF
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter

    # Menulis judul
    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, height - 50, "Prediksi dan Kombinasi Angka")
    
    # Menulis nomor prediksi
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 100, f"Prediksi Nomor Berikutnya: {prediksi[0][0]:.2f}")

    # Menulis kombinasi
    c.drawString(100, height - 130, "Kombinasi Angka:")
    y_position = height - 150
    for length, comb in kombinasi.items():
        c.drawString(100, y_position, f"{length} Digit Kombinasi: {', '.join(sorted(comb))}")
        y_position -= 20  # Menambahkan jarak untuk baris berikutnya

    # Menyelesaikan dan menyimpan PDF
    c.save()
    print(f"File PDF berhasil dibuat: {pdf_filename}")

# Di bagian akhir kode sebelumnya, setelah mencetak hasil kombinasi
    # Menyimpan hasil ke PDF
    kombinasi_hasil = {}
    for length in range(2, min(5, len(prediksi_angka) + 1)):
        kombinasi_hasil[length] = generate_permutations(prediksi_angka, length)
    
    save_to_pdf(prediksi, kombinasi_hasil)
    