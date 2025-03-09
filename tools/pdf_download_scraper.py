import os
import json
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.getcwd())
JSON_FILE = os.path.join(OUTPUT_DIR, "top3_results_scholar.json")

def read_json(filename):
    """Reads a JSON file and returns the parsed data."""
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return []

def download_pdf(pdf_url, save_path):
    """Downloads a PDF from a given URL without CAPTCHA handling."""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(pdf_url, headers=headers, stream=True)
        if response.status_code == 200:
            with open(save_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"PDF saved to {save_path}")
        else:
            print(f"Failed to download PDF ({response.status_code}): {pdf_url}")
    except Exception as e:
        print(f"Error downloading PDF: {e}")

def get_scihub_pdf(doi):
    """Fetch PDF URL from Sci-Hub using a given DOI."""
    scihub_url = f"https://sci-hub.se/{doi}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(scihub_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch Sci-Hub page: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        iframe = soup.find("iframe")

        if iframe:
            pdf_url = iframe.get("src")
            if pdf_url.startswith("//"):
                pdf_url = "https:" + pdf_url
            return pdf_url

    except Exception as e:
        print(f"Error fetching Sci-Hub PDF: {e}")

    return None

def get_pdf_from_html(html_url):
    """Uses Selenium to extract the PDF download link from an article page."""
    options = Options()
    options.headless = True
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    driver.get(html_url)
    time.sleep(3)

    pdf_url = None
    try:
        pdf_element = driver.find_element("xpath", "//a[contains(@href, 'pdf')]")
        pdf_url = pdf_element.get_attribute("href")
    except Exception as e:
        print(f"PDF link not found on page: {html_url} | Error: {e}")

    driver.quit()
    return pdf_url

def process_papers():
    """Reads JSON, processes each paper, and downloads PDFs."""
    papers = read_json(JSON_FILE)
    
    if not papers:
        print("No papers found in the JSON file.")
        return
    
    for index, paper in enumerate(papers, start=1):
        title = paper.get("title", f"paper_{index}")
        pdf_url = paper.get("pdf_url", None)
        html_url = paper.get("html_url", None)
        doi = paper.get("doi", None)

        print(f"\nProcessing: {title}")

        if pdf_url:
            print(f"Direct PDF found: {pdf_url}")
            save_path = f"{title.replace(' ', '_')}.pdf"
            download_pdf(pdf_url, save_path)

        elif html_url:
            print(f"Extracting PDF from: {html_url}")
            pdf_url = get_pdf_from_html(html_url)
            if pdf_url:
                save_path = f"{title.replace(' ', '_')}.pdf"
                download_pdf(pdf_url, save_path)
            else:
                print("No PDF URL extracted from the HTML page.")

        elif doi:
            print(f"Trying Sci-Hub for DOI: {doi}")
            pdf_url = get_scihub_pdf(doi)
            if pdf_url:
                save_path = f"{title.replace(' ', '_')}.pdf"
                download_pdf(pdf_url, save_path)
            else:
                print("No PDF URL obtained from Sci-Hub.")
        else:
            print(f"No PDF URL found for: {title}")

if __name__ == "__main__":
    try:
        process_papers()
    except ValueError as e:
        print(f"Error: {e}")