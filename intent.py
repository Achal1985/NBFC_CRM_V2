def process_query(text):
    text = text.lower()

    if "loan status" in text:
        return "Please tell customer ID"

    elif "emi" in text:
        return "EMI is 15000 rupees"

    elif "customer details" in text:
        return "Customer is active"

    else:
        return "Sorry, I did not understand"
