import streamlit as st
import pandas as pd
import os
from loader_b3 import carregar_dados_b3

st.set_page_config(
    page_title="Dashboard Financeiro B3SA3",
    page_icon="📈",
    layout="wide"
)

st.title("📊 Dashboard Financeiro B3SA3")
st.markdown("Análise financeira integrada: Dados padronizados da CVM e DRE Gerencial Detalhado da B3.")

# --------------------------------------------------
# CONFIGURAÇÃO DE PERÍODOS E CARREGAMENTO CVM (SE HOUVER)
# --------------------------------------------------
PERIODOS = ["2020", "2021", "2022", "2023", "2024", "2025", "1T26"]

# Tentativa de carregar dados locais da CVM (se existirem na pasta dados)
dados = pd.DataFrame()
caminho_dados = "dados"
if os.path.exists(caminho_dados):
    # Lógica opcional caso coloque os zips futuramente
    pass

# --------------------------------------------------
# TRATAMENTO SEGURO DA CVM
# --------------------------------------------------
if not dados.empty:
    tabela = dados.pivot_table(
        index=["CD_CONTA", "DS_CONTA"],
        columns="Periodo",
        values="Valor",
        aggfunc="first",
    ).reset_index()

    for periodo in PERIODOS:
        if periodo not in tabela.columns:
            tabela[periodo] = float("nan")

    tabela = tabela[["CD_CONTA", "DS_CONTA"] + PERIODOS].copy()
    tabela.columns.name = None
else:
    tabela = pd.DataFrame()
    st.info("💡 **Modo Online:** Os dados padronizados da CVM exigem os arquivos locais. Exibindo abaixo o **DRE Gerencial Completo obtido via API da B3**.")

# --------------------------------------------------
# DRE GERENCIAL COMPLETO (B3 - API RI)
# --------------------------------------------------
st.markdown("---")
st.subheader("DRE Gerencial Completo — B3 (API RI)")
st.caption("Detalhamento completo (Receitas, Despesas, EBITDA, Ajustes, Hedge) obtido diretamente da planilha oficial de resultados da B3 (Aba 'IS (New Seg)'). Valores em R$ mil.")

df_b3_raw = carregar_dados_b3()

if df_b3_raw is not None:
    colunas_validas = [0]
    nomes_colunas = ["Conta / Indicador"]
    
    for col in range(2, df_b3_raw.shape[1]):
        val_ano = str(df_b3_raw.iloc[1, col]).strip()
        val_trim = str(df_b3_raw.iloc[2, col]).strip()
        
        rotulo = val_trim if val_trim != "nan" and val_trim != "" else val_ano
        if rotulo != "nan" and rotulo != "":
            colunas_validas.append(col)
            nomes_colunas.append(rotulo)

    # Pega da linha 3 até o final
    df_gerencial = df_b3_raw.iloc[3:, colunas_validas].copy()
    df_gerencial.columns = nomes_colunas
    df_gerencial = df_gerencial.dropna(subset=["Conta / Indicador"])
    
    # Converte todas as colunas de valores para string/objeto para evitar erro do Arrow no Streamlit
    for c in df_gerencial.columns[1:]:
        df_gerencial[c] = df_gerencial[c].astype(str).str.replace('nan', '')

    # Campo de busca para filtrar rapidamente
    busca_b3 = st.text_input(
        "Pesquisar no DRE Gerencial da B3",
        placeholder="Ex.: EBITDA, Despesas, Lucro recorrente, Mercados...",
        key="busca_b3"
    )

    if busca_b3:
        mascara_b3 = df_gerencial["Conta / Indicador"].astype(str).str.contains(busca_b3, case=False, na=False)
        df_gerencial = df_gerencial[mascara_b3]

    st.dataframe(
        df_gerencial,
        use_container_width=True,
        hide_index=True,
        height=550,
    )

    csv_b3 = df_gerencial.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")
    st.download_button(
        "⬇️ Exportar DRE Gerencial B3 para CSV",
        data=csv_b3,
        file_name="B3SA3_DRE_Gerencial_Completo_B3.csv",
        mime="text/csv",
    )
else:
    st.warning("⚠️ Não foi possível carregar os dados gerenciais da B3 no momento (verifique a conexão com a API de RI).")
