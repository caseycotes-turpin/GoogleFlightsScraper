✈️ Google Flights Tracker (Air Canada)

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Playwright](https://img.shields.io/badge/Playwright-Automated-green.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-lightgrey.svg)

A lightweight, automated desktop application designed to monitor and record Air Canada flight prices from Google Flights.
Built with Python, Tkinter, and Playwright, this tool provides a user-friendly graphical interface (GUI) that allows non-technical users to scrape flight prices at regular intervals without touching a single line of code or opening a terminal.
✨ Features
User-Friendly GUI: Simple interface to paste your Google Flights URL and set the scanning interval.
Automated Monitoring: Runs silently in the background, fetching prices at your defined frequency (e.g., every 30 minutes).
Data Logging (CSV): Automatically logs the flight URL, target price, and precise timestamps (EST/EDT) into a `prix_vol.csv` file.
Visual Verification: Takes a full-page screenshot (`.png`) during every scan to visually verify the price and page state.
Raw Data Auditing: Saves the raw network response or HTML (`.txt`) for data validation and debugging.
Standalone Executable: Can be distributed as a portable `.exe` for Windows users (no Python installation required).
🚀 How to Use (For Non-Technical Users)
If you have received the packaged version of this software (the ZIP file):
Extract the ZIP file to your Desktop or a folder of your choice.
Important: Ensure the `_internal` folder stays in the exact same location as the executable.
Double-click on `Google_Flights_Bot.exe` to launch the application.
Go to Google Flights in your normal web browser, set up your desired itinerary, and copy the full URL from the address bar.
Paste the URL into the application, set your scan interval (e.g., 30 minutes), and click Start.
All extracted data, screenshots, and logs will be automatically saved in a `data` folder located right next to the `.exe` file.
💻 For Developers (Build from Source)
If you want to clone this repository and build the executable yourself:
Prerequisites
Python 3.10 or higher
Windows OS (for compiling the `.exe`)
1. Install Dependencies
Clone the repository and install the required Python packages:
```bash
pip install playwright tzdata pyinstaller
```
2. Download Playwright Browsers Locally
To package the Chromium browser with the executable, you must force a local installation:
```powershell
$env:PLAYWRIGHT_BROWSERS_PATH="0"
playwright install chromium
```
3. Run Locally (Testing)
```bash
python app.py
```
4. Compile the Executable
Use PyInstaller to bundle the application into a single directory:
```powershell
pyinstaller --noconfirm --onedir --windowed --name "Google_Flights_Bot" --hidden-import tzdata app.py
```
Once finished, you will find the distributable application inside the `dist/Google_Flights_Bot/` directory. Zip this entire folder to share it with your users.
📂 Output Folder Structure
After the first successful scan, the application generates a `data` folder with the following structure:
```text
data/
├── prix_vol.csv                  # Main spreadsheet with historical prices
├── screenshot_20261019_103000.png # Visual proof of the 10:30 AM scan
├── brut_20261019_103000.txt      # Raw JSON/HTML trace of the 10:30 AM scan
└── ...
```
⚠️ Disclaimer
This tool is built for educational and research purposes. Web scraping Google Flights may be subject to their Terms of Service. Changes to the Google Flights DOM or API structure may break the regex extraction logic in the future.
