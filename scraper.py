import requests
from bs4 import BeautifulSoup
import time
import re
import sys

# === KONFIGURASI ===
# Masukkan URL Google Apps Script kamu di sini
API_URL = "https://script.google.com/macros/s/AKfycbyYXpniK8KsEe3z1bfMbPQocLclT_HbbdawOAO_OqFr9xuMdNeEpLKpi6Fw4NY2TXAPnw/execw"

class UniversalAnimeScraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive'
        }

    def kirim_ke_sheets(self, judul, eps, link, thumb):
        """Mengirim data hasil scrap ke Google Sheets"""
        payload = {
            "judul": judul,
            "episode": eps,
            "link_video": link,
            "thumbnail": thumb
        }
        try:
            r = self.session.post(API_URL, json=payload, timeout=15)
            print(f"   [Sheets] Respon: {r.text}")
            return True
        except Exception as e:
            print(f"   [Sheets] Gagal Kirim: {e}")
            return False

    def scrap_otakudesu(self):
        url = "https://otakudesu.blog/"
        print(f"\n[1] Memeriksa Otakudesu: {url}")
        try:
            res = self.session.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.find_all('div', class_='utul')
            for item in items[:3]:
                judul = item.find('h3').text.strip()
                link_hal = item.find('a')['href']
                thumb = item.find('img')['src'] if item.find('img') else ""
                # Ambil link video dasar (iframe)
                v_res = self.session.get(link_hal, headers=self.headers, timeout=10)
                v_soup = BeautifulSoup(v_res.text, 'html.parser')
                iframe = v_soup.find('iframe')
                link_video = iframe['src'] if iframe else link_hal
                self.kirim_ke_sheets(judul, "Baru", link_video, thumb)
        except Exception as e:
            print(f"    Error Otakudesu: {e}")

    def scrap_anoboy(self):
        url = "https://anoboy7.com/"
        print(f"\n[2] Memeriksa Anoboy: {url}")
        try:
            res = self.session.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            # Anoboy biasanya menggunakan class 'home_index' atau 'column-content'
            items = soup.find_all('div', class_='home_index')
            for item in items[:3]:
                judul = item.find('h3').text.strip() if item.find('h3') else "Anime Anoboy"
                link_hal = item.find('a')['href']
                thumb = item.find('img')['src'] if item.find('img') else ""
                self.kirim_ke_sheets(judul, "Update", link_hal, thumb)
        except Exception as e:
            print(f"    Error Anoboy: {e}")

    def scrap_gomunime(self):
        url = "https://gomunime.top/"
        print(f"\n[3] Memeriksa Gomunime: {url}")
        try:
            # Gomunime seringkali butuh verifikasi header Referer
            headers = self.headers.copy()
            headers['Referer'] = url
            res = self.session.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            # Gomunime biasanya menggunakan tag article atau div class 'utcl'
            items = soup.select('.list-update .item') or soup.find_all('div', class_='utcl')
            for item in items[:3]:
                judul = item.find('h3').text.strip() if item.find('h3') else "Anime Gomunime"
                link_hal = item.find('a')['href']
                thumb = item.find('img')['src'] if item.find('img') else ""
                self.kirim_ke_sheets(judul, "Terbaru", link_hal, thumb)
        except Exception as e:
            print(f"    Error Gomunime: {e}")

    def run_all(self):
        if "URL_WEB_APP" in API_URL:
            print("!!! ERROR: API_URL belum diisi !!!")
            return
        
        self.scrap_otakudesu()
        time.sleep(2)
        self.scrap_anoboy()
        time.sleep(2)
        self.scrap_gomunime()

if __name__ == "__main__":
    scraper = UniversalAnimeScraper()
    scraper.run_all()
