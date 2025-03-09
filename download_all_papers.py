import os
import re
import json
from tools.pdf_download_scraper import download_pdf, get_scihub_pdf, get_pdf_from_html

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.path.join(os.getcwd(), "output"))
input_file = os.path.join(OUTPUT_DIR, "deep_reference_results.json")
output_folder = os.path.join(OUTPUT_DIR, "research_papers")

def download_paper_pdf(paper, output_folder=output_folder):
    """
    Downloads the PDF for a given paper and saves it to the specified output folder.
    Special characters in the title are replaced with underscores.
    """
    os.makedirs(output_folder, exist_ok=True)
    
    title = paper.get("title", "paper")
    # Remove special characters by replacing non-alphanumeric with underscores.
    safe_title = re.sub(r'[^A-Za-z0-9]+', '_', title)
    local_pdf = os.path.join(output_folder, f"{safe_title}.pdf")
    
    if os.path.exists(local_pdf):
        print(f"PDF for '{title}' already exists in {output_folder}.")
        return local_pdf

    pdf_url = paper.get("pdf_url")
    html_url = paper.get("html_url")
    doi = paper.get("doi")
    
    if pdf_url:
        print(f"Downloading direct PDF for '{title}'...")
        download_pdf(pdf_url, local_pdf)
    elif html_url:
        print(f"Scraping PDF from HTML for '{title}'...")
        pdf_url = get_pdf_from_html(html_url)
        if pdf_url:
            download_pdf(pdf_url, local_pdf)
    elif doi:
        print(f"Using Sci-Hub for DOI '{doi}' for '{title}'...")
        pdf_url = get_scihub_pdf(doi)
        if pdf_url:
            download_pdf(pdf_url, local_pdf)
    else:
        print(f"No PDF source available for '{title}'.")
        return None

    if os.path.exists(local_pdf):
        return local_pdf
    return None

def download_all_papers(json_file=input_file, output_folder=output_folder):
    """
    Reads the JSON file containing the paper references and downloads each PDF
    to the specified output folder.
    """
    with open(json_file, "r", encoding="utf-8") as f:
        papers = json.load(f)
    
    for paper in papers:
        download_paper_pdf(paper, output_folder)

if __name__ == "__main__":
    download_all_papers()
