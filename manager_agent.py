import os
from dotenv import load_dotenv
from langchain_openai import OpenAI  # Updated import for LangChain v0.3
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain  # Updated import for LangChain v0.3

load_dotenv()

OPENAI_API_KEY=os.environ.get("OPENAI_API_KEY")

BASE_OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.path.join(os.getcwd(), "output"))
os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

# Import the tool functions from langchain_tools.py (which use the @tool decorator)
from langchain_tools import (
    reference_scraper_tool,
    downloader_tool,
    pdf_extraction_tool,
    summarizer_tool,
    review_writer_tool,
)

class ManagerAgent:
    def __init__(self, research_topic: str, log_fn=print, output_dir: str = None):
        self.research_topic = research_topic
        self.log_fn = log_fn
        
        # Use the provided output directory or fall back to BASE_OUTPUT_DIR
        self.output_dir = output_dir if output_dir else BASE_OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Optionally, set an environment variable so that other components use the same directory.
        os.environ["OUTPUT_DIR"] = self.output_dir
        
        # Initialize the LLM and other chains as before...
        self.llm = OpenAI(temperature=0.2, api_key=OPENAI_API_KEY)
        
        # Chain to decide whether to proceed or revise a step.
        self.decision_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["step", "output"],
                template=(
                    "You just completed the {step} step of a research pipeline. "
                    "Here is the output:\n{output}\n\n"
                    "Based on this, should we proceed to the next step or revise our approach? "
                    "Respond with 'proceed' or 'revise' and provide a brief explanation."
                ),
            )
        )
        
        # Chain to request revision suggestions if needed.
        self.revision_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["step", "output"],
                template=(
                    "The {step} step produced the following output:\n{output}\n\n"
                    "It was evaluated as needing revision. Provide concrete suggestions on how to adjust "
                    "or improve this step to get better results."
                ),
            )
        )
        
        self.max_attempts = 3

    def evaluate_step(self, step: str, tool_output: str) -> bool:
        response = self.decision_chain.run(step=step, output=tool_output)
        self.log_fn(f"LLM Evaluation for {step}: {response}")
        # Proceed if the LLM response mentions 'proceed'
        return "proceed" in response.lower()

    def run_step_with_guidance(self, step: str, tool, tool_input: str = "") -> str:
        attempts = 0
        while attempts < self.max_attempts:
            self.log_fn(f"\n=== Attempt {attempts+1} for step: {step} ===")
            # Call the tool function; if input is provided, pass it; otherwise, use an empty string.
            output = tool(tool_input) if tool_input else tool("")
            self.log_fn(f"Output for {step}:\n{output}")
            if self.evaluate_step(step, output):
                return output
            else:
                revision_suggestion = self.revision_chain.run(step=step, output=output)
                self.log_fn(f"Revision suggestions for {step}:\n{revision_suggestion}")
                attempts += 1
        self.log_fn(f"Maximum attempts reached for {step}. Aborting process.")
        raise Exception(f"Step {step} failed to meet requirements after {self.max_attempts} attempts.")

    def run(self):
        self.log_fn("Manager Agent: Starting the research process.\n")
        
        # Step 1: Reference Scraper with dynamic guidance
        ref_result = self.run_step_with_guidance("Reference Scraper", reference_scraper_tool, self.research_topic)
        
        # Step 2: Downloader with dynamic guidance
        down_result = self.run_step_with_guidance("Downloader", downloader_tool)
        
        # Step 3: PDF Extraction with dynamic guidance
        pdf_result = self.run_step_with_guidance("PDF Extraction", pdf_extraction_tool)
        
        # Step 4: Summarizer with dynamic guidance
        sum_result = self.run_step_with_guidance("Summarization", summarizer_tool)
        
        # Step 5: Review Writer with dynamic guidance
        # Store the review result as an attribute for later use
        self.review_result = self.run_step_with_guidance("Review Writing", review_writer_tool)
        
        self.log_fn("Manager Agent: Research process complete. Check the output folder for results.")

