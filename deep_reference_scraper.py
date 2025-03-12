import os
import json
import time
from tools.top3_scholar_results import search_google_scholar, extract_research_info  # Existing code for Scholar queries :contentReference[oaicite:0]{index=0}
from tools.pdf_download_scraper import download_pdf, get_scihub_pdf, get_pdf_from_html  # Existing PDF download utilities :contentReference[oaicite:1]{index=1}
from tools.extract_data_from_pdf import process_pdf_with_unstructured, extract_references  # Existing PDF parsing functions :contentReference[oaicite:2]{index=2}

# Global variables
processed_papers = {}  # Dictionary to keep track of processed papers (keyed by DOI or title)
MAX_PAPERS = 100    # Maximum number of papers to collect
MAX_LEVEL = 3          # Maximum BFS levels (depth)

def download_paper_pdf(paper, output_folder, log_fn=print):
    title = paper.get("title", "paper").replace(" ", "_")
    # Ensure the output folder exists.
    os.makedirs(output_folder, exist_ok=True)
    local_pdf = os.path.join(output_folder, f"{title}.pdf")
    if os.path.exists(local_pdf):
        log_fn(f"PDF for '{title}' already exists in {output_folder}.")
        return local_pdf

    pdf_url = paper.get("pdf_url")
    html_url = paper.get("html_url")
    doi = paper.get("doi")
    
    if pdf_url:
        log_fn(f"Downloading direct PDF for '{title}'...")
        download_pdf(pdf_url, local_pdf, log_fn=log_fn)
    elif html_url:
        log_fn(f"Scraping PDF from HTML for '{title}'...")
        pdf_url = get_pdf_from_html(html_url, log_fn=log_fn)
        if pdf_url:
            download_pdf(pdf_url, local_pdf, log_fn=log_fn)
    elif doi:
        log_fn(f"Using Sci-Hub for DOI '{doi}' for '{title}'...")
        pdf_url = get_scihub_pdf(doi, log_fn=log_fn)
        if pdf_url:
            download_pdf(pdf_url, local_pdf, log_fn=log_fn)
    else:
        log_fn(f"No PDF source available for '{title}'.")
        return None

    if os.path.exists(local_pdf):
        return local_pdf
    return None


def extract_references_from_pdf(pdf_path):
    """
    Processes a PDF file to extract and return a list of reference strings.
    """
    content_by_page = process_pdf_with_unstructured(pdf_path)
    combined_text = ""
    
    # Define a custom sort key that handles both integer and string keys.
    def sort_key(k):
        try:
            return int(k)
        except Exception:
            return float('inf')
    
    for page in sorted(content_by_page.keys(), key=sort_key):
        combined_text += content_by_page[page]["text"] + "\n"
    
    # Extract the references block using the existing function.
    research_content, references_text = extract_references(combined_text)
    
    # Split references into individual lines.
    references_list = [ref.strip() for ref in references_text.splitlines() if ref.strip()]
    
    # Filter out entries that are just numbers or very short (likely artifacts)
    filtered_references = [ref for ref in references_list if not ref.isdigit() and len(ref) > 5]
        
    return filtered_references


def bfs_scrape(seed_papers, api_key, output_folder, log_fn=print):
    level = 1
    queue = seed_papers[:]  # Start with seed papers
    while queue and level <= MAX_LEVEL and len(processed_papers) < MAX_PAPERS:
        next_queue = []
        log_fn(f"\nProcessing level {level} with {len(queue)} papers.")
        for paper in queue:
            title = paper.get("title")
            log_fn(f"\nProcessing paper: {title}")
            pdf_path = download_paper_pdf(paper, output_folder, log_fn=log_fn)
            if not pdf_path:
                log_fn(f"Skipping '{title}' due to missing PDF.")
                continue

            references = extract_references_from_pdf(pdf_path)
            log_fn(f"Found {len(references)} references in '{title}'")
            for ref in references:
                if len(processed_papers) >= MAX_PAPERS:
                    break
                results = search_google_scholar(ref, api_key, log_fn=log_fn)
                new_papers = extract_research_info(results)
                if new_papers:
                    new_paper = new_papers[0]  # Take the top result
                    key = new_paper.get("doi") or new_paper.get("title")
                    if key in processed_papers:
                        continue
                    processed_papers[key] = new_paper
                    next_queue.append(new_paper)
                    log_fn(f"Added new paper: {new_paper.get('title')}")
                else:
                    log_fn(f"No paper found for reference: {ref}")
        queue = next_queue
        level += 1


def main(research_topic=None, output_dir=None, log_fn=print):
    import os
    import json
    SERPER_API_KEY = os.environ["SERPER_API_KEY"]
    if not SERPER_API_KEY:
        print("SERPER_API_KEY is not set in the environment.")
        return

    if research_topic is None:
        research_topic = input("Enter your research topic: ")

    results = search_google_scholar(research_topic, SERPER_API_KEY, log_fn=log_fn)
    seed_papers = extract_research_info(results)
    
    if not seed_papers:
        log_fn("No seed papers found for the query.")
        return

    log_fn(f"Found {len(seed_papers)} seed papers. Starting BFS reference scraping...")

    # Define the PDF output folder inside the temporary directory.
    pdf_output_folder = os.path.join(output_dir, "research_papers")
    os.makedirs(pdf_output_folder, exist_ok=True)
    
    # Register seed papers as processed.
    for paper in seed_papers:
        key = paper.get("doi") or paper.get("title")
        processed_papers[key] = paper

    # Call bfs_scrape with the output folder.
    bfs_scrape(seed_papers, SERPER_API_KEY, pdf_output_folder, log_fn=log_fn)
    
    log_fn(f"\nBFS reference scraping complete. Total papers collected: {len(processed_papers)}")
    
    output_path = os.path.join(output_dir, "deep_reference_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(list(processed_papers.values()), f, indent=4)
    log_fn("Results saved to deep_reference_results.json")


if __name__ == "__main__":
    main()
