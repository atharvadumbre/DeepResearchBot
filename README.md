# Deep Research Bot

## Overview
The **Deep Research Bot** is an automated AI-driven research assistant designed to streamline and enhance the academic literature review process. It performs end-to-end automation—from searching scholarly databases, downloading and extracting content from research papers, to generating precise summaries and compiling structured academic review papers.

## Key Features
- **Automated Literature Search**: Queries Google Scholar and IEEE Xplore for relevant research.
- **Advanced Reference Scraping**: Employs Breadth-First Search (BFS) to gather references up to three levels deep (maximum 100 papers).
- **Comprehensive PDF Acquisition**: Downloads PDFs via direct links, HTML scraping, and Sci-Hub integration.
- **Structured Data Extraction**: Utilizes the Unstructured library to accurately parse PDFs into structured JSON files.
- **AI-Powered Summarization**: Generates concise summaries using GPT-4.
- **Automated Review Paper Generation**: Compiles summaries into structured, academically rigorous review papers.
- **Dynamic Workflow Management**: Managed by the Manager Agent with LangChain tools for process optimization.

## Technology Stack
- **Languages**: Python
- **AI Models**: GPT-4 via OpenAI API
- **PDF Processing**: Unstructured library
- **Automation and Coordination**: LangChain Tools
- **Web Scraping**: Selenium, SerperDev API
- **Deployment**: Streamlit interface

## Workflow
1. **Search and Reference Scraping** (`deep_reference_scraper.py`): Automates the search for seed papers and references from Google Scholar and IEEE Xplore.
2. **PDF Downloading** (`download_all_papers.py`): Downloads research papers, handling various acquisition methods.
3. **PDF Data Extraction** (`extract_all_data_to_json.py`, `extract_data_from_pdf.py`): Parses PDFs and structures extracted content and references.
4. **Summarization** (`summary_agent.py`): Creates concise, informative paper summaries.
5. **Review Paper Generation** (`review_writer_agent.py`): Synthesizes summaries into a coherent academic review paper.
6. **Manager Agent** (`manager_agent.py`): Dynamically evaluates and manages workflow execution to ensure optimal outcomes.

## Limitations
- Dependency on external services and APIs.
- Accuracy of PDF extraction limited by document quality and formatting.
- Summarization nuances and domain-specific terminologies may occasionally be missed.

## Future Enhancements
- Integrate advanced OCR for better handling of poorly formatted documents.
- Include additional databases like PubMed to widen disciplinary coverage.
- Enhance AI with deeper semantic analysis for identifying emerging trends and predictive insights.

## Getting Started
### Installation
Clone the repository and install dependencies:
```bash
git clone [repository_link]
cd deep-research-bot
pip install -r requirements.txt
```

### Usage
Run the Streamlit app to interact with the bot:
```bash
streamlit run app.py
```
Enter your research topic, initiate the process, and download your review paper upon completion.

