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
    total_deductions = 0

    # Section 80C
    max_80c_deduction = 150000
    total_deductions += min(deductions.get('80C', 0), max_80c_deduction)

    # Section 80D (Health Insurance) - Simplified Max
    max_80d_deduction = 25000 # For general
    if age_group in ["60 to 80 years", "Above 80 years"]:
        max_80d_deduction = 50000 # For senior citizens
    total_deductions += min(deductions.get('80D', 0), max_80d_deduction)

    # Section 80CCD(1B) (NPS)
    max_80ccd1b_deduction = 50000
    total_deductions += min(deductions.get('80CCD(1B)', 0), max_80ccd1b_deduction)

    # Section 24(b) (Home Loan Interest)
    max_24b_deduction = 200000
    total_deductions += min(deductions.get('24b_interest', 0), max_24b_deduction)

    # Combine all income sources for total taxable income
    # Note: For simplicity, assuming these are added to the 'annual_income'
    # In a real scenario, income from sources like house property, capital gains, PGBP
    # would be calculated separately and then aggregated to Gross Total Income (GTI)
    # before applying Chapter VI-A deductions.
    # Here, 'income' is treated as Gross Total Income for deduction purposes.

    taxable_income = max(0, income - total_deductions)

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
    st.set_page_config(page_title="Jivanshu Tax Assistant", layout="centered") # Changed page_title

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
            background: linear-gradient(to bottom right, #E0F7FA, #E1BEE7); /* Light Cyan to Light Purple Gradient */
        }

        .header-container {
            background: linear-gradient(to right, #00BCD4, #9C27B0); /* Cyan to Deep Purple Gradient */
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
            color: #E0F7FA; /* Lighter cyan for subtitle */
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
            border: 1px solid #B2EBF2; /* Light cyan border */
            box-shadow: inset 2px 2px 5px #80DEEA, inset -5px -5px 10px #FFFFFF;
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
            background: linear-gradient(to right, #00BCD4, #9C27B0); /* Match header button gradient */
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
            background: linear-gradient(to right, #00ACC1, #8E24AA); /* Darker gradient on hover */
            transform: translateY(-2px); /* Slight lift effect */
            box-shadow: 0 7px 20px rgba(0, 0, 0, 0.3);
        }
        .result-box {
            background-color: #E0F7FA; /* Very light cyan */
            border-left: 6px solid #00BCD4; /* Stronger cyan border */
            padding: 25px;
            border-radius: 10px;
            margin-top: 30px;
            font-size: 1.1em;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
        .result-box h3 {
            color: #00BCD4; /* Cyan */
            margin-top: 0;
            font-weight: 700;
        }
        .stMetric {
            background-color: #F3F8FA; /* Lighter cyan background for metric */
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
            color: #00BCD4; /* Cyan */
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
    st.markdown('<p class="header-title">💰 Jivanshu Tax Assistant</p>', unsafe_allow_html=True) # Changed header_title
    st.markdown('<p class="header-subtitle">Calculate your tax for Financial Year 2024-25 (Assessment Year 2025-26)</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("---") # Visual separator

    # --- Input Section ---
    with st.container():
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.subheader("Your Income Details")

        annual_income = st.number_input(
            "Enter your Total Annual Income (₹) (Sum of all income sources)", # Clarified input
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
            
            st.subheader("Detailed Deductions (Old Regime)")
            st.markdown("*(Enter amounts for applicable deductions. Max limits apply.)*")

            deductions['80C'] = st.number_input(
                "Deduction u/s 80C (Max ₹1,50,000)",
                min_value=0, max_value=150000, value=0, step=1000, format="%d", key="deduction_80c_input"
            )
            deductions['80D'] = st.number_input(
                "Deduction u/s 80D (Health Insurance - Max ₹25k/50k)",
                min_value=0, max_value=50000, value=0, step=1000, format="%d", key="deduction_80d_input"
            )
            deductions['80CCD(1B)'] = st.number_input(
                "Deduction u/s 80CCD(1B) (NPS - Max ₹50,000)",
                min_value=0, max_value=50000, value=0, step=1000, format="%d", key="deduction_80ccd1b_input"
            )
            deductions['24b_interest'] = st.number_input(
                "Deduction u/s 24(b) (Home Loan Interest - Max ₹2,00,000)",
                min_value=0, max_value=200000, value=0, step=1000, format="%d", key="deduction_24b_input"
            )
            # Add more common deductions here if needed, e.g., 80E, 80G, etc.
            # For this simplified calculator, we'll stick to a few key ones.

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
                    # The rebate calculation needs to consider the tax *before* it's zeroed out by the rebate
                    # The calculate_tax_new_regime returns the final tax after rebate.
                    # To show the rebate amount, we need to re-calculate tax without rebate first.
                    temp_tax_without_rebate = 0
                    temp_taxable_income = max(0, annual_income - 50000) # Apply standard deduction
                    if temp_taxable_income <= 300000: temp_tax_without_rebate = 0
                    elif temp_taxable_income <= 600000: temp_tax_without_rebate = (temp_taxable_income - 300000) * 0.05
                    elif temp_taxable_income <= 900000: temp_tax_without_rebate = (300000 * 0.05) + (temp_taxable_income - 600000) * 0.10
                    elif temp_taxable_income <= 1200000: temp_tax_without_rebate = (300000 * 0.05) + (300000 * 0.10) + (temp_taxable_income - 900000) * 0.15
                    elif temp_taxable_income <= 1500000: temp_tax_without_rebate = (300000 * 0.05) + (300000 * 0.10) + (300000 * 0.15) + (temp_taxable_income - 1200000) * 0.20
                    else: temp_tax_without_rebate = (300000 * 0.05) + (300000 * 0.10) + (300000 * 0.15) + (300000 * 0.20) + (temp_taxable_income - 1500000) * 0.30
                    
                    rebate_amount = min(temp_tax_without_rebate, 25000)
                    gross_tax = max(0, temp_tax_without_rebate - rebate_amount) # Gross tax for surcharge/cess is after rebate
                else:
                    gross_tax = gross_tax_initial # If no rebate, gross_tax is simply the calculated tax

                surcharge = calculate_surcharge(gross_tax, annual_income, tax_regime)
                tax_plus_surcharge = gross_tax + surcharge
                cess = calculate_cess(tax_plus_surcharge)
                total_tax_payable = tax_plus_surcharge + cess
                
            else: # Old Tax Regime
                gross_tax_initial = calculate_tax_old_regime(annual_income, age_group, deductions)
                # Rebate is already handled inside calculate_tax_old_regime, but for display clarity:
                # To show rebate amount, need to calculate tax without rebate first
                temp_tax_without_rebate = 0
                temp_taxable_income_old = annual_income
                temp_total_deductions = 0
                max_80c_deduction = 150000
                temp_total_deductions += min(deductions.get('80C', 0), max_80c_deduction)
                max_80d_deduction = 25000
                if age_group in ["60 to 80 years", "Above 80 years"]: max_80d_deduction = 50000
                temp_total_deductions += min(deductions.get('80D', 0), max_80d_deduction)
                max_80ccd1b_deduction = 50000
                temp_total_deductions += min(deductions.get('80CCD(1B)', 0), max_80ccd1b_deduction)
                max_24b_deduction = 200000
                temp_total_deductions += min(deductions.get('24b_interest', 0), max_24b_deduction)
                temp_taxable_income_old = max(0, annual_income - temp_total_deductions)

                if age_group == "Below 60 years":
                    if temp_taxable_income_old <= 250000: temp_tax_without_rebate = 0
                    elif temp_taxable_income_old <= 500000: temp_tax_without_rebate = (temp_taxable_income_old - 250000) * 0.05
                    elif temp_taxable_income_old <= 1000000: temp_tax_without_rebate = (250000 * 0.05) + (temp_taxable_income_old - 500000) * 0.20
                    else: temp_tax_without_rebate = (250000 * 0.05) + (500000 * 0.20) + (temp_taxable_income_old - 1000000) * 0.30
                elif age_group == "60 to 80 years":
                    if temp_taxable_income_old <= 300000: temp_tax_without_rebate = 0
                    elif temp_taxable_income_old <= 500000: temp_tax_without_rebate = (temp_taxable_income_old - 300000) * 0.05
                    elif temp_taxable_income_old <= 1000000: temp_tax_without_rebate = (200000 * 0.05) + (temp_taxable_income_old - 500000) * 0.20
                    else: temp_tax_without_rebate = (200000 * 0.05) + (500000 * 0.20) + (temp_taxable_income_old - 1000000) * 0.30
                elif age_group == "Above 80 years":
                    if temp_taxable_income_old <= 500000: temp_tax_without_rebate = 0
                    elif temp_taxable_income_old <= 1000000: temp_tax_without_rebate = (temp_taxable_income_old - 500000) * 0.20
                    else: temp_tax_without_rebate = (500000 * 0.20) + (temp_taxable_income_old - 1000000) * 0.30
                
                if annual_income <= 500000:
                     rebate_amount = min(temp_tax_without_rebate, 12500)
                     gross_tax = max(0, temp_tax_without_rebate - rebate_amount)
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
                'deductions': deductions, # Store full deductions dict
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
            st.write(f"**Total Deductions Considered:**")
            for ded_name, ded_val in results['deductions'].items():
                st.write(f"  - {ded_name}: ₹{ded_val:,.2f}")

        st.write(f"**Tax (before Surcharge & Cess):** ₹{results['gross_tax']:,.2f}")
        if results['rebate_amount'] > 0:
            st.write(f"**Less: Rebate u/s 87A:** ₹{results['rebate_amount']:,.2f}")
        st.write(f"**Add: Surcharge:** ₹{results['surcharge']:,.2f}")
        st.write(f"**Add: Health & Education Cess (4%):** ₹{results['cess']:,.2f}")
        
        st.markdown('</div>', unsafe_allow_html=True) # Close result-section div

    st.write("---") # Separator before new section

    # --- New Section: Tax Saving & Investment Insights ---
    st.markdown('<div class="input-section">', unsafe_allow_html=True) # Reusing input-section style
    st.markdown('<h2><center>💡 Tax Saving & Investment Insights</center></h2>', unsafe_allow_html=True)

    with st.expander("Common Tax Saving Sections"):
        st.markdown("""
        The Indian Income Tax Act offers various sections under which you can claim deductions to reduce your taxable income. Here are some of the most common ones:

        * **Section 80C (Max ₹1,50,000):** This is one of the most popular sections. Investments and expenses covered include:
            * Provident Fund (PF) / Employee Provident Fund (EPF)
            * Public Provident Fund (PPF)
            * Life Insurance Premiums
            * Equity Linked Savings Schemes (ELSS) - Mutual Funds
            * Home Loan Principal Repayment
            * Children's Tuition Fees (up to 2 children)
            * Fixed Deposits (5-year tax-saving FDs)
            * National Savings Certificate (NSC)
            * Sukanya Samriddhi Yojana (SSY)
        * **Section 80D (Health Insurance):** Deductions for health insurance premiums for yourself, spouse, dependent children, and parents. Limits vary based on age (senior citizens get higher limits).
        * **Section 80CCD(1B) (NPS):** An additional deduction of up to ₹50,000 for contributions to the National Pension System (NPS), over and above the 80C limit.
        * **Section 24(b) (Home Loan Interest):** Deduction for interest paid on housing loans (up to ₹2,00,000 for self-occupied property).
        * **Section 80G (Donations):** Deductions for donations to certain approved charitable institutions.
        * **Section 80EEA (Affordable Housing Loan Interest):** Additional deduction for interest on housing loans for affordable housing, over and above Section 24(b) (conditions apply).

        *Note: The New Tax Regime generally does not allow these deductions, except for the Standard Deduction for salaried individuals and employer's contribution to NPS.*
        """)

    with st.expander("Popular Tax-Saving Investment Options"):
        st.markdown("""
        Investing in tax-saving instruments not only helps you save tax but also aids in wealth creation.

        * **Equity Linked Savings Schemes (ELSS):**
            * **Type:** Mutual Funds (Equity)
            * **Lock-in:** 3 years (shortest among 80C options)
            * **Potential:** High growth potential, market-linked returns.
            * **Suitability:** For investors with a moderate to high-risk appetite.
        * **Public Provident Fund (PPF):**
            * **Type:** Government-backed savings scheme
            * **Lock-in:** 15 years (with partial withdrawals allowed after 7 years)
            * **Potential:** Guaranteed, tax-free returns, low risk.
            * **Suitability:** For conservative investors seeking long-term, safe growth.
        * **National Pension System (NPS):**
            * **Type:** Retirement savings scheme
            * **Lock-in:** Until retirement (age 60)
            * **Potential:** Market-linked returns, dual tax benefits (80C and 80CCD(1B)).
            * **Suitability:** For long-term retirement planning, moderate risk.
        * **Tax-Saving Fixed Deposits (FDs):**
            * **Type:** Bank Fixed Deposits
            * **Lock-in:** 5 years
            * **Potential:** Guaranteed returns, low risk.
            * **Suitability:** For conservative investors preferring fixed returns.
        * **Life Insurance Policies:**
            * **Type:** Various plans (Term, Endowment, ULIPs)
            * **Lock-in:** Varies by policy
            * **Potential:** Provides life cover; returns vary (ULIPs are market-linked).
            * **Suitability:** For financial protection and long-term savings.

        **Always consider your financial goals, risk tolerance, and liquidity needs before choosing any investment option.**
        """)
    st.markdown('</div>', unsafe_allow_html=True) # Close input-section div

    st.write("---") # Separator before new section

    # --- New Section: Understanding Complex Tax Scenarios ---
    st.markdown('<div class="input-section">', unsafe_allow_html=True) # Reusing input-section style
    st.markdown('<h2><center>🔍 Understanding Complex Tax Scenarios</center></h2>', unsafe_allow_html=True)
    st.markdown("""
    This calculator provides a general overview based on common scenarios. However, the Indian Income Tax Act is vast and complex. Here are some areas that require specialized understanding and are **not fully covered** by this simplified calculator:
    """)

    with st.expander("Different Income Sources"):
        st.markdown("""
        Beyond salary income, individuals can have various other income sources, each with specific tax treatments:
        * **Income from House Property:** Rental income, deductions for municipal taxes, standard deduction (30% of Net Annual Value), and interest on home loan.
        * **Profits and Gains from Business or Profession (PGBP):** Income from self-employment, professional fees, deductions for business expenses, depreciation, etc. This is a highly complex head.
        * **Capital Gains:** Gains from selling assets like shares, mutual funds, property (short-term vs. long-term capital gains, different tax rates, indexation benefits).
        * **Income from Other Sources:** Interest from savings accounts/FDs, dividends, gifts (above certain limits), casual income (lottery, gambling), family pension.
        """)

    with st.expander("Comprehensive Deductions & Exemptions"):
        st.markdown("""
        While Section 80C and 80D are common, there are many other deductions and exemptions that can significantly impact your tax liability, especially in the Old Tax Regime:
        * **House Rent Allowance (HRA) Exemption:** For salaried individuals living in rented accommodation.
        * **Leave Travel Allowance (LTA) Exemption:** For travel expenses during leave.
        * **Section 80E:** Deduction for interest on education loan.
        * **Section 80DD:** Deduction for medical treatment of a dependent with disability.
        * **Section 80DDB:** Deduction for medical treatment of specified diseases.
        * **Section 80TTA/80TTB:** Deduction for interest on savings bank accounts (80TTA for general, 80TTB for senior citizens).
        * **Agricultural Income:** Fully exempt from tax, but considered for rate purposes.
        * **Allowances & Perquisites:** Specific rules for various allowances (e.g., transport, children's education) and perquisites (e.g., company car, furnished accommodation).
        """)

    with st.expander("Complex Tax Scenarios"):
        st.markdown("""
        Several situations can make tax calculation intricate:
        * **Multiple Income Heads:** When an individual has income from salary, house property, business, and capital gains simultaneously.
        * **Set-off and Carry Forward of Losses:** Rules for adjusting losses from one income head against another, or carrying forward losses to future years.
        * **Alternate Minimum Tax (AMT) / Minimum Alternate Tax (MAT):** Applicable to certain entities or individuals with specific deductions/exemptions, ensuring a minimum tax is paid.
        * **Taxation of NRIs (Non-Resident Indians):** Different rules apply to NRIs, including income taxable in India, DTAA (Double Taxation Avoidance Agreements) benefits, and specific filing requirements.
        * **International Taxation:** Complexities arising from income earned abroad, foreign tax credits, and residency status.
        * **Presumptive Taxation:** Simplified schemes for small businesses and professionals (e.g., Section 44AD, 44ADA) where income is presumed as a percentage of turnover.
        * **Specific Business Deductions:** A wide array of deductions available for different types of businesses and professions.
        * **TDS (Tax Deducted at Source) / TCS (Tax Collected at Source):** Understanding how these impact your final tax liability and claiming credits.
        """)
    st.markdown('</div>', unsafe_allow_html=True) # Close input-section div


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

