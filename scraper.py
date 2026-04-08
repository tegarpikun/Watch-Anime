import requests
from bs4 import BeautifulSoup
import time
import json
import sys

# === KONFIGURASI ===
# GANTI DENGAN URL DEPLOYMENT GOOGLE APPS SCRIPT KAMU (akhiran /exec)
API_URL = "https://script.google.com/macros/s/AKfycbyYXpniK8KsEe3z1bfMbPQocLclT_HbbdawOAO_OqFr9xuMdNeEpLKpi6Fw4NY2TXAPnw/exec"

# Header agar menyerupai browser asli (menghindari blokir server)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

def ambil_video_embed(url_episode):
    """Mencari link video player (iframe) di dalam halaman episode"""
    try:
        print(f"   [-] Membongkar halaman: {url_episode}")
        res = requests.get(url_episode, headers=HEADERS, timeout=15)
        if res.status_code != 200:
            print(f"   [!] Gagal akses halaman episode. Status: {res.status_code}")
            return None
            
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Mencari iframe (teknik dari gogoanime_scraper)
        # Kita cari yang mengarah ke provider video populer
        iframes = soup.find_all('iframe')
        for ifrm in iframes:
            src = ifrm.get('src', '')
            if src and any(p in src for p in ['vtyu', 'vidoza', 'blogger', 'ok.ru', 'embed', 'stream']):
                return src
        return None
    except Exception as e:
        print(f"   [!] Error saat ambil embed: {e}")
        return None

def jalankan_scraper():
    target_web = "https://otakudesu.blog/"
    
    print(f"\n--- STEP 1: Akses {target_web} ---")
    try:
        response = requests.get(target_web, headers=HEADERS, timeout=15)
        print(f"Status Koneksi: {response.status_code}")
        
        if response.status_code != 200:
            print("Gagal memuat halaman utama. Mungkin IP diblokir.")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Mencari daftar update terbaru (biasanya di class 'utul')
        items = soup.find_all('div', class_='utul')
        
        if not items:
            print("Gagal menemukan list anime. Struktur HTML mungkin berubah.")
            return

        print(f"Ditemukan {len(items)} update terbaru. Mengambil 5 teratas...")

        for item in items[:5]:
            try:
                judul = item.find('h3').text.strip()
                link_eps = item.find('a')['href']
                thumb = item.find('img')['src'] if item.find('img') else ""
                
                print(f"\n> Judul: {judul}")
                
                # Ekstrak link video player
                video_url = ambil_video_embed(link_eps)
                
                if video_url:
                    print(f"   [OK] Link ditemukan: {video_url[:50]}...")
                    
                    # Kirim ke Google Sheets
                    payload = {
                        "judul": judul,
                        "episode": "Terbaru",
                        "link_video": video_url,
                        "thumbnail": thumb
                    }
                    
                    print("   [-] Mengirim data ke Sheets...")
                    r_gs = requests.post(API_URL, json=payload, timeout=15)
                    print(f"   [-] Respon Sheets: {r_gs.text}")
                else:
                    print("   [!] Tidak ada link video yang bisa diputar.")
                
                time.sleep(3) # Jeda lebih lama agar tidak dianggap spam
                
            except Exception as e:
                print(f"   [!] Gagal memproses item: {e}")

    except Exception as e:
        print(f"ERROR FATAL: {e}")

if __name__ == "__main__":
    print("========================================")
    print("      ANIME SCRAPER SYSTEM START       ")
    print("========================================")
    
    # Cek apakah API_URL sudah diganti
    if "URL_WEB_APP" in API_URL:
        print("KESALAHAN: Kamu belum mengganti API_URL dengan link dari Google Apps Script!")
        sys.exit()
        
    jalankan_scraper()
    print("\n========================================")
    print("           SCRAPER SELESAI             ")
    print("========================================")
