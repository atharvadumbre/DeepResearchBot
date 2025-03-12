import os
import json
import requests

SERPER_API_KEY = os.environ["SERPER_API_KEY"]

def search_google_scholar(query, api_key, log_fn=print):
    """Search Google Scholar using the SerperDev API and return the top 3 results."""
    url = "https://google.serper.dev/scholar"
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    payload = json.dumps({"q": query})

    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json().get("organic", [])[:3]  # Get top 3 results
    else:
        log_fn("Error fetching data:", response.text)
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