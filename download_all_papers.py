import os
import re
import json
from tools.pdf_download_scraper import download_pdf, get_scihub_pdf, get_pdf_from_html

def download_paper_pdf(paper, output_folder, log_fn=print):
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
        log_fn(f"PDF for '{title}' already exists in {output_folder}.")
        return local_pdf

    pdf_url = paper.get("pdf_url")
    html_url = paper.get("html_url")
    doi = paper.get("doi")
    
    if pdf_url:
        log_fn(f"Downloading direct PDF for '{title}'...")
        download_pdf(pdf_url, local_pdf)
    elif html_url:
        log_fn(f"Scraping PDF from HTML for '{title}'...")
        pdf_url = get_pdf_from_html(html_url)
        if pdf_url:
            download_pdf(pdf_url, local_pdf)
    elif doi:
        log_fn(f"Using Sci-Hub for DOI '{doi}' for '{title}'...")
        pdf_url = get_scihub_pdf(doi)
        if pdf_url:
            download_pdf(pdf_url, local_pdf)
    else:
        log_fn(f"No PDF source available for '{title}'.")
        return None

    if os.path.exists(local_pdf):
        return local_pdf
    return None

def download_all_papers(json_file=None, output_folder=None, log_fn=print):
    """
    Reads the JSON file containing the paper references and downloads each PDF
    to the specified output folder.
    """
    if output_folder is None:
        raise ValueError("An output folder must be provided.")
    
    # Assume the JSON file is stored inside the provided output folder
    if json_file is None:
        json_file = os.path.join(os.path.dirname(output_folder), "deep_reference_results.json")
    with open(json_file, "r", encoding="utf-8") as f:
        papers = json.load(f)
    
    for paper in papers:
        download_paper_pdf(paper, output_folder, log_fn=print)

if __name__ == "__main__":
    download_all_papers()
