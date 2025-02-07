import requests
import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from sklearn.preprocessing import MinMaxScaler
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from itertools import permutations
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import joblib
import time
import os

class NumberPredictor:
    def __init__(self, url, seq_length=5, cache_file='data_cache.joblib'):
        self.url = url
        self.seq_length = seq_length
        self.cache_file = cache_file
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        
    def fetch_data(self):
        # Cek cache
        if os.path.exists(self.cache_file):
            return joblib.load(self.cache_file)
            
        with ThreadPoolExecutor() as executor:
            future = executor.submit(requests.get, self.url)
            response = future.result()
            
        if response.status_code != 200:
            raise Exception("Gagal mengakses URL")
            
        soup = BeautifulSoup(response.content, 'html.parser')
        data_numbers = []
        
        # Optimasi parsing HTML
        rows = soup.select('#myTable tr')
        for row in rows:
            numbers = [int(col.text.strip()) for col in row.find_all('td') 
                      if col.text.strip().isdigit()]
            data_numbers.extend(numbers)
            
        df = pd.DataFrame(data_numbers, columns=['angka'])
        joblib.dump(df, self.cache_file)
        return df

    def preprocess_data(self, df):
        data = df['angka'].values.reshape(-1, 1)
        data_scaled = self.scaler.fit_transform(data)
        
        X, y = [], []
        for i in range(len(data_scaled) - self.seq_length):
            X.append(data_scaled[i:i+self.seq_length])
            y.append(data_scaled[i+self.seq_length])
            
        return np.array(X), np.array(y)

    def build_model(self):
        model = Sequential([
            LSTM(100, activation='relu', input_shape=(self.seq_length, 1), 
                 return_sequences=True),
            Dropout(0.2),
            BatchNormalization(),
            LSTM(50, activation='relu'),
            Dropout(0.2),
            BatchNormalization(),
            Dense(25, activation='relu'),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='huber')
        return model

    def train_model(self, X, y, epochs=300, batch_size=32):
        self.model = self.build_model()
        self.model.fit(X, y, 
                      epochs=epochs, 
                      batch_size=batch_size,
                      validation_split=0.2,
                      verbose=1)

    def predict_next(self, df):
        last_sequence = df['angka'].values[-self.seq_length:].reshape(-1, 1)
        last_sequence_scaled = self.scaler.transform(last_sequence)
        last_sequence_reshaped = last_sequence_scaled.reshape((1, self.seq_length, 1))
        
        prediction_scaled = self.model.predict(last_sequence_reshaped)
        prediction = self.scaler.inverse_transform(prediction_scaled)
        
        return prediction[0][0]

    def generate_combinations(self, prediction):
        pred_str = str(int(prediction))
        combinations = {}
        
        for length in range(2, min(5, len(pred_str) + 1)):
            perms = set([''.join(p) for p in permutations(pred_str, length)])
            combinations[length] = sorted(perms)
            
        return combinations

    def display_terminal_output(self, df, prediction, combinations):
        print("\n=== 5 Data Terakhir ===")
        print(df['angka'].tail().to_string())
        
        print("\n=== Hasil Prediksi ===")
        print(f"Prediksi angka berikutnya: {prediction:.0f}")
        
        print("\n=== Kombinasi Angka ===")
        for length, combs in combinations.items():
            print(f"{length}-digit: {', '.join(combs)}")

    def save_pdf_report(self, prediction, combinations, filename=None):
        if not filename:
            filename = f'Prediksi_{int(time.time())}.pdf'
            
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Header
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, height - 50, "Laporan Prediksi Angka")
        
        # Prediction
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 100, f"Prediksi: {prediction:.0f}")
        
        # Combinations
        y_pos = height - 130
        for length, combs in combinations.items():
            c.drawString(50, y_pos, f"{length}-digit: {', '.join(combs)}")
            y_pos -= 20
            
        c.save()
        return filename

def main():
    predictor = NumberPredictor("https://rankcrack.com/data-hongkong.php")
    
    try:
        print("Memulai proses prediksi...")
        
        # Load and process data
        df = predictor.fetch_data()
        X, y = predictor.preprocess_data(df)
        
        print("Training model...")
        predictor.train_model(X, y)
        
        # Make prediction
        prediction = predictor.predict_next(df)
        combinations = predictor.generate_combinations(prediction)
        
        # Display results in terminal
        predictor.display_terminal_output(df, prediction, combinations)
        
        # Save report
        pdf_file = predictor.save_pdf_report(prediction, combinations)
        print(f"\nLaporan lengkap tersimpan di: {pdf_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()