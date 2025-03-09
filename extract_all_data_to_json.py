import os
import json
from tools.extract_data_from_pdf import process_pdf_with_unstructured, extract_references

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.path.join(os.getcwd(), "output"))
input_folder = os.path.join(OUTPUT_DIR, "research_papers")
output_file = os.path.join(OUTPUT_DIR, "all_research_content.json")

def extract_content_from_pdf(pdf_path):
    """
    Extracts research content (ignoring references) from a PDF file.
    Returns the extracted content as a string.
    """
    content_by_page = process_pdf_with_unstructured(pdf_path)
    combined_text = ""
    
    # Define a custom sort key that handles both integer and non-integer keys.
    def sort_key(k):
        try:
            return int(k)
        except Exception:
            return float('inf')
    
    # Combine text from all pages.
    for page in sorted(content_by_page.keys(), key=sort_key):
        combined_text += content_by_page[page]["text"] + "\n"
    
    # Use the extract_references function to split the content.
    # We ignore the references part and only keep the research content.
    research_content, _ = extract_references(combined_text)
    return research_content

def extract_all_contents(input_folder=input_folder):
    """
    Iterates over each PDF in the input folder, extracts its research content,
    and stores it in a dictionary where the key is the sanitized filename (without extension)
    and the value is the extracted content.
    """
    all_contents = {}
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_folder, filename)
            try:
                content = extract_content_from_pdf(pdf_path)
                # Sanitize filename by removing extension.
                key = os.path.splitext(filename)[0]
                all_contents[key] = content
                print(f"Extracted content from {filename}")
            except Exception as e:
                print(f"Error extracting from {filename}: {e}")
    return all_contents

def main():
    # Extract all research content from the PDFs.
    data = extract_all_contents()
    
    # Save the collected content to a single JSON file.
    output_file = output_file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Saved all research content to {output_file}")

if __name__ == "__main__":
    main()
