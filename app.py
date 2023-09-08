import streamlit as st
import requests
from lxml import etree
import pandas as pd

def fetch_13F(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        return None

def parse_13F(xml_data):
    tree = etree.fromstring(xml_data)
    rows = []
    for infoTable in tree.xpath('//infoTable'):
        row = {}
        for element in infoTable:
            row[element.tag] = element.text
        rows.append(row)
    return pd.DataFrame(rows)

def main():
    st.title("SEC 13F Filings")

    # For demonstration, a sample 13F XML URL is provided
    sample_url = "https://www.sec.gov/Archives/edgar/data/0001166559/000116655920000003/xslForm13F_X01/form13fInfoTable.xml"

    st.write("Sample 13F XML URL: ", sample_url)

    url_input = st.text_input("Enter the 13F XML URL:", sample_url)

    if st.button("Fetch and Display 13F Data"):
        xml_data = fetch_13F(url_input)
        if xml_data:
            df = parse_13F(xml_data)
            st.dataframe(df)
        else:
            st.warning("Could not fetch the 13F data.")

if __name__ == "__main__":
    main()
