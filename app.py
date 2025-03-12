import os
import re
import tempfile
import streamlit as st
from manager_agent import ManagerAgent

st.title("Deep Research Bot")
st.markdown(
    "This app runs a deep research pipeline that searches for relevant papers, downloads them, "
    "extracts content, generates summaries, and finally produces a review paper."
)

# Determine the root directory (where app.py is located)
app_root = os.path.dirname(os.path.abspath(__file__))

# Create a temporary directory for this session if not already created.
if "output_dir" not in st.session_state:
    temp_dir_obj = tempfile.TemporaryDirectory(prefix="user_", dir=app_root)
    st.session_state.temp_dir_obj = temp_dir_obj  # Save the object so it isn’t garbage-collected
    st.session_state.output_dir = temp_dir_obj.name

st.write("Temporary directory for this session: " + st.session_state.output_dir)

# Input for research topic
research_topic = st.text_input("Enter your research topic:")

if st.button("Start Research") and research_topic:
    st.session_state.research_topic = research_topic
    # Run the pipeline synchronously with a spinner
    with st.spinner("Running research pipeline, please wait..."):
        # Use st.write as the log function to immediately display log messages
        manager = ManagerAgent(st.session_state.research_topic, log_fn=st.write, output_dir=st.session_state.output_dir)
        manager.run()
        st.session_state.review_result = getattr(manager, "review_result", "")
    
    # Display the final review PDF download if generated
    if st.session_state.review_result:
        match = re.search(r'Output saved as:\s*(.*)', st.session_state.review_result)
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
            st.success("The review paper has been generated!")
        else:
            st.error("Review PDF not found!")
    else:
        st.error("No review result generated.")
