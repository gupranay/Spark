import streamlit as st
import requests
import pandas as pd
import json
from bs4 import BeautifulSoup

def send_data_to_make(category_id):
    # st.write(category_id)
    secret_url = st.secrets["MAKE_URL_V2"]
    
    make_webhook_url = f'{secret_url}?category_id={category_id}'
    
    payload = {}
    response = requests.request("POST", make_webhook_url, data=payload)

    if response.status_code == 200:
        st.success("Pulled data from Salesforce successfully.")
        response_text = response.text.strip()
        
        if response_text:
            # st.write("Response from Make:")
            # st.write(response_text)
            try:
                # Parse the JSON response
                json_data = json.loads(response_text)
                return json_data
            except json.JSONDecodeError:
                st.error("Failed to parse JSON response.")
                return None
        else:
            st.write("No response content.")
            return None
    else:
        st.error(f"Error: {response.status_code}")
        st.error(response.text)
        return None

def extract_rows(data):
    # Extract column headers
    columns_info = data['reportExtendedMetadata']['detailColumnInfo']
    column_headers = [value['label'] for value in columns_info.values()]
    
    extracted_data = []
    fact_map = data['factMap']
    
    for key, group in fact_map.items():
        if key == "T!T":
            continue
        rows = group["rows"]
        for row in rows:
            row_data = {}
            for i, cell in enumerate(row["dataCells"]):
                column_name = column_headers[i]
                cell_value = cell.get("label", "")
                # If cell value contains HTML, parse and extract the link text
                if "<a href=" in cell_value:
                    soup = BeautifulSoup(cell_value, "html.parser")
                    link = soup.find("a")
                    if link and link.text:
                        cell_value = link.text.strip()
                row_data[column_name] = cell_value
            extracted_data.append(row_data)
    
    return extracted_data, column_headers

def main():
    st.title("Pull Consultant Data from Salesforce")

    # Dictionary of categories and their corresponding IDs
    categories = {
        "Video": "00O38000004giwtEAA",
        "Branding": "00O38000004ghWpEAI",
        "Designers": "00O38000004gR4TEAU",
        "Website": "00O38000004ghMuEAI",
        "UI/UX": "00O38000004eUfBEAU",
        "All": "00O38000004QRwJEAW",
        "Marketing": "00O38000004ghMBEAY",
        "Accountants": "00O38000004gR4OEAU",
        "AR/VR": "00O0z000005I1NQEA0",
        "PR": "00O0z000005IMFNEA4",
        "Legal": "00O38000004gR4EEAU",
        "Software": "00O38000004stl2EAA",
        "HR": "00O0z000005TmfdEAC",
        "PR/Communications Consultants": "00O4z0000064iFkEAI",
        "UI/Ux, Software Development Contacts": "00O4z0000064t8QEAQ",
        "Legal/ Intellectual Property Contacts": "00O4z0000064tA2EAI",
        "EIR": "00O38000004spAvEAI",
        "Insurance (8-21)": "00O4z0000061DkMEAU",
        "Mobility Consultants": "00O4z0000061GZ7EAM",
        "Consumer Products and Services Industry": "00O4z0000061N75EAE",
        "Insurance": "00O4z0000064w8nEAA",
        "Photography": "00O4z0000069k6CEAQ",
        "IP": "00O38000004gR4JEAU",
        "BootCamp Mentors": "00O4z000005mO0oEAE",
        "Writers": "00O4z000006OiN5EAK"
    }

    # Create a dropdown for category selection
    selected_category_name = st.selectbox("Select a category of consultants", list(categories.keys()))

    # Find the corresponding ID for the selected category name
    selected_category_id = categories[selected_category_name]

    # Add a button to trigger the sending of data to Make
    if st.button("Pull Data"):
        json_data = send_data_to_make(selected_category_id)
        if json_data:
            # Extract relevant data from JSON
            extracted_data, column_headers = extract_rows(json_data)
            
            # Convert the extracted data to a DataFrame
            df = pd.DataFrame(extracted_data, columns=column_headers)
            
            # Display the DataFrame in Streamlit
            # st.write("Extracted Data")
            st.dataframe(df)

if __name__ == "__main__":
    main()
