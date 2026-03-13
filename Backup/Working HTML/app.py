from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)

file_path = "C:/CRM_PROJECT/NBFC_CRM_Windows11_Chatbot.xlsx"

customer_df = pd.read_excel(file_path, sheet_name="Customer_Master")
loan_df = pd.read_excel(file_path, sheet_name="Loan_Details")

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/getdata", methods=["POST"])
def getdata():

    query = str(request.form.get("query")).strip()

    # Search by Loan Account Number
    loan = loan_df[loan_df["Loan_Account_Number"].astype(str) == query]

    # Search by Customer ID
    if loan.empty:
        cust = customer_df[customer_df["Customer_ID"].astype(str) == query]

        if not cust.empty:
            cust_id = cust.iloc[0]["Customer_ID"]
            loan = loan_df[loan_df["Customer_ID"] == cust_id]

    # Search by Mobile Number
    if loan.empty:
        cust = customer_df[customer_df["Mobile_Number"].astype(str) == query]

        if not cust.empty:
            cust_id = cust.iloc[0]["Customer_ID"]
            loan = loan_df[loan_df["Customer_ID"] == cust_id]

    if loan.empty:
        return jsonify({"Message": "No Record Found"})

    cust_id = loan.iloc[0]["Customer_ID"]
    customer = customer_df[customer_df["Customer_ID"] == cust_id]

    data = {
        "Customer Name": str(customer.iloc[0]["Customer_Name"]),
        "Customer ID": str(cust_id),
        "Mobile Number": str(customer.iloc[0]["Mobile_Number"]),
        "Loan Account Number": str(loan.iloc[0]["Loan_Account_Number"]),
        "Loan Amount": str(loan.iloc[0]["Loan_Amount"]),
        "Principal Outstanding": str(loan.iloc[0]["Principal_Outstanding"]),
        "Interest Outstanding": str(loan.iloc[0]["Interest_Outstanding"]),
        "Balance Principal": str(loan.iloc[0]["Balance_Principal"]),
        "Charges Outstanding": str(loan.iloc[0]["Charges_Outstanding"]),
        "EMI Amount": str(loan.iloc[0]["EMI_Amount"]),
        "Loan Status": str(loan.iloc[0]["Loan_Status"])
    }

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
