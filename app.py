#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import requests # For making API calls
import pandas as pd # For potential data processing from API responses

# --- Configuration ---
# IMPORTANT: Replace with your actual Alpha Vantage API Key
ALPHA_VANTAGE_API_KEY = "O1PB5ILLRT2BRIR2"

# --- Main Streamlit Application ---
def main():
    st.set_page_config(page_title="FinBot: Your Financial Assistant", layout="centered")

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
        .chat-message {
            padding: 10px 15px;
            border-radius: 15px;
            margin-bottom: 10px;
            max-width: 70%;
            display: inline-block;
        }
        .user-message {
            background-color: #EBF5FB; /* Light blue */
            color: #333333;
            float: right;
            border-bottom-right-radius: 2px;
        }
        .bot-message {
            background-color: #D6EAF8; /* Slightly darker blue */
            color: #333333;
            float: left;
            border-bottom-left-radius: 2px;
        }
        .stTextInput > div > div > input {
            border-radius: 20px;
            padding: 10px 15px;
        }
        .stButton button {
            border-radius: 20px;
            padding: 10px 20px;
            background-color: #2E86C1;
            color: white;
            border: none;
            font-weight: bold;
        }
        .stButton button:hover {
            background-color: #1A5276;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<p class="header-title">📊 FinBot</p>', unsafe_allow_html=True)
    st.markdown('<p class="header-subtitle">Your Intelligent Financial Assistant</p>', unsafe_allow_html=True)

    # --- Initialize Chat History ---
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "bot", "content": "Hello! I'm FinBot. I can help you with basic stock prices. What stock are you interested in today?"})

    # --- Display Chat Messages ---
    for message in st.session_state.messages:
        with st.container():
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message bot-message">{message["content"]}</div>', unsafe_allow_html=True)
            st.write("") # Add a bit of spacing

    # --- User Input & Chat Logic ---
    st.write("---") # Separator for input area

    user_query = st.text_input("Ask FinBot a question...", key="user_input")

    if st.button("Send", key="send_button") and user_query:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_query})

        # --- Generate Chatbot Response ---
        # No more delinquency_df passed, as we removed local data
        bot_response = generate_bot_response(user_query)

        # Add bot response to history
        st.session_state.messages.append({"role": "bot", "content": bot_response})

        # Clear input box (optional)
        st.session_state.user_input = ""
        st.rerun() # Rerun to update chat display

def get_stock_price(symbol):
    """
    Fetches the latest stock price for a given symbol using Alpha Vantage.
    """
    if not ALPHA_VANTAGE_API_KEY or ALPHA_VANTAGE_API_KEY == "YOUR_ALPHA_VANTAGE_API_KEY":
        return "Please set your Alpha Vantage API key in the code to fetch live data."

    # Alpha Vantage API endpoint for Global Quote
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if "Global Quote" in data and data["Global Quote"]:
            quote = data["Global Quote"]
            # Alpha Vantage returns keys like '05. price', '02. open', etc.
            price = quote.get("05. price")
            open_price = quote.get("02. open")
            high_price = quote.get("03. high")
            low_price = quote.get("04. low")
            volume = quote.get("06. volume")
            last_trading_day = quote.get("07. latest trading day")

            if price:
                return (
                    f"The current price of {symbol.upper()} is ${float(price):,.2f}. "
                    f"Today's Open: ${float(open_price):,.2f}, High: ${float(high_price):,.2f}, Low: ${float(low_price):,.2f}. "
                    f"Volume: {int(float(volume)):,}. Last trading day: {last_trading_day}."
                )
            else:
                return f"Could not retrieve price for {symbol.upper()}. It might be an invalid symbol or no data available."
        elif "Error Message" in data:
            return f"Error from API: {data['Error Message']}. Please check the stock symbol or API key."
        else:
            return "Could not retrieve stock information. The API response was not as expected."
    except requests.exceptions.RequestException as e:
        return f"An error occurred while connecting to the API: {e}. Please try again later."
    except ValueError:
        return "Could not parse API response. Please try again."

def generate_bot_response(query):
    """
    Enhanced function to include stock price lookup via Alpha Vantage API.
    """
    query_lower = query.lower()

    if "hello" in query_lower or "hi" in query_lower:
        return "Hello there! How can I help you with finance today?"
    elif "stock price of" in query_lower or "what is the price of" in query_lower:
        # Simple extraction for demonstration. For robustness, use NLU.
        parts = query_lower.split("stock price of") if "stock price of" in query_lower else query_lower.split("what is the price of")
        symbol_candidate = parts[-1].strip().replace("?", "").replace(".", "").split(" ")[0] # Get first word after phrase

        # Basic symbol extraction, might need refinement for complex queries
        if symbol_candidate:
            return get_stock_price(symbol_candidate.upper())
        else:
            return "Please specify the stock symbol (e.g., AAPL, GOOG, MSFT)."
    elif "thank you" in query_lower or "thanks" in query_lower:
        return "You're welcome! Feel free to ask more questions."
    else:
        return "I'm a financial assistant! You can ask me for stock prices (e.g., 'What is the stock price of AAPL?'). I'm still learning more about other financial questions."

if __name__ == "__main__":
    main()

