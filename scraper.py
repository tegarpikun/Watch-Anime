import requests
from bs4 import BeautifulSoup
import json
import re  # Tambahkan ini di paling atas agar lebih rapi

# 1. KONFIGURASI (WAJIB ADA)
API_URL = "https://script.google.com/macros/s/AKfycbxzT1aXzxJML4fwr5aR6aMKkxbq1ASHbBAl1IMF4os3Gf-FRpaki0nagsBOCdK8_2evjg/exec"

# 2. FUNGSI PENGIRIM DATA (Menggunakan API_URL)
def send_to_sheets(judul, eps, link, thumb):
    payload = {
        "judul": judul,
        "episode": eps,
        "link_video": link,
        "thumbnail": thumb
    }
    try:
        # Di sini API_URL digunakan
        r = requests.post(API_URL, json=payload, timeout=30)
        print(f">>> RESPON GOOGLE: {r.text}")
    except Exception as e:
        print(f">>> GAGAL KIRIM KE SHEETS: {e}")

# 3. FUNGSI PEMBONGKAR (Yang kamu tanyakan)
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
            if any(key in src for key in ['blogger.com', 'google.com/video', 'ok.ru', 'vidoza']):
                video_link = src
                break
        
        # Cari di Teks Mentah jika Iframe gagal
        if not video_link:
            match = re.search(r'https?://www\.blogger\.com/video\.g\?token=[^"\']+', response.text)
            if match:
                video_link = match.group(0)

        thumb = soup.find('meta', property='og:image').get('content', '') if soup.find('meta', property='og:image') else ""

        if video_link:
            if video_link.startswith('//'):
                video_link = 'https:' + video_link
            
            print(f">>> BERHASIL! Link Video: {video_link}")
            # MEMANGGIL FUNGSI KIRIM
            send_to_sheets(judul, "Baru", video_link, thumb)
        else:
            print(f">>> GAGAL: Tidak ada link video di halaman ini.")
            
    except Exception as e:
        print(f">>> ERROR FATAL: {e}")

# 4. FUNGSI UTAMA (Looping)
def cari_link_terbaru():
    # ... (kode fungsi cari_link_terbaru yang sebelumnya) ...
    # Jangan lupa panggil ambil_data_anime(link) di sini

if __name__ == "__main__":
    cari_link_terbaru()
