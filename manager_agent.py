import os
from langchain_openai import OpenAI  # Updated import for LangChain v0.3
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain  # Updated import for LangChain v0.3

# Use the factory functions from langchain_tools.py
from langchain_tools import (
    create_reference_scraper_tool,
    create_downloader_tool,
    create_pdf_extraction_tool,
    create_summarizer_tool,
    create_review_writer_tool,
)

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

class ManagerAgent:
    def __init__(self, research_topic: str, log_fn=print, output_dir: str = None):
        self.research_topic = research_topic
        self.log_fn = log_fn
        self.output_dir = output_dir
        print("ManagerAgent using OUTPUT_DIR:", self.output_dir)
        self.llm = OpenAI(temperature=0.2, api_key=OPENAI_API_KEY)
        
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
        return "proceed" in response.lower()

    def run_step_with_guidance(self, step: str, tool, tool_input: str = "") -> str:
        attempts = 0
        while attempts < self.max_attempts:
            self.log_fn(f"\n=== Attempt {attempts+1} for step: {step} ===")
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
        
        # Create tool instances using the factory functions
        ref_tool = create_reference_scraper_tool(self.output_dir, self.log_fn)
        down_tool = create_downloader_tool(self.output_dir, self.log_fn)
        pdf_tool = create_pdf_extraction_tool(self.output_dir, self.log_fn)
        sum_tool = create_summarizer_tool(self.output_dir, self.log_fn)
        rev_tool = create_review_writer_tool(self.output_dir, self.log_fn)
        
        ref_result = self.run_step_with_guidance(
            "Reference Scraper",
            lambda input: ref_tool(input),
            self.research_topic
        )
        
        down_result = self.run_step_with_guidance(
            "Downloader",
            lambda _: down_tool(""),
        )
        
        pdf_result = self.run_step_with_guidance(
            "PDF Extraction",
            lambda _: pdf_tool(""),
        )
        
        sum_result = self.run_step_with_guidance(
            "Summarization",
            lambda _: sum_tool(""),
        )
        
        self.review_result = self.run_step_with_guidance(
            "Review Writing",
            lambda _: rev_tool(""),
        )
        
        self.log_fn("Manager Agent: Research process complete. Check the output folder for results.")
