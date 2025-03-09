from langchain.tools import tool
from agents import (
    ReferenceScraperAgent,
    DownloaderAgent,
    PDFExtractionAgent,
    SummarizerAgent,
    ReviewWriterAgent,
)

@tool()
def reference_scraper_tool(input: str) -> str:
    """Scrapes references from a research topic using deep_reference_scraper. Input: a research topic string."""
    agent = ReferenceScraperAgent()
    agent.run(input)
    return f"Reference scraping complete. Output saved to: {agent.output_file}"

@tool()
def downloader_tool(input: str = "") -> str:
    """Downloads PDFs based on scraped references. No input needed."""
    agent = DownloaderAgent()
    agent.run()
    return f"Download complete. PDFs saved in: {agent.output_folder}"

@tool()
def pdf_extraction_tool(input: str = "") -> str:
    """Extracts research content from downloaded PDFs and saves it to a JSON file. No input needed."""
    agent = PDFExtractionAgent()
    agent.run()
    return f"PDF extraction complete. Output saved to: {agent.output_file}"

@tool()
def summarizer_tool(input: str = "") -> str:
    """Generates summaries for the extracted research content. No input needed."""
    agent = SummarizerAgent()
    agent.run()
    return f"Summaries generated. Output saved to: {agent.output_file}"

@tool()
def review_writer_tool(input: str = "") -> str:
    """Generates the final review paper using the summaries. No input needed."""
    agent = ReviewWriterAgent()
    agent.run()
    return f"Review paper generated. Output saved as: {agent.output_file}"
