import os
import sys
import re
from collections import defaultdict
from unstructured.partition.pdf import partition_pdf  # Actual import

os.environ["PATH"] += os.pathsep + r"C:\Users\athar\AppData\Local\Programs\Python\Python310\Lib\poppler-24.08.0\Library\bin" 
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Tesseract-OCR"

def clean_text(text):
    """Clean text by stripping extra whitespace."""
    return text.strip()

def process_pdf_with_unstructured(pdf_path):
    """Processes the PDF using the unstructured library and organizes data."""
    elements = partition_pdf(
        filename=pdf_path,
        include_page_breaks=True,
        strategy="auto",
        infer_table_structure=True,
        extract_images_in_pdf=False,
    )
    content_by_page = defaultdict(lambda: {"text": [], "images": [], "tables": []})

    for element in elements:
        metadata = element.metadata.to_dict() if hasattr(element, "metadata") else {}
        page_number = metadata.get("page_number", "Unknown")
        element_type = getattr(element, "type", None)

        if element_type == "Text":
            content_by_page[page_number]["text"].append(clean_text(element.text or ""))
        elif element_type == "Image":
            content_by_page[page_number]["images"].append(element.to_dict())
        elif element_type == "Table":
            content_by_page[page_number]["tables"].append(element.to_dict())
        else:
            content_by_page[page_number]["text"].append(clean_text(str(element)))

    for page, content in content_by_page.items():
        # Join text parts on each page into a single string.
        content["text"] = " ".join(content["text"])

    # Remove any content with an 'Unknown' page if present.
    content_by_page.pop("Unknown", None)
    return content_by_page

def extract_references(full_text):
    """
    Splits the full text into research content and references based on the occurrence
    of the word "References" or "Bibliography". It then cleans the references block by
    joining broken lines (removing newline characters within a reference), and attempts 
    to split the references into individual items, saving each reference on a new line.
    
    If no numbering pattern is found, it falls back to splitting by period+space.
    """
    import re

    match = re.search(r'\b(References|Bibliography)\b', full_text, re.IGNORECASE)
    if match:
        split_index = match.start()
        research_content = full_text[:split_index].strip()
        references = full_text[split_index:].strip()

        # Remove the header (e.g., "References:" or "Bibliography:")
        references = re.sub(r'^(References|Bibliography)\s*[:\-]*\s*', '', references, flags=re.IGNORECASE)
        
        # Join lines that may have been broken by page breaks or OCR errors.
        # This replaces newline characters with a space.
        references = " ".join(references.splitlines())
        
        # First, try splitting using numbering patterns like "[1]" or "1. "
        references_list = re.split(r'\s*(?=(?:\[\d+\])|(?:\d+\.\s))', references)
        references_list = [ref.strip() for ref in references_list if ref.strip()]
        
        # If splitting by numbering didn't work (i.e. no multiple items), try a fallback:
        if len(references_list) <= 1:
            # Fallback: split by a period followed by a space (this may not be perfect).
            references_list = re.split(r'\.\s+', references)
            # Add back the period to each item except the last (if needed).
            references_list = [ref.strip() + ('.' if i < len(references_list) - 1 else '') 
                               for i, ref in enumerate(references_list) if ref.strip()]
        
        references = "\n".join(references_list)
    else:
        research_content = full_text.strip()
        references = ""
    return research_content, references



def main(pdf_path, output_dir):
    # Extract content by page from the PDF.
    content_by_page = process_pdf_with_unstructured(pdf_path)

    # Combine text from all pages. Sort pages numerically when possible.
    combined_text = ""
    def sort_key(key):
        try:
            return int(key)
        except ValueError:
            return float('inf')
    for page in sorted(content_by_page.keys(), key=sort_key):
        combined_text += content_by_page[page]["text"] + "\n"

    # Extract research content and references using the updated function.
    research_content, references = extract_references(combined_text)

    # Ensure the output directory exists.
    os.makedirs(output_dir, exist_ok=True)
    research_file = os.path.join(output_dir, "research_content.txt")
    references_file = os.path.join(output_dir, "references.txt")

    with open(research_file, "w", encoding="utf-8") as f:
        f.write(research_content)
    with open(references_file, "w", encoding="utf-8") as f:
        f.write(references)

    print(f"Saved research content to: {research_file}")
    print(f"Saved references to: {references_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_pdf_data.py <pdf_path> <output_directory>")
        sys.exit(1)
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    main(pdf_path, output_dir)
