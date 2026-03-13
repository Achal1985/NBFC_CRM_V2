def process_query(text):
    text = text.lower()

    # Loan Status
    if "loan status" in text or "लोन स्टेटस" in text:
        return "Loan is active"

    # EMI
    elif "emi" in text or "ईएमआई" in text:
        return "EMI amount is fifteen thousand rupees"

    # Customer details
    elif "customer" in text or "ग्राहक" in text:
        return "Customer details found"

    elif "exit" in text or "बंद" in text:
        return "Goodbye"

    else:
        return "Sorry, I did not understand your request"
