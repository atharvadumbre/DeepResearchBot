import os
import json
import requests
from dotenv import load_dotenv

# Load API Key from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

def search_google_scholar(query, api_key):
    """Search Google Scholar using the SerperDev API and return the top 3 results."""
    url = "https://google.serper.dev/scholar"
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    payload = json.dumps({"q": query})

    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json().get("organic", [])[:3]  # Get top 3 results
    else:
        print("Error fetching data:", response.text)
        return []

def extract_research_info(results):
    """Extract relevant details like DOI, PDF link, and fallback URL."""
    research_data = []
    
    for result in results:
        title = result.get("title", "No Title")
        year = result.get("year", "Unknown Year")
        cited_by = result.get("citedBy", 0)
        pdf_url = result.get("pdfUrl", None)
        html_url = result.get("htmlUrl", None)
        link = result.get("link", None)

        # Extract DOI if available in the link
        doi = None
        if link and "doi.org" in link:
            doi = link.split("doi.org/")[-1]  # Extract DOI

        research_data.append({
            "title": title,
            "year": year,
            "cited_by": cited_by,
            "doi": doi,
            "pdf_url": pdf_url,
            "html_url": html_url,
            "fallback_url": link  # Last resort
        })

    return research_data

def save_to_file(data, filename="top3_results_scholar.json"):
    """Save extracted research paper details to a local JSON file."""
    OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.getcwd())
    filename = os.path.join(OUTPUT_DIR, "top3_results_scholar.json")
    
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)
    print(f"Research papers saved to {filename}")

def main(query):
    """Main function to search for a query, extract details, and save them."""
    if not SERPER_API_KEY:
        print("API key not found. Make sure to set SERPERDEV_API_KEY in .env")
        return

    results = search_google_scholar(query, SERPER_API_KEY)
    research_data = extract_research_info(results)
    save_to_file(research_data)

if __name__ == "__main__":
    query = input("Enter search query: ")
    main(query)
