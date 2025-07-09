#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import streamlit as st

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
        tax = (300000 * 0.05) + (300000 * 0.10) + (300000 * 0.15) + (300000 * 0.20)
        tax += (taxable_income - 1500000) * 0.30
    else:
        tax = (300000 * 0.05) + (300000 * 0.10) + (300000 * 0.15) + (300000 * 0.20)
        tax += (taxable_income - 1500000) * 0.30 # For income > 15 lakhs, 30% on excess

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
    elif income > 5000000: # Above 50 Lakhs up to 1 Crore
        surcharge_rate = 0.10
    
    return tax_amount * surcharge_rate

def calculate_cess(tax_plus_surcharge):
    """
    Calculates Health and Education Cess at 4%.
    """
    return tax_plus_surcharge * 0.04

# --- Streamlit UI ---
def main():
    # >>> IMPORTANT: st.set_page_config MUST be the very first Streamlit command <<<
    st.set_page_config(page_title="Geldium Tax Calculator", layout="centered", icon="💰")

    # --- Custom CSS for Eye-Catching GUI ---
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        html, body, [class*="st-"] {
            font-family: 'Inter', sans-serif;
            color: #333333;
        }

        .stApp {
            background: linear-gradient(to bottom right, #F0F8FF, #E0FFFF); /* Light blue gradient background */
        }

        .header-container {
            background: linear-gradient(to right, #2E86C1, #4CAF50); /* Blue to Green Gradient */
            padding: 20px 0;
            border-radius: 15px;
            margin-bottom: 2em;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            text-align: center;
        }
        .header-title {
            font-size: 3.5em;
            font-weight: bold;
            color: white; /* White text for contrast */
            text-align: center;
            margin-bottom: 0.2em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .header-subtitle {
            font-size: 1.4em;
            color: #ECF0F1; /* Light gray for subtitle */
            text-align: center;
            margin-bottom: 0;
        }
        .input-section, .result-section {
            background-color: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
        .stNumberInput > div > div > input {
            border-radius: 10px;
            padding: 10px 15px;
            border: 1px solid #D1D9E6;
            box-shadow: inset 2px 2px 5px #B8C0D0, inset -5px -5px 10px #FFFFFF;
        }
        .stRadio > label {
            font-weight: 600; /* Semi-bold */
            color: #333;
            font-size: 1.1em;
        }
        .stRadio div[role="radiogroup"] {
            display: flex;
            flex-direction: row; /* Arrange radio buttons horizontally */
            gap: 30px; /* Space between radio buttons */
            justify-content: center;
            margin-bottom: 20px;
        }
        .stButton button {
            border-radius: 25px; /* More rounded */
            padding: 12px 25px;
            background: linear-gradient(to right, #2E86C1, #4CAF50); /* Button gradient */
            color: white;
            border: none;
            font-weight: bold;
            font-size: 1.1em;
            display: block;
            margin: 25px auto;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2); /* Button shadow */
            transition: all 0.3s ease;
        }
        .stButton button:hover {
            background: linear-gradient(to right, #1A5276, #388E3C); /* Darker gradient on hover */
            transform: translateY(-2px); /* Slight lift effect */
            box-shadow: 0 7px 20px rgba(0, 0, 0, 0.3);
        }
        .result-box {
            background-color: #EBF5FB; /* Light blue */
            border-left: 6px solid #2E86C1; /* Stronger border */
            padding: 25px;
            border-radius: 10px;
            margin-top: 30px;
            font-size: 1.1em;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
        .result-box h3 {
            color: #2E86C1;
            margin-top: 0;
            font-weight: 700;
        }
        .stMetric {
            background-color: #F8F9FA; /* Light background for metric */
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            text-align: center;
            margin-top: 20px;
        }
        .stMetric > div > div > div:first-child { /* Metric label */
            font-size: 1.2em;
            color: #566573;
            font-weight: 600;
        }
        .stMetric > div > div > div:last-child { /* Metric value */
            font-size: 2.5em;
            font-weight: bold;
            color: #2E86C1;
        }
        .disclaimer {
            font-size: 0.85em;
            color: #777;
            margin-top: 40px;
            text-align: center;
            padding: 15px;
            background-color: #F0F0F0;
            border-radius: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # --- Header Section ---
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    st.markdown('<p class="header-title">💰 Geldium Income Tax Calculator</p>', unsafe_allow_html=True)
    st.markdown('<p class="header-subtitle">Calculate your tax for Financial Year 2024-25 (Assessment Year 2025-26)</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("---") # Visual separator

    # --- Input Section ---
    with st.container():
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.subheader("Your Income Details")

        annual_income = st.number_input(
            "Enter your Annual Income (₹)",
            min_value=0,
            value=750000, # Default value
            step=10000,
            format="%d",
            key="annual_income_input" # Added key for reset
        )

        tax_regime = st.radio(
            "Choose Tax Regime:",
            ("New Tax Regime", "Old Tax Regime"),
            index=0, # Default to New Tax Regime
            key="tax_regime_radio" # Added key for reset
        )

        age_group = "Below 60 years" # Default for New Regime, will be used if Old Regime is selected
        deductions = {} # Dictionary to store deduction values

        if tax_regime == "Old Tax Regime":
            st.info("The Old Tax Regime calculation is simplified here. For a precise calculation, consult a tax professional as it involves many specific deductions.")
            age_group = st.radio(
                "Select Your Age Group:",
                ("Below 60 years", "60 to 80 years", "Above 80 years"),
                index=0,
                key="age_group_radio" # Added key for reset
            )
            with st.expander("Add Common Deductions (Old Regime - Simplified)"):
                deductions['80C'] = st.number_input(
                    "Deduction under Section 80C (Max ₹1,50,000 for investments like PPF, ELSS, EPF, Home Loan Principal, Life Insurance Premium, etc.)",
                    min_value=0,
                    max_value=150000,
                    value=0,
                    step=1000,
                    format="%d",
                    key="deduction_80c_input" # Added key for reset
                )
                # You would add more deduction fields here for a comprehensive Old Regime calculator
                # e.g., st.number_input("Deduction under Section 80D (Health Insurance)", ...)
        st.markdown('</div>', unsafe_allow_html=True) # Close input-section div

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Calculate Tax", key="calculate_button"):
            gross_tax = 0
            surcharge = 0
            cess = 0
            total_tax_payable = 0
            rebate_amount = 0 # To display rebate separately

            if tax_regime == "New Tax Regime":
                gross_tax_initial = calculate_tax_new_regime(annual_income)
                # Rebate is already handled inside calculate_tax_new_regime, but for display clarity:
                if annual_income <= 700000:
                    rebate_amount = min(gross_tax_initial + 50000, 25000) # Rebate based on income before SD
                    # Gross tax for surcharge/cess is after rebate
                    gross_tax = max(0, gross_tax_initial) # gross_tax_initial already has rebate applied
                else:
                    gross_tax = gross_tax_initial

                surcharge = calculate_surcharge(gross_tax, annual_income, tax_regime)
                tax_plus_surcharge = gross_tax + surcharge
                cess = calculate_cess(tax_plus_surcharge)
                total_tax_payable = tax_plus_surcharge + cess
                
            else: # Old Tax Regime
                gross_tax_initial = calculate_tax_old_regime(annual_income, age_group, deductions)
                # Rebate is already handled inside calculate_tax_old_regime, but for display clarity:
                if annual_income <= 500000:
                     rebate_amount = min(gross_tax_initial, 12500)
                     gross_tax = max(0, gross_tax_initial) # gross_tax_initial already has rebate applied
                else:
                    gross_tax = gross_tax_initial

                surcharge = calculate_surcharge(gross_tax, annual_income, tax_regime)
                tax_plus_surcharge = gross_tax + surcharge
                cess = calculate_cess(tax_plus_surcharge)
                total_tax_payable = tax_plus_surcharge + cess

            # Store results in session state to persist after rerun
            st.session_state['results'] = {
                'regime': tax_regime,
                'income': annual_income,
                'age_group': age_group,
                'deductions_80c': deductions.get('80C', 0),
                'gross_tax': gross_tax,
                'rebate_amount': rebate_amount,
                'surcharge': surcharge,
                'cess': cess,
                'total_tax_payable': total_tax_payable
            }
    with col2:
        if st.button("Reset", key="reset_button"):
            # Clear session state and rerun to reset inputs
            for key in st.session_state.keys():
                if key.endswith("_input") or key.endswith("_radio") or key == 'results':
                    del st.session_state[key]
            st.rerun()

    # --- Display Results Section (only if calculation has been performed) ---
    if 'results' in st.session_state:
        results = st.session_state['results']
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.markdown('<h3><center>✅ Your Tax Calculation Summary</center></h3>', unsafe_allow_html=True)
        
        st.metric(label="Total Tax Payable", value=f"₹{results['total_tax_payable']:,.2f}")

        st.write(f"**Selected Regime:** {results['regime']}")
        st.write(f"**Annual Income:** ₹{results['income']:,.2f}")
        
        if results['regime'] == "Old Tax Regime":
            st.write(f"**Selected Age Group:** {results['age_group']}")
            st.write(f"**80C Deduction:** ₹{results['deductions_80c']:,.2f}")

        st.write(f"**Tax (before Surcharge & Cess):** ₹{results['gross_tax']:,.2f}")
        if results['rebate_amount'] > 0:
            st.write(f"**Less: Rebate u/s 87A:** ₹{results['rebate_amount']:,.2f}")
        st.write(f"**Add: Surcharge:** ₹{results['surcharge']:,.2f}")
        st.write(f"**Add: Health & Education Cess (4%):** ₹{results['cess']:,.2f}")
        
        st.markdown('</div>', unsafe_allow_html=True) # Close result-section div


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
