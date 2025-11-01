import streamlit as st
from PIL import Image
import pandas as pd
import io # Used for handling file bytes
from pdf2image import convert_from_bytes # Our new PDF library

# --- Import all our modules ---
from core.ocr_processor import perform_ocr
from core.data_extractor import extract_data_nlp
from core.verification import verify_claim
from core.online_checker import get_provider_stats
from core.llm_recommender import get_gemini_recommendations

# --- Page Setup ---
st.set_page_config(layout="wide")
st.title("🤖 AI Insurance Claim Analyzer")
st.write("Upload an insurance claim form (JPG, PNG, or PDF) to begin processing.")

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
    # --- NEW: Added 'pdf' to accepted types ---
    uploaded_file = st.file_uploader("Choose a file", type=["png", "jpg", "jpeg", "pdf"])

    if uploaded_file is not None:
        
        # --- NEW: Logic to handle PDF vs Image ---
        images_to_process = []
        if uploaded_file.type == "application/pdf":
            st.subheader("Uploaded PDF (First Page):")
            try:
                # Read file bytes
                pdf_bytes = uploaded_file.read()
                # Convert PDF bytes to a list of PIL Images
                pdf_images = convert_from_bytes(pdf_bytes, poppler_path=None) # poppler_path=None assumes Poppler is in your PATH
                
                if pdf_images:
                    # Display the first page
                    st.image(pdf_images[0], caption="First page of uploaded PDF", use_column_width=True)
                    # Add all pages to our processing list
                    images_to_process.extend(pdf_images)
                else:
                    st.error("Could not extract any images from the PDF.")
                    
            except Exception as e:
                st.error(f"Error processing PDF. Is Poppler installed and in your PATH? Error: {e}")
                
        else:
            # It's an image, process as before
            st.subheader("Uploaded Claim Image:")
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            images_to_process.append(image)
        # --- END NEW LOGIC ---


        if st.button("Analyze Claim") and images_to_process:
            st.session_state.processing_complete = False 
            
            # --- NEW: Process all images (from PDF or single upload) ---
            full_extracted_text = ""
            with st.spinner("Processing image(s) with OCR..."):
                for i, img in enumerate(images_to_process):
                    if len(images_to_process) > 1:
                        st.text(f"Processing page {i+1}...")
                    # We pass the PIL Image object directly to OCR
                    full_extracted_text += perform_ocr(img) + "\n\n--- Page Break ---\n\n"
            
            st.session_state.extracted_text = full_extracted_text
            # --- END NEW LOGIC ---

            if "ERROR:" not in st.session_state.extracted_text:
                with st.spinner("Extracting key information with NLP..."):
                    st.session_state.extracted_data = extract_data_nlp(st.session_state.extracted_text)
                
                with st.spinner("Verifying claim against business rules..."):
                    st.session_state.final_status, st.session_state.results_list = verify_claim(st.session_state.extracted_data)
                
                provider = st.session_state.extracted_data.get("Insurance Provider")
                if provider != "Not Found":
                    with st.spinner(f"Checking online reputation for {provider}..."):
                        provider_stats = get_provider_stats(provider)
                    
                    with st.spinner("Generating AI recommendations..."):
                        st.session_state.recommendations = get_gemini_recommendations(st.session_state.extracted_data, provider_stats)
                else:
                    st.session_state.recommendations = ["Could not identify provider to generate recommendations."]
                
                st.session_state.processing_complete = True
            else:
                st.error(st.session_state.extracted_text)

# --- Column 2: Results Display (No changes here) ---
with col2:
    st.subheader("Processing Results:")
    if not st.session_state.processing_complete:
        st.info("Upload an image or PDF and click 'Analyze Claim' to see the results.")
    else:
        status = st.session_state.final_status
        if status == "Approved": st.success("✅ Verdict: Approved")
        elif status == "Rejected": st.error("❌ Verdict: Rejected")
        elif status == "Manual Review": st.warning("⚠️ Verdict: Flagged for Manual Review")
        else: st.error(f"An error occurred: {status}")

        st.markdown("---")
        st.write("#### 🤖 AI-Powered Recommendations")
        for reco in st.session_state.recommendations: st.markdown(f"- {reco}")
        st.markdown("---")
        
        with st.expander("Show Verification Checklist"):
            for item in st.session_state.results_list:
                if item['status'] == 'Pass': st.markdown(f"✔️ **Pass:** {item['message']}")
                else: st.markdown(f"❌ **Fail:** {item['message']}")
        with st.expander("Show Extracted Data (NLP)"):
            df = pd.DataFrame(list(st.session_state.extracted_data.items()), columns=['Field', 'Value'])
            st.dataframe(df, use_container_width=True)
        with st.expander("Show Raw Extracted Text"):
            st.text_area("Raw Text", st.session_state.extracted_text, height=300)