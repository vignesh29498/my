import streamlit as st
import pandas as pd
import numpy as np
import json
import os

# Set up the Streamlit page configuration
st.set_page_config(layout="wide", page_title="Excel Pivot Viewer")

# Load configuration
CONFIG_FILE = "config.json"
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

config = load_config()

st.title("Excel Pivot Table Viewer")
st.markdown("""
This application displays multiple pivot tables from your Excel sheet in the order specified in your `config.json` file.
""")

# Configuration inputs
st.sidebar.header("Configuration")

# Use config values as defaults
default_excel = config.get("excel_file", "")
default_sheet = config.get("sheet_name", "")
pivot_order = config.get("pivot_order", [])

uploaded_file = st.sidebar.file_uploader("1. Upload Excel File", type=["xlsx", "xls"])

# If no file uploaded, try to load the default one from config
excel_source = uploaded_file
if excel_source is None and default_excel and os.path.exists(default_excel):
    excel_source = default_excel
    st.sidebar.info(f"Using default file: {default_excel}")

if excel_source is not None:
    try:
        # Load the Excel file
        xls = pd.ExcelFile(excel_source)
        sheet_names = xls.sheet_names
        
        # Select sheet - try to default to config
        default_sheet_idx = 0
        if default_sheet in sheet_names:
            default_sheet_idx = sheet_names.index(default_sheet)
            
        selected_sheet = st.sidebar.selectbox("2. Select Sheet Name", options=sheet_names, index=default_sheet_idx)
        
        st.sidebar.subheader("Pivot Order (from config)")
        for p in pivot_order:
            st.sidebar.text(f"• {p}")

        if st.sidebar.button("Load All Pivot Tables") or (excel_source and not uploaded_file):
            with st.spinner("Extracting tables..."):
                # Read the sheet without headers
                df = pd.read_excel(excel_source, sheet_name=selected_sheet, header=None)
                
                for pivot_heading in pivot_order:
                    # Search for the heading
                    found = False
                    start_row = 0
                    start_col = 0
                    
                    for r_idx, row in df.iterrows():
                        for c_idx, val in row.items():
                            if pd.notna(val) and isinstance(val, str):
                                if pivot_heading.strip().lower() in val.strip().lower():
                                    start_row = r_idx
                                    start_col = c_idx
                                    found = True
                                    break
                        if found:
                            break
                            
                    if not found:
                        st.warning(f"Heading '{pivot_heading}' not found in the sheet '{selected_sheet}'.")
                        continue
                    
                    # Find the extent of the table (end row)
                    end_row = df.shape[0]
                    for r in range(start_row + 1, df.shape[0]):
                        row_data = df.iloc[r, start_col:]
                        if row_data.isna().all() or (row_data == "").all():
                            end_row = r
                            break
                            
                    # Find the extent of the table (end col)
                    header_row_idx = start_row
                    if start_row + 1 < end_row:
                        if df.iloc[start_row+1, start_col:].notna().sum() > df.iloc[start_row, start_col:].notna().sum():
                            header_row_idx = start_row + 1
                            
                    end_col = df.shape[1]
                    for c in range(start_col, df.shape[1]):
                        col_data = df.iloc[header_row_idx:end_row, c]
                        if col_data.isna().all() or (col_data == "").all():
                            end_col = c
                            break
                            
                    # Extract and display
                    extracted_df = df.iloc[start_row:end_row, start_col:end_col].copy()
                    extracted_df = extracted_df.fillna("")
                    
                    st.markdown(f"### {pivot_heading}")
                    st.dataframe(extracted_df, use_container_width=True)
                    st.markdown("---")
                        
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Awaiting file upload or default file in config.json...")

