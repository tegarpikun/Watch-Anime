import requests
from bs4 import BeautifulSoup
import time
import re
import random
import urllib3

# Menonaktifkan peringatan SSL Insecure (karena kita pakai verify=False nanti)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === KONFIGURASI ===
API_URL = "https://script.google.com/macros/s/AKfycbx3ApBu4ynG8H8R-aRofIomjiLEJni3d2J0pEMLn7sTGWzSVWIzVgvZ_j6eTaBL08Yh5Q/exec"

class UniversalAnimeScraper:
    def __init__(self):
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/123.0.0.0'
        ]

    def get_headers(self, referer=None):
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9',
            'Connection': 'keep-alive',
        }
        if referer: headers['Referer'] = referer
        return headers

    def kirim_ke_sheets(self, judul, eps, link, thumb):
        payload = {"judul": judul.strip(), "episode": eps, "link_video": link, "thumbnail": thumb}
        try:
            r = self.session.post(API_URL, json=payload, timeout=30)
            print(f"    [Sheets] Berhasil: {judul[:30]}...")
            return True
        except: return False

    def scrap_otakudesu(self):
        url = "https://otakudesu.blog/" 
        print(f"\n[1] Memeriksa Otakudesu: {url}")
        try:
            # TAMBAHAN: verify=False untuk melewati SSL Error
            res = self.session.get(url, headers=self.get_headers(), timeout=15, verify=False)
            soup = BeautifulSoup(res.text, 'html.parser')
            # Gunakan selector yang lebih stabil
            items = soup.select('.venz ul li') or soup.find_all('div', class_='utul')
            
            for item in items[:5]:
                try:
                    judul = item.find('h2').text if item.find('h2') else item.find('h3').text
                    link = item.find('a')['href']
                    thumb = item.find('img')['src'] if item.find('img') else ""
                    self.kirim_ke_sheets(judul, "Baru", link, thumb)
                except: continue
        except Exception as e:
            print(f"    Error Otakudesu: {e}")

    def scrap_anoboy(self):
        url = "anoboy7.com"
        print(f"\n[2] Memeriksa Anoboy: {url}")
        try:
            res = self.session.get(url, headers=self.get_headers(), timeout=15)
            soup = BeautifulSoup(res.text, 'html.parser')
            # Update selector Anoboy
            items = soup.select('.column-content a') or soup.select('.home_index')
            
            for item in items[:5]:
                try:
                    link = item['href'] if item.name == 'a' else item.find('a')['href']
                    judul = item.find('h3').text if item.find('h3') else item.get('title', 'Anime')
                    thumb = item.find('img')['src'] if item.find('img') else ""
                    self.kirim_ke_sheets(judul, "Update", link, thumb)
                except: continue
        except Exception as e:
            print(f"    Error Anoboy: {e}")

    def scrap_gomunime(self):
        url = "gomunime.top"
        print(f"\n[3] Memeriksa Gomunime: {url}")
        try:
            res = self.session.get(url, headers=self.get_headers(referer=url), timeout=15)
            soup = BeautifulSoup(res.text, 'html.parser')
            # Update selector Gomunime
            items = soup.select('.list-update .item') or soup.select('article')
            
            for item in items[:5]:
                try:
                    judul = item.find('h3').text if item.find('h3') else item.find('h2').text
                    link = item.find('a')['href']
                    thumb = item.find('img')['src'] if item.find('img') else ""
                    self.kirim_ke_sheets(judul, "Terbaru", link, thumb)
                except: continue
        except Exception as e:
            print(f"    Error Gomunime: {e}")

if __name__ == "__main__":
    scraper = UniversalAnimeScraper()
    scraper.scrap_otakudesu()
    scraper.scrap_anoboy()
    scraper.scrap_gomunime()
    print("\n=== SELESAI ===")
