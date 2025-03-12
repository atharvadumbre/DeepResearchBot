import os
from deep_reference_scraper import main as run_deep_reference_scraper
from download_all_papers import download_all_papers
from extract_all_data_to_json import main as run_extract_data
from summary_agent import generate_summaries
from review_writer_agent import main as run_review_writer

class ReferenceScraperAgent:
    """
    Agent that uses deep_reference_scraper to search for seed papers
    and perform a BFS to gather references up to 3 levels deep (max 100 papers).
    """
    def __init__(self, output_dir, log_fn=print):
        self.log_fn = log_fn
        self.output_file = os.path.join(output_dir, "deep_reference_results.json")
        self.log_fn("ReferenceScraperAgent initialized.")
        RESEARCH_PAPERS_DIR = os.path.join(output_dir, "research_papers")
        os.makedirs(RESEARCH_PAPERS_DIR, exist_ok=True)

    def run(self, research_topic):
        self.log_fn(f"ReferenceScraperAgent: Starting scraping for topic '{research_topic}'.")
        run_deep_reference_scraper(research_topic, output_dir=os.path.dirname(self.output_file), log_fn=self.log_fn)
        # Check directly in the output directory
        if os.path.exists(self.output_file):
            self.log_fn(f"ReferenceScraperAgent: Scraping complete. Results saved to {self.output_file}.")
        else:
            self.log_fn("ReferenceScraperAgent: Expected output file not found in the output directory.")

class DownloaderAgent:
    """
    Agent that downloads PDFs based on the reference JSON file.
    """
    def __init__(self, output_dir, log_fn=print):
        self.log_fn = log_fn
        self.input_file = os.path.join(output_dir, "deep_reference_results.json")
        RESEARCH_PAPERS_DIR = os.path.join(output_dir, "research_papers")
        os.makedirs(RESEARCH_PAPERS_DIR, exist_ok=True)
        self.output_folder = RESEARCH_PAPERS_DIR
        self.log_fn("DownloaderAgent initialized.")

    def run(self):
        self.log_fn("DownloaderAgent: Starting PDF download process.")
        download_all_papers(output_folder=self.output_folder, log_fn=self.log_fn)
        self.log_fn("DownloaderAgent: Download process complete.")


class PDFExtractionAgent:
    """
    Agent that extracts research content from downloaded PDFs and compiles it into a JSON file.
    """
    def __init__(self, output_dir, log_fn=print):
        self.log_fn = log_fn
        RESEARCH_PAPERS_DIR = os.path.join(output_dir, "research_papers")
        os.makedirs(RESEARCH_PAPERS_DIR, exist_ok=True)
        self.input_folder = RESEARCH_PAPERS_DIR
        self.output_file = os.path.join(output_dir, "all_research_content.json")
        self.log_fn("PDFExtractionAgent initialized.")

    def run(self):
        self.log_fn("PDFExtractionAgent: Extracting content from PDFs.")
        run_extract_data(self.input_folder, self.output_file, log_fn=self.log_fn)
        self.log_fn(f"PDFExtractionAgent: Extraction complete. Output saved to {self.output_file}.")


class SummarizerAgent:
    """
    Agent that generates summaries for the extracted research content.
    """
    def __init__(self, output_dir, log_fn=print):
        self.log_fn = log_fn
        self.input_file = os.path.join(output_dir, "all_research_content.json")
        self.output_file = os.path.join(output_dir, "summaries.json")
        self.log_fn("SummarizerAgent initialized.")

    def run(self):
        self.log_fn("SummarizerAgent: Generating summaries for each paper.")
        generate_summaries(json_file=self.input_file, output_file=self.output_file, log_fn=self.log_fn)
        self.log_fn(f"SummarizerAgent: Summaries complete. Output saved to {self.output_file}.")


class ReviewWriterAgent:
    """
    Agent that generates a final review paper based on the generated summaries.
    """
    def __init__(self, output_dir, log_fn=print):
        self.log_fn = log_fn
        self.output_dir = output_dir         # <--- ADD THIS LINE
        self.input_file = os.path.join(output_dir, "summaries.json")
        self.output_file = os.path.join(output_dir, "review_paper.pdf")
        self.log_fn("ReviewWriterAgent initialized.")

    def run(self):
        self.log_fn("ReviewWriterAgent: Generating the final review paper.")
        run_review_writer(self.output_dir, log_fn=self.log_fn)
        self.log_fn(f"ReviewWriterAgent: Review paper generated and saved as {self.output_file}.")


