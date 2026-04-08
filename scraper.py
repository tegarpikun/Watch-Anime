import requests
from bs4 import BeautifulSoup
import time
import json

# GANTI DENGAN URL DEPLOYMENT GOOGLE APPS SCRIPT KAMU
API_URL = "https://script.google.com/macros/s/AKfycbyYXpniK8KsEe3z1bfMbPQocLclT_HbbdawOAO_OqFr9xuMdNeEpLKpi6Fw4NY2TXAPnw/exec"

def ambil_video_embed(url_episode):
    """Membongkar halaman episode untuk mencari link video yang bisa diputar"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        res = requests.get(url_episode, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Mencari iframe yang biasanya berisi video (vtyu, blogger, dsb)
        for ifrm in soup.find_all('iframe'):
            src = ifrm.get('src', '')
            if src and any(p in src for p in ['vtyu', 'vidoza', 'blogger', 'ok.ru', 'youtube']):
                return src
        return None
    except:
        return None

def jalankan_scraper():
    base_url = "https://otakudesu.blog/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    print(">>> MEMULAI SCRAPING OTAKUDESU...")
    
    try:
        response = requests.get(base_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Mencari daftar update terbaru (biasanya dalam class 'utul')
        items = soup.find_all('div', class_='utul')
        
        if not items:
            print(">>> ERROR: Tidak bisa menemukan daftar anime. Class website mungkin berubah.")
            return

        # Ambil 10 anime terbaru
        for item in items[:10]:
            try:
                judul = item.find('h3').text.strip()
                link_eps = item.find('a')['href']
                # Mengambil gambar thumbnail
                thumb = item.find('img')['src'] if item.find('img') else ""
                
                print(f"\n>>> MENGAMBIL: {judul}")
                
                # Masuk ke halaman episode untuk cari link video
                video_url = ambil_video_embed(link_eps)
                
                if video_url:
                    # Menyiapkan data sesuai kebutuhan Apps Script kamu
                    payload = {
                        "judul": judul,
                        "episode": "Terbaru",
                        "link_video": video_url,
                        "thumbnail": thumb
                    }
                    
                    # Mengirim data ke Google Sheets
                    print(f"--- Mengirim ke Google Sheets...")
                    r = requests.post(API_URL, json=payload, timeout=15)
                    print(f"--- RESPON GOOGLE: {r.text}")
                else:
                    print("--- SKIPPED: Tidak ada link video yang bisa diputar.")
                
                # Jeda agar tidak terkena blokir (Anti-Spam)
                time.sleep(2)
                
            except Exception as e:
                print(f"--- ERROR PADA ITEM: {e}")
                
    except Exception as e:
        print(f">>> GAGAL AKSES WEBSITE: {e}")

if __name__ == "__main__":
    jalankan_scraper()
