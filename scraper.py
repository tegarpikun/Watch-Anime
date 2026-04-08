import requests
from bs4 import BeautifulSoup
import re
import time

# 1. KONFIGURASI API (Ganti dengan URL hasil Deploy terbaru)
API_URL = "https://script.google.com/macros/s/AKfycbxzT1aXzxJML4fwr5aR6aMKkxbq1ASHbBAl1IMF4os3Gf-FRpaki0nagsBOCdK8_2evjg/exec"

def send_to_sheets(judul, sumber, link, thumb):
    payload = {"judul": judul, "episode": sumber, "link_video": link, "thumbnail": thumb}
    try:
        r = requests.post(API_URL, json=payload, timeout=30)
        print(f">>> [TERKIRIM] {judul} ({sumber})")
    except:
        print(f">>> [GAGAL] Gagal mengirim data ke Sheets")

def bongkar_video(url):
    """Mencari link video di berbagai provider (Blogger, Google, Anime, Drive, dll)"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        # Mencari link video langsung menggunakan pola teks (Regex)
        # Mencakup Blogger, Vtyu, Google Drive, dan pola umum video lainnya
        match = re.search(r'https?://(?:www\.blogger\.com/video\.g\?token=|vtyu\.to/|drive\.google\.com/file/d/|www\.fembed\.com/v/)[^"\']+', res.text)
        if match:
            return match.group(0)
        
        # Jika tidak ketemu lewat teks, cari di dalam tag iframe
        soup = BeautifulSoup(res.text, 'html.parser')
        for ifrm in soup.find_all('iframe'):
            src = ifrm.get('src', '')
            # Filter provider video populer di situs anime
            if any(k in src for k in ['blogger', 'anime', 'google', 'ok.ru', 'vidoza', 'archive.org']):
                return src
    except:
        return None
    return None

def scrape_anime_sites(name, url, link_pattern):
    """Fungsi untuk mengambil daftar anime dari berbagai sumber"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        print(f"\n>>> MENYAPU SUMBER: {name} - {url}")
        res = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Mencari link yang mengarah ke konten video/episode
            if any(p in href for p in link_pattern):
                if href.startswith('/'): 
                    domain = "/".join(url.split("/")[:3])
                    href = domain + href
                links.append(href)
        
        # Ambil 10 link unik terbaru
        unique_links = list(dict.fromkeys(links))[:10]
        for link in unique_links:
            video = bongkar_video(link)
            if video:
                # Ambil judul dari halaman episode
                p_res = requests.get(link, headers=headers)
                p_soup = BeautifulSoup(p_res.text, 'html.parser')
                judul = p_soup.find('h1').text.strip() if p_soup.find('h1') else "Judul Anime"
                
                # Kirim data ke Google Sheets
                send_to_sheets(judul, name, video, "")
                time.sleep(1) # Jeda agar tidak dianggap spam oleh Google
    except Exception as e:
        print(f">>> ERROR DI {name}: {e}")

if __name__ == "__main__":
    # DAFTAR TARGET SITUS ANIME (Bisa kamu tambah lagi sesuai keinginan)
    targets = [
        {"name": "Anoboy", "url": "https://typemyessays.com//", "pattern": ["/episode/"]},
        {"name": "Otakudesu", "url": "https://otakudesu.blog//", "pattern": ["/episode/"]},
        {"name": "Gomunime", "url": "https://gomunime.top//", "pattern": ["/episode/"]}
    ]

    print(">>> MEMULAI BOT PENCARI ANIME MULTI-SUMBER...")
    for target in targets:
        scrape_anime_sites(target['name'], target['url'], target['pattern'])
