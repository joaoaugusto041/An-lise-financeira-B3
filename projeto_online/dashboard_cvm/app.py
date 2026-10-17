import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from loader_b3 import carregar_dados_b3

st.set_page_config(
    page_title="Dashboard Financeiro B3SA3",
    page_icon="📈",
    layout="wide"
)

# Estilização visual corporativa
st.markdown("""
    <style>
        .metric-card {
            background-color: #f8f9fa;
            border-left: 5px solid #1f77b4;
            padding: 12px 18px;
            border-radius: 6px;
            margin-bottom: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .metric-title { font-size: 0.85rem; color: #6c757d; font-weight: 600; text-transform: uppercase; }
        .metric-value { font-size: 1.4rem; font-weight: 700; color: #212529; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard Financeiro B3SA3 — Drill Down Interativo")
st.markdown("Explore os detalhes financeiros com gráficos hierárquicos interativos (estilo Power BI). Clique nas fatias para navegar entre os níveis.")

# --------------------------------------------------
# 1. CARREGAMENTO DOS DADOS DA B3
# --------------------------------------------------
df_b3_raw = carregar_dados_b3()

df_gerencial = pd.DataFrame()
if df_b3_raw is not None:
    colunas_validas = [0]
    nomes_colunas = ["Conta / Indicador"]
    
    for col in range(2, df_b3_raw.shape[1]):
        val_ano = str(df_b3_raw.iloc[1, col]).strip()
        val_trim = str(df_b3_raw.iloc[2, col]).strip()
        
        rotulo = val_trim if val_trim != "nan" and val_trim != "" else val_ano
        if rotulo != "nan" and rotulo != "":
            if rotulo.endswith('.0'):
                rotulo = rotulo[:-2]
            colunas_validas.append(col)
            nomes_colunas.append(rotulo)

    df_gerencial = df_b3_raw.iloc[3:, colunas_validas].copy()
    df_gerencial.columns = nomes_colunas
    df_gerencial = df_gerencial.dropna(subset=["Conta / Indicador"])
    
    # Formatação numérica padrão Brasil (anos limpos sem ponto de milhar)
    for c in df_gerencial.columns[1:]:
        def formatar_valor(val, nome_coluna):
            try:
                if pd.isna(val) or str(val).strip() == "" or str(val).strip().lower() == "nan":
                    return ""
                texto = str(val).strip()
                nome_limpo = str(nome_coluna).replace('.0', '').strip()
                if nome_limpo.isdigit() and len(nome_limpo) == 4:
                    return texto.replace('.0', '')
                num = float(texto)
                return f"{num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except:
                return str(val)
        
        df_gerencial[c] = df_gerencial[c].apply(lambda x: formatar_valor(x, c))

# --------------------------------------------------
# 2. PAINEL DE CONTROLE DE FILTROS GLOBAIS
# --------------------------------------------------
st.markdown("---")
col_f1, col_f2 = st.columns([2, 2])
with col_f1:
    lista_periodos = df_gerencial.columns[1:].tolist() if not df_gerencial.empty else []
    periodo_filtro = st.selectbox(
        "📅 Recorte Temporal para Análise",
        ["Todos os Períodos"] + lista_periodos,
        index=0
    )
with col_f2:
    st.markdown("<br>", unsafe_allow_html=True)
    destacar_oportunidades = st.checkbox("🎯 Destacar Contas Críticas / Oportunidades", value=False)

# --------------------------------------------------
# 3. GRÁFICO DE DRILL DOWN HIERÁRQUICO INTERATIVO (ESTILO POWER BI)
# --------------------------------------------------
st.markdown("#### 🔍 Drill Down Hierárquico: Estrutura de Custos, Tributos e Receitas")
st.caption("💡 *Dica:* Clique em qualquer categoria no gráfico abaixo para 'entrar' nela (drill down) e ver os subníveis detalhados. Clique no centro para voltar.")

# Construção de base hierárquica (Pai -> Filho -> Valor)
dados_hierarquia = pd.DataFrame([
    # Ramo 1: Receitas
    {"Categoria Macro": "Receitas", "Subcategoria": "Renda Variável & Ações", "Valor (R$ mi)": 1150.0},
    {"Categoria Macro": "Receitas", "Subcategoria": "Renda Fixa & Derivativos", "Valor (R$ mi)": 980.0},
    {"Categoria Macro": "Receitas", "Subcategoria": "Serviços de Tecnologia e Dados", "Value": 355.0, "Valor (R$ mi)": 355.0},
    {"Categoria Macro": "Receitas", "Subcategoria": "Outras Receitas Operacionais", "Valor (R$ mi)": 383.0},
    
    # Ramo 2: Despesas Operacionais (Drill down detalhado)
    {"Categoria Macro": "Despesas Operacionais", "Subcategoria": "Pessoal: Salários e Encargos", "Valor (R$ mi)": 285.0},
    {"Categoria Macro": "Despesas Operacionais", "Subcategoria": "Pessoal: Bônus e DHO", "Valor (R$ mi)": 110.2},
    {"Categoria Macro": "Despesas Operacionais", "Subcategoria": "TI: Licenças de Software & Cloud", "Valor (R$ mi)": 165.4},
    {"Categoria Macro": "Despesas Operacionais", "Subcategoria": "TI: Links e Processamento", "Valor (R$ mi)": 82.1},
    {"Categoria Macro": "Despesas Operacionais", "Subcategoria": "Terceiros: Consultorias e Jurídico", "Valor (R$ mi)": 95.3},
    {"Categoria Macro": "Despesas Operacionais", "Subcategoria": "Terceiros: Market Maker", "Valor (R$ mi)": 42.0},
    {"Categoria Macro": "Despesas Operacionais", "Subcategoria": "Amortização de Intangíveis (Cetip)", "Valor (R$ mi)": 125.8},
    {"Categoria Macro": "Despesas Operacionais", "Subcategoria": "Despesas Administrativas Diversas", "Valor (R$ mi)": 39.4},

    # Ramo 3: Tributos e Impostos
    {"Categoria Macro": "Tributos e Impostos", "Subcategoria": "PIS / COFINS", "Valor (R$ mi)": 185.4},
    {"Categoria Macro": "Tributos e Impostos", "Subcategoria": "Imposto de Renda (IRPJ)", "Valor (R$ mi)": 145.2},
    {"Categoria Macro": "Tributos e Impostos", "Subcategoria": "ISS (Municipal)", "Valor (R$ mi)": 92.1},
    {"Categoria Macro": "Tributos e Impostos", "Subcategoria": "CSLL", "Valor (R$ mi)": 58.3}
])

# Gráfico Sunburst (Hierarquia interativa estilo drill down)
fig_sunburst = px.sunburst(
    dados_hierarquia,
    path=["Categoria Macro", "Subcategoria"],
    values="Valor (R$ mi)",
    color="Valor (R$ mi)",
    color_continuous_scale="RdBu",
    title="<b>Navegação Hierárquica por Clique (Clique nas fatias para abrir os detalhes)</b>"
)
fig_sunburst.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=40, b=20, l=20, r=20)
)
st.plotly_chart(fig_sunburst, use_container_width=True)

# --------------------------------------------------
# 4. GRÁFICOS DE COLUNAS INTERATIVOS (COMPARATIVO TRIMESTRAL)
# --------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📊 EBITDA Reportado vs. Recorrente por Trimestre")
    df_ebitda_comp = pd.DataFrame({
        "Período": ["1T25", "2T25", "3T25", "4T25", "1T26"],
        "EBITDA Reportado": [1680, 1710, 1730, 1620, 1700],
        "EBITDA Recorrente": [1722, 1735, 1742, 1660, 1742]
    })
    fig_bar = px.bar(
        df_ebitda_comp, x="Período", y=["EBITDA Reportado", "EBITDA Recorrente"],
        barmode="group", color_discrete_sequence=["#aec7e8", "#1f77b4"],
        title="<b>Evolução de Geração de Caixa Operacional</b>"
    )
    fig_bar.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.markdown("#### 📈 Evolução das Margens de Rentabilidade (%)")
    df_margens = pd.DataFrame({
        "Período": ["1T24", "2T24", "3T24", "4T24", "1T25", "2T25", "3T25", "4T25", "1T26"],
        "Margem EBITDA Recorrente (%)": [69.5, 70.2, 71.1, 68.8, 71.5, 72.0, 72.4, 70.0, 72.8],
        "Margem Líquida (%)": [42.1, 43.5, 44.0, 41.2, 44.5, 45.0, 45.8, 43.1, 46.2]
    })
    fig_linhas = px.line(
        df_margens, x="Período", y=["Margem EBITDA Recorrente (%)", "Margem Líquida (%)"],
        markers=True, color_discrete_sequence=["#1f77b4", "#2ca02c"],
        title="<b>Eficiência de Conversão de Receita</b>"
    )
    fig_linhas.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_linhas, use_container_width=True)

# --------------------------------------------------
# 5. DRE GERENCIAL COMPLETO (B3 - API RI)
# --------------------------------------------------
st.markdown("---")
st.subheader("📋 DRE Gerencial Completo — B3 (API RI)")
st.markdown("🔎 *Ferramentas de Análise:* Filtre períodos, pesquise contas e localize oportunidades de middle-line instantaneamente.")

if df_b3_raw is not None and not df_gerencial.empty:
    
    col_sel1, col_sel2 = st.columns([2, 2])
    with col_sel1:
        tipo_visao = st.selectbox(
            "🎛️ Visão Temporal da Tabela",
            ["Visão Completa (Trimestres e Anos)", "Apenas Anos Consolidados", "Apenas Trimestres"],
            index=0
        )
    with col_sel2:
        destacar_oportunidades_tabela = st.checkbox("🎯 Modo Foco / Auditoria", value=destacar_oportunidades)

    colunas_atuais = df_gerencial.columns.tolist()
    colunas_anos = [c for c in colunas_atuais if str(c).replace('.0', '').strip().isdigit() and len(str(c).replace('.0', '').strip()) == 4]
    colunas_trim = [c for c in colunas_atuais if c not in colunas_anos and c != "Conta / Indicador"]

    if periodo_filtro != "Todos os Períodos" and periodo_filtro in colunas_atuais:
        colunas_filtradas = [colunas_atuais[0], periodo_filtro]
        df_exibicao = df_gerencial[colunas_filtradas].copy()
    else:
        if tipo_visao == "Apenas Anos Consolidados":
            colunas_filtradas = [colunas_atuais[0]] + colunas_anos
            df_exibicao = df_gerencial[colunas_filtradas].copy()
        elif tipo_visao == "Apenas Trimestres":
            colunas_filtradas = [colunas_atuais[0]] + colunas_trim
            df_exibicao = df_gerencial[colunas_filtradas].copy()
        else:
            df_exibicao = df_gerencial.copy()

    busca_b3 = st.text_input(
        "🔍 Pesquisar conta ou indicador específico no DRE",
        placeholder="Ex.: EBITDA, Despesas de Pessoal, Impostos, Lucro líquido, Intangível...",
        key="busca_b3"
    )

    if busca_b3:
        mascara_b3 = df_exibicao["Conta / Indicador"].astype(str).str.contains(busca_b3, case=False, na=False)
        df_exibicao = df_exibicao[mascara_b3]
    elif destacar_oportunidades_tabela:
        termos_foco = ["EBITDA", "Despesas", "Lucro", "Receita Líquida", "Impostos", "Tecnologia"]
        padrao = "|".join(termos_foco)
        df_exibicao = df_exibicao[df_exibicao["Conta / Indicador"].astype(str).str.contains(padrao, case=False, na=False)]

    st.dataframe(
        df_exibicao,
        use_container_width=True,
        hide_index=True,
        height=520,
    )

    csv_b3 = df_exibicao.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")
    st.download_button(
        "⬇️ Exportar Tabela DRE Ajustada para CSV / Excel",
        data=csv_b3,
        file_name="B3SA3_DRE_Gerencial_DrillDown.csv",
        mime="text/csv",
    )
else:
    st.warning("⚠️ Não foi possível carregar os dados gerenciais da B3 no momento.")
