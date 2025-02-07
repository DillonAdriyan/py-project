import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse

def expand_short_url(short_url):
    """Konversi URL pendek pin.it ke URL asli."""
    try:
        response = requests.get(short_url, allow_redirects=False)
        if 300 <= response.status_code < 400:
            return response.headers['Location']
        return short_url
    except Exception as e:
        print(f"Gagal mengembangkan URL: {e}")
        return short_url

def download_image(img_url, save_dir, filename):
    """Unduh gambar dari URL."""
    os.makedirs(save_dir, exist_ok=True)
    try:
        response = requests.get(img_url, stream=True)
        if response.status_code == 200:
            ext = img_url.split('.')[-1].split('?')[0]
            ext = ext if ext.lower() in ['jpg', 'jpeg', 'png', 'webp'] else 'jpg'
            filepath = os.path.join(save_dir, f"{filename}.{ext}")
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Unduh berhasil: {filepath}")
    except Exception as e:
        print(f"Gagal mengunduh {img_url}: {e}")

def scrape_pinterest(url, save_dir="pinterest_images"):
    """Scraping gambar dari URL Pinterest."""
    # Konversi URL pendek ke URL asli
    expanded_url = expand_short_url(url)
    print(f"URL asli: {expanded_url}")

    # Setup Selenium untuk browser Chrome # Setup Selenium untuk browser Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Jalankan di latar belakang
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    # Specify the path to the chromedriver executable
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options) 




    try:
        driver.get(expanded_url)
        driver.implicitly_wait(10)  # Tunggu hingga konten dimuat

        # Scroll halaman untuk memuat gambar (ulangi sesuai kebutuhan)
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            driver.implicitly_wait(2)

        # Parse HTML dengan BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Cari semua tag gambar (sesuaikan selector sesuai struktur Pinterest)
        img_elements = soup.find_all('img', {'data-testid': 'pin-image'})  # Selector mungkin berubah!

        for idx, img in enumerate(img_elements):
            img_url = img.get('src') or img.get('srcset', '').split()[0]
            if img_url and '236x' not in img_url:  # Hindari thumbnail kecil
                high_res_url = img_url.replace('236x', '564x')  # Coba dapatkan resolusi lebih tinggi
                download_image(high_res_url, save_dir, f"pin_{idx+1}")

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
    finally:
        driver.quit()

if __name__ == '__main__':
    url = "https://pin.it/36ZKaiJQz"  # Ganti dengan URL target
    scrape_pinterest(url, save_dir="pinterest_downloads")