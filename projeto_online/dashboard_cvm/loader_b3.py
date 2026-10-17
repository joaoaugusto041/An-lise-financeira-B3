import io
import requests
import pandas as pd
import streamlit as st

# Link direto permanente da última planilha interativa de resultados da B3 (Aba IS (New Seg))
URL_B3_DIRETO = "https://api.mziq.com/mzfilemanager/v2/d/5fd7b7d8-54a1-472d-8426-eb896ad8a3c4/b49b75fa-208b-11af-d633-b02f2465f058?origin=2"

@st.cache_data(show_spinner=False)
def carregar_dados_b3():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://ri.b3.com.br/"
        }
        
        # Tenta o download direto otimizado com cabeçalhos de navegador
        response = requests.get(URL_B3_DIRETO, headers=headers, timeout=60)
        response.raise_for_status()
        
        excel_file = pd.ExcelFile(io.BytesIO(response.content))
        df = pd.read_excel(excel_file, sheet_name="IS (New Seg)", header=None)
        return df
        
    except Exception as e:
        print(f"Erro ao carregar dados da B3: {e}")
        return None
