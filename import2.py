import pandas as pd

file_path = "C:/CRM_PROJECT/NBFC_CRM_Windows11_Chatbot.xlsx"

customer_df = pd.read_excel(file_path, sheet_name="Customer_Master")
loan_df = pd.read_excel(file_path, sheet_name="Loan_Details")
