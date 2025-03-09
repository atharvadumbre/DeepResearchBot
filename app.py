# app.py (modified excerpt)
import streamlit as st
import tempfile
import os
import re
from manager_agent import ManagerAgent

st.title("Deep Research Bot")
st.markdown(
    "This app runs a deep research pipeline that searches for relevant papers, downloads them, extracts content, generates summaries, and finally produces a review paper."
)
research_topic = st.text_input("Enter your research topic:")
start_button = st.button("Start Research")
log_container = st.empty()
logs = []

def log_fn(message: str):
    logs.append(message)
    log_container.text("\n".join(logs))

if start_button and research_topic:
    try:
        # Create a temporary directory for this session
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            st.write(f"Using temporary output directory: {tmp_output_dir}")
            
            # Instantiate the ManagerAgent with the temporary output directory.
            manager = ManagerAgent(research_topic, log_fn=log_fn, output_dir=tmp_output_dir)
            manager.run()
            
            # Extract the review paper file path from the review writer's output.
            review_result = getattr(manager, "review_result", "")
            match = re.search(r'Output saved as:\s*(.*)', review_result)
            if match:
                review_pdf_path = match.group(1).strip()
            else:
                review_pdf_path = None

            if review_pdf_path and os.path.exists(review_pdf_path):
                with open(review_pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                st.download_button(
                    label="Download Review PDF",
                    data=pdf_bytes,
                    file_name="review_paper.pdf",
                    mime="application/pdf"
                )
                st.markdown("### Final Review Paper")
                st.info("The review paper has been generated. You can download it using the button above.")
            else:
                st.error("Review PDF not found!")
            # Note: When the "with" block ends, tmp_output_dir and its contents are automatically deleted.
    except Exception as e:
        st.error(f"An error occurred: {e}")
