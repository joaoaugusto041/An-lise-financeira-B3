import io
import requests
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup

@st.cache_data(show_spinner=False)
def carregar_dados_b3():
    try:
        # Acessa a página de resultados da B3 para capturar o link mais recente da planilha de DRE/Resultados
        url_ri = "https://ri.b3.com.br/informacoes-financeiras/planilhas-interativas/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(url_ri, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Procura pelo link do Excel (.xlsx) na página de RI
        link_excel = None
        for a in soup.find_all("a", href=True):
            if ".xlsx" in a["href"] or "mzfilemanager" in a["href"]:
                link_excel = a["href"]
                break
                
        if not link_excel:
            return None
            
        # Faz o download do arquivo encontrado no site
        res_excel = requests.get(link_excel, headers=headers, timeout=60)
        res_excel.raise_for_status()
        
        excel_file = pd.ExcelFile(io.BytesIO(res_excel.content))
        df = pd.read_excel(excel_file, sheet_name="IS (New Seg)", header=None)
        return df
        
    except Exception as e:
        print(f"Erro ao buscar dados no site da B3: {e}")
        return None
