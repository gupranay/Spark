import streamlit as st
import requests
import json
import pandas as pd
import re

def send_data_to_make(industry):
    make_webhook_url = f'https://hook.us1.make.com/rru8an438cktoaf51f3j8pd86oiigmqt?industry={industry}'

    # Send the POST request
    response = requests.post(make_webhook_url, data={})

    if response.status_code == 200:
        st.success("Data pulled from Salesforce successfully.")
        response_text = response.text.strip()  # Get the response text

        if response_text:

            # Prepare the response text for JSON parsing using regex
            entries = re.findall(r'\{[^}]+\}', response_text)

            items = []
            for entry in entries:
                entry = entry.strip()
                
                try:
                    item = json.loads(entry)
                    items.append(item)
                except Exception as e:
                    st.write(f"Error parsing entry: {e}")
                    st.write(entry)
            
            # Convert the list of dictionaries into a pandas DataFrame
            df = pd.DataFrame(items)
            
            # Display the DataFrame as a table in Streamlit
            st.table(df)
        else:
            st.write("No response content.")
    else:
        st.error(f"Error: {response.status_code}")
        st.error(response.text)  # Display the error message

def main():
    st.title("Pull Consultant Data from Salesforce")
    st.write("Select an industry experience")

    # Static list of industry options for simplicity
    industry_options = [
        "Accounting", "Advanced Manufacturing", "Advanced Materials", "Aeronautics", 
        "Alt Energy-Battery", "Alt Energy-Solar", "Alt Energy-Wind", "Alternative Energy", 
        "Auto-Connected Vehicle", "Auto-Design", "Auto-Engineering", "Automotive", 
        "Biofuels", "Business Services", "Call Center", "Cannabis", "Clean Technology", 
        "Communications", "Digital Media", "Education", "Energy", "Engineering", 
        "Environmental", "Financial Services", "Food & Beverage processing", "Headquarters", 
        "Healthcare", "Home Improvement", "Homeland Security", "Hospitality", 
        "Human Resources", "Information Technology", "Insurance Provider", "Internet Security", 
        "IT-Applications", "IT-Database Management", "IT-Infrastructure", "IT-Networking/Computers-Hardware", 
        "IT-Social Networking", "Landscape /Lawn Care", "Legal", "Legal-Corporate", 
        "Legal-IP", "Life Science - Bioagriculture", "Life Science - Medical Device", 
        "Life Science - Other", "Life Science - Pharma/Biotech", "Liquor", "Logistics", 
        "Manufacturing", "MEMS", "Mobility", "Non-profit agencies", "Optics", "R&D", 
        "Real Estate", "Retail", "Software", "Software - SaaS", "Space/Satellites", 
        "Sports", "Telecom", "Water Testing"
    ]

    # Create a dropdown for industry selection
    selected_industry = st.selectbox("Select Industry", industry_options)

    # Add a button to trigger the sending of data to Make
    if st.button("Pull Data"):
        send_data_to_make(selected_industry)

if __name__ == "__main__":
    main()
