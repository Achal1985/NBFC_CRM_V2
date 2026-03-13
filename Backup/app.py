from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Excel File Path
file_path = "C:/CRM_Project/NBFC_CRM_Windows11_Chatbot.xlsx"

# Load Excel Sheets
customer_df = pd.read_excel(file_path, sheet_name="Customer_Master")
loan_df = pd.read_excel(file_path, sheet_name="Loan_Details")
emi_df = pd.read_excel(file_path, sheet_name="EMI_Tracking")

# Convert important columns to string (VERY IMPORTANT)
customer_df["CustomerID"] = customer_df["CustomerID"].astype(str).str.strip()
customer_df["LoanAccountNo"] = customer_df["LoanAccountNo"].astype(str).str.strip()

loan_df["LoanAccountNo"] = loan_df["LoanAccountNo"].astype(str).str.strip()
emi_df["LoanAccountNo"] = emi_df["LoanAccountNo"].astype(str).str.strip()


@app.route("/", methods=["GET", "POST"])
def home():
    result = ""

    if request.method == "POST":

        customer_id = request.form.get("CustomerID")
        option = request.form.get("option")

        if not customer_id or not option:
            result = "Please enter Customer ID and select option."
            return render_template("index.html", result=result)

        customer_id = customer_id.strip()

        # Search Customer
        customer = customer_df[customer_df["CustomerID"] == customer_id]

        if customer.empty:
            result = "Customer not found."
        else:
            loan_no = customer.iloc[0]["LoanAccountNo"]

            # Loan Details
            if option == "loan":
                loan = loan_df[loan_df["LoanAccountNo"] == loan_no]

                if loan.empty:
                    result = "Loan details not available."
                else:
                    result = f"""
                    Loan Amount: {loan.iloc[0]['DisbursedAmount']}
                    EMI Amount: {loan.iloc[0]['EMIAmount']}
                    """

            # EMI Details
            elif option == "emi":
                emi = emi_df[emi_df["LoanAccountNo"] == loan_no]

                if emi.empty:
                    result = "EMI details not available."
                else:
                    result = f"""
                    Next Due Date: {emi.iloc[0]['NextDueDate']}
                    Overdue Amount: {emi.iloc[0]['OverdueAmount']}
                    """

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
