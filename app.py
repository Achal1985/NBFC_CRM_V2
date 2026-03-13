from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)

import os

# Use relative path
file_path = os.path.join(os.path.dirname(__file__), "NBFC_CRM_Windows11_Chatbot.xlsx")

customer_df = pd.read_excel(file_path, sheet_name="Customer_Master")
loan_df = pd.read_excel(file_path, sheet_name="Loan_Details")


@app.route("/")
def home():
    return render_template("index.html")
    


@app.route("/search", methods=["POST"])
def search():

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
            "voice": "ग्राहक की जानकारी नहीं मिली"
        })

    cust_id = loan.iloc[0]["Customer_ID"]

    customer = customer_df[customer_df["Customer_ID"] == cust_id]

    data = {

        "Customer Name": str(customer.iloc[0]["Customer_Name"]),
        "Customer ID": str(cust_id),
        "Mobile": str(customer.iloc[0]["Mobile_Number"]),
        "Loan Account": str(loan.iloc[0]["Loan_Account_Number"]),
        "Loan Amount": str(loan.iloc[0]["Loan_Amount"]),
        "Principal Outstanding": str(loan.iloc[0]["Principal_Outstanding"]),
        "Interest Outstanding": str(loan.iloc[0]["Interest_Outstanding"]),
        "Charges Outstanding": str(loan.iloc[0]["Charges_Outstanding"]),
        "Interest Rate": str(loan.iloc[0]["Interest_Rate"]),
        "EMI Amount": str(loan.iloc[0]["EMI_Amount"]),
        "Loan Status": str(loan.iloc[0]["Loan_Status"]),

        "voice": f"""
        Welcome to RFL AI CRM Chatbot,मैं जल्द ही आपको Loan Details बताऊंगी
        ग्राहक का नाम {customer.iloc[0]['Customer_Name']} है।
        लोन अकाउंट नंबर {loan.iloc[0]['Loan_Account_Number']} है।
        EMI अमाउंट {loan.iloc[0]['EMI_Amount']} रुपये है।
        Principal Outstanding अमाउंट {loan.iloc[0]['Principal_Outstanding']} रुपये है।
        Interest Outstanding अमाउंट {loan.iloc[0]['Interest_Outstanding']} रुपये है।
        Balance Principal अमाउंट {loan.iloc[0]['Balance_Principal']} रुपये है।
        Charges Outstanding अमाउंट {loan.iloc[0]['Charges_Outstanding']} रुपये है।
        Interest Rate  {loan.iloc[0]['Interest_Rate']} percent है।
        लोन स्टेटस {loan.iloc[0]['Loan_Status']} है।
        क्या आप कोई और जानकारी लेना चाहते हैं
        """

    }

    return jsonify(data)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

