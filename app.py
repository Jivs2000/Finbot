#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import streamlit as st

# --- Tax Calculation Logic ---

# Income Tax Slabs for FY 2024-25 (AY 2025-26)

def calculate_tax_new_regime(gross_total_income):
    """
    Calculates income tax as per the New Tax Regime for FY 2024-25.
    Includes Standard Deduction for salaried individuals and Section 87A rebate.
    """
    # Standard Deduction (only for salaried income, but applied to GTI for simplicity in this calculator)
    # In a real scenario, Standard Deduction is only on Salary Income.
    # For this calculator, we apply it to GTI to simplify the flow.
    taxable_income = max(0, gross_total_income - 50000) # Apply standard deduction of 50,000

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
        tax += (taxable_income - 1500000) * 0.30
    else:
        tax = (300000 * 0.05) + (300000 * 0.10) + (300000 * 0.15) + (300000 * 0.20)
        tax += (taxable_income - 1500000) * 0.30 # For income > 15 lakhs, 30% on excess

    # Section 87A Rebate (for New Regime: up to 25,000 if total income <= 7,00,000)
    rebate = 0
    if gross_total_income <= 700000: # Note: rebate is on 'total income' before standard deduction
        rebate = min(tax, 25000) # Rebate is lesser of tax payable or 25,000

    net_tax_before_surcharge_cess = tax - rebate
    return max(0, net_tax_before_surcharge_cess) # Ensure tax is not negative

def calculate_tax_old_regime(gross_total_income, age_group, deductions):
    """
    Calculates income tax as per the Old Tax Regime for FY 2024-25.
    Accounts for various deductions.
    """
    total_deductions = 0

    # Chapter VI-A Deductions
    total_deductions += min(deductions.get('80C', 0), 150000) # Max 1.5 Lakh
    
    # 80D - Health Insurance (simplified max)
    max_80d_deduction = 25000 # Self, spouse, dependent children
    if age_group in ["60 to 80 years", "Above 80 years"]:
        max_80d_deduction = 50000 # Senior citizens
    total_deductions += min(deductions.get('80D', 0), max_80d_deduction)

    total_deductions += min(deductions.get('80CCD(1B)', 0), 50000) # NPS additional
    total_deductions += min(deductions.get('80E', 0), gross_total_income) # Education Loan Interest (no max limit, but limited by interest paid)
    total_deductions += min(deductions.get('80G', 0), gross_total_income) # Donations (limits apply based on donee)
    total_deductions += min(deductions.get('80TTA', 0), 10000) # Savings interest (for non-seniors)
    if age_group in ["60 to 80 years", "Above 80 years"]:
        total_deductions += min(deductions.get('80TTB', 0), 50000) # Savings/FD interest (for seniors)

    # Section 24(b) - Home Loan Interest (deduction from House Property Income, but here treated as general deduction for simplicity)
    total_deductions += min(deductions.get('24b_interest', 0), 200000) # Max 2 Lakh

    taxable_income = max(0, gross_total_income - total_deductions)

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
    if gross_total_income <= 500000: # Note: rebate is on 'total income' before deductions
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
    st.set_page_config(page_title="Jivanshu Tax Assistant", layout="centered") 

    # --- Custom CSS for Eye-Catching GUI ---
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        html, body, [class*="st-"] {
            font-family: 'Inter', sans-serif;
            color: #000000; /* Changed to Black */
            font-weight: normal; /* Ensure general text is not forced bold unless specified */
        }

        .stApp {
            background: linear-gradient(to bottom right, #FCE4EC, #E1BEE7); /* Light Pink to Light Purple Gradient */
        }

        .header-container {
            background: linear-gradient(to right, #880E4F, #AD1457); /* Darker Pink/Maroon Gradient */
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
            color: #F8BBD0; /* Lighter pink for subtitle */
            text-align: center;
            margin-bottom: 0;
        }
        .input-section, .result-section, .info-section { /* Added .info-section */
            background-color: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
        .stNumberInput > div > div > input {
            border-radius: 10px;
            padding: 10px 15px;
            border: 1px solid #F48FB1; /* Pink border */
            box-shadow: inset 2px 2px 5px #F06292, inset -5px -5px 10px #FFFFFF;
        }
        .stRadio > label {
            font-weight: 600; /* Semi-bold */
            color: #000000; /* Changed to Black */
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
            background: linear-gradient(to right, #880E4F, #AD1457); /* Match header button gradient */
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
            background: linear-gradient(to right, #5C002B, #7B1FA2); /* Darker gradient on hover, transitioning to purple */
            transform: translateY(-2px); /* Slight lift effect */
            box_shadow: 0 7px 20px rgba(0, 0, 0, 0.3);
        }
        .result-box {
            background-color: #FCE4EC; /* Very light pink */
            border-left: 6px solid #880E4F; /* Stronger pink/maroon border */
            padding: 25px;
            border-radius: 10px;
            margin-top: 30px;
            font-size: 1.1em;
            box_shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
        .result-box h3 {
            color: #880E4F; /* Dark Pink/Maroon */
            margin-top: 0;
            font-weight: 700;
        }
        .stMetric {
            background-color: #F3E5F5; /* Lighter purple background for metric */
            border-radius: 10px;
            padding: 20px;
            box_shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
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
            color: #AD1457; /* Dark Pink */
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
    st.markdown('<p class="header-title">💰 Jivanshu Tax Assistant</p>', unsafe_allow_html=True)
    st.markdown('<p class="header-subtitle">Calculate your tax for Financial Year 2024-25 (Assessment Year 2025-26)</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("---") # Visual separator

    # --- Input Section ---
    with st.container():
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.subheader("Your Income Details")

        # Basic Income Input
        gross_salary = st.number_input(
            "Gross Salary Income (₹)",
            min_value=0,
            value=750000,
            step=10000,
            format="%d",
            key="gross_salary_input"
        )

        tax_regime = st.radio(
            "Choose Tax Regime:",
            ("New Tax Regime", "Old Tax Regime"),
            index=0,
            key="tax_regime_radio"
        )

        age_group = "Below 60 years" # Default for New Regime, will be used if Old Regime is selected
        deductions = {} # Dictionary to store deduction values
        other_income_sources = {} # Dictionary to store other income sources

        if tax_regime == "Old Tax Regime":
            st.info("For Old Tax Regime, you can claim various deductions and exemptions. Please fill in the applicable amounts below.")
            age_group = st.radio(
                "Select Your Age Group:",
                ("Below 60 years", "60 to 80 years", "Above 80 years"),
                index=0,
                key="age_group_radio"
            )
            
            st.subheader("Other Income Sources (Old Regime)")
            st.markdown("*(Enter amounts for applicable income sources)*")
            other_income_sources['house_property'] = st.number_input(
                "Income from House Property (Rent Received - Expenses) (₹)",
                min_value=0, value=0, step=1000, format="%d", key="income_hp_input"
            )
            other_income_sources['capital_gains_long_term'] = st.number_input(
                "Long Term Capital Gains (LTCG) (₹)",
                min_value=0, value=0, step=1000, format="%d", key="income_ltcg_input"
            )
            other_income_sources['capital_gains_short_term'] = st.number_input(
                "Short Term Capital Gains (STCG) (₹)",
                min_value=0, value=0, step=1000, format="%d", key="income_stcg_input"
            )
            other_income_sources['other_sources'] = st.number_input(
                "Income from Other Sources (Interest, Dividends, etc.) (₹)",
                min_value=0, value=0, step=1000, format="%d", key="income_os_input"
            )
            
            st.subheader("Detailed Deductions & Exemptions (Old Regime)")
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
            deductions['80E'] = st.number_input(
                "Deduction u/s 80E (Education Loan Interest)",
                min_value=0, value=0, step=1000, format="%d", key="deduction_80e_input"
            )
            deductions['80G'] = st.number_input(
                "Deduction u/s 80G (Donations - Limits Apply)",
                min_value=0, value=0, step=1000, format="%d", key="deduction_80g_input"
            )
            deductions['80TTA'] = st.number_input(
                "Deduction u/s 80TTA (Savings A/C Interest - Max ₹10,000)",
                min_value=0, max_value=10000, value=0, step=100, format="%d", key="deduction_80tta_input"
            )
            if age_group in ["60 to 80 years", "Above 80 years"]:
                deductions['80TTB'] = st.number_input(
                    "Deduction u/s 80TTB (Senior Citizen Savings/FD Interest - Max ₹50,000)",
                    min_value=0, max_value=50000, value=0, step=1000, format="%d", key="deduction_80ttb_input"
                )

        st.markdown('</div>', unsafe_allow_html=True) # Close input-section div

    # Calculate Gross Total Income based on regime
    # For New Regime, we assume annual_income is already GTI
    # For Old Regime, we sum up the specific income sources
    if tax_regime == "Old Tax Regime":
        total_gross_income = gross_salary + \
                             other_income_sources.get('house_property', 0) + \
                             other_income_sources.get('capital_gains_long_term', 0) + \
                             other_income_sources.get('capital_gains_short_term', 0) + \
                             other_income_sources.get('other_sources', 0)
    else:
        total_gross_income = gross_salary # For new regime, we stick to the initial single input for simplicity

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Calculate Tax", key="calculate_button"):
            gross_tax = 0
            surcharge = 0
            cess = 0
            total_tax_payable = 0
            rebate_amount = 0 

            if tax_regime == "New Tax Regime":
                gross_tax_initial = calculate_tax_new_regime(total_gross_income)
                
                # To show the rebate amount, we need to re-calculate tax without rebate first.
                temp_tax_without_rebate = 0
                temp_taxable_income = max(0, total_gross_income - 50000) # Apply standard deduction
                if temp_taxable_income <= 300000: temp_tax_without_rebate = 0
                elif temp_taxable_income <= 600000: temp_tax_without_rebate = (temp_taxable_income - 300000) * 0.05
                elif temp_taxable_income <= 900000: temp_tax_without_rebate = (300000 * 0.05) + (temp_taxable_income - 600000) * 0.10
                elif temp_taxable_income <= 1200000: temp_tax_without_rebate = (300000 * 0.05) + (300000 * 0.10) + (temp_taxable_income - 900000) * 0.15
                elif temp_taxable_income <= 1500000: temp_tax_without_rebate = (300000 * 0.05) + (300000 * 0.10) + (300000 * 0.15) + (temp_taxable_income - 1200000) * 0.20
                else: temp_tax_without_rebate = (300000 * 0.05) + (300000 * 0.10) + (300000 * 0.15) + (300000 * 0.20) + (temp_taxable_income - 1500000) * 0.30
                
                if total_gross_income <= 700000:
                    rebate_amount = min(temp_tax_without_rebate, 25000)
                    gross_tax = max(0, temp_tax_without_rebate - rebate_amount) # Gross tax for surcharge/cess is after rebate
                else:
                    gross_tax = gross_tax_initial # If no rebate, gross_tax is simply the calculated tax

                surcharge = calculate_surcharge(gross_tax, total_gross_income, tax_regime)
                tax_plus_surcharge = gross_tax + surcharge
                cess = calculate_cess(tax_plus_surcharge)
                total_tax_payable = tax_plus_surcharge + cess
                
            else: # Old Tax Regime
                gross_tax_initial = calculate_tax_old_regime(total_gross_income, age_group, deductions)
                
                # To show rebate amount, need to calculate tax without rebate first
                temp_tax_without_rebate = 0
                temp_total_deductions_old = 0
                temp_total_deductions_old += min(deductions.get('80C', 0), 150000)
                max_80d_deduction = 25000
                if age_group in ["60 to 80 years", "Above 80 years"]: max_80d_deduction = 50000
                temp_total_deductions_old += min(deductions.get('80D', 0), max_80d_deduction)
                temp_total_deductions_old += min(deductions.get('80CCD(1B)', 0), 50000)
                temp_total_deductions_old += min(deductions.get('80E', 0), total_gross_income)
                temp_total_deductions_old += min(deductions.get('80G', 0), total_gross_income)
                temp_total_deductions_old += min(deductions.get('80TTA', 0), 10000)
                if age_group in ["60 to 80 years", "Above 80 years"]:
                    temp_total_deductions_old += min(deductions.get('80TTB', 0), 50000)
                temp_total_deductions_old += min(deductions.get('24b_interest', 0), 200000)

                temp_taxable_income_old = max(0, total_gross_income - temp_total_deductions_old)

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
                
                if total_gross_income <= 500000:
                     rebate_amount = min(temp_tax_without_rebate, 12500)
                     gross_tax = max(0, temp_tax_without_rebate - rebate_amount)
                else:
                    gross_tax = gross_tax_initial

                surcharge = calculate_surcharge(gross_tax, total_gross_income, tax_regime)
                tax_plus_surcharge = gross_tax + surcharge
                cess = calculate_cess(tax_plus_surcharge)
                total_tax_payable = tax_plus_surcharge + cess

            # Store results in session state to persist after rerun
            st.session_state['results'] = {
                'regime': tax_regime,
                'gross_total_income': total_gross_income,
                'age_group': age_group,
                'deductions': deductions, # Store full deductions dict
                'other_income_sources': other_income_sources, # Store other income sources
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
        st.write(f"**Gross Total Income:** ₹{results['gross_total_income']:,.2f}")
        
        if results['regime'] == "Old Tax Regime":
            st.write(f"**Selected Age Group:** {results['age_group']}")
            st.write(f"**Income from Other Sources:**")
            for source_name, source_val in results['other_income_sources'].items():
                if source_val > 0:
                    st.write(f"  - {source_name.replace('_', ' ').title()}: ₹{source_val:,.2f}")
            st.write(f"**Total Deductions Considered:**")
            for ded_name, ded_val in results['deductions'].items():
                if ded_val > 0:
                    st.write(f"  - {ded_name}: ₹{ded_val:,.2f}")

        st.write(f"**Tax (before Surcharge & Cess):** ₹{results['gross_tax']:,.2f}")
        if results['rebate_amount'] > 0:
            st.write(f"**Less: Rebate u/s 87A:** ₹{results['rebate_amount']:,.2f}")
        st.write(f"**Add: Surcharge:** ₹{results['surcharge']:,.2f}")
        st.write(f"**Add: Health & Education Cess (4%):** ₹{results['cess']:,.2f}")
        
        st.markdown('</div>', unsafe_allow_html=True) # Close result-section div

    st.write("---") # Separator before new section

    # --- New Section: Tax Saving & Investment Insights ---
    st.markdown('<div class="info-section">', unsafe_allow_html=True) # Reusing info-section style
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
        * **Section 80E (Education Loan Interest):** Deduction for interest paid on education loans. No upper limit, but limited to interest paid.
        * **Section 80G (Donations):** Deductions for donations to certain approved charitable institutions. Limits and eligibility apply.
        * **Section 80TTA/80TTB (Savings Interest):** Deduction for interest from savings accounts. 80TTA (Max ₹10,000) for general, 80TTB (Max ₹50,000) for senior citizens (replaces 80TTA for them).
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
    st.markdown('</div>', unsafe_allow_html=True) # Close info-section div

    st.write("---") # Separator before new section

    # --- New Section: Detailed Income & Deduction Inputs (for Old Regime) ---
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown('<h2><center>📝 Detailed Income & Deduction Inputs (Old Regime Only)</center></h2>', unsafe_allow_html=True)
    st.markdown("""
    **This section is primarily relevant for the Old Tax Regime.** If you've chosen the New Tax Regime, most of these deductions and separate income calculations are not applicable.
    """)

    with st.expander("Enter Specific Income Sources (Old Regime)"):
        st.subheader("Income from House Property")
        hp_income = st.number_input(
            "Gross Rental Income (₹)",
            min_value=0, value=0, step=1000, format="%d", key="hp_gross_rent"
        )
        hp_municipal_tax = st.number_input(
            "Municipal Taxes Paid (₹)",
            min_value=0, value=0, step=1000, format="%d", key="hp_municipal_tax"
        )
        # Net Annual Value (NAV) = Gross Rental Income - Municipal Taxes
        nav = max(0, hp_income - hp_municipal_tax)
        st.write(f"Net Annual Value (NAV): ₹{nav:,.2f}")
        
        # Standard Deduction on HP Income (30% of NAV)
        hp_standard_deduction = nav * 0.30
        st.write(f"Standard Deduction (30% of NAV): ₹{hp_standard_deduction:,.2f}")

        hp_interest_loan = st.number_input(
            "Interest on Home Loan for House Property (Section 24(b) - covered in deductions below) (₹)",
            min_value=0, value=0, step=1000, format="%d", key="hp_interest_loan_input"
        )
        
        # This is a simplified calculation for display.
        # Actual HP income calculation is more detailed.
        income_from_hp_calc = nav - hp_standard_deduction - hp_interest_loan
        st.info(f"Calculated Income from House Property (simplified): ₹{income_from_hp_calc:,.2f}")
        st.markdown("*(This value is for display. The home loan interest deduction is added to your total deductions if you are in the Old Regime.)*")

        st.subheader("Capital Gains")
        ltcg_amount = st.number_input(
            "Long Term Capital Gains (LTCG) (₹)",
            min_value=0, value=0, step=1000, format="%d", key="ltcg_input_detailed"
        )
        stcg_amount = st.number_input(
            "Short Term Capital Gains (STCG) (₹)",
            min_value=0, value=0, step=1000, format="%d", key="stcg_input_detailed"
        )
        st.markdown("*(Taxation of capital gains is complex and depends on asset type, holding period, and specific sections. This calculator only takes the amount as input.)*")

        st.subheader("Profits and Gains from Business or Profession (PGBP)")
        pnbp_income = st.number_input(
            "Net Income from Business/Profession (₹)",
            min_value=0, value=0, step=1000, format="%d", key="pnbp_input"
        )
        st.markdown("*(This is a highly complex head. Please enter your net taxable income after all applicable business expenses and depreciation.)*")

        st.subheader("Income from Other Sources")
        interest_income = st.number_input(
            "Interest Income (Savings, FDs, etc.) (₹)",
            min_value=0, value=0, step=1000, format="%d", key="interest_income_input"
        )
        dividend_income = st.number_input(
            "Dividend Income (₹)",
            min_value=0, value=0, step=1000, format="%d", key="dividend_income_input"
        )
        casual_income = st.number_input(
            "Casual Income (Lottery, Gambling, etc.) (₹)",
            min_value=0, value=0, step=1000, format="%d", key="casual_income_input"
        )
        st.markdown("*(Note: Casual income is taxed at a flat 30% without deductions.)*")

        # Update total_gross_income based on these detailed inputs if Old Regime is selected
        if tax_regime == "Old Tax Regime":
            total_gross_income = gross_salary + \
                                 max(0, income_from_hp_calc) + \
                                 ltcg_amount + stcg_amount + \
                                 pnbp_income + \
                                 interest_income + dividend_income + casual_income
            st.session_state['annual_income_input'] = total_gross_income # Update the main input for consistency

    with st.expander("Enter Specific Exemptions (Old Regime)"):
        st.subheader("Exempt Income & Allowances (Not part of GTI)")
        hra_exemption = st.number_input(
            "HRA Exemption (as per rules) (₹)",
            min_value=0, value=0, step=1000, format="%d", key="hra_exemption_input"
        )
        lta_exemption = st.number_input(
            "LTA Exemption (as per rules) (₹)",
            min_value=0, value=0, step=1000, format="%d", key="lta_exemption_input"
        )
        # Note: These are usually deducted from Gross Salary to arrive at Taxable Salary.
        # For simplicity, we are showing them as inputs but not directly using them in the main calculation flow
        # as the 'Gross Salary Income' is assumed to be the taxable portion after these.
        st.info("These are typically excluded from Gross Salary before tax calculation. Ensure your 'Gross Salary Income' input reflects this if applicable.")

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
