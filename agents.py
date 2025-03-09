import os
import shutil
import logging

# Import functions from your provided project files.
# Adjust the import paths if necessary.
from deep_reference_scraper import main as run_deep_reference_scraper
from download_all_papers import download_all_papers
from extract_all_data_to_json import main as run_extract_data
from summary_agent import generate_summaries
from review_writer_agent import main as run_review_writer

# Define a base output directory.
BASE_OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.path.join(os.getcwd(), "output"))
os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

# Define additional folders inside the base directory.
RESEARCH_PAPERS_DIR = os.path.join(BASE_OUTPUT_DIR, "research_papers")
os.makedirs(RESEARCH_PAPERS_DIR, exist_ok=True)

# Configure logging for visibility.
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


class ReferenceScraperAgent:
    """
    Agent that uses deep_reference_scraper to search for seed papers
    and perform a BFS to gather references up to 3 levels deep (max 100 papers).
    """
    def __init__(self):
        # Set the output file to be inside the base output folder.
        self.output_file = os.path.join(BASE_OUTPUT_DIR, "deep_reference_results.json")
        logging.info("ReferenceScraperAgent initialized.")

    def run(self, research_topic):
        logging.info(f"ReferenceScraperAgent: Starting scraping for topic '{research_topic}'.")
        # Assume run_deep_reference_scraper writes output to "deep_reference_results.json" in the root.
        run_deep_reference_scraper(research_topic)
        # Move the output file into the designated output folder.
        if os.path.exists("deep_reference_results.json"):
            shutil.move("deep_reference_results.json", self.output_file)
            logging.info(f"ReferenceScraperAgent: Scraping complete. Results saved to {self.output_file}.")
        else:
            logging.error("ReferenceScraperAgent: Expected output file not found.")


class DownloaderAgent:
    """
    Agent that downloads PDFs based on the reference JSON file.
    """
    def __init__(self):
        # Use the output file from the ReferenceScraperAgent.
        self.input_file = os.path.join(BASE_OUTPUT_DIR, "deep_reference_results.json")
        # Set the download folder inside the base output directory.
        self.output_folder = RESEARCH_PAPERS_DIR
        logging.info("DownloaderAgent initialized.")

    def run(self):
        logging.info("DownloaderAgent: Starting PDF download process.")
        download_all_papers()
        logging.info("DownloaderAgent: Download process complete.")


class PDFExtractionAgent:
    """
    Agent that extracts research content from downloaded PDFs and compiles it into a JSON file.
    """
    def __init__(self):
        # PDFs are now located in the common research papers folder.
        self.input_folder = RESEARCH_PAPERS_DIR
        self.output_file = os.path.join(BASE_OUTPUT_DIR, "all_research_content.json")
        logging.info("PDFExtractionAgent initialized.")

    def run(self):
        logging.info("PDFExtractionAgent: Extracting content from PDFs.")
        run_extract_data()
        logging.info(f"PDFExtractionAgent: Extraction complete. Output saved to {self.output_file}.")


class SummarizerAgent:
    """
    Agent that generates summaries for the extracted research content.
    """
    def __init__(self):
        self.input_file = os.path.join(BASE_OUTPUT_DIR, "all_research_content.json")
        self.output_file = os.path.join(BASE_OUTPUT_DIR, "summaries.json")
        logging.info("SummarizerAgent initialized.")

    def run(self):
        logging.info("SummarizerAgent: Generating summaries for each paper.")
        generate_summaries()
        logging.info(f"SummarizerAgent: Summaries complete. Output saved to {self.output_file}.")


class ReviewWriterAgent:
    """
    Agent that generates a final review paper based on the generated summaries.
    """
    def __init__(self):
        self.input_file = os.path.join(BASE_OUTPUT_DIR, "summaries.json")
        self.output_file = os.path.join(BASE_OUTPUT_DIR, "review_paper.pdf")
        logging.info("ReviewWriterAgent initialized.")

    def run(self):
        logging.info("ReviewWriterAgent: Generating the final review paper.")
        run_review_writer()
        logging.info(f"ReviewWriterAgent: Review paper generated and saved as {self.output_file}.")


if __name__ == "__main__":
    # For demonstration purposes, the agents are run sequentially.
    research_topic = input("Enter your research topic: ")

    # Initialize agents.
    ref_scraper = ReferenceScraperAgent()
    downloader = DownloaderAgent()
    extractor = PDFExtractionAgent()
    summarizer = SummarizerAgent()
    review_writer = ReviewWriterAgent()

    # Execute each agent's task in sequence.
    ref_scraper.run(research_topic)
    downloader.run()
    extractor.run()
    summarizer.run()
    review_writer.run()

    logging.info("All agents have completed their tasks. Check the 'output' folder for results.")
