import os
import json
from openai import OpenAI

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Initialize the OpenAI client using the new style.
client = OpenAI(api_key=OPENAI_API_KEY)

def summarize_text(text, model="gpt-4o", temperature=0.3, log_fn=print):
    """
    Generates a summary of the provided research paper content in no more than 500 words.
    
    Parameters:
        text (str): The full research paper content.
        model (str): The OpenAI model to use.
        temperature (float): Sampling temperature.
        
    Returns:
        str: The generated summary.
    """
    prompt = (
        "Summarize the following research paper content in no more than 500 words:\n\n"
        f"{text}\n\nSummary:"
    )
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a research assistant that summarizes academic papers."},
                {"role": "user", "content": prompt},
            ],
            model=model,
        )
        # Access the summary from the response structure.
        summary = chat_completion.choices[0].message.content.strip()
        return summary
    except Exception as e:
        log_fn(f"Error generating summary: {e}")
        return ""

def generate_summaries(json_file=None, output_file=None, log_fn=print):
    """
    Reads research content from a JSON file and creates summaries for each paper.
    The resulting summaries are saved in a single JSON file.
    """
    if output_file is None or json_file is None:
        raise ValueError("json_file and output_file must be provided.")
    
    with open(json_file, "r", encoding="utf-8") as f:
        papers = json.load(f)
    
    summaries = {}
    for paper_key, content in papers.items():
        log_fn(f"Generating summary for paper: {paper_key}")
        if not content.strip():
            log_fn(f"Content for {paper_key} is empty. Skipping.")
            summaries[paper_key] = ""
            continue
        
        summary = summarize_text(content)
        summaries[paper_key] = summary
        log_fn(f"Summary for {paper_key} generated.")
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=4, ensure_ascii=False)
    
    log_fn(f"Summaries saved to {output_file}")

if __name__ == "__main__":
    generate_summaries()
