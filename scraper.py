import requests
from bs4 import BeautifulSoup
import json
import re
import sys

# 1. KONFIGURASI
API_URL = "https://script.google.com/macros/s/AKfycbxzT1aXzxJML4fwr5aR6aMKkxbq1ASHbBAl1IMF4os3Gf-FRpaki0nagsBOCdK8_2evjg/exec"

# 2. FUNGSI PENGIRIM DATA
def send_to_sheets(judul, eps, link, thumb):
    payload = {
        "judul": judul,
        "episode": eps,
        "link_video": link,
        "thumbnail": thumb
    }
    try:
        r = requests.post(API_URL, json=payload, timeout=30)
        print(f">>> RESPON GOOGLE: {r.text}")
    except Exception as e:
        print(f">>> GAGAL KIRIM KE SHEETS: {e}")

# 3. FUNGSI PEMBONGKAR DETAIL
def ambil_data_anime(url_tujuan):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        print(f">>> MEMBONGKAR HALAMAN: {url_tujuan}")
        response = requests.get(url_tujuan, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        judul = soup.find('h1').text.strip() if soup.find('h1') else "Tanpa Judul"
        video_link = None
        
        # Cari di Iframe
        all_iframes = soup.find_all('iframe')
        for ifrm in all_iframes:
            src = ifrm.get('src', '')
            if any(key in src for key in ['blogger.com', 'google.com/video', 'ok.ru', 'vidoza', 'facebook']):
                video_link = src
                break
        
        # Cari di Teks Mentah (Regex) jika Iframe gagal
        if not video_link:
            match = re.search(r'https?://www\.blogger\.com/video\.g\?token=[^"\']+', response.text)
            if match:
                video_link = match.group(0)

        thumb_tag = soup.find('meta', property='og:image')
        thumb = thumb_tag.get('content', '') if thumb_tag else ""

        if video_link:
            if video_link.startswith('//'):
                video_link = 'https:' + video_link
            print(f">>> BERHASIL! Link Video: {video_link}")
            send_to_sheets(judul, "Baru", video_link, thumb)
        else:
            print(f">>> GAGAL: Tidak ada link video di {url_tujuan}")
            
    except Exception as e:
        print(f">>> ERROR FATAL DI DETAIL: {e}")

# 4. FUNGSI UTAMA (Pencari Link di Homepage)
def cari_link_terbaru():
    url_home = "https://anoboy.my.id/" 
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        print(f">>> MENCARI UPDATE TERBARU DI: {url_home}")
        res = requests.get(url_home, headers=headers, timeout=20)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Ambil link yang mengarah ke halaman episode
            if "/episode/" in href:
                if href.startswith('/'):
                    href = "https://anoboy.my.id" + href
                links.append(href)
        
        # Hapus duplikat
        links = list(dict.fromkeys(links)) 
        print(f">>> DITEMUKAN {len(links)} LINK. MEMPROSES 10 TERATAS...")

        for link in links[:10]:
            ambil_data_anime(link)
            
    except Exception as e:
        print(f">>> ERROR DI HOMEPAGE: {e}")

# --- EKSEKUSI ---
if __name__ == "__main__":
    cari_link_terbaru()
