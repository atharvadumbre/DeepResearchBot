import os
import json
import re
from openai import OpenAI
from fpdf import FPDF

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Initialize the OpenAI client using the new style.
client = OpenAI(api_key=OPENAI_API_KEY)

def train_manager_agent():
    """
    Returns a string of best-practice guidelines for writing a good review paper,
    synthesized from blogs, articles, and YouTube videos.
    """
    guidelines = (
        "Guidelines for Writing a Good Review Paper:\n"
        "1. Start with a clear introduction that outlines the scope, purpose, and relevance of the review.\n"
        "2. Provide a structured overview of the field, summarizing key research findings from the available literature.\n"
        "3. Critically evaluate the strengths and weaknesses of the research, noting common methodologies, results, and limitations.\n"
        "4. Identify gaps in the literature and suggest future research directions.\n"
        "5. Conclude with a synthesis that integrates insights, discusses implications, and offers actionable recommendations.\n"
        "6. Maintain an academic tone, clarity, and coherence throughout the document.\n"
        "7. Use subheadings to organize the review and ensure smooth transitions between sections.\n"
    )
    return guidelines

def generate_review_paper(summaries, model="gpt-4o", temperature=0.3, max_tokens=5000):
    """
    Generates a comprehensive review paper based on provided paper summaries.
    The prompt includes training guidelines to instruct the agent on how to write a good review.
    """
    training_guidelines = train_manager_agent()
    
    # Combine all summaries into a coherent block.
    combined_summaries = "\n\n".join(
        [f"Paper: {key}\nSummary: {value}" for key, value in summaries.items() if value.strip()]
    )
    
    prompt = (
        "Using the training guidelines provided below and the summaries of individual research papers, "
        "write a comprehensive review paper. The review should:\n"
        "- Introduce the topic and explain the significance of the research area.\n"
        "- Summarize the key findings from the papers.\n"
        "- Critically analyze strengths and weaknesses in the current literature.\n"
        "- Identify research gaps and suggest future directions.\n"
        "- Conclude with a synthesis of the insights.\n"
        "The review should be well-structured, coherent, and written in an academic tone, and it should be no longer than 1500 words.\n\n"
        "Training Guidelines:\n"
        f"{training_guidelines}\n\n"
        "Paper Summaries:\n"
        f"{combined_summaries}\n\n"
        "Review Paper:"
    )
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert research manager specialized in writing academic review papers."},
                {"role": "user", "content": prompt},
            ],
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        review_paper = chat_completion.choices[0].message.content.strip()
        return review_paper
    except Exception as e:
        print(f"Error generating review paper: {e}")
        return ""

def save_text_to_pdf(text, output_file, log_fn=print):
    """
    Saves the provided text as a PDF file.
    This function removes Markdown bold markers (i.e. **text**) instead of converting them to HTML.
    """
    # Remove Markdown bold markers by replacing **text** with just text.
    clean_text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    
    # Create an FPDF instance.
    pdf = FPDF()
    pdf.add_page()
    
    # Using a core font (Arial, which is mapped to Helvetica) - note: this supports only Latin-1.
    pdf.set_font("Arial", size=12)
    
    # Write the cleaned text line by line.
    pdf.multi_cell(0, 10, clean_text)
    
    pdf.output(output_file)
    log_fn(f"PDF saved to {output_file}")

def main(output_dir, log_fn=print):
    summaries_file = os.path.join(output_dir, "summaries.json")
    output_pdf = os.path.join(output_dir, "review_paper.pdf")

    # Load summaries.
    try:
        with open(summaries_file, "r", encoding="utf-8") as f:
            summaries = json.load(f)
    except Exception as e:
        log_fn(f"Error reading {summaries_file}: {e}")
        return
    
    # Generate the review paper.
    review_paper = generate_review_paper(summaries)
    if not review_paper:
        log_fn("No review paper generated.")
        return
    
    # Save the review as a PDF file.
    save_text_to_pdf(review_paper, output_pdf)

if __name__ == "__main__":
    main()
