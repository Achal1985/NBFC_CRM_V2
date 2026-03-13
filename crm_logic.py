def process_query(text):

    text = text.lower()

    if "loan" in text or "लोन" in text:
        return "Your loan is approved"

    elif "emi" in text or "किस्त" in text:
        return "Your next EMI date is 10th"

    elif "customer" in text or "ग्राहक" in text:
        return "Please provide customer ID"

    elif "status" in text or "स्टेटस" in text:
        return "Your loan status is active"

    else:
        return "Sorry, I did not understand your request"
