# AI Insurance Claim Analyzer

**Project for the Loop x IIT-B Hackathon 2025**

This project is a Streamlit web application that automates and enhances the insurance claim verification process. It moves beyond simple validation by using **OCR**, **Natural Language Processing (NLP)**, and **live web searches** to analyze a claim and provide AI-powered, non-rigid recommendations to the user.



## Features

* **OCR Processing:** Uses Tesseract to extract raw text from uploaded claim form images (PNG, JPG).
* **NLP-Powered Data Extraction:** Employs `spaCy` (with a custom `EntityRuler`) to intelligently extract key information like patient name, policy number, claim amount, patient age, and insurance provider, making it robust to changes in form layout.
* **Live Web Analysis:** Uses the **Google Custom Search JSON API** to perform a live search for the insurance provider's name to fetch recent customer reviews or news.
* **AI Recommendation Engine:** Dynamically generates helpful, non-rigid advice for the user based on their extracted data (like age, claim amount) and the live web search results.
* **Automated Verification:** Checks extracted data against a set of business rules (e.g., valid policy numbers, claim limits) to provide an [Approved], [Rejected], or [Manual Review] verdict.
* **Interactive UI:** A clean, multi-column Streamlit interface to display the uploaded image, the final verdict, the AI recommendations, and expandable sections for the detailed verification checklist and raw data.

## How It Works (The Pipeline)

1.  **Upload:** A user uploads a JPG or PNG image of their claim form.
2.  **OCR (`core/ocr_processor.py`):** The image is processed by Tesseract, and raw text is extracted.
3.  **NLP Extraction (`core/data_extractor.py`):** The raw text is fed into a `spaCy` model, which finds and extracts specific entities (Name, Age, Amount, Provider).
4.  **Verification (`core/verification.py`):** The extracted data is checked against local "mock databases" (`mock_data/*.json`) for basic validity (e.g., is the policy ID on our list?).
5.  **Live Check (`core/online_checker.py`):** The app takes the extracted **Insurance Provider** name and uses the Google Search API to find the latest customer reviews or news about them.
6.  **Recommendation (`core/recommendations.py`):** An "AI" logic module combines the patient's data (age, claim amount) with the live Google Search results to generate personalized, helpful recommendations.
7.  **Display (`app.py`):** All results—the verdict, the AI advice, and the detailed data—are presented to the user.

## Setup & Installation

### 1. Prerequisites: Install Tesseract

This app requires Google's Tesseract OCR engine.

1.  Download the Tesseract installer for Windows from [here](https://github.com/UB-Mannheim/tesseract/wiki).
2.  Run the installer.
3.  **Crucially, you must add Tesseract to your Windows `PATH`** so Python can find it.
    * Find your Tesseract install folder (e.g., `C:\Program Files\Tesseract-OCR`).
    * Search for "Edit the system environment variables" in your Start Menu.
    * Click "Environment Variables...", select "Path" under "System variables," and click "Edit...".
    * Click "New" and paste in your Tesseract path: `C:\Program Files\Tesseract-OCR`.
    * Click OK on all windows and **restart your command prompt/VS Code** for the change to take effect.

### 2. Clone the Repository

```bash
git clone [https://github.com/VatshVan/Insurance-verifier.git](https://github.com/VatshVan/Insurance-verifier.git)
cd insurance-claim-verifier
```

### 3. Set Up Python Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate
```

### 4. Install Dependencies

```bash
# Install all required Python packages
pip install -r requirements.txt

# Download the spaCy English model
python -m spacy download en_core_web_sm
```

### 5. Configure API Keys (Critical!)
This project requires two API keys from Google to power the live web search.
1.  Create a file named .env in the root of the project directory.
2.  Paste the following into the .env file:

    ```bash
    GOOGLE_API_KEY="YOUR_API_KEY_HERE"
    SEARCH_ENGINE_ID="YOUR_SEARCH_ENGINE_ID_HERE"
    ```

3.  To get your GOOGLE_API_KEY:
    * Go to the Google Cloud Console.
    * Create a new project.
    * Go to APIs & Services > Library and enable the "Custom Search JSON API".
    * Go to APIs & Services > Credentials and create a new API Key. Copy it.

4.  To get your SEARCH_ENGINE_ID (cx):
    * Go to the Programmable Search Engine website.
    * Create a new search engine.
    * Turn ON the option to "Search the entire web".
    * Create the engine, and from the "Basics" or "Customize" page, copy the "Search engine ID".

## How to Run
With your virtual environment active and your .env file configured:

```Bash
streamlit run app.py
```

> Your browser will automatically open to the application, ready for you to upload a claim form.
"# Insurance-verifier" 
