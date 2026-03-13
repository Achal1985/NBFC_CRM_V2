import pandas as pd

file_path = "C:/CRM_Project/NBFC_CRM_Windows11_Chatbot.xlsx"

# Load sheets
customer_df = pd.read_excel(file_path, sheet_name="Customer_Master")
loan_df = pd.read_excel(file_path, sheet_name="Loan_Details")
emi_df = pd.read_excel(file_path, sheet_name="EMI_Tracking")

def crm_chatbot():
    customer_id = int(input("Enter Customer ID: "))

    customer = customer_df[customer_df["CustomerID"] == customer_id]

    if customer.empty:
        print("Customer not found")
        return

    loan_no = customer.iloc[0]["LoanAccountNo"]

    print("\nSelect Option:")
    print("1. Loan Details")
    print("2. EMI Details")

    choice = input("Enter choice: ")

    if choice == "1":
        loan = loan_df[loan_df["LoanAccountNo"] == loan_no]
        print("\nLoan Amount:", loan.iloc[0]["DisbursedAmount"])
        print("EMI Amount:", loan.iloc[0]["EMIAmount"])
        print("Tenure:", loan.iloc[0]["TenureMonths"])

    elif choice == "2":
        emi = emi_df[emi_df["LoanAccountNo"] == loan_no]
        print("\nNext Due Date:", emi.iloc[0]["NextDueDate"])
        print("Overdue Amount:", emi.iloc[0]["OverdueAmount"])
        print("DPD:", emi.iloc[0]["DPD"])

    else:
        print("Invalid choice")

crm_chatbot()
