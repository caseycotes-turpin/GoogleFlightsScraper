import json
import re
import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright
from datetime import datetime
from zoneinfo import ZoneInfo

TARGET_API_ENDPOINT = "GetShoppingResults"
TARGET_FLIGHT_URL = "https://www.google.com/travel/flights/search?tfs=CBwQAhooEgoyMDI2LTExLTA4agwIAxIIL20vMGg3aDZyDAgDEggvbS8wODBoMhooEgoyMDI2LTExLTE1agwIAxIIL20vMDgwaDJyDAgDEggvbS8waDdoNkABSAFwAYIBCwj___________8BmAEB&tfu=EgYIABAAGAA"

def extract_air_canada_price(raw_text):
    """
    Searching 'Air Canada' and extract the first price
    """
    # Looking for all Air Canada occurences
    ac_indices = [m.start() for m in re.finditer(r'Air Canada', raw_text)]
    
    if not ac_indices:
        print("Impossible to find Air Canada for this request.")
        return None

    # For every Air Canada occurence we are searching the price in the next 500 chars.
    for index in ac_indices:
        #Extract window after finding an Air Canada occurence
        window = raw_text[index:index + 600]
        
        # Looking for price patterns [null, PRICE] in the specific window
        matches = re.findall(r'\[null,\s*(\d{2,5})\]', window)
        for m in matches:
            val = int(m)
            if 50 <= val <= 10000:  # Prix réaliste
                print(f"Air Canada price targeted successfully : {val} $")
                return val
                
    # Fallback if the targeting fails.
    print("Air Canada Targeting failed. Choosing first overall price.")
    fallback_matches = re.findall(r'\[null,\s*(\d{2,5})\]', raw_text)
    for m in fallback_matches:
        val = int(m)
        if 50 <= val <= 10000:
            return val
            
    return None

def run(playwright):
    browser = playwright.chromium.launch(
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        locale='fr-CA',
        timezone_id='America/Toronto',
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36' 
    )# based on standard eastern time ^
    context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    page = context.new_page()
    captured_price = None
    raw_response_data = None

    def handle_response(response):
        nonlocal captured_price, raw_response_data
        if TARGET_API_ENDPOINT in response.url and response.status == 200:
            try:
                raw_text = response.text()
                raw_response_data = raw_text
                price = extract_air_canada_price(raw_text)
                if price:
                    captured_price = price
            except Exception:
                pass

    page.on("response", handle_response)
    print("Navigation to Google Flights...")
    page.goto(TARGET_FLIGHT_URL, wait_until="domcontentloaded")
    
    # Gestion des cookies
    try:
        consent_button = page.locator('button:has-text("Accept all"), button:has-text("Accept all"), button:has-text("I accept")').first
        if consent_button.is_visible(timeout=3000):
            consent_button.click()
    except Exception:
        pass

    page.wait_for_load_state("networkidle")
    time.sleep(random.uniform(3.0, 5.0))

    if not captured_price:
        content = page.content()
        raw_response_data = content
        captured_price = extract_air_canada_price(content)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save a screenshot
    debug_image_path = f"/app/data/screenshot_{timestamp}.png"
    page.screenshot(path=debug_image_path, full_page=True)
    
    # Save raw data
    if raw_response_data:
        raw_filename = f"/app/data/brut_{timestamp}.txt"
        with open(raw_filename, "w", encoding="utf-8") as f:
            f.write(raw_response_data)

    # Save data to CSV file
    if captured_price:
        # Standard eastern time
        now_est = datetime.now(ZoneInfo("America/Toronto"))
        date_str = now_est.strftime('%Y-%m-%d')
        heure_str = now_est.strftime('%H:%M:%S')
        flight_id = "YUL-YVR-20261108"
        
        csv_path = "/app/data/prix_vol.csv"
        import os
        file_exists = os.path.exists(csv_path)
        
        with open(csv_path, "a", encoding="utf-8") as f:
            if not file_exists:
                f.write("ID,prix,date,heure\n")
            f.write(f"{flight_id},{captured_price},{date_str},{heure_str}\n")
            
        print(f" Air Canada Data added to CSV : Price={captured_price}$, Date={date_str}, Hour={heure_str} (Eastern Time)")
    else:
        print("No Air Canada price has been saved. Error.")

    context.close()
    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)