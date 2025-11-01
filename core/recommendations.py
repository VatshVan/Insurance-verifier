import re

def clean_amount(amount_str):
    """Helper to convert string to float."""
    if isinstance(amount_str, (int, float)):
        return float(amount_str)
    cleaned_str = re.sub(r"[,\$€£]", "", str(amount_str))
    try:
        return float(cleaned_str)
    except ValueError:
        return 0.0

def generate_recommendations(extracted_data, provider_stats):
    """
    Generates dynamic recommendations based on claim data and online stats.
    """
    recommendations = []
    
    # Get the data
    age = extracted_data.get("Patient Age")
    claim_amount_str = extracted_data.get("Claim Amount")
    claim_amount = clean_amount(claim_amount_str)
    provider_name = extracted_data.get("Insurance Provider", "Your provider")
    
    # --- Logic 1: Based on Online Stats ---
    if provider_stats.get("status") == "warning":
        reco = f"**Provider Alert:** {provider_stats.get('summary', '')} We recommend you follow up on this claim in 5-7 business days to ensure it is processed correctly."
        recommendations.append(reco)
    elif provider_stats.get("status") == "success":
        reco = f"**Provider Info:** {provider_stats.get('summary', '')}"
        recommendations.append(reco)

    # --- Logic 2: Based on Age and Claim Amount ---
    if age != "Not Found" and int(age) > 50 and claim_amount > 1000:
        reco = f"**Plan Review Suggestion:** This was a significant procedure for a patient over 50. It may be beneficial to review your plan's *out-of-pocket maximum* and *deductible* during the next open enrollment period to ensure it still fits your needs."
        recommendations.append(reco)
        
    if age != "Not Found" and int(age) < 30 and claim_amount < 200:
        reco = f"**Preventative Care:** We've noted this routine claim. Great job staying on top of your health! {provider_stats.get('details', '')}"
        recommendations.append(reco)

    if not recommendations:
        recommendations.append("Your claim has been processed. No specific actions are recommended at this time.")

    return recommendations