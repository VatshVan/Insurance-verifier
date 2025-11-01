import streamlit as st
from PIL import Image
import pandas as pd

# --- Import all our modules ---
from core.ocr_processor import perform_ocr
from core.data_extractor import extract_data_nlp # Use the new NLP extractor
from core.verification import verify_claim
from core.online_checker import get_provider_stats # New
from core.recommendations import generate_recommendations # New

# --- Page Setup ---
st.set_page_config(layout="wide")
st.title("🤖 AI Insurance Claim Analyzer")
st.write("Upload an insurance claim form (JPG, PNG) to begin processing.")

# --- Columns for Layout ---
col1, col2 = st.columns(2)

# --- Session State to hold results ---
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False
    st.session_state.extracted_text = ""
    st.session_state.extracted_data = {}
    st.session_state.final_status = ""
    st.session_state.results_list = []
    st.session_state.recommendations = []

# --- Column 1: File Uploader and Image Display ---
with col1:
    uploaded_file = st.file_uploader("Choose a file", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        st.subheader("Uploaded Claim Image:")
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        if st.button("Analyze Claim"):
            st.session_state.processing_complete = False # Reset on new click
            
            with st.spinner("Processing image with OCR..."):
                st.session_state.extracted_text = perform_ocr(uploaded_file)
            
            if "ERROR:" not in st.session_state.extracted_text:
                with st.spinner("Extracting key information with NLP..."):
                    st.session_state.extracted_data = extract_data_nlp(st.session_state.extracted_text)
                
                with st.spinner("Verifying claim against business rules..."):
                    st.session_state.final_status, st.session_state.results_list = verify_claim(st.session_state.extracted_data)
                
                # --- This is our new "Robust" section ---
                provider = st.session_state.extracted_data.get("Insurance Provider")
                if provider != "Not Found":
                    with st.spinner(f"Checking online reputation for {provider}..."):
                        provider_stats = get_provider_stats(provider)
                    
                    with st.spinner("Generating AI recommendations..."):
                        st.session_state.recommendations = generate_recommendations(st.session_state.extracted_data, provider_stats)
                else:
                    st.session_state.recommendations = ["Could not identify provider to generate recommendations."]
                
                st.session_state.processing_complete = True
            else:
                st.error(st.session_state.extracted_text)

# --- Column 2: Results Display ---
with col2:
    st.subheader("Processing Results:")
    
    if not st.session_state.processing_complete:
        st.info("Upload an image and click 'Analyze Claim' to see the results.")
    
    else:
        # --- 1. Display Final Verdict ---
        status = st.session_state.final_status
        if status == "Approved":
            st.success("✅ Verdict: Approved")
        elif status == "Rejected":
            st.error("❌ Verdict: Rejected")
        elif status == "Manual Review":
            st.warning("⚠️ Verdict: Flagged for Manual Review")
        else:
            st.error(f"An error occurred: {status}")

        # --- 2. NEW: AI Recommendations Section ---
        st.markdown("---")
        st.write("#### 🤖 AI-Powered Recommendations")
        for reco in st.session_state.recommendations:
            st.markdown(f"- {reco}")
        st.markdown("---")
        
        # --- 3. Display Verification Checklist ---
        with st.expander("Show Verification Checklist"):
            for item in st.session_state.results_list:
                if item['status'] == 'Pass':
                    st.markdown(f"✔️ **Pass:** {item['message']}")
                else:
                    st.markdown(f"❌ **Fail:** {item['message']}")

        # --- 4. Display Extracted Data ---
        with st.expander("Show Extracted Data (NLP)"):
            df = pd.DataFrame(list(st.session_state.extracted_data.items()), columns=['Field', 'Value'])
            st.dataframe(df, use_container_width=True)

        # --- 5. Display Raw Text ---
        with st.expander("Show Raw Extracted Text"):
            st.text_area("Raw Text", st.session_state.extracted_text, height=300)