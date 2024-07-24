import streamlit as st
import requests
import pandas as pd
import json
from bs4 import BeautifulSoup
from PIL import Image

def send_data_to_make(category_id):
    secret_url = st.secrets["MAKE_URL_V2"]
    
    make_webhook_url = f'{secret_url}?category_id={category_id}'
    
    payload = {}
    response = requests.request("POST", make_webhook_url, data=payload)

    if response.status_code == 200:
        response_text = response.text.strip()
        
        if response_text:
            try:
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
    columns_info = data['reportExtendedMetadata']['detailColumnInfo']
    column_headers = ['*'] + [value['label'] for value in columns_info.values()]  # Add a column for the warning icon

    extracted_data = []
    fact_map = data['factMap']
    
    for key, group in fact_map.items():
        if key == '3!T' or key == '4!T':
            continue

        rows = group["rows"]
        for row in rows:
            row_data = {}
            for i, cell in enumerate(row["dataCells"]):
                column_name = column_headers[i + 1]  # Offset by 1 due to the warning icon column
                cell_value = cell.get("label", "")
                if "<a href=" in cell_value:
                    soup = BeautifulSoup(cell_value, "html.parser")
                    link = soup.find("a")
                    if link and link.text:
                        cell_value = link.text.strip()
                row_data[column_name] = cell_value

            # Add a warning icon if the key is '2!T'
            if key == '2!T':
                row_data['*'] = '*'
            else:
                row_data['*'] = ''

            extracted_data.append(row_data)
    
    return extracted_data, column_headers

def main():
    im = Image.open("spark_logo.png")
    st.set_page_config(page_title="Spark Consultant Data", page_icon=im, layout="wide")
    st.title("Pull Consultant Data from Salesforce")
    # "⚡️"

    categories = {
        "Branding": "00O38000004ghWpEAI",
        "Designers": "00O38000004gR4TEAU",
        "Website": "00O38000004ghMuEAI",
        "UI/UX": "00O38000004eUfBEAU",
        "Marketing": "00O38000004ghMBEAY",
        "Accountants": "00O38000004gR4OEAU",
        "AR/VR": "00O0z000005I1NQEA0",
        "PR": "00O0z000005IMFNEA4",
        "Legal": "00O38000004gR4EEAU",
        "Software": "00O38000004stl2EAA",
        "HR": "00O0z000005TmfdEAC",
        "PR/Communications Consultants": "00O4z0000064iFkEAI",
        "EIR": "00O38000004spAvEAI",
        "Insurance": "00O4z0000064w8nEAA",
        "Photography": "00O4z0000069k6CEAQ",
        "IP": "00O38000004gR4JEAU",
        "BootCamp Mentors": "00O4z000005mO0oEAE",
        "Writers": "00O4z000006OiN5EAK"
    }

    selected_category_name = st.selectbox("Select a category of consultants", list(categories.keys()))
    selected_category_id = categories[selected_category_name]

    if st.button("Pull Data"):
        json_data = send_data_to_make(selected_category_id)
        if json_data:
            extracted_data, column_headers = extract_rows(json_data)
            
            df = pd.DataFrame(extracted_data, columns=column_headers)
            
            st.session_state['dataframe'] = df
            st.session_state['column_headers'] = column_headers

    if 'dataframe' in st.session_state:
        df = st.session_state['dataframe']
        column_headers = st.session_state['column_headers']
        search_value = st.text_input("Enter search value")

        if search_value:
            filtered_df = df[
                df['Description'].str.contains(search_value, case=False, na=False) |
                df['Functional Expertise'].str.contains(search_value, case=False, na=False)
            ]
        else:
            filtered_df = df
        
        st.dataframe(filtered_df)

        # Display note explaining the warning icon
        st.markdown("""
        **Note:** Rows marked with * indicate that the vendor is not an established vendor with Spark and Spark holds no responsibility.
        """)

if __name__ == "__main__":
    main()
