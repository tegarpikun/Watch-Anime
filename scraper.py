import requests
from bs4 import BeautifulSoup
import json

# Konfigurasi - Ganti dengan URL Apps Script kamu (Pastikan berakhiran /exec)
API_URL = "https://script.google.com/macros/s/AKfycbxzT1aXzxJML4fwr5aR6aMKkxbq1ASHbBAl1IMF4os3Gf-FRpaki0nagsBOCdK8_2evjg/exec"

def send_to_sheets(judul, eps, link, thumb):
    """Fungsi khusus untuk mengirim data ke Google Sheets"""
    payload = {
        "judul": judul,
        "episode": eps,
        "link_video": link,
        "thumbnail": thumb
    }
    try:
        # Menggunakan json=payload secara otomatis mengatur Header ke Application/JSON
        # Ini jauh lebih stabil untuk diterima oleh doPost Apps Script
        r = requests.post(API_URL, json=payload) 
        print(f"Respon Google: {r.text}")
    except Exception as e:
        print(f"Gagal mengirim ke Sheets: {e}")

def ambil_data_anime(url_tujuan):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        print(f"Mencoba mencari data di: {url_tujuan}")
        response = requests.get(url_tujuan, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Cari Judul
        judul_tag = soup.find('h1')
        judul = judul_tag.text.strip() if judul_tag else "Judul Tidak Ditemukan"
        
        # 2. Cari Iframe Video
        iframe = soup.find('iframe', id='mediaplayer')
        link_video = iframe.get('src') if iframe else None
        
        # 3. Cari Thumbnail (Meta Tag)
        thumb_tag = soup.find('meta', property='og:image')
        thumbnail = thumb_tag.get('content') if thumb_tag else ""

        # Jika data penting ditemukan, kirim ke Sheets
        if link_video:
            print(f"Data ditemukan! Judul: {judul}")
            # Panggil fungsi pengirim data
            send_to_sheets(judul, "01", link_video, thumbnail)
        else:
            print("Gagal menemukan link video (iframe). Periksa apakah ID 'mediaplayer' benar.")
            
    except Exception as e:
        print(f"Error saat scraping: {e}")

# --- EKSEKUSI ---
# Masukkan link episode yang mau di-scan
link_target = "https://anoboy.my.id/episode/judul-anime-eps-1/" 
ambil_data_anime(link_target)
