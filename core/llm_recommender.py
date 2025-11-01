import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load all environment variables
load_dotenv()

# Configure the Gemini API
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash') # Use the fast model
except Exception as e:
    print(f"Error configuring Gemini: {e}")
    model = None

def get_gemini_recommendations(extracted_data, provider_stats):
    """
    Generates dynamic recommendations using the Gemini AI model.
    """
    if model is None:
        return ["Error: Gemini AI model is not configured. Check your GEMINI_API_KEY."]

    # Create a detailed prompt for the AI
    prompt = f"""
    You are an "AI Insurance Claim Assistant". Your job is to provide short, empathetic, and actionable recommendations to a user about their insurance claim.
    
    Here is the data you have:
    
    1.  **Extracted Claim Data:**
        - Patient Age: {extracted_data.get('Patient Age', 'Unknown')}
        - Insurance Provider: {extracted_data.get('Insurance Provider', 'Unknown')}
        - Claim Amount: {extracted_data.get('Claim Amount', 'Unknown')}
        - Final Verification Status: {st.session_state.final_status} # Accessing status from session state

    2.  **Live Google Search Result for the Provider:**
        - Snippet: {provider_stats.get('summary', 'No info found.')}

    Based **only** on this information, please generate 2-3 bullet points of helpful advice.
    
    - **Tone:** Be helpful, empathetic, and professional.
    - **Actionable:** Suggest what the user might do next (e.g., "follow up," "review your plan," "check for errors").
    - **Do Not:** Do not give financial or medical advice.
    - **Example:** If the provider has bad reviews, you might say: "Your provider's recent reviews mention slow processing. We recommend you call them in 5-7 days to confirm they received your claim."
    
    Please provide only the bullet points.
    """

    try:
        response = model.generate_content(prompt)
        # Split the text response into a list of bullet points
        recommendations = [reco.strip() for reco in response.text.split('- ') if reco.strip()]
        return recommendations
    
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return [f"Error generating AI recommendations: {e}"]

# We need to access session state for the status, so import streamlit
import streamlit as st