import io
import requests
import pandas as pd
import streamlit as st

URL_B3 = "https://api.mziq.com/mzfilemanager/v2/d/5fd7b7d8-54a1-472d-8426-eb896ad8a3c4/b49b75fa-208b-11af-d633-b02f2465f058?origin=2"

@st.cache_data(show_spinner=False)
def carregar_dados_b3():
    try:
        response = requests.get(URL_B3, timeout=60)
        response.raise_for_status()
        excel_file = pd.ExcelFile(io.BytesIO(response.content))
        df = pd.read_excel(excel_file, sheet_name="IS (New Seg)", header=None)
        return df
    except Exception as e:
        return None

