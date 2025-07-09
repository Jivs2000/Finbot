#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# --- Tax Calculation Logic ---

# Income Tax Slabs for FY 2024-25 (AY 2025-26)

def calculate_tax_new_regime(income):
    """
    Calculates income tax as per the New Tax Regime for FY 2024-25.
    Includes Standard Deduction for salaried individuals and Section 87A rebate.
    """
    taxable_income = income

    # Standard Deduction for salaried individuals in New Regime (from FY 2023-24)
    # This is automatically applied if income is above 15.5 lakhs, or 50,000 otherwise.
    # For simplicity, we'll assume it's applied if income is above 0 and salaried.
    # In a real app, you'd ask if the user is salaried. For this basic calculator,
    # we'll apply it for incomes > 0.
    if income > 0:
        taxable_income = max(0, income - 50000) # Apply standard deduction of 50,000

    tax = 0
    if taxable_income <= 300000:
        tax = 0
    elif taxable_income <= 600000:
        tax = (taxable_income - 300000) * 0.05
    elif taxable_income <= 900000:
        tax = (300000 * 0.05) + (taxable_income - 600000) * 0.10
    elif taxable_income <= 1200000:
        tax = (300000 * 0.05) + (300000 * 0.10) + (taxable_income - 900000) * 0.15
    elif taxable_income <= 1500000:
        tax = (300000 * 0.05) + (300000 * 0.10) + (300000 * 0.15) + (taxable_income - 1200000) * 0.20
    else:
        tax = (300000 * 0.05) + (300000 * 0.10) + (300000 * 0.15) + (300000 * 0.20) + (taxable_income - 1500000) * 0.30

    # Section 87A Rebate (for New Regime: up to 25,000 if total income <= 7,00,000)
    rebate = 0
    if income <= 700000: # Note: rebate is on 'total income' before standard deduction
        rebate = min(tax, 25000) # Rebate is lesser of tax payable or 25,000

    net_tax_before_surcharge_cess = tax - rebate
    return max(0, net_tax_before_surcharge_cess) # Ensure tax is not negative

def calculate_tax_old_regime(income, age_group, deductions):
    """
    Calculates income tax as per the Old Tax Regime for FY 2024-25.
    This is a simplified version and does NOT include all possible deductions.
    """
    # Apply deductions for Old Regime
    # For simplicity, we'll only consider a basic 80C deduction here.
    # A full calculator would need many more deduction fields (80D, HRA, etc.)
    max_80c_deduction = 150000
    deduction_80c = min(deductions.get('80C', 0), max_80c_deduction)
    
    taxable_income = max(0, income - deduction_80c)

    tax = 0
    if age_group == "Below 60 years":
        if taxable_income <= 250000:
            tax = 0
        elif taxable_income <= 500000:
            tax = (taxable_income - 250000) * 0.05
        elif taxable_income <= 1000000:
            tax = (250000 * 0.05) + (taxable_income - 500000) * 0.20
        else:
            tax = (250000 * 0.05) + (500000 * 0.20) + (taxable_income - 1000000) * 0.30
    elif age_group == "60 to 80 years": # Senior Citizen
        if taxable_income <= 300000:
            tax = 0
        elif taxable_income <= 500000:
            tax = (taxable_income - 300000) * 0.05
        elif taxable_income <= 1000000:
            tax = (200000 * 0.05) + (taxable_income - 500000) * 0.20
        else:
            tax = (200000 * 0.05) + (500000 * 0.20) + (taxable_income - 1000000) * 0.30
    elif age_group == "Above 80 years": # Super Senior Citizen
        if taxable_income <= 500000:
            tax = 0
        elif taxable_income <= 1000000:
            tax = (taxable_income - 500000) * 0.20
        else:
            tax = (500000 * 0.20) + (taxable_income - 1000000) * 0.30
    
    # Section 87A Rebate (for Old Regime: up to 12,500 if total income <= 5,00,000)
    rebate = 0
    if income <= 500000: # Note: rebate is on 'total income' before deductions
        rebate = min(tax, 12500)

    net_tax_before_surcharge_cess = tax - rebate
    return max(0, net_tax_before_surcharge_cess) # Ensure tax is not negative


def calculate_surcharge(tax_amount, income, regime):
    """
    Calculates surcharge based on income and regime.
    New Regime has capped surcharge at 25% for highest income bracket.
    """
    surcharge_rate = 0
    if income > 50000000: # Above 5 Crore
        surcharge_rate = 0.37 if regime == "Old Tax Regime" else 0.25 # New regime capped at 25%
    elif income > 20000000: # Above 2 Crore up to 5 Crore
        surcharge_rate = 0.25
    elif income > 10000000: # Above 1 Crore up to 2 Crore
        surcharge_rate = 0.15
    elif income > 500000: # Above 50 Lakhs up to 1 Crore
        surcharge_rate = 0.10
    
    return tax_amount * surcharge_rate

def calculate_cess(tax_plus_surcharge):
    """
    Calculates Health and Education Cess at 4%.
    """
    return tax_plus_surcharge * 0.04

# --- Streamlit UI ---
def main():
    st.set_page_config(page_title="Geldium Tax Calculator", layout="centered")

    # --- Custom CSS for Styling ---
    st.markdown(
        """
        <style>
        .header-title {
            font-size: 3em;
            font-weight: bold;
            color: #2E86C1; /* A nice blue color */
            text-align: center;
            margin-bottom: 0.5em;
        }
        .header-subtitle {
            font-size: 1.2em;
            color: #566573;
            text-align: center;
            margin-bottom: 2em;
        }
        .stNumberInput > div > div > input {
            border-radius: 10px;
            padding: 8px 12px;
            border: 1px solid #ccc;
        }
        .stRadio > label {
            font-weight: bold;
            color: #333;
        }
        .stRadio div[role="radiogroup"] {
            display: flex;
            flex-direction: row; /* Arrange radio buttons horizontally */
            gap: 20px; /* Space between radio buttons */
            justify-content: center;
            margin-bottom: 20px;
        }
        .stButton button {
            border-radius: 20px;
            padding: 10px 20px;
            background-color: #2E86C1;
            color: white;
            border: none;
            font-weight: bold;
            display: block; /* Make button take full width */
            margin: 20px auto; /* Center the button */
        }
        .stButton button:hover {
            background-color: #1A5276;
            color: white;
        }
        .result-box {
            background-color: #EBF5FB;
            border-left: 5px solid #2E86C1;
            padding: 20px;
            border-radius: 8px;
            margin-top: 30px;
            font-size: 1.1em;
        }
        .result-box h3 {
            color: #2E86C1;
            margin-top: 0;
        }
        .disclaimer {
            font-size: 0.85em;
            color: #777;
            margin-top: 40px;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<p class="header-title">💰 Geldium Income Tax Calculator</p>', unsafe_allow_html=True)
    st.markdown('<p class="header-subtitle">Calculate your tax for Financial Year 2024-25 (Assessment Year 2025-26)</p>', unsafe_allow_html=True)

    st.write("---")

    # --- User Inputs ---
    annual_income = st.number_input(
        "Enter your Annual Income (₹)",
        min_value=0,
        value=500000, # Default value
        step=10000,
        format="%d"
    )

    tax_regime = st.radio(
        "Choose Tax Regime:",
        ("New Tax Regime", "Old Tax Regime"),
        index=0 # Default to New Tax Regime
    )

    age_group = "Below 60 years" # Default for New Regime, will be used if Old Regime is selected
    deductions = {} # Dictionary to store deduction values

    if tax_regime == "Old Tax Regime":
        st.info("The Old Tax Regime calculation is simplified here. For a precise calculation, consult a tax professional as it involves many specific deductions.")
        age_group = st.radio(
            "Select Your Age Group:",
            ("Below 60 years", "60 to 80 years", "Above 80 years"),
            index=0
        )
        st.subheader("Common Deductions (Old Regime - Simplified)")
        deductions['80C'] = st.number_input(
            "Deduction under Section 80C (Max ₹1,50,000 for investments like PPF, ELSS, EPF, Home Loan Principal, Life Insurance Premium, etc.)",
            min_value=0,
            max_value=150000,
            value=0,
            step=1000,
            format="%d"
        )
        # You would add more deduction fields here for a comprehensive Old Regime calculator
        # e.g., deductions['80D'] = st.number_input("Deduction under Section 80D (Health Insurance)", ...)

    st.write("---")

    if st.button("Calculate Tax"):
        gross_tax = 0
        surcharge = 0
        cess = 0
        total_tax_payable = 0
        rebate_amount = 0 # To display rebate separately

        if tax_regime == "New Tax Regime":
            # Pass original income for rebate check, then apply standard deduction internally
            gross_tax = calculate_tax_new_regime(annual_income)
            # Rebate is already handled inside calculate_tax_new_regime, but for display clarity:
            if annual_income <= 700000:
                rebate_amount = min(gross_tax, 25000)
                # Recalculate gross_tax after rebate for surcharge/cess calculation
                gross_tax = max(0, gross_tax - rebate_amount)

            surcharge = calculate_surcharge(gross_tax, annual_income, tax_regime)
            tax_plus_surcharge = gross_tax + surcharge
            cess = calculate_cess(tax_plus_surcharge)
            total_tax_payable = tax_plus_surcharge + cess
            
        else: # Old Tax Regime
            gross_tax = calculate_tax_old_regime(annual_income, age_group, deductions)
            # Rebate is already handled inside calculate_tax_old_regime, but for display clarity:
            if annual_income <= 500000:
                 rebate_amount = min(gross_tax, 12500)
                 gross_tax = max(0, gross_tax - rebate_amount)

            surcharge = calculate_surcharge(gross_tax, annual_income, tax_regime)
            tax_plus_surcharge = gross_tax + surcharge
            cess = calculate_cess(tax_plus_surcharge)
            total_tax_payable = tax_plus_surcharge + cess

        # --- Display Results ---
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.markdown('<h3>Tax Calculation Summary:</h3>', unsafe_allow_html=True)
        st.write(f"**Selected Regime:** {tax_regime}")
        st.write(f"**Annual Income:** ₹{annual_income:,.2f}")
        
        if tax_regime == "Old Tax Regime":
            st.write(f"**Selected Age Group:** {age_group}")
            st.write(f"**80C Deduction:** ₹{deductions.get('80C', 0):,.2f}")

        st.write(f"**Gross Tax (before Surcharge & Cess):** ₹{gross_tax:,.2f}")
        if rebate_amount > 0:
            st.write(f"**Less: Rebate u/s 87A:** ₹{rebate_amount:,.2f}")
        st.write(f"**Add: Surcharge:** ₹{surcharge:,.2f}")
        st.write(f"**Add: Health & Education Cess (4%):** ₹{cess:,.2f}")
        st.markdown(f"## **Total Tax Payable: ₹{total_tax_payable:,.2f}**")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Disclaimer ---
    st.markdown(
        """
        <div class="disclaimer">
        <p><strong>Disclaimer:</strong> This calculator is for informational purposes only and is based on the Income Tax Act, 1961 (as amended for FY 2024-25 / AY 2025-26) for resident individuals. It provides a simplified calculation and does not account for all possible income sources, deductions, exemptions, or complex tax scenarios. It is not a substitute for professional tax advice. Please consult a qualified tax advisor for accurate tax planning and filing.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
