from langchain.tools import tool
from agents import (
    ReferenceScraperAgent,
    DownloaderAgent,
    PDFExtractionAgent,
    SummarizerAgent,
    ReviewWriterAgent,
)

def create_reference_scraper_tool(output_dir: str, log_fn=print):
    @tool()
    def reference_scraper_tool(input: str) -> str:
        """Scrapes references from a research topic using deep_reference_scraper. Input: a research topic string."""
        agent = ReferenceScraperAgent(output_dir=output_dir, log_fn=log_fn)
        agent.run(input)
        return f"Reference scraping complete. Output saved to: {agent.output_file}"
    return reference_scraper_tool

def create_downloader_tool(output_dir: str, log_fn=print):
    @tool()
    def downloader_tool(input: str = "") -> str:
        """Downloads PDFs based on scraped references. No input needed."""
        agent = DownloaderAgent(output_dir=output_dir, log_fn=log_fn)
        agent.run()
        return f"Download complete. PDFs saved in: {agent.output_folder}"
    return downloader_tool

def create_pdf_extraction_tool(output_dir: str, log_fn=print):
    @tool()
    def pdf_extraction_tool(input: str = "") -> str:
        """Extracts research content from downloaded PDFs and saves it to a JSON file. No input needed."""
        agent = PDFExtractionAgent(output_dir=output_dir, log_fn=log_fn)
        agent.run()
        return f"PDF extraction complete. Output saved to: {agent.output_file}"
    return pdf_extraction_tool

def create_summarizer_tool(output_dir: str, log_fn=print):
    @tool()
    def summarizer_tool(input: str = "") -> str:
        """Generates summaries for the extracted research content. No input needed."""
        agent = SummarizerAgent(output_dir=output_dir, log_fn=log_fn)
        agent.run()
        return f"Summaries generated. Output saved to: {agent.output_file}"
    return summarizer_tool

def create_review_writer_tool(output_dir: str, log_fn=print):
    @tool()
    def review_writer_tool(input: str = "") -> str:
        """Generates the final review paper using the summaries. No input needed."""
        agent = ReviewWriterAgent(output_dir=output_dir, log_fn=log_fn)
        agent.run()
        return f"Review paper generated. Output saved as: {agent.output_file}"
    return review_writer_tool
