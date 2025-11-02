import spacy
import re

insurance_providers = ["Aetna", "Cigna", "UnitedHealthcare", "Anthem", "Humana", "Blue Cross Blue Shield"]
patterns = [{"label": "PROVIDER", "pattern": provider} for provider in insurance_providers]

try:
    nlp = spacy.load("en_core_web_sm")
    
    if "entity_ruler" not in nlp.pipe_names:
        ruler = nlp.add_pipe("entity_ruler", before="ner")
        ruler.add_patterns(patterns)

except IOError:
    print("\n--- Error: 'en_core_web_sm' model not found. ---")
    print("Please run: python -m spacy download en_core_web_sm")
    print("---\n")
    nlp = None

POLICY_PATTERN = re.compile(r"Policy\s?Number[:\s]+(\w+-\w+)", re.IGNORECASE)
AGE_PATTERN = re.compile(r"Age[:\s]+(\d{1,2})\n", re.IGNORECASE)

def extract_data_nlp(raw_text):
    """
    Extracts key information from raw OCR text using a spaCy NER model
    and a custom EntityRuler.
    """
    if nlp is None:
        return {"Error": "NLP model not loaded."}

    doc = nlp(raw_text)
    
    extracted_data = {
        "Patient Name": "Not Found",
        "Policy Number": "Not Found",
        "Claim Amount": "Not Found",
        "Date of Service": "Not Found",
        "Insurance Provider": "Not Found",
        "Patient Age": "Not Found"
    }
    
    persons = []
    dates = []
    money = []
    
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            persons.append(ent.text.strip())
        elif ent.label_ == "DATE":
            dates.append(ent.text.strip())
        elif ent.label_ == "MONEY":
            money.append(ent.text.strip())
        elif ent.label_ == "PROVIDER":
            extracted_data["Insurance Provider"] = ent.text.strip()
            
    if persons:
        extracted_data["Patient Name"] = persons[0]
        
    if dates:
        extracted_data["Date of Service"] = dates[0] 
        
    if money:
        max_amount = 0.0
        for m in money:
            cleaned_m = re.sub(r"[,\$€£]", "", m)
            try:
                amount = float(cleaned_m)
                if amount > max_amount:
                    max_amount = amount
                    extracted_data["Claim Amount"] = m
            except ValueError:
                continue
                
    policy_match = POLICY_PATTERN.search(raw_text)
    if policy_match:
        extracted_data["Policy Number"] = policy_match.group(1).strip()

    age_match = AGE_PATTERN.search(raw_text)
    if age_match:
        extracted_data["Patient Age"] = int(age_match.group(1).strip())
        
    return extracted_data