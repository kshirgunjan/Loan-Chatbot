# pip install streamlit pandas
import streamlit as st
import pandas as pd
import math

# EMI calculator function
def calculate_emi(p, r, n):
    r = r / (12 * 100)  # Convert annual to monthly rate
    emi = p * r * (1 + r) ** n / ((1 + r) ** n - 1)
    return round(emi, 2)

# Bank loan data
data = [
    {"Bank": "SBI", "Max Loan": 5000000, "Tenure (yrs)": 20, "Interest Rate (%)": 8.5},
    {"Bank": "HDFC", "Max Loan": 4500000, "Tenure (yrs)": 20, "Interest Rate (%)": 8.6},
    {"Bank": "ICICI", "Max Loan": 4800000, "Tenure (yrs)": 25, "Interest Rate (%)": 8.75},
    {"Bank": "Axis", "Max Loan": 4000000, "Tenure (yrs)": 15, "Interest Rate (%)": 8.3},
    {"Bank": "PNB", "Max Loan": 4200000, "Tenure (yrs)": 20, "Interest Rate (%)": 8.4},
    {"Bank": "BOB", "Max Loan": 4600000, "Tenure (yrs)": 25, "Interest Rate (%)": 8.7},
    {"Bank": "Kotak", "Max Loan": 4300000, "Tenure (yrs)": 18, "Interest Rate (%)": 8.6},
    {"Bank": "IDFC", "Max Loan": 4700000, "Tenure (yrs)": 20, "Interest Rate (%)": 8.55},
    {"Bank": "Canara", "Max Loan": 4100000, "Tenure (yrs)": 15, "Interest Rate (%)": 8.65},
    {"Bank": "IndusInd", "Max Loan": 3900000, "Tenure (yrs)": 20, "Interest Rate (%)": 8.45}
]

# Convert to DataFrame
df = pd.DataFrame(data)
df["Tenure (months)"] = df["Tenure (yrs)"] * 12
df["EMI"] = df.apply(lambda row: calculate_emi(row["Max Loan"], row["Interest Rate (%)"], row["Tenure (months)"]), axis=1)

# Streamlit UI
st.title("🏦 Loan Comparison Chatbot")
st.write("Chat with this tool to compare bank loan offers!")

query = st.text_input("Ask your question:")

if query:
    query = query.lower()
    words = query.split()
    banks = [word.upper() for word in words if word.upper() in df['Bank'].values]
    loan_amts = [int(w.replace("₹", "").replace(",", "")) for w in words if w.replace("₹", "").replace(",", "").isdigit()]
    
    # Lowest EMI
    if "lowest emi" in query:
        lowest = df.loc[df['EMI'].idxmin()]
        st.success(f"{lowest['Bank']} offers the lowest EMI: ₹{lowest['EMI']}/month for ₹{lowest['Max Loan']} over {lowest['Tenure (yrs)']} years at {lowest['Interest Rate (%)']}%.")

    # Lowest interest rate
    elif "lowest interest" in query:
        lowest = df.loc[df['Interest Rate (%)'].idxmin()]
        st.success(f"{lowest['Bank']} offers the lowest interest rate: {lowest['Interest Rate (%)']}%.")

    # EMI for custom loan amount
    elif "emi for" in query or loan_amts:
        loan_amt = loan_amts[0] if loan_amts else df["Max Loan"].min()
        temp_df = df.copy()
        temp_df["Custom EMI"] = temp_df.apply(lambda row: calculate_emi(loan_amt, row['Interest Rate (%)'], row['Tenure (months)']), axis=1)
        st.write(f"📊 EMI for ₹{loan_amt:,} across all banks:")
        st.table(temp_df[["Bank", "Interest Rate (%)", "Tenure (yrs)", "Custom EMI"]])

    # Compare total repayment between two banks
    elif ("compare" in query or "which one" in query or "saves me" in query) and len(banks) == 2:
        b1 = df[df['Bank'] == banks[0]].iloc[0]
        b2 = df[df['Bank'] == banks[1]].iloc[0]
        loan_amt = loan_amts[0] if loan_amts else min(b1["Max Loan"], b2["Max Loan"])

        emi1 = calculate_emi(loan_amt, b1["Interest Rate (%)"], b1["Tenure (months)"])
        emi2 = calculate_emi(loan_amt, b2["Interest Rate (%)"], b2["Tenure (months)"])

        total1 = emi1 * b1["Tenure (months)"]
        total2 = emi2 * b2["Tenure (months)"]

        cheaper = b1["Bank"] if total1 < total2 else b2["Bank"]
        diff = abs(total1 - total2)

        st.info(
            f"""
💰 Comparing for ₹{loan_amt:,}:
- {b1['Bank']} → EMI ₹{emi1}, Total ₹{total1:,.0f}
- {b2['Bank']} → EMI ₹{emi2}, Total ₹{total2:,.0f}

✅ **{cheaper} saves you ₹{diff:,.0f} overall**
            """
        )

    # What if I take lower than max loan
    elif "lower loan" in query or "less than max" in query:
        st.info("Taking a lower loan amount will reduce your EMI proportionally. Try asking: `EMI for ₹2500000` to compare actual amounts.")

    else:
        st.info("💡 Try asking: \n- 'Which bank has lowest EMI?'\n- 'Compare SBI and HDFC'\n- 'EMI for ₹3000000'\n- 'Which one saves me more overall?'")
