import os
import json
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os

def download_pdf(pdf_url, save_path, log_fn=print):
    """Downloads a PDF from a given URL without CAPTCHA handling."""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(pdf_url, headers=headers, stream=True)
        if response.status_code == 200:
            with open(save_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            log_fn(f"PDF saved to {save_path}")
        else:
            log_fn(f"Failed to download PDF ({response.status_code}): {pdf_url}")
    except Exception as e:
        log_fn(f"Error downloading PDF: {e}")

def get_scihub_pdf(doi, log_fn=print):
    """Fetch PDF URL from Sci-Hub using a given DOI."""
    scihub_url = f"https://sci-hub.se/{doi}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(scihub_url, headers=headers)
        if response.status_code != 200:
            log_fn(f"Failed to fetch Sci-Hub page: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        iframe = soup.find("iframe")

        if iframe:
            pdf_url = iframe.get("src")
            if pdf_url.startswith("//"):
                pdf_url = "https:" + pdf_url
            return pdf_url

    except Exception as e:
        log_fn(f"Error fetching Sci-Hub PDF: {e}")

    return None

def get_pdf_from_html(html_url, log_fn=print):
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
        log_fn(f"PDF link not found on page: {html_url} | Error: {e}")

    driver.quit()
    return pdf_url