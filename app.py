import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import os
import re
import random
from datetime import datetime
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright

class FlightScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Flights Scraper - Air Canada")
        self.root.geometry("700x500")
        self.is_running = False

        # Interface
        # Targeted URL
        tk.Label(root, text="URL Google Flights :").pack(pady=(10, 0), anchor="w", padx=20)
        self.url_entry = tk.Entry(root, width=80)
        self.url_entry.insert(0, "Paste complete URL here...")
        self.url_entry.pack(pady=5, padx=20)

        # Intervals
        frame_interval = tk.Frame(root)
        frame_interval.pack(pady=10)
        tk.Label(frame_interval, text="Intervalle de scan (en minutes) :").pack(side=tk.LEFT)
        self.interval_entry = tk.Entry(frame_interval, width=10)
        self.interval_entry.insert(0, "30")
        self.interval_entry.pack(side=tk.LEFT, padx=10)

        # Buttons
        frame_buttons = tk.Frame(root)
        frame_buttons.pack(pady=10)
        self.btn_start = tk.Button(frame_buttons, text="▶ Démarrer la collecte", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=self.start_scraping)
        self.btn_start.pack(side=tk.LEFT, padx=10)
        
        self.btn_stop = tk.Button(frame_buttons, text="⏹ Arrêter", bg="#F44336", fg="white", font=("Arial", 10, "bold"), state=tk.DISABLED, command=self.stop_scraping)
        self.btn_stop.pack(side=tk.LEFT, padx=10)

        # Console Log
        tk.Label(root, text="Journal d'activité :").pack(anchor="w", padx=20)
        self.log_area = scrolledtext.ScrolledText(root, width=80, height=15, state='disabled', bg="#f4f4f4")
        self.log_area.pack(pady=5, padx=20)

        # Data folder setup
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        os.makedirs(self.data_dir, exist_ok=True)

    def log(self, message):
        """Print a message in the console"""
        now = datetime.now().strftime("%H:%M:%S")
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, f"[{now}] {message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def extract_air_canada_price(self, raw_text):
        ac_indices = [m.start() for m in re.finditer(r'Air Canada', raw_text)]
        if not ac_indices:
            return None
        for index in ac_indices:
            window = raw_text[index:index + 600]
            matches = re.findall(r'\[null,\s*(\d{2,5})\]', window)
            for m in matches:
                val = int(m)
                if 50 <= val <= 10000:
                    return val
        return None

    def run_single_scan(self, url):
        """Execute a Playwright Scan"""
        self.log("Invisible browser is launching")
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    locale='fr-CA', timezone_id='America/Toronto'
                )
                context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                page = context.new_page()
                
                captured_price = None
                raw_response_data = None

                def handle_response(response):
                    nonlocal captured_price, raw_response_data
                    if "GetShoppingResults" in response.url and response.status == 200:
                        try:
                            raw_text = response.text()
                            raw_response_data = raw_text
                            price = self.extract_air_canada_price(raw_text)
                            if price: captured_price = price
                        except: pass

                page.on("response", handle_response)
                page.goto(url, wait_until="domcontentloaded")
                
                try:
                    consent_button = page.locator('button:has-text("Accept All"), button:has-text("Accept all"), button:has-text("I accept")').first
                    if consent_button.is_visible(timeout=3000):
                        consent_button.click()
                except: pass

                page.wait_for_load_state("networkidle")
                time.sleep(random.uniform(3.0, 5.0))

                if not captured_price:
                    content = page.content()
                    raw_response_data = content
                    captured_price = self.extract_air_canada_price(content)

                timestamp = datetime.now(ZoneInfo("America/Toronto")).strftime('%Y%m%d_%H%M%S')
                
                # Capture et brut
                page.screenshot(path=os.path.join(self.data_dir, f"screenshot_{timestamp}.png"), full_page=True)
                if raw_response_data:
                    with open(os.path.join(self.data_dir, f"brut_{timestamp}.txt"), "w", encoding="utf-8") as f:
                        f.write(raw_response_data)

                if captured_price:
                    now_est = datetime.now(ZoneInfo("America/Toronto"))
                    date_str = now_est.strftime('%Y-%m-%d')
                    heure_str = now_est.strftime('%H:%M:%S')
                    csv_path = os.path.join(self.data_dir, "prix_vol.csv")
                    file_exists = os.path.exists(csv_path)
                    
                    with open(csv_path, "a", encoding="utf-8") as f:
                        if not file_exists:
                            f.write("URL,prix,date,heure\n")
                        f.write(f"{url},{captured_price},{date_str},{heure_str}\n")
                    self.log(f"Success ! Air Canada Price : {captured_price}$ saved.")
                else:
                    self.log("No price has been found. Check the screenshot.")

                context.close()
                browser.close()
        except Exception as e:
            self.log(f"Scan Error : {e}")

    def scraping_loop(self, url, interval_minutes):
        """Infinite loop running in the background"""
        while self.is_running:
            self.log(f"! Start Scanning ! Make sure the CSV file is closed.")
            self.run_single_scan(url)
            
            if not self.is_running: break
            
            self.log(f"Waiting {interval_minutes} minutes before next scan.")
            for _ in range(int(interval_minutes * 60)):
                if not self.is_running: break
                time.sleep(1)

    def start_scraping(self):
        url = self.url_entry.get().strip()
        try:
            interval = float(self.interval_entry.get())
        except ValueError:
            self.log("Please enter a valid entry for the interval (minutes)")
            return

        if not url.startswith("http"):
            self.log("Please enter a valid Google Flights URL.")
            return

        self.is_running = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.url_entry.config(state=tk.DISABLED)
        self.interval_entry.config(state=tk.DISABLED)
        
        self.log(f"Starting automatic data collection for every {interval} min.")
        
        # Open the scraper on a different thread so it won't freeze.
        threading.Thread(target=self.scraping_loop, args=(url, interval), daemon=True).start()

    def stop_scraping(self):
        self.log("Stopping in progress.")
        self.is_running = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.url_entry.config(state=tk.NORMAL)
        self.interval_entry.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = FlightScraperApp(root)
    root.mainloop()