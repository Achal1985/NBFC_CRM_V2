from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
from groq import Groq

app = Flask(__name__)

# Initialize Groq Client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

file_path = os.path.join(os.path.dirname(__file__), "NBFC_CRM_Windows11_Chatbot.xlsx")

customer_df = pd.read_excel(file_path, sheet_name="Customer_Master")
loan_df = pd.read_excel(file_path, sheet_name="Loan_Details")

# =================================
# STORE LAST SEARCHED CUSTOMER DATA
# =================================
last_customer_data = {}

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():

    global last_customer_data

    query = request.form.get("query")

    loan = loan_df[loan_df["Loan_Account_Number"].astype(str) == query]

    if loan.empty:
        cust = customer_df[customer_df["Mobile_Number"].astype(str) == query]

        if not cust.empty:
            cust_id = cust.iloc[0]["Customer_ID"]
            loan = loan_df[loan_df["Customer_ID"] == cust_id]

    if loan.empty:
        cust = customer_df[customer_df["Customer_ID"].astype(str) == query]

        if not cust.empty:
            cust_id = cust.iloc[0]["Customer_ID"]
            loan = loan_df[loan_df["Customer_ID"] == cust_id]

    if loan.empty:
        return jsonify({
            "Message": "Customer Not Found",
            "voice": "Customer Not Found"
        })

    cust_id = loan.iloc[0]["Customer_ID"]

    customer = customer_df[customer_df["Customer_ID"] == cust_id]

    data = {

        "Customer Name": str(customer.iloc[0]["Customer_Name"]),
        "Customer ID": str(cust_id),
        "Mobile": str(customer.iloc[0]["Mobile_Number"]),
        "Loan Account Number": str(loan.iloc[0]["Loan_Account_Number"]),
        "Loan Amount": str(loan.iloc[0]["Loan_Amount"]),
        "Principal Outstanding": str(loan.iloc[0]["Principal_Outstanding"]),
        "Interest Outstanding": str(loan.iloc[0]["Interest_Outstanding"]),
        "Balance Principal": str(loan.iloc[0]["Balance_Principal"]),
        "Charges Outstanding": str(loan.iloc[0]["Charges_Outstanding"]),
        "Interest Rate": str(loan.iloc[0]["Interest_Rate"]),
        "E M I Amount": str(loan.iloc[0]["EMI_Amount"]),
        "Loan Status": str(loan.iloc[0]["Loan_Status"]),

        "Address": str(customer.iloc[0]["Address"]),
        "City": str(customer.iloc[0]["City"]),
        "State": str(customer.iloc[0]["State"]),
        "Pincode": str(customer.iloc[0]["Pincode"]),
        "Email ID": str(customer.iloc[0]["Email_ID"]),
        "GST Number": str(customer.iloc[0]["GST_Number"]),

        "voice": f"""
        Welcome to RFL AI Enabled CRM Chatbot,मैं जल्द ही आपकी Loan Details बताऊंगी
        Customer का नाम {customer.iloc[0]['Customer_Name']} है।
        लोन अकाउंट नंबर {loan.iloc[0]['Loan_Account_Number']} है।
        E M I अमाउंट {loan.iloc[0]['EMI_Amount']} रुपये है।
        Principal Outstanding अमाउंट {loan.iloc[0]['Principal_Outstanding']} रुपये है।
        Interest Outstanding अमाउंट {loan.iloc[0]['Interest_Outstanding']} रुपये है।
        Balance Principal अमाउंट {loan.iloc[0]['Balance_Principal']} रुपये है।
        Charges Outstanding अमाउंट {loan.iloc[0]['Charges_Outstanding']} रुपये है।
        Interest Rate {loan.iloc[0]['Interest_Rate']} percent है।
        लोन स्टेटस {loan.iloc[0]['Loan_Status']} है।
        अगर आपको कोई और जानकारी चाहिए तो AI enabled Helpdesk Tab पर जाएं
        """
    }

    last_customer_data = data

    return jsonify(data)


# ===============================
# AI HELPDESK
# ===============================

@app.route("/aihelp", methods=["POST"])
def aihelp():

    question = request.form.get("question","").lower()

    global last_customer_data

    if not last_customer_data:
        return jsonify({"answer":"Please search a customer first."})

    row = last_customer_data

    # ===============================
    # FAST RESPONSES FROM EXCEL DATA
    # ===============================

    if "loan summary" in question:

        answer = f"""
Loan Summary

Customer Name : {row.get("Customer Name")}
Loan Account Number : {row.get("Loan Account Number")}
Loan Amount : {row.get("Loan Amount")}
EMI Amount : {row.get("E M I Amount")}
Principal Outstanding : {row.get("Principal Outstanding")}
Interest Outstanding : {row.get("Interest Outstanding")}
Loan Status : {row.get("Loan Status")}
"""

        return jsonify({"answer":answer})

    elif "mobile" in question:
        return jsonify({"answer":row.get("Mobile","Mobile not available")})

    elif "address" in question:
        return jsonify({"answer":row.get("Address","Address not available")})

    elif "city" in question:
        return jsonify({"answer":row.get("City","City not available")})

    elif "state" in question:
        return jsonify({"answer":row.get("State","State not available")})

    elif "pincode" in question:
        return jsonify({"answer":row.get("Pincode","Pincode not available")})

    elif "gst" in question:
        return jsonify({"answer":row.get("GST Number","GST not available")})

    elif "email" in question:
        return jsonify({"answer":row.get("Email ID","Email not available")})

    elif "emi" in question:
        return jsonify({"answer":row.get("E M I Amount","EMI not available")})

    elif "loan amount" in question:
        return jsonify({"answer":row.get("Loan Amount","Loan amount not available")})

    elif "thanks" in question or "thank you" in question:
        return jsonify({"answer":"You're welcome. Let me know if you need more help."})


    # ===================================
    # IF NOT FOUND → CALL AI MODEL
    # ===================================

    try:

        prompt = f"""
You are an NBFC CRM helpdesk assistant.

Customer Data:
{row}

Question:
{question}

Answer shortly.
"""

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant"
        )

        answer = chat_completion.choices[0].message.content

        return jsonify({"answer":answer})

    except Exception as e:
        return jsonify({"answer":"AI service unavailable"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
