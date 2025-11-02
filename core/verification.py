import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

POLICIES_DB_PATH = os.path.join(BASE_DIR, '..', 'mock_data', 'policies_db.json')
PROCEDURES_DB_PATH = os.path.join(BASE_DIR, '..', 'mock_data', 'procedures_db.json')

def load_json(file_path):
    """Helper function to load a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}")
        return None

def clean_amount(amount_str):
    """Converts a formatted string (e.g., '1,500.00') to a float."""
    if isinstance(amount_str, (int, float)):
        return float(amount_str)
    
    cleaned_str = re.sub(r"[,\$€£]", "", str(amount_str))
    try:
        return float(cleaned_str)
    except ValueError:
        return None

def verify_claim(extracted_data):
    """
    Verifies the extracted claim data against business rules.
    """
    valid_policies = load_json(POLICIES_DB_PATH)
    procedure_rules = load_json(PROCEDURES_DB_PATH)
    
    if valid_policies is None or procedure_rules is None:
        return "ERROR", [{"status": "Error", "message": "Could not load validation databases."}]
        
    results = []
    is_approved = True

    if "Not Found" in extracted_data.values():
        results.append({
            "status": "Fail", 
            "message": "Key information missing from form. Flagging for manual review."
        })
        return "Manual Review", results

    policy_num = extracted_data.get('Policy Number')
    if policy_num in valid_policies:
        results.append({
            "status": "Pass", 
            "message": f"Policy Number '{policy_num}' is valid."
        })
    else:
        results.append({
            "status": "Fail", 
            "message": f"Policy Number '{policy_num}' is NOT valid."
        })
        is_approved = False
        
    MAX_CLAIM_LIMIT = 5000.00
    claim_amount_str = extracted_data.get('Claim Amount', '0')
    
    claim_amount = clean_amount(claim_amount_str)

    if claim_amount is None:
        results.append({
            "status": "Fail", 
            "message": f"Claim Amount '{claim_amount_str}' is not a valid number."
        })
        is_approved = False
    elif claim_amount > MAX_CLAIM_LIMIT:
        results.append({
            "status": "Fail", 
            "message": f"Claim Amount ${claim_amount:,.2f} exceeds the ${MAX_CLAIM_LIMIT:,.2f} limit."
        })
        is_approved = False
    elif claim_amount <= 0:
        results.append({
            "status": "Fail", 
            "message": f"Claim Amount must be greater than $0."
        })
        is_approved = False
    else:
        results.append({
            "status": "Pass", 
            "message": f"Claim Amount ${claim_amount:,.2f} is within limits."
        })

    final_status = "Approved" if is_approved else "Rejected"
    
    return final_status, results

import re