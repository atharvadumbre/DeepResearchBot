import os
import json
import time
from tools.top3_scholar_results import search_google_scholar, extract_research_info  # Existing code for Scholar queries :contentReference[oaicite:0]{index=0}
from tools.pdf_download_scraper import download_pdf, get_scihub_pdf, get_pdf_from_html  # Existing PDF download utilities :contentReference[oaicite:1]{index=1}
from tools.extract_data_from_pdf import process_pdf_with_unstructured, extract_references  # Existing PDF parsing functions :contentReference[oaicite:2]{index=2}

# Global variables
processed_papers = {}  # Dictionary to keep track of processed papers (keyed by DOI or title)
MAX_PAPERS = 100     # Maximum number of papers to collect
MAX_LEVEL = 3          # Maximum BFS levels (depth)

def download_paper_pdf(paper):
    """
    Downloads the PDF for a given paper using available methods.
    Returns the local filename if successful.
    """
    title = paper.get("title", "paper").replace(" ", "_")
    pdf_url = paper.get("pdf_url")
    html_url = paper.get("html_url")
    doi = paper.get("doi")
    local_pdf = f"{title}.pdf"
    
    if os.path.exists(local_pdf):
        print(f"PDF for '{title}' already exists.")
        return local_pdf

    if pdf_url:
        print(f"Downloading direct PDF for '{title}'...")
        download_pdf(pdf_url, local_pdf)
    elif html_url:
        print(f"Scraping PDF from HTML for '{title}'...")
        pdf_url = get_pdf_from_html(html_url)
        if pdf_url:
            download_pdf(pdf_url, local_pdf)
    elif doi:
        print(f"Using Sci-Hub for DOI '{doi}'...")
        pdf_url = get_scihub_pdf(doi)
        if pdf_url:
            download_pdf(pdf_url, local_pdf)
    else:
        print(f"No PDF source available for '{title}'.")
        return None

    return local_pdf if os.path.exists(local_pdf) else None

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
    
    # Debug: Print each filtered reference.
    print("Filtered References:")
    for idx, ref in enumerate(filtered_references, start=1):
        print(f"Reference {idx}: {ref}")
        
    return filtered_references


def bfs_scrape(seed_papers, api_key):
    """
    Uses breadth-first search to extract references from the given seed papers.
    Processes all papers at a given level before moving to the next.
    """
    level = 1
    queue = seed_papers[:]  # Start with seed papers
    while queue and level <= MAX_LEVEL and len(processed_papers) < MAX_PAPERS:
        next_queue = []
        print(f"\nProcessing level {level} with {len(queue)} papers.")
        for paper in queue:
            title = paper.get("title")
            print(f"\nProcessing paper: {title}")
            pdf_path = download_paper_pdf(paper)
            if not pdf_path:
                print(f"Skipping '{title}' due to missing PDF.")
                continue

            references = extract_references_from_pdf(pdf_path)
            print(f"Found {len(references)} references in '{title}'")
            for ref in references:
                if len(processed_papers) >= MAX_PAPERS:
                    break
                # Use the reference text as a query to fetch the top result.
                results = search_google_scholar(ref, api_key)
                new_papers = extract_research_info(results)
                if new_papers:
                    new_paper = new_papers[0]  # Take the top result
                    key = new_paper.get("doi") or new_paper.get("title")
                    if key in processed_papers:
                        continue
                    processed_papers[key] = new_paper
                    next_queue.append(new_paper)
                    print(f"Added new paper: {new_paper.get('title')}")
                else:
                    print(f"No paper found for reference: {ref}")
        # Move to next level
        queue = next_queue
        level += 1

def main(research_topic=None):
    from dotenv import load_dotenv
    import os
    import json
    load_dotenv()
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")
    if not SERPER_API_KEY:
        print("SERPER_API_KEY is not set in the environment.")
        return

    # If no research topic was provided, fallback to prompting the user.
    if research_topic is None:
        research_topic = input("Enter your research topic: ")

    results = search_google_scholar(research_topic, SERPER_API_KEY)
    seed_papers = extract_research_info(results)
    
    if not seed_papers:
        print("No seed papers found for the query.")
        return

    print(f"Found {len(seed_papers)} seed papers. Starting BFS reference scraping...")

    # Register seed papers as processed
    for paper in seed_papers:
        key = paper.get("doi") or paper.get("title")
        processed_papers[key] = paper

    bfs_scrape(seed_papers, SERPER_API_KEY)

    print(f"\nBFS reference scraping complete. Total papers collected: {len(processed_papers)}")
    OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.path.join(os.getcwd(), "output"))
    output_path = os.path.join(OUTPUT_DIR, "deep_reference_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(list(processed_papers.values()), f, indent=4)

    print("Results saved to deep_reference_results.json")


if __name__ == "__main__":
    main()
