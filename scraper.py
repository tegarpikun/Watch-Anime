import requests
from bs4 import BeautifulSoup
import json

# Konfigurasi - Ganti dengan URL Apps Script kamu
API_URL = "https://script.google.com/macros/s/AKfycbxzT1aXzxJML4fwr5aR6aMKkxbq1ASHbBAl1IMF4os3Gf-FRpaki0nagsBOCdK8_2evjg/exec"

def ambil_data_anime(url_tujuan):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url_tujuan, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Contoh mencari judul & link blogger (sesuaikan dengan struktur situs)
        judul = soup.find('h1').text.strip()
        iframe = soup.find('iframe', id='mediaplayer')
        link_video = iframe.get('src') if iframe else None
        
        # Thumbnail (biasanya ada di meta tag og:image)
        thumb_tag = soup.find('meta', property='og:image')
        thumbnail = thumb_tag.get('content') if thumb_tag else ""

        if judul and link_video:
            data = {
                "judul": judul,
                "episode": "01", # Bisa dikembangkan untuk ambil angka eps
                "link_video": link_video,
                "thumbnail": thumbnail
            }
            # Kirim ke Google Sheets lewat Apps Script
            r = requests.post(API_URL, data=json.dumps(data))
            print(f"Status: {r.text} | Anime: {judul}")
            
    except Exception as e:
        print(f"Error: {e}")

# Masukkan link episode yang mau di-scan
ambil_data_anime("https://anoboy.my.id/episode/judul-anime-eps-1/")
