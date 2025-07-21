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
    st.set_page_config(page_title="TaxSavvy Assistant", layout="centered") 

    # --- Custom CSS for Eye-Catching GUI ---
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap'); /* Added 800 weight */

        html, body, [class*="st-"] {
            font-family: 'Inter', sans-serif;
            color: #212121; /* Dark gray for general text */
            font-weight: normal; 
        }

        .stApp {
            background: linear-gradient(to bottom right, #F5F7FA, #E6E9ED); /* Very light gray/blue gradient */
        }

        .header-container {
            background: linear-gradient(to right, #0A2342, #1E4072); /* Deep Navy Blue to Dark Blue Gradient */
            padding: 25px 0;
            border-radius: 15px;
            margin-bottom: 2.5em;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
            text-align: center;
        }
        .header-title {
            font-size: 3.8em; 
            font-weight: 800; /* Made bolder */
            color: #000000; /* Changed to Black */
            text-align: center;
            margin-bottom: 0.2em;
            text-shadow: 2px 2px 6px rgba(255,255,255,0.6); /* Changed shadow to white for contrast */
        }
        .header-subtitle {
            font-size: 1.5em; 
            color: #000000; /* Changed to Black */
            font-weight: 800; /* Made bolder */
            text-align: center;
            margin-bottom: 0;
            text-shadow: 1px 1px 3px rgba(255,255,255,0.3); /* Changed shadow to white */
        }
        .input-section, .result-section, .info-section { 
            background-color: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
        .stNumberInput > div > div > input {
            border-radius: 10px;
            padding: 10px 15px;
            border: 1px solid #B0BEC5; /* Light gray-blue border */
            box-shadow: inset 2px 2px 5px #90A4AE, inset -5px -5px 10px #F5F7FA; /* Neumorphic effect */
        }
        .stRadio > label {
            font-weight: 600; 
            color: #212121; 
            font-size: 1.1em;
        }
        .stRadio div[role="radiogroup"] {
            display: flex;
            flex-direction: row; 
            gap: 30px; 
            justify-content: center;
            margin-bottom: 20px;
        }
        .stButton button {
            border-radius: 28px; 
            padding: 14px 30px; 
            background: linear-gradient(to right, #0A2342, #2A60A0); 
            color: white;
            border: none;
            font-weight: bold;
            font-size: 1.2em; 
            display: block;
            margin: 25px auto;
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.25); 
            transition: all 0.3s ease;
        }
        .stButton button:hover {
            background: linear-gradient(to right, #071A33, #1A4D8A); 
            transform: translateY(-3px); 
            box-shadow: 0 8px 22px rgba(0, 0, 0, 0.35);
        }
        .result-box {
            background-color: #E3F2FD; 
            border-left: 6px solid #0A2342; 
            padding: 25px;
            border-radius: 10px;
            margin-top: 30px;
            font-size: 1.1em;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        .result-box h3 {
            color: #0A2342; 
            margin-top: 0;
            font-weight: 700;
        }
        .stMetric {
            background-color: #E0F2F7; 
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
            text-align: center;
            margin-top: 20px;
        }
        .stMetric > div > div > div:first-child { 
            font-size: 1.2em;
            color: #546E7A; 
            font-weight: 600;
        }
        .stMetric > div > div > div:last-child { 
            font-size: 2.8em; 
            font-weight: bold;
            color: #0A2342; 
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
        /* Tab specific styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px; /* Space between tabs */
            justify-content: center; /* Center the tabs */
            margin-bottom: 20px;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: #CFD8DC; /* Light gray for inactive tabs */
            border-radius: 10px 10px 0 0;
            padding: 10px 20px;
            font-weight: 600;
            color: #455A64; /* Darker gray for inactive tab text */
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background-color: #B0BEC5; /* Slightly darker on hover */
            color: #212121;
        }

        .stTabs [aria-selected="true"] {
            background-color: #0A2342; /* Deep Navy Blue for active tab */
            color: white;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
            border-bottom: 3px solid #FFC107; /* Amber underline for active tab */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # --- Header Section ---
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    st.markdown('<p class="header-title"> TaxSavvy Assistant</p>', unsafe_allow_html=True) 
    st.markdown('<p class="header-subtitle">Your Smart Guide to Indian Income Tax</p>', unsafe_allow_html=True) 
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("---") # Visual separator

    # --- Tabbed Interface ---
    tab1, tab2, tab3 = st.tabs(["📊 Tax Calculator", "📝 Detailed Old Regime Inputs", "💡 Tax Saving & Investment Insights"])

    # --- Tab 1: Tax Calculator ---
    with tab1:
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
                st.info("For Old Tax Regime, you can claim various deductions and exemptions. Please fill in the applicable amounts in the 'Detailed Old Regime Inputs' tab.")
                age_group = st.radio(
                    "Select Your Age Group:",
                    ("Below 60 years", "60 to 80 years", "Above 80 years"),
                    index=0,
                    key="age_group_radio"
                )
            
            st.markdown('</div>', unsafe_allow_html=True) # Close input-section div

        # Initialize session state for detailed inputs if not already present
        # This ensures values persist when switching tabs
        if 'hp_gross_rent' not in st.session_state: st.session_state['hp_gross_rent'] = 0
        if 'hp_municipal_tax' not in st.session_state: st.session_state['hp_municipal_tax'] = 0
        if 'hp_interest_loan_input' not in st.session_state: st.session_state['hp_interest_loan_input'] = 0
        if 'income_ltcg_input' not in st.session_state: st.session_state['income_ltcg_input'] = 0
        if 'income_stcg_input' not in st.session_state: st.session_state['income_stcg_input'] = 0
        if 'pnbp_input' not in st.session_state: st.session_state['pnbp_input'] = 0
        if 'interest_income_input' not in st.session_state: st.session_state['interest_income_input'] = 0
        if 'dividend_income_input' not in st.session_state: st.session_state['dividend_income_input'] = 0
        if 'casual_income_input' not in st.session_state: st.session_state['casual_income_input'] = 0

        if 'deduction_80c_input' not in st.session_state: st.session_state['deduction_80c_input'] = 0
        if 'deduction_80d_input' not in st.session_state: st.session_state['deduction_80d_input'] = 0
        if 'deduction_80ccd1b_input' not in st.session_state: st.session_state['deduction_80ccd1b_input'] = 0
        if 'deduction_24b_input' not in st.session_state: st.session_state['deduction_24b_input'] = 0
        if 'deduction_80e_input' not in st.session_state: st.session_state['deduction_80e_input'] = 0
        if 'deduction_80g_input' not in st.session_state: st.session_state['deduction_80g_input'] = 0
        if 'deduction_80tta_input' not in st.session_state: st.session_state['deduction_80tta_input'] = 0
        if 'deduction_80ttb_input' not in st.session_state: st.session_state['deduction_80ttb_input'] = 0 # Only for seniors
        
        # Populate deductions and other_income_sources from session state for calculation
        if tax_regime == "Old Tax Regime":
            # Income Sources
            other_income_sources['house_property'] = st.session_state['hp_gross_rent'] - st.session_state['hp_municipal_tax'] - st.session_state['hp_interest_loan_input'] # Simplified HP income
            other_income_sources['capital_gains_long_term'] = st.session_state['income_ltcg_input']
            other_income_sources['capital_gains_short_term'] = st.session_state['income_stcg_input']
            other_income_sources['pnbp_income'] = st.session_state['pnbp_input']
            other_income_sources['interest_income'] = st.session_state['interest_income_input']
            other_income_sources['dividend_income'] = st.session_state['dividend_income_input']
            other_income_sources['casual_income'] = st.session_state['casual_income_input']

            # Deductions
            deductions['80C'] = st.session_state['deduction_80c_input']
            deductions['80D'] = st.session_state['deduction_80d_input']
            deductions['80CCD(1B)'] = st.session_state['deduction_80ccd1b_input']
            deductions['24b_interest'] = st.session_state['deduction_24b_input']
            deductions['80E'] = st.session_state['deduction_80e_input']
            deductions['80G'] = st.session_state['deduction_80g_input']
            deductions['80TTA'] = st.session_state['deduction_80tta_input']
            if age_group in ["60 to 80 years", "Above 80 years"]:
                deductions['80TTB'] = st.session_state['deduction_80ttb_input']


        # Calculate Gross Total Income based on regime and inputs
        if tax_regime == "Old Tax Regime":
            total_gross_income = gross_salary + \
                                 other_income_sources.get('house_property', 0) + \
                                 other_income_sources.get('capital_gains_long_term', 0) + \
                                 other_income_sources.get('capital_gains_short_term', 0) + \
                                 other_income_sources.get('pnbp_income', 0) + \
                                 other_income_sources.get('interest_income', 0) + \
                                 other_income_sources.get('dividend_income', 0) + \
                                 other_income_sources.get('casual_income', 0)
        else:
            total_gross_income = gross_salary 

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
                    if key.endswith("_input") or key.endswith("_radio") or key == 'results' or key.endswith("_info"):
                        del st.session_state[key]
                st.rerun()

        # --- Display Results Section (only if calculation has been performed) ---
        if 'results' in st.session_state:
            results = st.session_state['results']
            st.markdown('<div class="result-section">', unsafe_allow_html=True)
            st.markdown('<h3><center> Your Tax Calculation Summary</center></h3>', unsafe_allow_html=True)
            
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

    # --- Tab 2: Detailed Old Regime Inputs ---
    with tab2:
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.markdown('<h2><center> Detailed Income & Deduction Inputs (Old Regime Only)</center></h2>', unsafe_allow_html=True)
        st.markdown("""
        **This section is primarily relevant for the Old Tax Regime.** If you've chosen the New Tax Regime, most of these deductions and separate income calculations are not applicable.
        """)

        with st.expander("Enter Specific Income Sources (Old Regime)"):
            st.subheader("Income from House Property")
            st.number_input(
                "Gross Rental Income (₹)",
                min_value=0, value=st.session_state.get('hp_gross_rent', 0), step=1000, format="%d", key="hp_gross_rent"
            )
            st.number_input(
                "Municipal Taxes Paid (₹)",
                min_value=0, value=st.session_state.get('hp_municipal_tax', 0), step=1000, format="%d", key="hp_municipal_tax"
            )
            nav = max(0, st.session_state.get('hp_gross_rent', 0) - st.session_state.get('hp_municipal_tax', 0))
            st.write(f"Net Annual Value (NAV): ₹{nav:,.2f}")
            hp_standard_deduction = nav * 0.30
            st.write(f"Standard Deduction (30% of NAV): ₹{hp_standard_deduction:,.2f}")

            st.number_input(
                "Interest on Home Loan for House Property (₹)",
                min_value=0, value=st.session_state.get('hp_interest_loan_input', 0), step=1000, format="%d", key="hp_interest_loan_input"
            )
            st.markdown("*(Note: Home loan interest deduction is also separately available under Section 24(b) in the deductions section below, up to ₹2,00,000 for self-occupied property.)*")

            st.subheader("Capital Gains")
            st.number_input(
                "Long Term Capital Gains (LTCG) (₹)",
                min_value=0, value=st.session_state.get('income_ltcg_input', 0), step=1000, format="%d", key="income_ltcg_input"
            )
            st.number_input(
                "Short Term Capital Gains (STCG) (₹)",
                min_value=0, value=st.session_state.get('income_stcg_input', 0), step=1000, format="%d", key="income_stcg_input"
            )
            st.markdown("*(Taxation of capital gains is complex and depends on asset type, holding period, and specific sections. This calculator only takes the amount as input.)*")

            st.subheader("Profits and Gains from Business or Profession (PGBP)")
            st.number_input(
                "Net Income from Business/Profession (₹)",
                min_value=0, value=st.session_state.get('pnbp_input', 0), step=1000, format="%d", key="pnbp_input"
            )
            st.markdown("*(This is a highly complex head. Please enter your net taxable income after all applicable business expenses and depreciation.)*")

            st.subheader("Income from Other Sources")
            st.number_input(
                "Interest Income (Savings, FDs, etc.) (₹)",
                min_value=0, value=st.session_state.get('interest_income_input', 0), step=1000, format="%d", key="interest_income_input"
            )
            st.number_input(
                "Dividend Income (₹)",
                min_value=0, value=st.session_state.get('dividend_income_input', 0), step=1000, format="%d", key="dividend_income_input"
            )
            st.number_input(
                "Casual Income (Lottery, Gambling, etc.) (₹)",
                min_value=0, value=st.session_state.get('casual_income_input', 0), step=1000, format="%d", key="casual_income_input"
            )
            st.markdown("*(Note: Casual income is taxed at a flat 30% without deductions.)*")
        
        with st.expander("Enter Specific Deductions (Old Regime)"):
            st.subheader("Detailed Deductions (Old Regime)")
            st.markdown("*(Enter amounts for applicable deductions. Max limits apply.)*")

            st.number_input(
                "Deduction u/s 80C (Max ₹1,50,000)",
                min_value=0, max_value=150000, value=st.session_state.get('deduction_80c_input', 0), step=1000, format="%d", key="deduction_80c_input"
            )
            st.number_input(
                "Deduction u/s 80D (Health Insurance - Max ₹25k/50k)",
                min_value=0, max_value=50000, value=st.session_state.get('deduction_80d_input', 0), step=1000, format="%d", key="deduction_80d_input"
            )
            st.number_input(
                "Deduction u/s 80CCD(1B) (NPS - Max ₹50,000)",
                min_value=0, max_value=50000, value=st.session_state.get('deduction_80ccd1b_input', 0), step=1000, format="%d", key="deduction_80ccd1b_input"
            )
            st.number_input(
                "Deduction u/s 24(b) (Home Loan Interest - Max ₹2,00,000)",
                min_value=0, max_value=200000, value=st.session_state.get('deduction_24b_input', 0), step=1000, format="%d", key="deduction_24b_input"
            )
            st.number_input(
                "Deduction u/s 80E (Education Loan Interest)",
                min_value=0, value=st.session_state.get('deduction_80e_input', 0), step=1000, format="%d", key="deduction_80e_input"
            )
            st.number_input(
                "Deduction u/s 80G (Donations - Limits Apply)",
                min_value=0, value=st.session_state.get('deduction_80g_input', 0), step=1000, format="%d", key="deduction_80g_input"
            )
            st.number_input(
                "Deduction u/s 80TTA (Savings A/C Interest - Max ₹10,000)",
                min_value=0, max_value=10000, value=st.session_state.get('deduction_80tta_input', 0), step=100, format="%d", key="deduction_80tta_input"
            )
            if st.session_state.get('age_group_radio', 'Below 60 years') in ["60 to 80 years", "Above 80 years"]:
                st.number_input(
                    "Deduction u/s 80TTB (Senior Citizen Savings/FD Interest - Max ₹50,000)",
                    min_value=0, max_value=50000, value=st.session_state.get('deduction_80ttb_input', 0), step=1000, format="%d", key="deduction_80ttb_input"
                )
            
        with st.expander("Exemptions (for info - typically reduce Gross Salary)"):
            st.subheader("Exempt Income & Allowances (Not part of GTI)")
            st.markdown("*(These are usually excluded from Gross Salary before tax calculation. Ensure your 'Gross Salary Income' input reflects this if applicable.)*")
            st.number_input(
                "HRA Exemption (as per rules) (₹)",
                min_value=0, value=st.session_state.get('hra_exemption_info', 0), step=1000, format="%d", key="hra_exemption_info"
            )
            st.number_input(
                "LTA Exemption (as per rules) (₹)",
                min_value=0, value=st.session_state.get('lta_exemption_info', 0), step=1000, format="%d", key="lta_exemption_info"
            )

        st.markdown('</div>', unsafe_allow_html=True) # Close input-section div

    # --- Tab 3: Tax Saving & Investment Insights ---
    with tab3:
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
