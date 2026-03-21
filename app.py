from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import pandas as pd
import os
from groq import Groq

app = Flask(__name__)
app.secret_key = "crm_secret_key"

# ==============================
# SAFE GROQ CLIENT INITIALIZATION
# ==============================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY") or os.environ.get("RAILWAY_GROQ_API_KEY")

if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
else:
    print("WARNING: GROQ_API_KEY not found. AI service will be disabled.")
    client = None


file_path = os.path.join(os.path.dirname(__file__), "NBFC_CRM_Windows11_Chatbot.xlsx")

customer_df = pd.read_excel(file_path, sheet_name="Customer_Master")
loan_df = pd.read_excel(file_path, sheet_name="Loan_Details")

# =================================
# STORE LAST SEARCHED CUSTOMER DATA
# =================================
last_customer_data = {}


# ===============================
# LOGIN PAGE
# ===============================

@app.route("/")
def login():
    return render_template("login.html")

@app.route('/login_existing')
def login_existing():
    return render_template('existing_login.html')

@app.route('/new_customer')
def new_customer():
    return render_template('new_customer.html')



# ===============================
# OTP VALIDATION
# ===============================

@app.route("/validate_otp", methods=["POST"])
def validate_otp():

    mobile = request.form.get("mobile")
    otp = request.form.get("otp")

    if otp == "123456":

        session["mobile"] = mobile

        return redirect(url_for("home"))

    else:
        return render_template("login.html", error="Invalid OTP")


# ===============================
# CRM DASHBOARD
# ===============================

@app.route("/dashboard")
def home():
    return render_template("index.html")


# ===============================
# CUSTOMER SEARCH
# ===============================

@app.route("/search", methods=["POST"])
def search():

    global last_customer_data

    query = request.form.get("query","").strip()
    logged_mobile = session.get("mobile")

    loan = None
    cust = None

    # SEARCH BY MOBILE
    cust = customer_df[customer_df["Mobile_Number"].astype(str) == query]

    if not cust.empty:
        cust_id = cust.iloc[0]["Customer_ID"]
        loan = loan_df[loan_df["Customer_ID"] == cust_id]

    # SEARCH BY LOAN ACCOUNT NUMBER
    if cust.empty:
        loan = loan_df[loan_df["Loan_Account_Number"].astype(str) == query]

        if not loan.empty:
            cust_id = loan.iloc[0]["Customer_ID"]
            cust = customer_df[customer_df["Customer_ID"] == cust_id]

    # SEARCH BY CUSTOMER ID
    if cust.empty:
        cust = customer_df[customer_df["Customer_ID"].astype(str) == query]

        if not cust.empty:
            cust_id = cust.iloc[0]["Customer_ID"]
            loan = loan_df[loan_df["Customer_ID"] == cust_id]

    if cust.empty or loan.empty:
        return jsonify({
            "Message": "Customer Not Found",
            "voice": "Customer Not Found"
        })

    # SECURITY CHECK → only allow logged mobile data
    if str(cust.iloc[0]["Mobile_Number"]) != str(logged_mobile):
        return jsonify({
            "Message": "Access Denied",
            "voice": "आप केवल अपने मोबाइल नंबर की जानकारी देख सकते हैं"
        })

    cust_id = cust.iloc[0]["Customer_ID"]

    data = {

        "Customer Name": str(cust.iloc[0]["Customer_Name"]),
        "Customer ID": str(cust_id),
        "Mobile": str(cust.iloc[0]["Mobile_Number"]),
        "Loan Account Number": str(loan.iloc[0]["Loan_Account_Number"]),
        "Loan Amount": str(loan.iloc[0]["Loan_Amount"]),
        "Principal Outstanding": str(loan.iloc[0]["Principal_Outstanding"]),
        "Interest Outstanding": str(loan.iloc[0]["Interest_Outstanding"]),
        "Balance Principal": str(loan.iloc[0]["Balance_Principal"]),
        "Charges Outstanding": str(loan.iloc[0]["Charges_Outstanding"]),
        "Interest Rate": str(loan.iloc[0]["Interest_Rate"]),
        "E M I Amount": str(loan.iloc[0]["EMI_Amount"]),
        "Loan Status": str(loan.iloc[0]["Loan_Status"]),

        "Address": str(cust.iloc[0]["Address"]),
        "City": str(cust.iloc[0]["City"]),
        "State": str(cust.iloc[0]["State"]),
        "Pincode": str(cust.iloc[0]["Pincode"]),
        "Email ID": str(cust.iloc[0]["Email_ID"]),
        "GST Number": str(cust.iloc[0]["GST_Number"]),

        "voice": f"""
Welcome to RFL AI Enabled CRM Chatbot.
Customer का नाम {cust.iloc[0]['Customer_Name']} है।
लोन अकाउंट नंबर {loan.iloc[0]['Loan_Account_Number']} है।
E M I अमाउंट {loan.iloc[0]['EMI_Amount']} रुपये है।
Principal Outstanding {loan.iloc[0]['Principal_Outstanding']} रुपये है।
Interest Outstanding {loan.iloc[0]['Interest_Outstanding']} रुपये है।
Balance Principal {loan.iloc[0]['Balance_Principal']} रुपये है।
Charges Outstanding {loan.iloc[0]['Charges_Outstanding']} रुपये है।
Interest Rate {loan.iloc[0]['Interest_Rate']} percent है।
Loan Status {loan.iloc[0]['Loan_Status']} है।
For more information go to our AI enabled helpdesk tab
"""
    }

    last_customer_data = data

    return jsonify(data)

# ===============================
# AI HELPDESK
# ===============================

@app.route("/aihelp", methods=["POST"])
def aihelp():

    question = request.form.get("question", "").lower()

    global last_customer_data

    if not last_customer_data:
        return jsonify({"answer": "Please search a customer first."})

    row = last_customer_data

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

        return jsonify({"answer": answer})

    if client is None:
        return jsonify({"answer": "AI service unavailable."})

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

        return jsonify({"answer": answer})

    except:
        return jsonify({"answer": "AI service unavailable"})
# ===============================
# TICKET RAISE API
# ===============================

@app.route("/raise_ticket", methods=["POST"])
def raise_ticket():

    mobile = session.get("mobile")
    issue_type = request.form.get("type")
    description = request.form.get("desc")

    if not mobile:
        return jsonify({"message": "User not logged in"})

    ticket_id = f"TKT{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}"

    ticket_data = {
        "Ticket ID": ticket_id,
        "Mobile": mobile,
        "Issue Type": issue_type,
        "Description": description,
        "Status": "Open"
    }

    file = "tickets.csv"

    if os.path.exists(file):
        df = pd.read_csv(file)
        df = pd.concat([df, pd.DataFrame([ticket_data])], ignore_index=True)
    else:
        df = pd.DataFrame([ticket_data])

    df.to_csv(file, index=False)

    return jsonify({"message": f"✅ Ticket Raised Successfully: {ticket_id}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
