import requests
from bs4 import BeautifulSoup
import json
import sys

# Konfigurasi - URL Web App kamu (Pastikan berakhiran /exec)
API_URL = "https://script.google.com/macros/s/AKfycbxzT1aXzxJML4fwr5aR6aMKkxbq1ASHbBAl1IMF4os3Gf-FRpaki0nagsBOCdK8_2evjg/exec"

def send_to_sheets(judul, eps, link, thumb):
    """Fungsi mengirim data ke Google Sheets"""
    payload = {
        "judul": judul,
        "episode": eps,
        "link_video": link,
        "thumbnail": thumb
    }
    try:
        # Kirim data sebagai JSON
        r = requests.post(API_URL, json=payload, timeout=30) 
        print(f">>> RESPON GOOGLE: {r.text}")
    except Exception as e:
        print(f">>> GAGAL KIRIM KE SHEETS: {e}")

def ambil_data_anime(url_tujuan):
    """Fungsi scraping detail satu episode"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        print(f">>> SCRAPING DETAIL: {url_tujuan}")
        response = requests.get(url_tujuan, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Ambil Judul
        judul_tag = soup.find('h1')
        judul = judul_tag.text.strip() if judul_tag else "Judul Tidak Ditemukan"
        
        # 2. Ambil Iframe Video
        iframe = soup.find('iframe', id='mediaplayer')
        link_video = iframe.get('src') if iframe else None
        
        # 3. Ambil Thumbnail
        thumb_tag = soup.find('meta', property='og:image')
        thumbnail = thumb_tag.get('content') if thumb_tag else ""

        if link_video:
            print(f">>> DATA VALID: {judul}")
            send_to_sheets(judul, "Baru", link_video, thumbnail)
        else:
            print(f">>> SKIP: Video tidak ditemukan di {url_tujuan}")
            
    except Exception as e:
        print(f">>> ERROR SCRAPING DETAIL: {e}")

def cari_link_terbaru():
    """Fungsi menyapu halaman depan untuk mencari list episode terbaru"""
    url_home = "https://anoboy.my.id/" 
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        print(f">>> MENCARI UPDATE TERBARU DI: {url_home}")
        res = requests.get(url_home, headers=headers, timeout=20)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        links = []
        # Mencari semua tag <a> yang memiliki link ke /episode/
        for a in soup.find_all('a', href=True):
            href = a['href']
            if "/episode/" in href:
                # Pastikan link lengkap (tambahkan domain jika linknya relatif)
                if href.startswith('/'):
                    href = "https://anoboy.my.id" + href
                links.append(href)
        
        # Hapus duplikat dan ambil 10 teratas agar tidak kena spam/limit
        links = list(dict.fromkeys(links)) 
        print(f">>> DITEMUKAN {len(links)} LINK POTENSIAL. MEMPROSES 10 TERBARU...")

        for link in links[:10]:
            ambil_data_anime(link)
            
    except Exception as e:
        print(f">>> ERROR SAAT MENCARI LINK: {e}")

# --- EKSEKUSI ---
if __name__ == "__main__":
    cari_link_terbaru()
