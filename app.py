#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st

# ... (rest of your tax calculation functions remain unchanged) ...

# --- Streamlit UI ---
def main():
    # >>> MOVE THIS LINE TO THE VERY TOP OF THE MAIN FUNCTION <<<
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

    # ... (rest of your main function code) ...

if __name__ == "__main__":
    main()
